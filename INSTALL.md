These are prototypes and tests for a tool which analyzes git repositories, email
activity and possibly other stats that needs to be tracked.

First, ensure that the `swig suitesparse atlas-lapack` packages (these are
specific to Arch Linux, please modify according to your distribution) are
installed, these are required by the `numpy` and `scipy` libraries.

To create a virtual environment with all the dependencies, from this directory,
type:

    source prepare-environment.sh virtenv

a new virtual environment will be created inside the directory `virtenv/`.
This may take a while, as it fetches and it compiles some big packages.

    which python

If it doesn't use python 3 from the virtual environment, then make sure it does:

    source virtenv/bin/activate
