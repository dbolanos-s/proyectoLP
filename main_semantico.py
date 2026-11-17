"""Ejecuta el análisis semántico y guarda un log."""
import argparse
import os
from datetime import datetime

import semantico
import sintactico


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('archivo')
    ap.add_argument('--user', required=True)
    ap.add_argument('--logs', default='logs')
    args = ap.parse_args()
    codigo = open(args.archivo, encoding='utf-8').read()
    arbol, sint_errors, lex_errors = sintactico.parsear(codigo)
    errores = [] if sint_errors or lex_errors else semantico.analizar(arbol)
    os.makedirs(args.logs, exist_ok=True)
    ahora = datetime.now()
    ruta = os.path.join(args.logs, f"semantico-{args.user}-{ahora:%d%m%Y-%Hh%M}.txt")
    lineas = [f'ANALIZADOR SEMÁNTICO - {args.archivo}', f'Desarrollador: {args.user}', '=' * 70]
    if sint_errors or lex_errors:
        lineas.append('ANÁLISIS OMITIDO: el archivo tiene errores léxicos o sintácticos')
    lineas.append(f'ERRORES SEMÁNTICOS ({len(errores)})')
    lineas.extend(f"Error {e['regla']} - línea {e['linea']}: {e['mensaje']}" for e in errores)
    if not errores:
        lineas.append('(sin errores)')
    texto = '\n'.join(lineas) + '\n'
    with open(ruta, 'w', encoding='utf-8') as salida:
        salida.write(texto)
    print(texto, end='')
    print(f'Log guardado en: {ruta}')
    return 1 if errores or sint_errors or lex_errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
