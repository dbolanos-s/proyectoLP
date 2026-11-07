# =====================================================================
# INICIO DEL APORTE - INTEGRANTE 2 (@usuario2)
# Componentes: operadores aritméticos, de asignación, de comparación y lógicos
# =====================================================================
reserved_i2 = {'and': 'AND', 'or': 'OR'}
tokens_i2 = [
    # aritméticos y concatenación
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POW', 'CONCAT',
    # asignación, incremento y decremento
    'ASSIGN', 'PLUSEQ', 'MINUSEQ', 'TIMESEQ', 'DIVEQ', 'CONCATEQ', 'INC', 'DEC',
    # comparación
    'EQ', 'IDENT', 'NEQ', 'NIDENT', 'LT', 'GT', 'LE', 'GE',
    # lógicos
    'AND', 'OR', 'NOT',
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
t_IDENT = r'==='
t_NIDENT = r'!=='
t_EQ = r'=='
t_NEQ = r'!='
t_LE = r'<='
t_GE = r'>='
t_AND = r'&&'
t_OR = r'\|\|'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_CONCAT = r'\.'
t_ASSIGN = r'='
t_LT = r'<'
t_GT = r'>'
t_NOT = r'!'
# =====================================================================
# FIN DEL APORTE - INTEGRANTE 2 (@usuario2)
# =====================================================================
