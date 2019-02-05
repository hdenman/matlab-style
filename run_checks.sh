for file in passing-examples/*.m ; do
    echo $file
    python style_check.py $file
done

echo

for file in failing-examples/*.m ; do
    echo $file
    python style_check.py $file
    echo
done


for file in private/*.m ; do
    echo $file
    python style_check.py $file
done
