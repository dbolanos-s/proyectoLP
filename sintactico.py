# -*- coding: utf-8 -*-
"""
Analizador sintáctico para un subconjunto de PHP (PLY - módulo yacc).  Avance 2.

Usa los tokens que define lexico.py.  Igual que en el léxico, el archivo se divide
en ZONAS: cada integrante escribe sus reglas dentro de su zona, entre los comentarios
INICIO / FIN, y no modifica las de los demás.

Cada regla se escribe como una función p_...(p) cuyo docstring es la gramática.
"""
import sys
import ply.yacc as yacc

import lexico
from lexico import tokens          # yacc necesita la lista de tokens del léxico

sint_errors = []                   # errores sintácticos del último análisis
uso = {}                           # cuántas veces se reconoció cada estructura
_parser = None
_lexer = None


def regla(nombre):
    """Cuenta una estructura reconocida (para el resumen del log)."""
    uso[nombre] = uso.get(nombre, 0) + 1


# Precedencia de operadores: cada integrante agrega la suya (mayor precedencia al final).
precedence_i1, precedence_i2, precedence_i3 = [], [], []

start = 'program'


# ---------------------------------------------------------------------------
# BASE COMÚN (no modificar): programa, sentencias y expresiones primarias.
# Sobre esta base cada integrante agrega sus reglas.
# ---------------------------------------------------------------------------
def p_program(p):
    '''program : OPEN_TAG statement_list CLOSE_TAG
               | OPEN_TAG statement_list'''
    p[0] = ('program', p[2])


def p_statement_list(p):
    '''statement_list : statement_list statement
                      | empty'''
    p[0] = (p[1] or []) + [p[2]] if len(p) == 3 else []


def p_empty(p):
    'empty :'
    p[0] = None


def p_block(p):
    'block : LBRACE statement_list RBRACE'
    p[0] = ('block', p[2])


def p_statement_expr(p):
    'statement : expression SEMI'
    p[0] = ('expr', p[1])


def p_statement_assign(p):
    'statement : expression ASSIGN expression SEMI'
    # el lado izquierdo debe ser una variable o un elemento de arreglo
    if p[1][0] not in ('var', 'index'):
        sint_errors.append({'tipo': 'sintáctico', 'linea': p.lineno(2), 'columna': _col(p, 2),
                            'mensaje': 'el lado izquierdo de la asignación debe ser una variable '
                                       'o un elemento de arreglo'})
    regla('asignación')
    p[0] = ('assign', p[1], p[3])


def p_statement_error(p):
    'statement : error SEMI'
    p[0] = ('error',)


def p_expression_literal(p):
    '''expression : INT
                  | FLOAT
                  | STRING
                  | TRUE
                  | FALSE
                  | NULL'''
    p[0] = ('lit', p[1])


def p_expression_var(p):
    'expression : VARIABLE'
    p[0] = ('var', p[1])


def p_expression_const(p):
    'expression : ID'
    p[0] = ('const', p[1])


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_call(p):
    'expression : ID LPAREN argument_list RPAREN'
    if p[1].lower() == 'readline':       # ingreso de datos por teclado
        regla('entrada por teclado')
    else:
        regla('llamada a función')
    p[0] = ('call', p[1], p[3])


def p_argument_list(p):
    '''argument_list : expression_list
                     | empty'''
    p[0] = p[1] or []


def p_expression_list(p):
    '''expression_list : expression_list COMMA expression
                       | expression'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# ZONA DEL INTEGRANTE 1
# INICIO DEL APORTE - dbolanos-s
# Componentes: impresión, estructura de datos (arreglos), estructura de control
# (if / elseif / else y ciclo for) y definición de funciones con tipos, valores por defecto y retorno
precedence_i1 = []


# impresión: echo a, b, c;   print a;
def p_statement_echo(p):
    'statement : ECHO expression_list SEMI'
    regla('impresión (echo)')
    p[0] = ('echo', p[2])


def p_statement_print(p):
    'statement : PRINT expression SEMI'
    regla('impresión (print)')
    p[0] = ('print', p[2])


# estructura de datos: arreglos  [1, 2]   array(1, 2)   ["a" => 1]   $v[0]
def p_expression_array_short(p):
    'expression : LBRACKET array_items RBRACKET'
    regla('arreglo')
    p[0] = ('array', p[2])


def p_expression_array_long(p):
    'expression : ARRAY LPAREN array_items RPAREN'
    regla('arreglo')
    p[0] = ('array', p[3])


def p_array_items(p):
    '''array_items : array_item_list
                   | array_item_list COMMA
                   | empty'''
    p[0] = p[1] or []


def p_array_item_list(p):
    '''array_item_list : array_item_list COMMA array_item
                       | array_item'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_array_item(p):
    '''array_item : expression
                  | expression ARROW expression'''
    p[0] = p[1] if len(p) == 2 else ('pair', p[1], p[3])


