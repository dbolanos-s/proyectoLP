"""
Inserta el bloque de un integrante en su zona de lexico.py.

Uso (desde la raíz del repositorio):
    python aportes/insertar_bloque.py 1 --user su_usuario_github
"""
import argparse
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument('integrante', type=int, choices=(1, 2, 3))
ap.add_argument('--user', default=os.environ.get('GITHUB_USER', ''),
                help='su usuario de GitHub (reemplaza @usuarioN en los comentarios)')
a = ap.parse_args()

aqui = os.path.dirname(os.path.abspath(__file__))
ruta_lexico = os.path.join(aqui, '..', 'lexico.py')
marcador = f'# <<<APORTE_INTEGRANTE_{a.integrante}>>>'
bloque = open(os.path.join(aqui, f'bloque_integrante{a.integrante}.py'), encoding='utf-8').read()
if a.user:
    bloque = bloque.replace(f'@usuario{a.integrante}', f'@{a.user}')

texto = open(ruta_lexico, encoding='utf-8').read()
if marcador not in texto:
    sys.exit(f'No se encontró el marcador del integrante {a.integrante}: ¿ya insertó su bloque?')
open(ruta_lexico, 'w', encoding='utf-8').write(texto.replace(marcador, bloque.rstrip('\n')))
print(f'Bloque del integrante {a.integrante} insertado en lexico.py')
