These are prototypes and tests for a tool which analyzes git repositories.

To create a virtual environment with all the dependencies, from this directory,
type:

    source prepare-environment.sh virtenv

a new virtual environment will be created inside the directory `virtenv/`.
This may take a while, as it fetches and it compiles some big packages.

    which python

If it doesn't use python 3 from the virtual environment, then make sure it does:

    source virtenv/bin/activate

## Prototype 1

Configure:

    cp prototype1.ini-example prototype1.ini

Do not forget to set the paths

To run prototype 1:

    python app-prototype1/reports.py -o

which will show an overview. This will take a while, as it builds up a cache.
Subsequent runs should be faster.
