<?php
// Errores semánticos a propósito: R1 (variable sin definir) y R2 (constante redefinida)
const MAX = 10;
const MAX = 20;
define('MIN', 1);
define('MIN', 5);

$a = 3;
echo $b;
$c = $a + $d;

function usar(int $p): int {
    return $p + $externa;
}

$e = $noexiste(2);
?>
