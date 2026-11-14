<?php
// Algoritmo 2 (sintáctico): expresiones, operadores, while, desestructuración y fn
# Integrante 2: fdiazoso
$precios = [12.5, 8, 3.75];
$cantidades = [2, 5, 10];
$cliente = ["nombre" => "Ana", "vip" => true];

// desestructuración de arreglos
[$p1, $p2, $p3] = $precios;
["nombre" => $nombre, "vip" => $vip] = $cliente;

// expresiones aritméticas y concatenación
$subtotal = $p1 * $cantidades[0] + $p2 * $cantidades[1] + $p3 * $cantidades[2];
$promedio = ($p1 + $p2 + $p3) / 3;
$cuadrado = 2 ** 3 ** 2;
$resto = $cantidades[2] % 3;
$negativo = -$resto + 1;
$etiqueta = "Cliente: " . $nombre . " (" . $subtotal . ")";

// función flecha
$descuento = fn($monto) => $monto * 0.1;
$conIva = fn(float $x): float => $x + $x * 0.12;
$total = $conIva($subtotal - $descuento($subtotal));

// asignación compuesta, incremento y decremento
$puntos = 0;
$puntos += 10;
$puntos -= 2;
$puntos *= 3;
$puntos /= 2;
$etiqueta .= " pts";
$puntos++;
$puntos--;

// ciclo while con comparaciones y conectores lógicos
$i = 0;
while ($i < 3 && $total > 0) {
    echo $i, ": ", $precios[$i] * $cantidades[$i], "\n";
    $i++;
}
$ok = ($vip === true || $total >= 100) and !($resto != 1);
$distinto = $resto !== 2 or $promedio <= 5;
$igual = $resto == 1;
echo $etiqueta, " total=", $total, "\n";
?>
