# -*- coding: utf-8 -*-
"""
Analizador semántico para un subconjunto de PHP.  Avance 3.

Trabaja sobre el árbol que construye sintactico.py (sintactico.arbol).  El archivo tiene
tres partes:

  1. MOTOR (no modificar): recorre el árbol una sola vez, lleva la tabla de símbolos
     (variables por ámbito, funciones, clases, constantes) y avisa a las reglas.
  2. ZONAS: cada integrante escribe aquí sus 2 reglas semánticas, entre los comentarios
     INICIO / FIN DEL APORTE con su nombre.
  3. analizar_semantico(): ejecuta el análisis y devuelve los errores.

CÓMO SE ESCRIBE UNA REGLA
-------------------------
Una regla es una función que se registra con el decorador @regla_semantica:

    @regla_semantica('R3', 'Operaciones permitidas', 'binop', 'cmp')
    def r3_operaciones(nodo, ctx):
        ...
        ctx.error('R3', 'Operaciones permitidas', nodo, "mensaje del error")

* Los últimos argumentos del decorador son las etiquetas de nodo que le interesan
  ('binop', 'cmp', 'return', 'break', 'foreach', 'call', 'const_def', ...), o bien
  'uso_var' (se lee una variable) y 'def_var' (se asigna una variable).
* El motor llama a la función cada vez que encuentra uno de esos nodos, ANTES de
  recorrer sus hijos.
* Lo que la función puede consultar en ctx:
    ctx.tipo_de(expr)        tipo de una expresión: 'int', 'float', 'string', 'bool',
                             'null', 'array', 'object', 'numero' (int o float) o
                             'desconocido'.  Con 'desconocido' NO se debe marcar error.
    ctx.variable_definida(n) True si la variable n existe en el ámbito actual
    ctx.funciones            funciones definidas: nombre en minúsculas -> {'nombre',
                             'params', 'ret', 'linea'}
    ctx.clases               clases definidas: nombre en minúsculas -> {'nombre', 'padre'}
    ctx.constantes           constantes ya definidas: nombre -> línea
    ctx.funcion_actual       dict de la función en la que se está, o None
    ctx.bucles               cuántos bucles contienen el punto actual (0 = ninguno)
* Las formas de los nodos están en sintactico.py (el segundo elemento de cada tupla).
"""
import sintactico

# Tipos que entiende el analizador
NUMERICOS = ('int', 'float', 'numero')

# Variables que PHP define siempre
PREDEFINIDAS = {'$this', '$GLOBALS', '$_GET', '$_POST', '$_SERVER', '$_SESSION',
                '$_COOKIE', '$_FILES', '$_ENV', '$_REQUEST', '$argv', '$argc'}

# Funciones propias de PHP que usamos: nombre -> tipo que devuelven (None = no se sabe)
FUNCIONES_PHP = {
    'readline': 'string', 'strlen': 'int', 'count': 'int', 'intval': 'int',
    'floatval': 'float', 'strval': 'string', 'strtoupper': 'string',
    'strtolower': 'string', 'abs': 'numero', 'round': 'float', 'floor': 'float',
    'ceil': 'float', 'max': None, 'min': None, 'sqrt': 'float', 'pow': 'numero',
    'define': 'bool', 'defined': 'bool', 'is_int': 'bool', 'is_array': 'bool',
    'is_string': 'bool', 'isset': 'bool', 'empty': 'bool', 'array_push': 'int',
    'implode': 'string', 'explode': 'array', 'range': 'array', 'in_array': 'bool',
    'var_dump': None, 'print_r': None, 'number_format': 'string', 'sprintf': 'string',
    'trim': 'string', 'str_repeat': 'string', 'array_sum': 'numero',
    'array_keys': 'array', 'array_values': 'array', 'array_merge': 'array',
    'sort': 'bool', 'rand': 'int', 'mt_rand': 'int', 'time': 'int', 'date': 'string',
}

sem_errors = []                    # errores del último análisis
verificaciones = {}                # cuántas veces trabajó cada regla (para el log)
_REGISTRO = {}                     # etiqueta de nodo -> [(id_regla, función), ...]


def regla_semantica(id_regla, categoria, *etiquetas):
    """Registra una regla semántica para las etiquetas de nodo indicadas."""
    def registrar(funcion):
        funcion.id_regla = id_regla
        funcion.categoria = categoria
        for etiqueta in etiquetas:
            _REGISTRO.setdefault(etiqueta, []).append((id_regla, funcion))
        return funcion
    return registrar


