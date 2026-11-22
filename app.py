# -*- coding: utf-8 -*-
"""
Interfaz gráfica del analizador de PHP (Streamlit).  Muestra, para un código PHP,
el resultado de las tres fases: léxico, sintáctico y semántico.

Uso:
    pip install streamlit ply
    streamlit run app.py
"""
import glob
import os

import streamlit as st

import lexico
import semantico
import sintactico

CARPETA = os.path.dirname(os.path.abspath(__file__))

NOMBRES_REGLAS = {
    'R1': 'Identificadores: variable usada antes de definirse',
    'R2': 'Asignación de tipo: constante redefinida',
    'R3': 'Operaciones permitidas: tipos de los operandos',
    'R4': 'Retorno de funciones: tipo del return',
    'R5': 'Estructuras de control: break/continue y foreach',
    'R6': 'Identificadores: función definida y argumentos',
}

st.set_page_config(page_title="Analizador de PHP", page_icon="🔎", layout="wide")


def leer(ruta):
    with open(ruta, encoding='utf-8') as f:
        return f.read()


def marcar_lineas(codigo, errores):
    """Código con números de línea; las líneas con error llevan una marca."""
    con_error = {e['linea'] for e in errores}
    filas = []
    for n, texto in enumerate(codigo.splitlines(), start=1):
        filas.append({'': '⚠' if n in con_error else '', 'Línea': n, 'Código': texto})
    return filas


# ---------------------------------------------------------------- barra lateral
st.sidebar.header("Entrada")
ejemplos = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CARPETA, '*.php')))
origen = st.sidebar.radio("Código a analizar", ["Archivo de ejemplo", "Escribir o pegar código"])
if origen == "Archivo de ejemplo" and ejemplos:
    por_defecto = 'algoritmo1_semantico_error.php' if 'algoritmo1_semantico_error.php' in ejemplos else ejemplos[0]
    nombre = st.sidebar.selectbox("Archivo", ejemplos, index=ejemplos.index(por_defecto))
    codigo = leer(os.path.join(CARPETA, nombre))
    st.sidebar.code(codigo, language='php')
else:
    codigo = st.sidebar.text_area("Código PHP", height=320, value="<?php\n$a = 1;\necho $b;\n?>")
    nombre = "(código escrito)"

st.sidebar.caption("Las pruebas con `_error` contienen errores a propósito.")

# ---------------------------------------------------------------- análisis
st.title("🔎 Analizador léxico, sintáctico y semántico de PHP")
st.caption(f"Archivo: **{nombre}** · Analizadores escritos en Python con PLY")

tokens, err_lex = lexico.tokenizar(codigo)
err_lex2, err_sint, err_sem, verif = semantico.analizar_semantico(codigo)
estructuras, _, _ = sintactico.analizar(codigo)
omitido = bool(err_lex or err_sint)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tokens", len(tokens))
c2.metric("Errores léxicos", len(err_lex))
c3.metric("Errores sintácticos", len(err_sint))
c4.metric("Errores semánticos", "—" if omitido else len(err_sem))

if err_lex:
    st.error("Hay errores léxicos: corrige el código antes de continuar con las siguientes fases.")
elif err_sint:
    st.warning("Hay errores sintácticos: el análisis semántico se omite porque el árbol no es confiable.")
elif err_sem:
    st.warning(f"El código es válido léxica y sintácticamente, pero tiene {len(err_sem)} error(es) semántico(s).")
else:
    st.success("Sin errores en ninguna fase.")

tab_lex, tab_sint, tab_sem = st.tabs(["1 · Léxico", "2 · Sintáctico", "3 · Semántico"])

with tab_lex:
    st.subheader("Tokens reconocidos")
    st.dataframe([{'Línea': t['linea'], 'Col': t['columna'], 'Tipo': t['tipo'], 'Valor': repr(t['valor'])}
                  for t in tokens], hide_index=True)
    st.subheader(f"Errores léxicos ({len(err_lex)})")
    if err_lex:
        for e in err_lex:
            st.error(f"Línea {e['linea']}, col {e['columna']}: {e['mensaje']}")
    else:
        st.write("Sin errores léxicos.")

with tab_sint:
    st.subheader("Estructuras reconocidas")
    if estructuras:
        st.dataframe([{'Estructura': k, 'Veces': v} for k, v in sorted(estructuras.items())],
                     hide_index=True)
    else:
        st.write("No se reconoció ninguna estructura.")
    st.subheader(f"Errores sintácticos ({len(err_sint)})")
    if err_sint:
        for e in err_sint:
            st.error(f"Línea {e['linea']}, col {e['columna']}: {e['mensaje']}")
    else:
        st.write("Sin errores sintácticos.")

with tab_sem:
    if omitido:
        st.info("Análisis semántico omitido: el archivo tiene errores léxicos o sintácticos.")
    else:
        st.subheader("Reglas verificadas")
        st.dataframe([{'Regla': r, 'Descripción': NOMBRES_REGLAS.get(r, ''), 'Veces': n}
                      for r, n in sorted(verif.items())], hide_index=True)
        st.subheader(f"Errores semánticos ({len(err_sem)})")
        if err_sem:
            for e in err_sem:
                st.error(f"[{e['categoria']}] Línea {e['linea']}: {e['mensaje']}")
            st.caption("Las líneas con error están marcadas con ⚠ en el código:")
            st.dataframe(marcar_lineas(codigo, err_sem), hide_index=True)
        else:
            st.write("Sin errores semánticos.")
