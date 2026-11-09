# -*- coding: utf-8 -*-
"""
Analizador léxico para un subconjunto de PHP (PLY - módulo lex).  Avance 1.

El archivo está dividido en ZONAS. Cada integrante agrega su aporte en su zona,
delimitado por los comentarios INICIO / FIN.  No modifique las zonas de los demás.
"""
import sys
import ply.lex as lex

lex_errors = []  # errores léxicos acumulados durante un análisis

# Valores por defecto; cada bloque de integrante los reemplaza con los suyos.
tokens_i1, tokens_i2, tokens_i3 = [], [], []
reserved_i1, reserved_i2, reserved_i3 = {}, {}, {}

# Caracteres que se ignoran entre tokens (espacios, tabulaciones, retorno de carro)
t_ignore = ' \t\r'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# INICIO DEL APORTE - dbolanos-s
# Componentes: variables, literales (int, float, string, true/false/null) y comentarios

reserved_i1 = {'true': 'TRUE', 'false': 'FALSE', 'null': 'NULL'}
tokens_i1 = ['VARIABLE', 'INT', 'FLOAT', 'STRING', 'TRUE', 'FALSE', 'NULL']


def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')      # comentario /* ... */ : se descarta


def t_COMMENT_UNCLOSED(t):
    r'/\*(.|\n)*'
    lex_errors.append({'tipo': 'léxico', 'linea': t.lineno,
                       'columna': _col(t.lexer.lexdata, t.lexpos),
                       'mensaje': "comentario de bloque sin cerrar (falta '*/')"})
    t.lexer.lineno += t.value.count('\n')


def t_COMMENT_LINE(t):
    r'(//|\#)[^\n]*'
    pass                                         # comentario // o # : se descarta


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''
    t.lexer.lineno += t.value.count('\n')
    return t


def t_VARIABLE(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    return t
def t_TRUE(t):
    r'(?i:true)(?![A-Za-z0-9_])'
    return t


def t_FALSE(t):
    r'(?i:false)(?![A-Za-z0-9_])'
    return t


def t_NULL(t):
    r'(?i:null)(?![A-Za-z0-9_])'
    return t


# FIN DEL APORTE - dbolanos-s
# (fin de la zona del integrante 1)


# INICIO DEL APORTE - Fernando
# Componentes: operadores aritméticos, de asignación, de comparación y lógicos
tokens_i2 = [
    # aritméticos y concatenación
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POW', 'CONCAT',
    # asignación, incremento y decremento
    'ASSIGN', 'PLUSEQ', 'MINUSEQ', 'TIMESEQ', 'DIVEQ', 'CONCATEQ', 'INC', 'DEC',
]
# PLY ordena estas reglas por longitud de la expresión (la más larga primero)
t_PLUSEQ = r'\+='
t_MINUSEQ = r'-='
t_TIMESEQ = r'\*='
t_DIVEQ = r'/='
t_CONCATEQ = r'\.='
t_INC = r'\+\+'
t_DEC = r'--'
t_POW = r'\*\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_CONCAT = r'\.'
t_ASSIGN = r'='
# FIN DEL APORTE - Fernando
# (fin de la zona del integrante 2)


# ZONA DE Symond
# <<<APORTE_INTEGRANTE_3>>>
# (fin de la zona del integrante 3)


# ENSAMBLADO (no modificar): junta los aportes de los tres integrantes
tokens = list(dict.fromkeys(tokens_i1 + tokens_i2 + tokens_i3))
reserved = {**reserved_i1, **reserved_i2, **reserved_i3}


def _col(data, pos):
    """Columna (base 1) de la posición `pos` dentro del texto `data`."""
    return pos - (data.rfind('\n', 0, pos) + 1) + 1


def t_error(t):
    """Se ejecuta ante un carácter que ninguna regla reconoce."""
    c = t.value[0]
    if c in '"\'':
        msg = "cadena de texto sin cerrar (falta la comilla de cierre)"
    elif c == '$':
        msg = "nombre de variable inválido: después de '$' debe ir una letra o '_'"
    else:
        msg = f"carácter no reconocido '{c}'"
    lex_errors.append({'tipo': 'léxico', 'linea': t.lineno,
                       'columna': _col(t.lexer.lexdata, t.lexpos), 'mensaje': msg})
    t.lexer.skip(1)


def build_lexer():
    lx = lex.lex(module=sys.modules[__name__])
    lx.lineno = 1
    return lx


def tokenizar(codigo):
    """Devuelve (tokens, errores) del código PHP recibido."""
    lex_errors.clear()
    lx = build_lexer()
    lx.input(codigo)
    salida = []
    for tok in lx:
        salida.append({'tipo': tok.type, 'valor': tok.value,
                       'linea': tok.lineno, 'columna': _col(codigo, tok.lexpos)})
    return salida, list(lex_errors)
