<?php
// Algoritmo 1 (sintáctico): arreglos, if/elseif/else, funciones e impresión
$nombre = "Belen";
$edad = 20;
$activo = true;
$notas = [8.5, 9, 7.25, 10];
$datos = array("nombre" => "Belen", "edad" => 20, "notas" => [1, 2]);

function describir(string $titulo, int $n = 3): string {
    echo "Describiendo ", $titulo, "\n";
    return $titulo;
}

function saludar() {
    print "Hola";
    return;
}

$primera = $notas[0];
$datos["edad"] = 21;
$notas[1] = 9.5;
$linea = readline();
$texto = describir($nombre, 5);

for ($i = 0; $activo; $i++) {
    echo $i, "\n";
}
for (;;) {
    print "infinito";
}
for ($j = 10, $k = 0; $edad; $j -= 2, $k += 1) {
    $total = $j;
}

if ($activo) {
    echo "Activo\n";
} elseif ($edad) {
    echo "Con edad\n";
} elseif ($primera) {
    print "Con nota";
} else {
    saludar();
}
?>
