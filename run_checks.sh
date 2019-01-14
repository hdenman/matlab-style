for file in passing-examples/* ; do
    echo $file
    python style_check.py $file
done

echo

for file in failing-examples/* ; do
    echo $file
    python style_check.py $file
done
