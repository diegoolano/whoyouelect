<?php
$response = $_POST['json'];
$filename = "./large-jsons-to-merge/".$_POST['fname'].".json";

if (file_exists($filename)) {
	copy($filename,$filename.".bak");    
} 

$fp = fopen($filename, 'w');
//fwrite($fp, json_encode($response));
fwrite($fp, $response);
fclose($fp);

print("Saved file "+$filename+" successfully");
?>
