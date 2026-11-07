# INICIO DEL APORTE - INTEGRANTE 3
# Componentes: palabras reservadas, identificadores, delimitadores y etiquetas <?php ?>
reserved_i3 = {
    'if': 'IF', 'else': 'ELSE', 'elseif': 'ELSEIF',
    'while': 'WHILE', 'for': 'FOR', 'foreach': 'FOREACH', 'as': 'AS',
    'break': 'BREAK', 'continue': 'CONTINUE',
    'function': 'FUNCTION', 'fn': 'FN', 'return': 'RETURN',
    'echo': 'ECHO', 'print': 'PRINT', 'const': 'CONST', 'array': 'ARRAY',
    'int': 'TYPE', 'float': 'TYPE', 'string': 'TYPE', 'bool': 'TYPE',
}
tokens_i3 = (
    ['OPEN_TAG', 'CLOSE_TAG', 'ID',
     'SEMI', 'COMMA', 'COLON', 'ARROW',
     'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET']
    + sorted(set(reserved_i3.values()))
)


def t_OPEN_TAG(t):
    r'<\?php'
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # PHP no distingue mayúsculas en palabras reservadas: se busca en minúsculas
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


t_ARROW = r'=>'
t_CLOSE_TAG = r'\?>'
t_SEMI = r';'
t_COMMA = r','
t_COLON = r':'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
# FIN DEL APORTE - INTEGRANTE 3
