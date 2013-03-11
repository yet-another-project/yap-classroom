VDIRNAME="$1"

mkdir "$VDIRNAME"
virtualenv3 --no-site-packages -p python3 "$VDIRNAME"
source "$VDIRNAME/bin/activate"

pip install git+git://github.com/numpy/numpy.git@master
pip install git+git://github.com/matplotlib/matplotlib.git@master
pip install diff-match-patch
pip install git+git://github.com/sunlightlabs/jellyfish.git@master
pip install networkx
pip install git+git://github.com/scipy/scipy.git@v0.12.0b1
