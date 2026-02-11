<?php
require 'connexion.php';

try {
    // Récupération des données POST
    $temperature = floatval($_POST['temperature']);
    $courant = floatval($_POST['courant']);

    if ($temperature === null || $courant === null) {
        die("Erreur: données manquantes");
    }

    // Requête INSERT avec paramètres préparés
    $sql = "INSERT INTO ta_table (date, heure, temperature, courant) 
            VALUES (CURDATE(), CURTIME(), :temp, :courant)";

    $stmt = $pdo->prepare($sql);
    $stmt->bindParam(':temp', $temperature, PDO::PARAM_STR);
    $stmt->bindParam(':courant', $courant, PDO::PARAM_STR);


    $stmt->execute();
    echo "OK: $temperature°C, $courant A enregistré";
} catch (PDOException $e) {
    echo "Erreur: " . $e->getMessage();
}
?>