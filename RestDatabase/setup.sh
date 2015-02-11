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

#install pip
sudo apt-get install -y python-pip

#install local mongodb server
sudo apt-key adv -y --keyserver hkp://keyserer.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update -y
sudo apt-get install -y mongodb-org

#install virtualenv
sudo pip install virtualenv

#setup python virtual environment for it's necessary libraries
virtualenv venv
. venv/bin/activate

#install necessary python libraries
cat requirements.txt | while read r; do pip install $r; done

echo done
