<?php
// Los tipos de datos de PHP que trabaja el analizador (valido)
$entero = 4195;                       // integer
$decimal = 3.14159;                   // double (float)
$activo = true;                       // boolean
$vacio = null;                        // NULL
$texto = "cadena de texto";           // string
$lista = [1, 2, 3];                   // array indexado
$datos = ["nombre" => "Ana", "edad" => 21];   // array asociativo

class Punto {
    public int $x = 0;
    public function mover(int $dx): int {
        return $dx + 1;
    }
}
$p = new Punto();                     // object
$paso = $p->mover(2);

$archivo = fopen("php://memory", "w+");      // resource
fwrite($archivo, "hola");
$estado = feof($archivo);
fclose($archivo);

echo $entero + $decimal, " ", $texto, " ", $lista[0], " ", $datos["nombre"], " ", $paso, "\n";
?>
