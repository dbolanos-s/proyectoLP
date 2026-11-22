<?php
// Uso incorrecto de un resource (error semantico en R3)
$archivo = fopen("php://memory", "w+");
$suma = $archivo + 1;
$texto = "dato" . $archivo;
fclose($archivo);
?>
