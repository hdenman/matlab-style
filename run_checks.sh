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

echo

for file in private_orig/*.m ; do
    echo $file
    python style_check.py $file
done

echo

for file in private_fixed/*.m ; do
    echo $file
    python style_check.py $file
done
