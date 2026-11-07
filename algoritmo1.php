<?php
// Algoritmo 1: promedio de notas y clasificación del estudiante
# Integrante 1: variables, literales y comentarios
/* Literales usados:
   int, float, string, bool y null */
$nombre = "Ana";
$apellido = 'Pérez';
$edad = 20;
$peso = 61.5;
$activo = true;
$graduado = FALSE;
$apodo = null;
$notas = [8.5, 9, 7.25, 10];

function promedio(array $lista, int $n): float {
    return ($lista[0] + $lista[1] + $lista[2] + $lista[3]) / $n;
}

$prom = promedio($notas, 4);
if ($prom >= 9.0) {
    $nivel = "Excelente";
} elseif ($prom >= 7) {
    $nivel = 'Bueno';
} else {
    $nivel = "Debe mejorar";
}

echo "Estudiante: ", $nombre, " ", $apellido, "\n";
echo "Promedio: " . $prom . "\n";
print "Nivel: " . $nivel . "\n";
if ($activo && $apodo === null) {
    echo "Sin apodo registrado\n"; // fin del algoritmo
}
?>
