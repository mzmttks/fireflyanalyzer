* How to install

sudo apt-get install python-setuptools
sudo apt-get install libopencv-dev
sudo apt-get install python-dev
sudo apt-get install libblas-dev libatlas-dev liblapack-dev libfftw3-dev gfortran
sudo apt-get install libfreenect-dev libpng12-dev libagg-dev
sudo apt-get install subversion

sudo easy_install install pip
sudo pip install -U --proxy=http://winnie:3128 cython
sudo pip install -U --proxy=http://winnie:3128 numpy
sudo pip install -U --proxy=http://winnie:3128 scipy
sudo pip install -U --proxy=http://winnie:3128 scikits-image
sudo pip install -U --proxy=http://winnie:3128 matplotlib

sudo apt-get install python-opencv

svn co http://winnie.kuis.kyoto-u.ac.jp/musicrobotsrepos/trunk/sandbox/mizumoto/FrogFireflyAnalyzer3


* How to run
edit run.py 
python run.py
