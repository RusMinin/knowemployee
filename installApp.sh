#!/bin/bash
sudo apt update -y # Update server to latest stable version
sudo apt install -y python*-venv # We need python

git clone git@github.com:KnowEmploee/knowemployee.git # Clone KnowEmployee repository as local branch

python3 -m venv ~/env/knowemployee # Create python virtual environment
sleep 3 # it may take time, so let's give it 3 seconds :)
source ~/env/knowemployee/bin/activate # Connect to python virtual environment

pip  install deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt gunicorn # Install needed dependencies 

sudo apt install sqlite3 sqlitebrowser -y # We need SQLite
sudo apt install nginx -y # We need NGINX 
sudo apt install cabextract -y # This is needed for msfonts extraction
sudo apt autoremove -y # Remove all tails (if there are any)

# Download and extract msfonts
wget https://www.freedesktop.org/software/fontconfig/webfonts/webfonts.tar.gz
tar -xzf webfonts.tar.gz
rm -rf webfonts.tar.gz
cd msfonts/
cabextract *.exe
rm -rf *.exe *.EXE
cd ..

# Add service file to system directory
sudo cp knowemployee.service /etc/systemd/system/

# Add configuration file to NGINX
sudo cp knowemployee.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/knowemployee.conf /etc/nginx/sites-enabled

