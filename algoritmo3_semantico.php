<?php
$valores = [1, 2, 3];
function duplicar(int $x): int { return $x * 2; }
foreach ($valores as $valor) {
    $resultado = duplicar($valor);
}
?>
