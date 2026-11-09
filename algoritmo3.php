<?php
// Algoritmo 3: mayor elemento de una matriz
// Integrante 3: palabras reservadas, delimitadores y etiquetas
const FILAS = 2;
define('TITULO', 'Matriz');
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
    foreach ($fila as $valor) {
        $mayor = mayor_de($mayor, $valor);
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
echo 'Filas: ', FILAS, ', iteraciones: ', $i, "\n";
?>
