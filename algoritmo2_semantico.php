<?php
// Algoritmo 2 (semántico): operaciones entre tipos compatibles y retornos correctos
# Integrante 2: fdiazoso - reglas R3 y R4
$precio = 12.5;
$cantidad = 4;
$nombre = "Tornillos";
$lista = [3, 5, 8];

// R3: aritmética entre números, concatenación de texto y comparaciones válidas
$subtotal = $precio * $cantidad;
$impuesto = $subtotal * 0.12 + 1;
$potencia = 2 ** 3 % 5;
$etiqueta = $nombre . ": " . $subtotal;
$caro = $subtotal >= 40;
$mismo = $nombre == "Tornillos";

// R4: cada return coincide con el tipo declarado
function total(float $p, int $c): float {
    return $p * $c;
}

function contar(array $datos): int {
    return count($datos);
}

function promedio(int $a, int $b): float {
    return ($a + $b) / 2;
}

function saludo(string $quien): string {
    return "Hola " . $quien;
}

function entero(): float {
    return 7;
}

$t = total($precio, $cantidad);
$n = contar($lista);
$m = promedio(3, 4);
echo saludo($nombre), " ", $t, " ", $n, " ", $m, " ", entero(), "\n";
?>