def hijos(nodo):
    """Nodos hijos de un nodo del árbol (tuplas y listas anidadas), en orden de aparición."""
    if isinstance(nodo, tuple):
        elementos = nodo[1:] if nodo and isinstance(nodo[0], str) else nodo
    elif isinstance(nodo, list):
        elementos = nodo
    else:
        return
    for e in elementos:
        if isinstance(e, (tuple, list)):
            yield e


# ---------------------------------------------------------------------------
# MOTOR (no modificar)
# ---------------------------------------------------------------------------
class Ambito:
    """Variables de una función (o del programa).  Una función flecha ve las de su padre."""

    def __init__(self, nombre=None, padre=None):
        self.nombre = nombre
        self.padre = padre
        self.vars = {}

    def definir(self, nombre, tipo='desconocido'):
        self.vars[nombre] = tipo

    def buscar(self, nombre):
        if nombre in self.vars:
            return self.vars[nombre]
        return self.padre.buscar(nombre) if self.padre else None


class Contexto:
    """Estado del análisis; es lo que reciben las reglas como `ctx`."""

    def __init__(self):
        self.funciones = {}
        self.clases = {}
        self.constantes = {}
        self.global_ = Ambito('global')
        self.ambito = self.global_
        self.bucles = 0
        self.funcion_actual = None
        self.clase_actual = None

    # --- consultas -------------------------------------------------------
    def variable_definida(self, nombre):
        return nombre in PREDEFINIDAS or self.ambito.buscar(nombre) is not None

    def tipo_variable(self, nombre):
        return self.ambito.buscar(nombre) or 'desconocido'

    def error(self, id_regla, categoria, nodo, mensaje):
        sem_errors.append({'regla': id_regla, 'categoria': categoria,
                           'linea': sintactico.linea_de(nodo), 'mensaje': mensaje})

    # --- tipos -----------------------------------------------------------
    def tipo_de(self, e):
        """Tipo de una expresión; 'desconocido' cuando no se puede saber."""
        if not isinstance(e, tuple) or not e:
            return 'desconocido'
        t = e[0]
        if t == 'lit':
            return e[2]
        if t == 'var':
            return self.tipo_variable(e[1])
        if t == 'array':
            return 'array'
        if t in ('cmp', 'logic', 'not'):
            return 'bool'
        if t == 'neg':
            return self.tipo_de(e[1]) if self.tipo_de(e[1]) in NUMERICOS else 'desconocido'
        if t == 'binop':
            op, a, b = e[1], self.tipo_de(e[2]), self.tipo_de(e[3])
            if op == '.':
                return 'string'
            if op == '%':
                return 'int'
            if a in NUMERICOS and b in NUMERICOS:
                if op in ('+', '-', '*') and a == b and a != 'numero':
                    return a
                if 'float' in (a, b) and op != '**':
                    return 'float'
                return 'numero'
            return 'desconocido'
        if t == 'call':
            nombre = e[1]
            if nombre.startswith('$'):
                return 'desconocido'
            info = self.funciones.get(nombre.lower())
            if info:
                return normalizar_tipo(info['ret'])
            return FUNCIONES_PHP.get(nombre.lower()) or 'desconocido'
        if t in ('new', 'arrow_fn'):
            return 'object'
        return 'desconocido'


def normalizar_tipo(tipo):
    """Pasa un tipo declarado (int, FLOAT, array, ...) al vocabulario del analizador."""
    if tipo is None:
        return 'desconocido'
    tipo = str(tipo).lower()
    return {'bool': 'bool', 'int': 'int', 'float': 'float', 'string': 'string',
            'array': 'array'}.get(tipo, 'desconocido')


def _avisar(etiqueta, nodo, ctx):
    for id_regla, funcion in _REGISTRO.get(etiqueta, ()):
        verificaciones[id_regla] = verificaciones.get(id_regla, 0) + 1
        funcion(nodo, ctx)


def _declarar_funciones(nodo, ctx):
    """PHP conoce las funciones y clases antes de ejecutar: se registran primero."""
    if isinstance(nodo, tuple) and nodo:
        if nodo[0] == 'function':
            ctx.funciones[nodo[1].lower()] = {'nombre': nodo[1], 'params': nodo[2],
                                              'ret': nodo[3], 'linea': sintactico.linea_de(nodo)}
        elif nodo[0] == 'class':
            ctx.clases[nodo[1].lower()] = {'nombre': nodo[1], 'padre': nodo[2][1] if nodo[2] else None}
    for h in hijos(nodo):
        _declarar_funciones(h, ctx)


