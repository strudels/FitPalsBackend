#!/bin/bash

#install python dev libraries
sudo apt-get install -y python-dev

#install libffi dev libraries (necessary for python pyapns library for apple push notifications)
sudo apt-get install -y libffi-dev

#install openssl dev libraries (needed for apple push notifications)
sudo apt-get install -y libssl-dev

#install mysql dev libraries
sudo apt-get install -y libmysqlclient-dev

#install postgres dev libraries
sudo apt-get install -y postgresql-server-dev-all

#install postgresql server
sudo apt-get install -y postgresql postgresql-contrib

#install postgresql server postgis support
sudo apt-get install -y postgis postgresql-9.3-postgis-2.1

#install pip
sudo apt-get install -y python-pip

#install virtualenv
sudo pip install virtualenv

#setup python virtual environment for it's necessary libraries
virtualenv venv
. venv/bin/activate

#install necessary python libraries
cat requirements.txt | while read r; do pip install $r; done

echo done
