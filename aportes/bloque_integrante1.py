# =====================================================================
# INICIO DEL APORTE - INTEGRANTE 1 (@usuario1)
# Componentes: variables, literales (int, float, string, true/false/null) y comentarios
# =====================================================================
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
# =====================================================================
# FIN DEL APORTE - INTEGRANTE 1 (@usuario1)
# =====================================================================
