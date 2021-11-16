<html>
 <head>
  <title>Matlab Style Checker</title>
 </head>
 <body>
<h3>Paste Matlab here:</h3>
<form action="matlab_check.php" method="post">
<textarea name="content" rows="40" cols="80"><?php echo $_POST["content"]; ?></textarea>

<input type="submit">

<?php
$file = tempnam("/tmp", "matlab-style");
$content = $_POST["content"];
file_put_contents($file, $content);

$response = "";
exec("python3.7 style_check.py $file", $response);
?>

<h3>Style checker:</h3>
<textarea name="response" rows="20" cols="80"><?php echo join("\n", $response) ?></textarea>
</form>
 </body>
</html>