def p_expression_index(p):
    'expression : expression LBRACKET expression RBRACKET'
    regla('acceso a elemento')
    p[0] = ('index', p[1], p[3])


# estructura de control: if (c) { ... } elseif (c) { ... } else { ... }
def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN block else_part'
    regla('condicional if')
    p[0] = ('if', p[3], p[5], p[6])


def p_else_part(p):
    '''else_part : ELSEIF LPAREN expression RPAREN block else_part
                 | ELSE block
                 | empty'''
    if len(p) == 7:
        regla('elseif')
        p[0] = ('elseif', p[3], p[5], p[6])
    elif len(p) == 3:
        regla('else')
        p[0] = ('else', p[2])
    else:
        p[0] = None



# estructura de control: for (inicio; condición; paso) { ... }
# Cada parte puede estar vacía o llevar varias expresiones separadas por coma.
# Los incrementos $i++ / $i-- se aceptan aquí; fuera del for son sentencias aparte.
def p_statement_for(p):
    'statement : FOR LPAREN for_clause SEMI for_clause SEMI for_clause RPAREN block'
    regla('ciclo for')
    p[0] = ('for', p[3], p[5], p[7], p[9])


def p_for_clause(p):
    '''for_clause : for_item_list
                  | empty'''
    p[0] = p[1] or []


def p_for_item_list(p):
    '''for_item_list : for_item_list COMMA for_item
                     | for_item'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_for_item(p):
    '''for_item : expression
                 | expression ASSIGN expression
                 | expression for_assign_op expression
                 | expression INC
                 | expression DEC'''
    p[0] = ('for_item',) + tuple(p[1:])


def p_for_assign_op(p):
    '''for_assign_op : PLUSEQ
                      | MINUSEQ
                      | TIMESEQ
                      | DIVEQ
                      | CONCATEQ'''
    p[0] = p[1]


# función: function nombre(tipo $a, $b = 0): tipo { ... }   return expr;
def p_statement_function(p):
    'statement : FUNCTION ID LPAREN param_list RPAREN return_type block'
    regla('definición de función')
    p[0] = ('function', p[2], p[4], p[6], p[7])


def p_param_list(p):
    '''param_list : param_items
                  | empty'''
    p[0] = p[1] or []


def p_param_items(p):
    '''param_items : param_items COMMA param
                   | param'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_param(p):
    '''param : type_name VARIABLE
             | type_name VARIABLE ASSIGN expression
             | VARIABLE
             | VARIABLE ASSIGN expression'''
    p[0] = ('param', p[len(p) - 1] if len(p) == 2 else p[2])


def p_type_name(p):
    '''type_name : TYPE
                 | ARRAY'''
    p[0] = p[1]


def p_return_type(p):
    '''return_type : COLON type_name
                   | empty'''
    p[0] = p[2] if len(p) == 3 else None


def p_statement_return(p):
    '''statement : RETURN expression SEMI
                 | RETURN SEMI'''
    regla('return')
    p[0] = ('return', p[2] if len(p) == 4 else None)
# FIN DEL APORTE - dbolanos-s
# (fin de la zona del integrante 1)


