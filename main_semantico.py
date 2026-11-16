"""
Ejecuta el analizador semántico sobre un archivo PHP y guarda un log en logs/.

Uso:
    python main_semantico.py algoritmo1_semantico.php --user su_usuario_github

Nombre del log:  semantico-<usuarioGit>-<ddmmaaaa>-<HH>h<MM>.txt
                 (ejemplo: semantico-fcisnero-20112025-23h32.txt)

Si el archivo tiene errores léxicos o sintácticos, el análisis semántico se omite y el
log lo indica: con un árbol incompleto sus resultados no serían confiables.
"""
import argparse
import os
import sys
import time
from datetime import datetime

import semantico

NOMBRES_REGLAS = {
    'R1': 'Identificadores: variable usada antes de definirse',
    'R2': 'Asignación de tipo: constante redefinida',
    'R3': 'Operaciones permitidas: tipos de los operandos',
    'R4': 'Retorno de funciones: tipo del return',
    'R5': 'Estructuras de control: break/continue y foreach',
    'R6': 'Identificadores: función definida y argumentos',
}


def usuario_git(valor):
    if not valor:
        raise SystemExit("Falta --user: escribe tu usuario de GitHub, por ejemplo --user dbolanos-s")
    return valor


def ruta_log(usuario, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    avisado = False
    while True:
        ahora = datetime.now()
        ruta = os.path.join(carpeta, f"semantico-{usuario}-{ahora:%d%m%Y-%Hh%M}.txt")
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
    err_lex, err_sint, err_sem, verif = semantico.analizar_semantico(codigo)
    usuario = usuario_git(a.user)
    ruta, ahora = ruta_log(usuario, a.logs)
    omitido = bool(err_lex or err_sint)

    lineas = [
        'ANALIZADOR SEMÁNTICO - PHP',
        f'Desarrollador : {usuario}',
        f'Archivo       : {a.archivo}',
        f'Fecha y hora  : {ahora:%d/%m/%Y %H:%M:%S}',
        '=' * 70,
    ]
    if omitido:
        lineas += [f'ANÁLISIS SEMÁNTICO OMITIDO: el archivo tiene {len(err_lex)} errores léxicos y '
                   f'{len(err_sint)} errores sintácticos.',
                   'Corríjalos primero; sin un árbol sintáctico correcto el resultado no sería confiable.']
        lineas += [f"Error léxico - línea {e['linea']}, col {e['columna']}: {e['mensaje']}" for e in err_lex]
        lineas += [f"Error sintáctico - línea {e['linea']}, col {e['columna']}: {e['mensaje']}" for e in err_sint]
    else:
        lineas.append('REGLAS VERIFICADAS (veces que se comprobó cada una)')
        lineas += [f'  {r}  {NOMBRES_REGLAS.get(r, ""):<52} {n}' for r, n in sorted(verif.items())] or ['  (ninguna)']
        lineas += ['-' * 70, f'ERRORES SEMÁNTICOS ({len(err_sem)})']
        lineas += [f"Error semántico [{e['categoria']}] - línea {e['linea']}: {e['mensaje']}" for e in err_sem]
        if not err_sem:
            lineas.append('(sin errores)')
    resumen = ('análisis omitido por errores previos' if omitido
               else f'{sum(verif.values())} verificaciones, {len(err_sem)} errores semánticos')
    lineas += ['=' * 70, f'RESUMEN: {resumen}']

    texto = '\n'.join(lineas) + '\n'
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(texto)
    print(f'Log guardado en: {ruta}')
    return 1 if (omitido or err_sem) else 0


if __name__ == '__main__':
    sys.exit(main())
