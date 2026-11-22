# proyectoLP – Analizador léxico, sintáctico y semántico de PHP

Proyecto de **Lenguajes de Programación**. Analiza código **PHP** (un subconjunto del lenguaje) en tres fases. Los analizadores están escritos en **Python** con la librería **PLY** (`lex` y `yacc`).

## Integrantes

| Integrante | Usuario de GitHub |
|---|---|
| Doménica Bolaños | `dbolanos-s` |
| Fernando | `fdiazoso` |
| Symond Salazar | `SymondSalazar` |

## Requisitos

- Python 3
- PLY: `pip install ply` (o `pip install -r requirements.txt`)

## Cómo ejecutar

Cada fase tiene su programa. Todos reciben un archivo PHP y generan un log en `logs/`.

```
python main_lexico.py algoritmo1.php --user SU_USUARIO_GITHUB
python main_sintactico.py algoritmo1.php --user SU_USUARIO_GITHUB
python main_semantico.py algoritmo1.php --user SU_USUARIO_GITHUB
```

- Si el archivo tiene errores léxicos o sintácticos, el análisis semántico se omite y el log lo indica, porque sin un árbol correcto el resultado no sería confiable.
- Si ya existe un log con el mismo nombre en ese minuto, el programa espera al minuto siguiente para no sobrescribirlo.

### Interfaz gráfica

```
pip install streamlit
streamlit run app.py
```

Se abre en el navegador. Permite elegir uno de los algoritmos de ejemplo o pegar código PHP, y muestra en pestañas el resultado de cada fase: tokens y errores léxicos, estructuras y errores sintácticos, y reglas verificadas y errores semánticos (con las líneas con error marcadas).

### Formato de los logs

| Fase | Nombre del log | Ejemplo |
|---|---|---|
| Léxico | `lexico-<usuario>-<dd-mm-aaaa>-<HH>h<MM>.txt` | `lexico-fdiazoso-14-11-2026-15h57.txt` |
| Sintáctico | `sintactico-<usuario>-<aaaammdd>-<HH>h<MM>.txt` | `sintactico-fdiazoso-20261114-15h57.txt` |
| Semántico | `semantico-<usuario>-<ddmmaaaa>-<HH>h<MM>.txt` | `semantico-dbolanos-s-16112026-15h56.txt` |

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `lexico.py` | Analizador léxico (tokens, errores léxicos) |
| `sintactico.py` | Analizador sintáctico: gramática y árbol sintáctico |
| `semantico.py` | Analizador semántico: motor compartido y reglas R1–R6 |
| `main_lexico.py`, `main_sintactico.py`, `main_semantico.py` | Programas que ejecutan cada fase y escriben el log |
| `app.py` | Interfaz gráfica (Streamlit) para probar las tres fases |
| `algoritmo1.php`, `algoritmo2.php`, `algoritmo3.php` | Algoritmos de prueba válidos (uno por integrante) |
| `*_sintactico.php`, `*_sintactico_error.php` | Pruebas del Avance 2 (válidas y con errores sintácticos) |
| `*_semantico.php`, `*_semantico_error.php` | Pruebas del Avance 3 (válidas y con errores semánticos) |
| `logs/` | Logs generados por cada prueba |

Cada archivo `.py` está dividido en **zonas**. Cada integrante escribe solo en la suya, entre los comentarios `INICIO DEL APORTE - usuario` y `FIN DEL APORTE - usuario`.

## Reglas semánticas (Avance 3)

| Regla | Categoría | Integrante | Qué comprueba |
|---|---|---|---|
| R1 | Identificadores | `dbolanos-s` | Una variable debe estar definida antes de usarse |
| R2 | Asignación de tipo | `dbolanos-s` | Una constante (`const` o `define`) no se puede redefinir |
| R3 | Operaciones permitidas | `fdiazoso` | Los tipos de los operandos permiten la operación o comparación |
| R4 | Retorno de funciones | `fdiazoso` | El `return` coincide con el tipo declarado de la función |
| R5 | Estructuras de control | `SymondSalazar` | `break`/`continue` solo dentro de bucles; `foreach` solo sobre arreglos |
| R6 | Identificadores | `SymondSalazar` | La función llamada existe y recibe el número correcto de argumentos |

Cuando el tipo de una expresión no se puede determinar, el analizador no marca error, para evitar falsos positivos.

## Pruebas por integrante

| Integrante | Algoritmo válido | Algoritmo con errores semánticos |
|---|---|---|
| `dbolanos-s` | `algoritmo1_semantico.php` | `algoritmo1_semantico_error.php` |
| `fdiazoso` | `algoritmo2_semantico.php` | `algoritmo2_semantico_error.php` |
| `SymondSalazar` | `algoritmo3_semantico.php` | `algoritmo3_semantico_error.php` |

## Limitaciones

Se analiza un subconjunto de PHP: la interpolación de variables dentro de cadenas no se analiza, y solo se reconocen las estructuras definidas en la gramática.
