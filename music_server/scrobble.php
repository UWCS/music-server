#!/usr/bin/php
<?php
/*

   Name: 	scrobble.php
   Author: 	Alex Wilson

   Syntax: ./scrobble.php "<path_to_file>"

   A script to scrobble (add to last.fm "Played" list) the music played on
   the UWCS's Music Server during LANs.

 */

define(API_KEY, 'b4d56d1faf13d849e0fb12e87cb8c443');
define(SEKRIT, 'c3c7c633a384ae00025b836d0f369b9d');
define(NAME, 'uwcslan');
define(PWD, 'ponies2010');	//OMG PONIES!

//Generate authorisation key for auth.getMobileSession
$auth = md5(utf8_encode(NAME.md5(utf8_encode(PWD))));

//Generate method signature for auth.getMobileSession.
$sig = md5(utf8_encode(
			"api_key".API_KEY.
			"authToken".$auth.
			"methodauth.getMobileSession".
			"username".NAME.
			SEKRIT)
	  );

//Generate URL where we'll get the session identifier.
$url=	'http://ws.audioscrobbler.com/2.0/'.
'?format=json'.
'&method=auth.getMobileSession'.
'&api_key='.API_KEY.
'&api_sig='.$sig.
'&username='.NAME.
'&authToken='.$auth; 

//Follow URL. Recieve Token.
$ch = curl_init(); 
curl_setopt($ch, CURLOPT_URL,$url); 
curl_setopt($ch, CURLOPT_RETURNTRANSFER,true);
$return = curl_exec($ch);

exec("mplayer -nosound \"$argv[1]\" 2>/dev/null|grep -Ei 'Name|Artist|Author|Title|Album|Year|Comment|Track|Genre|AUDIO'", $label); 		//Bash expression for getting track data from mplayer's output

$stats = Array(); 		//New array for track data

foreach($label as $data)
{
	if(preg_match("/ ?(.*): (.*)/",$data,$res))
	{
		$stats[strtolower($res[1])] = $res[2];	//Put track data into associate array.	
	}
}

if ((isset($stats['title']) || isset($stats['name'])) && (isset($stats['artist']) || isset($stats['author']))) {	//Only scrobble if Track and Artist information is present

	//Array with parameters drawn from cmd-line arguments.
	$paras = array (
			"track"  => $stats['title'],
			"artist" => $stats['artist'],
			"method" => "track.scrobble",
			"timestamp" => time(),
			"sk" => json_decode($return)->{'session'}->{'key'},
			"api_key" => API_KEY
		       );


if (isset($stats['album'])) {$paras['album'] = $stats['album'];} //Optional Album extra.

//SCROBBLE TIME
scrobble($paras);
}

function scrobble($data) {

	ksort($data);	//Sort the scrobbling array by key. Last.fm is fussy like that.
	$sig = "";

	foreach($data as $k => $v) {
		$sig .= $k.$v;
	}

	$sig .= SEKRIT;
	$sig = md5($sig);
	$data["api_sig"] = $sig;	//Method signature generated, add to $data.

	$dataString = "";

	foreach ($data as $l => $j) {
		$dataString .= $l."=".$j."&";
	}

	$dataString .= "format=json";	//Put all of $data into an appropriate string.

	$scr = curl_init();
	curl_setopt($scr, CURLOPT_URL,"http://ws.audioscrobbler.com/2.0");       
	curl_setopt($scr, CURLOPT_HEADER, 0);
	curl_setopt($scr, CURLOPT_RETURNTRANSFER,true);
	curl_setopt($scr, CURLOPT_POSTFIELDS, $dataString);
	curl_setopt($scr, CURLOPT_POST, count($data));

	curl_exec($scr);	//SCROBBLE.
	curl_close($scr);	//Job's a good'un.


}
?>
