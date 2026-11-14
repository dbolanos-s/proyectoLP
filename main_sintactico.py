"""
Ejecuta el analizador sintáctico sobre un archivo PHP y guarda un log en logs/.

Uso:
    python main_sintactico.py algoritmo1_sintactico.php --user su_usuario_github

Nombre del log:  sintactico-<usuarioGit>-<aaaammdd>-<HH>h<MM>.txt
                 (ejemplo: sintactico-fcisnero-20261104-23h32.txt)
"""
import argparse
import os
import sys
import time
from datetime import datetime

import sintactico


def usuario_git(valor):
    if not valor:
        raise SystemExit("Falta --user: escribe tu usuario de GitHub, por ejemplo --user dbolanos-s")
    return valor


def ruta_log(usuario, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    avisado = False
    while True:
        ahora = datetime.now()
        ruta = os.path.join(carpeta, f"sintactico-{usuario}-{ahora:%Y%m%d-%Hh%M}.txt")
        if not os.path.exists(ruta):
            return ruta, ahora
        if not avisado:   # el nombre solo llega hasta el minuto: se espera al siguiente
            print('Ya existe un log de este minuto; esperando al minuto siguiente para no sobrescribirlo...')
            avisado = True
        time.sleep(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('archivo')
    ap.add_argument('--user', default='')
    ap.add_argument('--logs', default='logs')
    a = ap.parse_args()

    codigo = open(a.archivo, encoding='utf-8').read()
    usadas, errores, lex_err = sintactico.analizar(codigo)
    usuario = usuario_git(a.user)
    ruta, ahora = ruta_log(usuario, a.logs)

    lineas = [
        'ANALIZADOR SINTÁCTICO - PHP (PLY yacc)',
        f'Desarrollador : {usuario}',
        f'Archivo       : {a.archivo}',
        f'Fecha y hora  : {ahora:%d/%m/%Y %H:%M:%S}',
        '=' * 70,
        'ESTRUCTURAS RECONOCIDAS',
    ]
    lineas += [f'  {n:<26} {c}' for n, c in sorted(usadas.items())] or ['  (ninguna)']
    lineas += ['-' * 70, f'ERRORES SINTÁCTICOS ({len(errores)})']
    lineas += [f"Error sintáctico - línea {e['linea']}, col {e['columna']}: {e['mensaje']}" for e in errores]
    if not errores:
        lineas.append('(sin errores)')
    if lex_err:
        lineas += ['-' * 70, f'AVISO: el archivo tiene {len(lex_err)} errores léxicos (ver el log léxico).']
    lineas += ['=' * 70, f'RESUMEN: {sum(usadas.values())} estructuras, {len(errores)} errores sintácticos']

    texto = '\n'.join(lineas) + '\n'
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(texto)
    print(f'Log guardado en: {ruta}')
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
