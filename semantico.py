"""Analizador semántico del AST producido por :mod:`sintactico`."""

FUNCIONES_PHP = {'array', 'define', 'print_r', 'count', 'strlen', 'readline'}
NUMERICOS = {'int', 'float', 'numero'}


class Contexto:
    def __init__(self):
        self.variables = [{}]; self.funciones = {}; self.constantes = set()
        self.bucles = 0; self.funcion_actual = None; self.errores = []

    def error(self, codigo, nombre, nodo, mensaje):
        self.errores.append({'regla': codigo, 'nombre': nombre, 'linea': 0, 'mensaje': mensaje})

    def _variable(self, name):
        for scope in reversed(self.variables):
            if name in scope: return scope[name]
        return {}

    def define(self, name, tipo='desconocido'):
        self.variables[-1][name] = {'tipo': str(tipo or 'desconocido').lower()}

    def tipo_de(self, n):
        if n is None: return 'desconocido'
        k = n[0]
        if k == 'lit': return n[2] if len(n) > 2 else 'desconocido'
        if k == 'var': return self._variable(n[1]).get('tipo', 'desconocido')
        if k == 'const': return 'constante' if n[1] in self.constantes else 'desconocido'
        if k == 'array': return 'array'
        if k == 'index': return 'desconocido'
        if k == 'neg': return self.tipo_de(n[1])
        if k == 'binop':
            a, b = self.tipo_de(n[2]), self.tipo_de(n[3])
            return 'string' if n[1] == '.' else ('float' if 'float' in (a, b) else 'int' if a in NUMERICOS and b in NUMERICOS else 'desconocido')
        if k in ('cmp', 'logic', 'not'): return 'bool'
        if k == 'call': return self.funciones.get(str(n[1]).lower(), {}).get('ret', 'desconocido')
        if k == 'new': return 'object'
        return 'desconocido'


def r1(n, c):
    if not any(n[1] in s for s in c.variables): c.error('R1', 'Identificadores', n, f"la variable '{n[1]}' no esta definida")

def r2(n, c):
    if n[1] in c.constantes: c.error('R2', 'Asignación de tipo', n, f"la constante '{n[1]}' ya esta definida")
    c.constantes.add(n[1])

def r3(n, c):
    a, b = c.tipo_de(n[2]), c.tipo_de(n[3])
    if 'desconocido' in (a, b): return
    if n[0] == 'binop' and n[1] in ('+', '-', '*', '/', '%', '**') and (a not in NUMERICOS or b not in NUMERICOS): c.error('R3', 'Operaciones permitidas', n, f"operacion '{n[1]}' no permitida entre {a} y {b}")
    if n[0] == 'binop' and n[1] == '.' and 'array' in (a, b): c.error('R3', 'Operaciones permitidas', n, 'la concatenacion no admite array')
    if n[0] == 'cmp' and n[1] in ('<', '>', '<=', '>=') and 'string' in (a, b) and (a in NUMERICOS or b in NUMERICOS): c.error('R3', 'Operaciones permitidas', n, f"comparacion '{n[1]}' entre {a} y {b}")

def r4(n, c):
    f = c.funcion_actual
    if not f or f.get('ret') is None or n[1] is None: return
    declared, got = str(f['ret']).lower(), c.tipo_de(n[1])
    if 'desconocido' not in (declared, got) and not (got == declared or declared == 'float' and got == 'int'):
        c.error('R4', 'Retorno de funciones', n, f"la funcion '{f['nombre']}' declara {declared} pero retorna {got}")

def r5_loop(n, c):
    if c.bucles == 0: c.error('R5', 'Estructuras de control', n, f"'{n[0]}' solo puede usarse dentro de un bucle")

def r5_foreach(n, c):
    t = c.tipo_de(n[1])
    if t not in ('array', 'object', 'desconocido'): c.error('R5', 'Estructuras de control', n, f'foreach requiere un array, pero recibio {t}')

def r6(n, c):
    name = str(n[1])
    if name.startswith('$') or name.lower() in {'array', 'define', 'print_r', 'count', 'strlen', 'readline'}: return
    f = c.funciones.get(name.lower())
    if not f: c.error('R6', 'Identificadores', n, f"la funcion '{name}' no esta definida"); return
    required = sum(p[3] is None for p in f['params']); received = len(n[2]); total = len(f['params'])
    if not required <= received <= total: c.error('R6', 'Identificadores', n, f"'{name}' espera {required} a {total} argumentos, recibio {received}")

def analizar(tree):
    c = Contexto(); register(tree, c); visit(tree, c); return c.errores

def register(n, c):
    if isinstance(n, list):
        for x in n: register(x, c)
    elif isinstance(n, tuple):
        if n[0] == 'function': c.funciones[n[1].lower()] = {'nombre': n[1], 'params': n[2], 'ret': n[3]}
        for x in n[1:]: register(x, c)

def visit(n, c):
    if n is None: return
    if isinstance(n, list):
        for x in n: visit(x, c)
        return
    if not isinstance(n, tuple): return
    k = n[0]
    if k in ('program', 'block'): return visit(n[1], c)
    if k == 'assign':
        visit(n[2], c)
        if n[1][0] == 'var': c.define(n[1][1], c.tipo_de(n[2]))
        visit(n[1], c); return
    if k == 'const_def': r2(n, c); visit(n[2], c); return
    if k == 'function':
        old = c.funcion_actual; c.funcion_actual = c.funciones[n[1].lower()]; c.variables.append({p[1]: {'tipo': str(p[2] or 'desconocido').lower()} for p in n[2]}); visit(n[4], c); c.variables.pop(); c.funcion_actual = old; return
    if k == 'method':
        c.variables.append({'$this': {'tipo': 'object'}, **{p[1]: {'tipo': str(p[2] or 'desconocido').lower()} for p in n[3]}})
        visit(n[5], c); c.variables.pop(); return
    if k == 'call' and str(n[1]).lower() == 'define' and n[2] and n[2][0][0] == 'lit': c.constantes.add(str(n[2][0][1]).strip("'\""))
    if k in ('break', 'continue'): r5_loop(n, c)
    if k == 'foreach':
        r5_foreach(n, c); visit(n[1], c); c.bucles += 1; c.define(n[3][1]);
        if n[2]: c.define(n[2][1])
        visit(n[4], c); c.bucles -= 1; return
    if k == 'arrow_fn':
        c.variables.append({p[1]: {'tipo': str(p[2] or 'desconocido').lower()} for p in n[1]}); visit(n[3], c); c.variables.pop(); return
    if k in ('while', 'for'):
        for x in n[1:-1]:
            if isinstance(x, list):
                for item in x:
                    if isinstance(item, tuple) and item[0] == 'for_item' and len(item) > 2 and item[2] == '=' and item[1][0] == 'var':
                        c.define(item[1][1], c.tipo_de(item[3]))
                    visit(item, c)
            else: visit(x, c)
        c.bucles += 1; visit(n[-1], c); c.bucles -= 1; return
    if k == 'var': r1(n, c)
    if k == 'call': r6(n, c)
    if k == 'return': r4(n, c)
    if k in ('binop', 'cmp'): r3(n, c)
    for x in n[1:]: visit(x, c)