def _definir_destino(destino, tipo, ctx):
    """Asigna una variable (o los elementos de un arreglo que se desestructura)."""
    if not isinstance(destino, tuple) or not destino:
        return
    if destino[0] == 'var':
        _avisar('def_var', destino, ctx)
        ctx.ambito.definir(destino[1], tipo)
    elif destino[0] == 'index':               # $a[0] = x  crea el arreglo si no existe
        base = destino[1]
        while isinstance(base, tuple) and base[0] == 'index':
            _visitar(base[2], ctx)
            base = base[1]
        _visitar(destino[2], ctx)
        if isinstance(base, tuple) and base[0] == 'var':
            if ctx.ambito.buscar(base[1]) is None:
                ctx.ambito.definir(base[1], 'array')
        else:
            _visitar(base, ctx)
    elif destino[0] == 'property':
        _visitar(destino[1], ctx)
    elif destino[0] == 'array':
        for item in destino[1]:
            _definir_destino(item[2] if item[0] == 'pair' else item, 'desconocido', ctx)
    else:
        _visitar(destino, ctx)


def _visitar_bloque(bloque, ctx):
    if isinstance(bloque, tuple) and bloque and bloque[0] == 'block':
        for sentencia in bloque[1]:
            _visitar(sentencia, ctx)
    else:
        _visitar(bloque, ctx)


def _visitar_funcion(nodo, params, ret, cuerpo, nombre, ctx, hereda=False, clase=False):
    anterior = (ctx.ambito, ctx.funcion_actual, ctx.bucles)
    ctx.ambito = Ambito(nombre, ctx.ambito if hereda else None)
    ctx.funcion_actual = {'nombre': nombre, 'params': params, 'ret': ret,
                          'linea': sintactico.linea_de(nodo)}
    ctx.bucles = 0
    if clase:
        ctx.ambito.definir('$this', 'object')
    for p in params:
        ctx.ambito.definir(p[1], normalizar_tipo(p[2]))
        if p[3] is not None:
            _visitar(p[3], ctx)
    if isinstance(cuerpo, tuple) and cuerpo and cuerpo[0] == 'block':
        _visitar_bloque(cuerpo, ctx)
    else:                                       # función flecha: el cuerpo es una expresión
        _visitar(cuerpo, ctx)
    ctx.ambito, ctx.funcion_actual, ctx.bucles = anterior


def _visitar(n, ctx):
    if isinstance(n, list):
        for x in n:
            _visitar(x, ctx)
        return
    if not isinstance(n, tuple) or not n or not isinstance(n[0], str):
        return
    t = n[0]
    _avisar(t, n, ctx)

    if t == 'program':
        _visitar(n[1], ctx)
    elif t == 'block':
        _visitar(n[1], ctx)
    elif t == 'var':
        _avisar('uso_var', n, ctx)
    elif t == 'assign':                        # ('assign', destino, valor)
        _visitar(n[2], ctx)
        _definir_destino(n[1], ctx.tipo_de(n[2]), ctx)
    elif t == 'assign_op':                     # ('assign_op', op, destino, valor)
        _visitar(n[2], ctx)
        _visitar(n[3], ctx)
    elif t == 'incdec':
        _visitar(n[2], ctx)
    elif t == 'destructure':                   # ('destructure', destinos, valor)
        _visitar(n[2], ctx)
        for item in n[1]:
            _definir_destino(item[2] if item[0] == 'pair' else item, 'desconocido', ctx)
    elif t == 'for':                           # ('for', inicio, condicion, paso, bloque)
        for parte in (n[1], n[2]):
            for item in parte:
                _visitar_for_item(item, ctx)
        ctx.bucles += 1
        _visitar_bloque(n[4], ctx)
        for item in n[3]:
            _visitar_for_item(item, ctx)
        ctx.bucles -= 1
    elif t == 'while':
        _visitar(n[1], ctx)
        ctx.bucles += 1
        _visitar_bloque(n[2], ctx)
        ctx.bucles -= 1
    elif t == 'foreach':                       # ('foreach', iterable, clave, valor, bloque)
        _visitar(n[1], ctx)
        for destino in (n[2], n[3]):
            if destino:
                _definir_destino(destino, 'desconocido', ctx)
        ctx.bucles += 1
        _visitar_bloque(n[4], ctx)
        ctx.bucles -= 1
    elif t == 'function':                      # ('function', nombre, params, ret, bloque)
        _visitar_funcion(n, n[2], n[3], n[4], n[1], ctx)
    elif t == 'arrow_fn':                      # ('arrow_fn', params, ret, expresion)
        _visitar_funcion(n, n[1], n[2], n[3], '{closure}', ctx, hereda=True)
    elif t == 'class':                         # ('class', nombre, extiende, miembros)
        anterior, ctx.clase_actual = ctx.clase_actual, n[1]
        for m in n[3]:
            if m[0] == 'property' and m[2][2] is not None:
                _visitar(m[2][2], ctx)
            elif m[0] == 'method':             # ('method', visibilidad, nombre, params, ret, bloque)
                _visitar_funcion(m, m[3], m[4], m[5], m[2], ctx, clase=True)
        ctx.clase_actual = anterior
    elif t == 'call':                          # ('call', nombre, argumentos)
        if n[1].startswith('$'):               # $f(...): la variable $f se lee
            _avisar('uso_var', n, ctx)
        _visitar(n[2], ctx)
    elif t == 'if':                            # ('if', condicion, bloque, resto)
        _visitar(n[1], ctx)
        _visitar_bloque(n[2], ctx)
        _visitar(n[3], ctx)
    elif t == 'elseif':                        # ('elseif', condicion, bloque, resto)
        _visitar(n[1], ctx)
        _visitar_bloque(n[2], ctx)
        _visitar(n[3], ctx)
    elif t == 'else':
        _visitar_bloque(n[1], ctx)
    elif t in ('lit', 'const', 'error', 'break', 'continue'):
        pass
    else:                                      # cualquier otro nodo: se recorren sus hijos
        for h in hijos(n):
            _visitar(h, ctx)


