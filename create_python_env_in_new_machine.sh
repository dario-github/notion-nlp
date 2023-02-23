sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt install python3.8 -y
sudo apt install python3-pip -y
sudo apt-get install python3.8-distutils -y
sudo curl -sS https://bootstrap.pypa.io/get-pip.py | python3.8

python3.8 -m pip install --upgrade pip
python3.8 -m pip install --upgrade wheel
python3.8 -m pip install --upgrade setuptools

python3.8 -m pip install --upgrade requests
python3.8 -m pip install --ignore-installed poetry
python3.8 -m poetry env use /usr/bin/python3.8
python3.8 -m poetry install
