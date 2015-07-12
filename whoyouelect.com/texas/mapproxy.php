<?php
  $did = $_GET["did"];
  $chamber = $_GET["chamber"];
  //http://openstates.org/get_district/ocd-division/country:us/state:tx/sldu:5/
  $url = "http://openstates.org/get_district/ocd-division/country:us/state:tx/sld".$chamber.":".$did."/";
  $json = file_get_contents($url); // this WILL do an http request for you
  $data = json_decode($json);
  //echo $data->{'token'};
  //print_r($data);
  //$ret = {"region":$data->{'region'}, "bbox":$data->bbox};
  $ret = json_encode(array('region' => $data->{'region'},'bbox' => $data->bbox));
  print $ret
?>
