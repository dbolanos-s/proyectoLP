<?php
// Errores sintácticos a propósito en expresiones y en mis estructuras
$a = 5 +;
$ok = 1;
$b = 3 * * 2;
$ok = 2;
$c = 1 < 2 < 3;
$ok = 3;
5 += $a;
$ok = 4;
[$x, 10] = [1, 2];
$ok = 5;
$f = fn($n) => ;
$ok = 6;
while ($a > 0 {
    $a--;
}
$fin = 7;
