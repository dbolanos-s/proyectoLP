<?php
// Algoritmo 1 (semántico): variables definidas antes de usarse y constantes sin redefinir
const IVA = 15;
define('ESCUELA', 'FIEC');

$nombre = "Belen";
$notas = [8.5, 9, 7.25, 10];
$total = 0;

function promedio(array $lista, int $n): float {
    $suma = 0;
    foreach ($lista as $valor) {
        $suma += $valor;
    }
    return $suma / $n;
}

$prom = promedio($notas, 4);
$resumen = fn($x) => $x + $prom;
$edad = readline();

if ($prom >= 9) {
    $nivel = "Excelente";
} else {
    $nivel = "Bueno";
}

echo ESCUELA, ": ", $nombre, " ", $nivel, " ", $resumen($edad), "\n";
?>
