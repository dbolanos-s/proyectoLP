# -*- coding: utf-8 -*-
"""
Analizador sintáctico para un subconjunto de PHP (PLY - módulo yacc).  Avance 2.

Usa los tokens que define lexico.py.  Igual que en el léxico, el archivo se divide
en ZONAS: cada integrante escribe sus reglas dentro de su zona, entre los comentarios
INICIO / FIN, y no modifica las de los demás.

Cada regla se escribe como una función p_...(p) cuyo docstring es la gramática.
"""
import sys
import types
import ply.yacc as yacc

import lexico
from lexico import tokens          # yacc necesita la lista de tokens del léxico

sint_errors = []                   # errores sintácticos del último análisis
uso = {}                           # cuántas veces se reconoció cada estructura
_parser = None
_lexer = None
arbol = None                       # árbol sintáctico del último análisis (lo usa semantico.py)
_lineas = {}                       # id(nodo) -> (nodo, línea donde empieza): ver linea_de()


def linea_de(nodo, defecto=0):
    """Línea del archivo donde empieza un nodo del árbol (para los errores semánticos)."""
    dato = _lineas.get(id(nodo))
    return dato[1] if dato and dato[0] is nodo else defecto


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
    if p[1][0] not in ('var', 'index', 'property'):
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
    tipo = {'INT': 'int', 'FLOAT': 'float', 'STRING': 'string',
            'TRUE': 'bool', 'FALSE': 'bool', 'NULL': 'null'}[p.slice[1].type]
    p[0] = ('lit', p[1], tipo)


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
    # ('param', nombre, tipo declarado o None, valor por defecto o None)
    if p.slice[1].type == 'type_name':
        p[0] = ('param', p[2], p[1], p[4] if len(p) == 5 else None)
    else:
        p[0] = ('param', p[1], None, p[3] if len(p) == 4 else None)


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

# constantes: const NOMBRE = expresión;   (define('NOMBRE', valor) es una llamada normal)
def p_statement_const(p):
    'statement : CONST ID ASSIGN expression SEMI'
    regla('constante')
    p[0] = ('const_def', p[2], p[4])
# FIN DEL APORTE - dbolanos-s
# (fin de la zona del integrante 1)