# ZONA DE Fernando
# INICIO DEL APORTE - fdiazoso
# Componentes: expresiones aritméticas, de comparación y lógicas con su precedencia,
# asignación compuesta, incremento/decremento, ciclo while, desestructuración de
# arreglos y función flecha
# Precedencia de menor a mayor (or/|| y and/&& comparten token en el léxico)
precedence_i2 = [
    ('left', 'OR'),                     # or  y  ||  (mismo token)
    ('left', 'AND'),                    # and y  &&  (mismo token)
    ('nonassoc', 'EQ', 'IDENT', 'NEQ', 'NIDENT', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS', 'CONCAT'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),                # menos unario
    ('right', 'POW'),
    ('right', 'NOT'),
    ('left', 'LBRACKET'),               # $a[0] se agrupa primero
]


# expresiones aritméticas y concatenación:  $a + $b * 2 ** 3 . "txt"
def p_expression_arith(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression POW expression
                  | expression CONCAT expression'''
    regla('concatenación' if p[2] == '.' else 'expresión aritmética')
    p[0] = ('binop', p[2], p[1], p[3])


def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    regla('expresión aritmética')
    p[0] = ('neg', p[2])


# comparaciones:  ==  ===  !=  !==  <  >  <=  >=
def p_expression_compare(p):
    '''expression : expression EQ expression
                  | expression IDENT expression
                  | expression NEQ expression
                  | expression NIDENT expression
                  | expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression'''
    regla('comparación')
    p[0] = ('cmp', p[2], p[1], p[3])


# conectores lógicos:  &&  ||  and  or  !
def p_expression_logic(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    regla('expresión lógica')
    p[0] = ('logic', p[2], p[1], p[3])


def p_expression_not(p):
    'expression : NOT expression'
    regla('expresión lógica')
    p[0] = ('not', p[2])


def _lado_izquierdo(p, n, que):
    """El lado izquierdo debe ser una variable o un elemento de arreglo."""
    if p[1][0] not in ('var', 'index'):
        sint_errors.append({'tipo': 'sintáctico', 'linea': p.lineno(n), 'columna': _col(p, n),
                            'mensaje': f'{que} solo se aplica a una variable o elemento de arreglo'})


# asignación compuesta como sentencia:  $a += 1;  $s .= "x";
# (usa los operadores de for_assign_op, definidos en la zona 1)
def p_statement_compound_assign(p):
    'statement : expression for_assign_op expression SEMI'
    _lado_izquierdo(p, 4, f"'{p[2]}'")
    regla('asignación compuesta')
    p[0] = ('assign_op', p[2], p[1], p[3])
# FIN DEL APORTE - fdiazoso
# (fin de la zona del integrante 2)


# ZONA DE Symond
# <<<APORTE_INTEGRANTE_3>>>
# (fin de la zona del integrante 3)


# ENSAMBLADO (no modificar): junta la precedencia de los tres integrantes
precedence = tuple(precedence_i1 + precedence_i2 + precedence_i3)


def _col(p, n):
    """Columna (base 1) del símbolo n de la regla p."""
    pos = p.lexpos(n)
    return pos - (p.lexer.lexdata.rfind('\n', 0, pos) + 1) + 1


def p_error(p):
    """Se ejecuta ante un token que la gramática no espera."""
    if p is None:
        sint_errors.append({'tipo': 'sintáctico', 'linea': _lexer.lineno, 'columna': 0,
                            'mensaje': 'fin de archivo inesperado (falta cerrar una sentencia o bloque)'})
        return
    col = p.lexpos - (p.lexer.lexdata.rfind('\n', 0, p.lexpos) + 1) + 1
    sint_errors.append({'tipo': 'sintáctico', 'linea': p.lineno, 'columna': col,
                        'mensaje': f"token inesperado '{p.value}' ({p.type})"})


def build_parser():
    global _parser
    _parser = yacc.yacc(module=sys.modules[__name__], write_tables=False, debug=False,
                        errorlog=yacc.NullLogger())
    return _parser


def analizar(codigo):
    """Devuelve (estructuras_usadas, errores_sintacticos, errores_lexicos)."""
    sint_errors.clear()
    uso.clear()
    lexico.lex_errors.clear()
    parser = build_parser()
    global _lexer
    _lexer = lexico.build_lexer()
    lexer = _lexer
    parser.parse(codigo, lexer=lexer)
    return dict(uso), list(sint_errors), list(lexico.lex_errors)
