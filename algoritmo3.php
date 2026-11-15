<?php
// Algoritmo 3: mayor elemento de una matriz
// Integrante 3: palabras reservadas, delimitadores y etiquetas
class Contador extends Base {
    private int $valor = 0;

    public function incrementar(int $pasos): int {
        $this->valor = $this->valor + $pasos;
        return $this->valor;
    }
}

$filas = 2;
define('TITULO', 'Matriz');
$contador = new Contador();
$matriz = [[3, 8, 1], [9, 4, 7]];
$mayor = $matriz[0][0];

function mayor_de(int $a, int $b): int {
    if ($a > $b) {
        return $a;
    } else {
        return $b;
    }
}

foreach ($matriz as $indice => $fila) {
    if ($indice == 1) {
        continue;
    }
    foreach ($fila as $valor) {
        $mayor = mayor_de($mayor, $valor);
    }
    if ($mayor > 8) {
        break;
    }
}

$doble = fn($x) => $x * 2;
echo TITULO, ': ', $mayor, ' x2 = ', $doble($mayor), "\n";
echo "Escriba un dato: ";
$dato = readline();
$viejo = array(1, 2, 3);
$i = 0;
while (true) {
    $i++;
    if ($i >= 3) {
        break;
    } else {
        continue;
    }
}
echo 'Filas: ', $filas, ', iteraciones: ', $i, "\n";
echo 'Contador: ', $contador->incrementar(2), "\n";
?>
