Check if python 3 from the virtual environment is used:

    which python

If it doesn't use python 3 from the virtual environment, then make sure it does:

    source ../virtenv/bin/activate

## Prototype 1

Configure:

    cp prototype1.ini-example prototype1.ini

Do not forget to set the paths

To run prototype 1:

    python app-prototype1/reports.py -o

which will show an overview. This will take a while, as it builds up a cache.
Subsequent runs should be faster.