def _visitar_for_item(item, ctx):
    """('for_item', expr) | ('for_item', destino, '=', valor) | (.., destino, op, valor) | (.., e, '++')"""
    if len(item) == 4 and item[2] == '=':
        _visitar(item[3], ctx)
        _definir_destino(item[1], ctx.tipo_de(item[3]), ctx)
    else:
        for h in item[1:]:
            if isinstance(h, tuple):
                _visitar(h, ctx)


def _ejecutar(arbol):
    ctx = Contexto()
    _declarar_funciones(arbol, ctx)
    _visitar(arbol, ctx)
    return ctx


# ---------------------------------------------------------------------------
# ZONA DEL INTEGRANTE 1
# INICIO DEL APORTE - dbolanos-s
# Reglas: R1 (identificadores: variable usada antes de definirse) y
#         R2 (asignación de tipo: una constante no puede redefinirse)


# R1: toda variable debe haber sido asignada antes de usarse, en el ámbito global
# o dentro de la función donde se usa.  También cubre $f(...) con $f sin definir.
@regla_semantica('R1', 'Identificadores', 'uso_var')
def r1_variable_definida(nodo, ctx):
    nombre = nodo[1]
    if not ctx.variable_definida(nombre):
        ctx.error('R1', 'Identificadores', nodo,
                  f'la variable {nombre} se usa sin haber sido definida')


# R2: una constante no puede redefinirse (const o define() repetidos sobre el mismo nombre).
def _registrar_constante(nodo, nombre, ctx):
    if nombre in ctx.constantes:
        ctx.error('R2', 'Asignación de tipo', nodo,
                  f'la constante {nombre} ya fue definida y no se puede modificar')
    else:
        ctx.constantes[nombre] = sintactico.linea_de(nodo)


@regla_semantica('R2', 'Asignación de tipo', 'const_def')
def r2_constante_const(nodo, ctx):
    _registrar_constante(nodo, nodo[1], ctx)


@regla_semantica('R2', 'Asignación de tipo', 'call')
def r2_constante_define(nodo, ctx):
    # define('NOMBRE', valor): el nombre es una cadena literal
    if nodo[1].lower() == 'define' and nodo[2]:
        primero = nodo[2][0]
        if isinstance(primero, tuple) and primero[0] == 'lit' and primero[2] == 'string':
            _registrar_constante(nodo, primero[1][1:-1], ctx)
# FIN DEL APORTE - dbolanos-s
# (fin de la zona del integrante 1)


# ZONA DE Fernando
# INICIO DEL APORTE - fdiazoso
# Reglas: R3 (operaciones permitidas: tipos de los operandos) y
#         R4 (retorno de funciones: el return coincide con el tipo declarado)


# R3: con los tipos conocidos de los operandos se comprueba que la operación tenga sentido:
#  - las operaciones aritméticas (+ - * / % **) solo se hacen entre números
#  - la concatenación (.) no admite arreglos
#  - no se compara una cadena con un número usando < > <= >=
# Si algún tipo es 'desconocido' no se marca error.
ARITMETICOS = ('+', '-', '*', '/', '%', '**')


