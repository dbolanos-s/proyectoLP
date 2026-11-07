<?php
// Algoritmo 2: inventario con descuento opcional
# Integrante 2: operadores aritméticos, de asignación, de comparación y lógicos
$inventario = ["tornillos" => 120, "tuercas" => 80, "clavos" => 200];
$precios = ["tornillos" => 0.25, "tuercas" => 0.4, "clavos" => 0.1];

function total(float $precio, int $cantidad, float $descuento = 0.0): float {
    $bruto = $precio * $cantidad;
    return $bruto - $bruto * $descuento;
}

$acumulado = 0;
$acumulado += total($precios["tornillos"], $inventario["tornillos"]);
$acumulado += total($precios["tuercas"], $inventario["tuercas"], 0.1);
$acumulado -= 1;
$acumulado *= 2;
$acumulado /= 4;
$mensaje = "Total: ";
$mensaje .= $acumulado;

for ($i = 1; $i <= 3; $i++) {
    echo $i ** 2, " ";
}

$j = 10;
while ($j > 0 && $j != 4) {
    $j -= 3;
    $j--;
}
$resto = 17 % 5;
$ok = ($resto === 2 || $j < 0) && !($acumulado <= 0);
$distinto = $resto !== 3;
$igual = $resto == 2;
$mayor = $j >= 1;
echo "\n", $mensaje, " resto=", $resto, "\n";
?>
