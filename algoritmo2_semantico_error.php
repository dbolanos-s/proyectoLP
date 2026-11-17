<?php
// Errores semánticos a propósito: R3 (operaciones permitidas) y R4 (retorno de funciones)
$texto = "hola";
$lista = [1, 2, 3];
$c = "hola" * 2;
$x = 5 > "a";
$suma = $texto + 1;
$mensaje = "Lista: " . $lista;

function f(): int {
    return "texto";
}

function precio(): float {
    return [1, 2];
}

function activo(): bool {
    return 1;
}
?>