# ZONA DE Fernando
# INICIO DEL APORTE - fdiazoso
# Componentes: expresiones aritméticas, de comparación y lógicas con su precedencia,
# asignación compuesta, incremento/decremento, ciclo while, desestructuración de
# arreglos y función flecha
# Precedencia de menor a mayor (or/|| y and/&& comparten token en el léxico)
precedence_i2 = [
    ('nonassoc', 'RBRACKET'),           # ']' antes de '=' (desestructuración)
    ('right', 'ASSIGN'),
    ('nonassoc', 'FN'),                 # el cuerpo de fn toma toda la expresión
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


# incremento y decremento como sentencias:  $i++;  $i--;
# (dentro del for ya los acepta for_item, por eso no son expresiones)
def p_statement_incdec(p):
    '''statement : expression INC SEMI
                 | expression DEC SEMI'''
    _lado_izquierdo(p, 2, f"'{p[2]}'")
    regla('incremento/decremento')
    p[0] = ('incdec', p[2], p[1])


# estructura de control: while (condición) { ... }
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN block'
    regla('ciclo while')
    p[0] = ('while', p[3], p[5])


# estructura de datos: desestructuración de arreglos  [$a, $b] = $lista;  ["x" => $x] = $d;
# El lado izquierdo se lee con array_items (zona 1).  Ante '=' después de ']' la
# precedencia (RBRACKET < ASSIGN) elige esta regla en vez de la asignación de la base.
def p_statement_destructuring(p):
    'statement : LBRACKET array_items RBRACKET ASSIGN expression SEMI'
    for item in p[2]:
        destino = item[2] if item[0] == 'pair' else item
        if destino[0] not in ('var', 'index', 'array'):
            sint_errors.append({'tipo': 'sintáctico', 'linea': p.lineno(4), 'columna': _col(p, 4),
                                'mensaje': 'en la desestructuración solo se aceptan variables'})
            break
    regla('desestructuración')
    p[0] = ('destructure', p[2], p[5])


# función flecha:  fn($x) => $x * 2      fn(int $x): int => $x + 1
# (reutiliza param_list y return_type de la zona 1)
def p_expression_arrow_fn(p):
    'expression : FN LPAREN param_list RPAREN return_type ARROW expression %prec FN'
    regla('función flecha')
    p[0] = ('arrow_fn', p[3], p[5], p[7])


# llamada a una función guardada en variable:  $doble(4)
def p_expression_var_call(p):
    'expression : VARIABLE LPAREN argument_list RPAREN'
    regla('llamada a función')
    p[0] = ('call', p[1], p[3])
# FIN DEL APORTE - fdiazoso
# (fin de la zona del integrante 2)


# ZONA DE Symond
# INICIO DEL APORTE - Symond
# Componentes: clases, propiedades, métodos, objetos, foreach, break y continue
precedence_i3 = [
    ('left', 'OBJECT_ACCESS'),
]


def p_statement_class(p):
    '''statement : CLASS ID class_extends LBRACE class_members RBRACE'''
    regla('definición de clase')
    p[0] = ('class', p[2], p[3], p[5])


def p_class_extends(p):
    '''class_extends : EXTENDS ID
                     | empty'''
    p[0] = ('extends', p[2]) if len(p) == 3 else None


def p_class_members(p):
    '''class_members : class_members class_member
                     | empty'''
    p[0] = (p[1] or []) + [p[2]] if len(p) == 3 else []


def p_class_member_property(p):
    'class_member : visibility class_property SEMI'
    regla('propiedad de clase')
    p[0] = ('property', p[1], p[2])


def p_class_property(p):
    '''class_property : type_name VARIABLE
                      | type_name VARIABLE ASSIGN expression'''
    p[0] = (p[2], p[1], p[4] if len(p) == 5 else None)


def p_visibility(p):
    '''visibility : PUBLIC
                  | PRIVATE
                  | PROTECTED'''
    p[0] = p[1]


def p_class_member_method(p):
    'class_member : visibility FUNCTION ID LPAREN param_list RPAREN return_type block'
    regla('método de clase')
    p[0] = ('method', p[1], p[3], p[5], p[7], p[8])


def p_class_member_method_default_visibility(p):
    'class_member : FUNCTION ID LPAREN param_list RPAREN return_type block'
    regla('método de clase')
    p[0] = ('method', None, p[2], p[4], p[6], p[7])


def p_expression_new(p):
    'expression : NEW ID LPAREN argument_list RPAREN'
    regla('creación de objeto')
    p[0] = ('new', p[2], p[4])


def p_expression_object_property(p):
    'expression : expression OBJECT_ACCESS ID'
    regla('acceso a propiedad')
    p[0] = ('property', p[1], p[3])


def p_expression_object_method(p):
    'expression : expression OBJECT_ACCESS ID LPAREN argument_list RPAREN'
    regla('llamada a método')
    p[0] = ('method_call', p[1], p[3], p[5])


def p_statement_foreach(p):
    '''statement : FOREACH LPAREN expression AS foreach_target RPAREN block
                 | FOREACH LPAREN expression AS foreach_target ARROW foreach_target RPAREN block'''
    regla('ciclo foreach')
    if len(p) == 8:
        p[0] = ('foreach', p[3], None, p[5], p[7])
    else:
        p[0] = ('foreach', p[3], p[5], p[7], p[9])


def p_foreach_target(p):
    'foreach_target : VARIABLE'
    p[0] = ('var', p[1])


def p_statement_break_continue(p):
    '''statement : BREAK SEMI
                 | CONTINUE SEMI'''
    regla('break' if p[1].lower() == 'break' else 'continue')
    p[0] = (p[1].lower(),)


# FIN DEL APORTE - Symond
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


def _con_lineas(f):
    """Envuelve una regla p_...: después de ejecutarla guarda la línea de inicio del nodo."""
    def regla_con_linea(p):
        f(p)
        nodo = p[0]
        if isinstance(nodo, (tuple, list)) and len(p.slice) > 1:
            _lineas[id(nodo)] = (nodo, p.lineno(1))
    regla_con_linea.__doc__ = f.__doc__
    regla_con_linea.__name__ = f.__name__
    # se conserva la posición original de la regla (PLY ordena las reglas por línea)
    regla_con_linea.__code__ = regla_con_linea.__code__.replace(
        co_firstlineno=f.__code__.co_firstlineno, co_filename=f.__code__.co_filename)
    return regla_con_linea


def build_parser():
    global _parser
    modulo = types.SimpleNamespace(**{
        nombre: (_con_lineas(valor) if nombre.startswith('p_') and nombre != 'p_error' and valor.__doc__ else valor)
        for nombre, valor in vars(sys.modules[__name__]).items()
        if not nombre.startswith('__')})
    modulo.__file__ = __file__
    _parser = yacc.yacc(module=modulo, write_tables=False, debug=False,
                        errorlog=yacc.NullLogger())
    return _parser


def analizar(codigo):
    """Devuelve (estructuras_usadas, errores_sintacticos, errores_lexicos)."""
    global _lexer, arbol
    sint_errors.clear()
    uso.clear()
    _lineas.clear()
    lexico.lex_errors.clear()
    parser = build_parser()
    _lexer = lexico.build_lexer()
    arbol = parser.parse(codigo, lexer=_lexer, tracking=True)
    return dict(uso), list(sint_errors), list(lexico.lex_errors)
