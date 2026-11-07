"""
Ejecuta el analizador léxico sobre un archivo PHP y guarda un log en logs/.

Uso:
    python main_lexico.py algoritmo1.php
    python main_lexico.py algoritmo1.php --user su_usuario_github

Nombre del log:  lexico-<usuarioGit>-<dd-mm-aaaa>-<HH>h<MM>.txt
                 (ejemplo: lexico-fcisnero-01-11-2026-14h32.txt)
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

import lexico


def usuario_git(valor):
    if not valor:
        raise SystemExit("Falta --user: escribe tu usuario de GitHub, por ejemplo --user dbolanos-s")
    return valor


def ruta_log(usuario, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    avisado = False
    while True:
        ahora = datetime.now()
        ruta = os.path.join(carpeta, f"lexico-{usuario}-{ahora:%d-%m-%Y-%Hh%M}.txt")
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
    tokens, errores = lexico.tokenizar(codigo)
    usuario = usuario_git(a.user)
    ruta, ahora = ruta_log(usuario, a.logs)

    lineas = [
        'ANALIZADOR LÉXICO - PHP (PLY)',
        f'Desarrollador : {usuario}',
        f'Archivo       : {a.archivo}',
        f'Fecha y hora  : {ahora:%d/%m/%Y %H:%M:%S}',
        '=' * 70,
        f'TOKENS RECONOCIDOS ({len(tokens)})',
        f'{"Línea":>5} {"Col":>4}  {"Tipo":<11} Valor',
    ]
    lineas += [f"{t['linea']:>5} {t['columna']:>4}  {t['tipo']:<11} {t['valor']!r}" for t in tokens]
    lineas += ['-' * 70, f'ERRORES LÉXICOS ({len(errores)})']
    lineas += [f"Error léxico - línea {e['linea']}, col {e['columna']}: {e['mensaje']}" for e in errores]
    if not errores:
        lineas.append('(sin errores)')
    lineas += ['=' * 70, f'RESUMEN: {len(tokens)} tokens, {len(errores)} errores']

    texto = '\n'.join(lineas) + '\n'
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(texto)
    print(f'Log guardado en: {ruta}')
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