@regla_semantica('R3', 'Operaciones permitidas', 'binop', 'cmp')
def r3_operaciones(nodo, ctx):
    op, a, b = nodo[1], ctx.tipo_de(nodo[2]), ctx.tipo_de(nodo[3])
    if 'desconocido' in (a, b):
        return
    if nodo[0] == 'binop' and op in ARITMETICOS and (a not in NUMERICOS or b not in NUMERICOS):
        ctx.error('R3', 'Operaciones permitidas', nodo,
                  f"la operación '{op}' no está permitida entre {a} y {b}")
    elif nodo[0] == 'binop' and op == '.' and 'array' in (a, b):
        ctx.error('R3', 'Operaciones permitidas', nodo,
                  'la concatenación no admite arreglos')
    elif (nodo[0] == 'cmp' and op in ('<', '>', '<=', '>=') and 'string' in (a, b)
          and (a in NUMERICOS or b in NUMERICOS)):
        ctx.error('R3', 'Operaciones permitidas', nodo,
                  f"no se puede comparar {a} con {b} usando '{op}'")


# R4: en una función con tipo de retorno declarado, cada return debe devolver ese tipo.
# Se acepta int donde se declara float, y un número sin tipo exacto donde se declara
# int o float.  Si la función no declara tipo o el tipo es 'desconocido', no se marca error.
@regla_semantica('R4', 'Retorno de funciones', 'return')
def r4_retorno(nodo, ctx):
    funcion = ctx.funcion_actual
    if not funcion or funcion['ret'] is None or nodo[1] is None:
        return
    declarado, devuelto = normalizar_tipo(funcion['ret']), ctx.tipo_de(nodo[1])
    if 'desconocido' in (declarado, devuelto):
        return
    valido = (devuelto == declarado
              or (declarado == 'float' and devuelto == 'int')
              or (devuelto == 'numero' and declarado in ('int', 'float')))
    if not valido:
        ctx.error('R4', 'Retorno de funciones', nodo,
                  f"la función '{funcion['nombre']}' declara {declarado} pero retorna {devuelto}")
# FIN DEL APORTE - fdiazoso
# (fin de la zona del integrante 2)


# ZONA DE Symond
# INICIO DEL APORTE - SymondSalazar
# R5: break/continue solo aparecen dentro de un ciclo y foreach recorre arrays/objetos.
@regla_semantica('R5', 'Estructuras de control', 'break', 'continue')
def r5_break_continue(nodo, ctx):
    if ctx.bucles == 0:
        ctx.error('R5', 'Estructuras de control', nodo,
                  f"'{nodo[0]}' solo puede usarse dentro de un bucle")


@regla_semantica('R5', 'Estructuras de control', 'foreach')
def r5_foreach(nodo, ctx):
    tipo = ctx.tipo_de(nodo[1])
    if tipo not in ('array', 'object', 'desconocido'):
        ctx.error('R5', 'Estructuras de control', nodo,
                  f'foreach requiere un array, pero recibio {tipo}')


# R6: una llamada debe apuntar a una función conocida y respetar sus argumentos.
@regla_semantica('R6', 'Identificadores', 'call')
def r6_funcion(nodo, ctx):
    nombre = nodo[1]
    if nombre.startswith('$') or nombre.lower() in FUNCIONES_PHP:
        return
    funcion = ctx.funciones.get(nombre.lower())
    if not funcion:
        ctx.error('R6', 'Identificadores', nodo,
                  f"la funcion '{nombre}' no esta definida")
        return
    obligatorios = sum(p[3] is None for p in funcion['params'])
    total, recibidos = len(funcion['params']), len(nodo[2])
    if not obligatorios <= recibidos <= total:
        ctx.error('R6', 'Identificadores', nodo,
                  f"'{nombre}' espera {obligatorios} a {total} argumentos, recibio {recibidos}")

# (fin de la zona del integrante 3)


# ---------------------------------------------------------------------------
# EJECUCIÓN (no modificar)
# ---------------------------------------------------------------------------
def analizar_semantico(codigo):
    """Análisis léxico + sintáctico + semántico.

    Devuelve (errores_lexicos, errores_sintacticos, errores_semanticos, verificaciones).
    Si hay errores léxicos o sintácticos NO se hace el análisis semántico: sin un árbol
    correcto sus resultados no serían confiables.
    """
    sem_errors.clear()
    verificaciones.clear()
    usadas, errores_sint, errores_lex = sintactico.analizar(codigo)
    if not errores_lex and not errores_sint and sintactico.arbol:
        _ejecutar(sintactico.arbol)
    return errores_lex, errores_sint, sorted(sem_errors, key=lambda e: e['linea']), dict(verificaciones)
