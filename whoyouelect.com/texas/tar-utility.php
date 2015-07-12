<?php
ini_set('display_errors',1);
//http://stackoverflow.com/questions/561066/fatal-error-allowed-memory-size-of-134217728-bytes-exhausted-codeigniter-xml
ini_set('memory_limit', '-1');
ini_set('max_execution_time', 0);

$action = $_GET['action'];     //untar
$person = $_GET['person'];     //entity
$net    = $_GET['net'] ;        //small or large .. //small needs smallnet, urls, and textsnippets  .....    large needs largenet and largesnippets
//["dan_huberty-smallnet-05-28_07-07-31.json", "dan_huberty-small-urls-05-28_07-07-31.json", "dan_huberty-textsnippets-05-28_07-07-31.json", 
// "dan_huberty-largenet-05-28_07-10-14.json", "dan_huberty-textsnippets-large-05-28_07-10-32.json"]

//http://www.binarytides.com/extract-tar-gz-archives-php/


//first load person from config.js
$str = file_get_contents('js/config.json');
$json = json_decode($str, true);

if( isset($json[$person]) ){
	//then do request action on netsize
	if( $action == "retrieve" ){
		$personunix = str_replace(" ","_",strtolower($person));
		if( $net == "small"){
			try {
				//untar small tar file,
				// decompress from gz
				$smallnetgz = "data/$personunix-small.tar.gz";
				$smallnettar = "data/$personunix-small.tar";
				$p = new PharData($smallnetgz);
				$p->decompress(); // creates smallnet.tar
				 
				// unarchive from the tar
				$phar = new PharData($smallnettar);
				$phar->extractTo('.',null,true); 
				
				print '{"success":"true"}';
			}
			catch (Exception $e) 
			{
			    //echo "Exception : " . $e;
				    //print '{"success":"false", "message":"'. $e .'" }';
				    print '{"success":"false", "message":"retrieve small fail" }';
			}
		}
		else{
			if($net == "large"){
				try {
					$largenetgz = "data/$personunix-large.tar.gz";
					$largenettar = "data/$personunix-large.tar";
					$p = new PharData($largenetgz);
					$p->decompress(); // creates largenet.tar
					 
					// unarchive from the tar
					$phar = new PharData($largenettar);
					$phar->extractTo('.',null,true); 
					
					print '{"success":"true"}';
				}
				catch (Exception $e) 
				{
				    //echo "Exception : " . $e;
				    //print '{"success":"false", "message":"'. $e .'" }';
				    print '{"success":"false", "message":"retrieve large fail" }';
				}
			}
			else{ 
				    print '{"success":"false", "message":"no net size specified"}';
			}
		}
	}

	else{
		if( $action == "compress" ){
			//here add correct json files to tarfile and then remove from system
			$personunix = str_replace(" ","_",strtolower($person));
			if( $net == "small"){
				$smallnetgz = "data/$personunix-small.tar.gz";
				$smallnettar = "data/$personunix-small.tar";
				try
				{
					$a = new PharData($smallnettar);
					$a->addFile("data/".$json[$person][0]);  //smallnet
					$a->addFile("data/".$json[$person][1]);  //urls
					$a->addFile("data/".$json[$person][2]);  //textsnips
					//$a->compress(Phar::GZ);
					file_put_contents($smallnetgz , gzencode(file_get_contents($smallnettar)));

					//now remove json files and tar file if it exists (not urls one since other is dependent on it )
					
					unlink("data/".$json[$person][0]);
					unlink("data/".$json[$person][2]);
					unlink($smallnettar);
					
					print '{"success":"true"}';
				} 
				catch (Exception $e) 
				{
				    //echo "Exception : " . $e;
				    //print '{"success":"false", "message":"'. $e .'" }';
				    print '{"success":"false", "message":"small compress fail" }';
				}
			}
			else{
				if( $net == "large" ){
					$largenetgz = "data/$personunix-large.tar.gz";
					$largenettar = "data/$personunix-large.tar";
					try
					{
						$a = new PharData($largenettar);
						$a->addFile("data/".$json[$person][3]);   //largenet
						$a->addFile("data/".$json[$person][1]);   //urls
						$a->addFile("data/".$json[$person][4]);   //textsnips
						//$a->compress(Phar::GZ);
						//file_put_contents($largenetgz , $a);
						file_put_contents($largenetgz , gzencode(file_get_contents($largenettar)));

						//now remove json files and tar file if it exists
						unlink("data/".$json[$person][3]);
						unlink("data/".$json[$person][4]);
						unlink($largenettar);
						
						print '{"success":"true"}';
					} 
					catch (Exception $e) 
					{
					    echo "Exception : " . $e;
				    	    //print '{"success":"false", "message":"'. $e .'" }';
				    	    print '{"success":"false", "message":"large compress fail" }';
					}
				}
				else{ 
					    print '{"success":"false", "message":"no net size specified"}';
				}
			}
		}
		else{ 
			print '{"success":"false","message":"action not specified"}';
		}
	}
}
else{
	print '{"success":"false","message":"person index does not exist"}';
}
?>
