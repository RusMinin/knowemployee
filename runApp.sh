#!/bin/bash
sudo apt update -y # Update server to latest stable version

git clone git@github.com:KnowEmploee/knowemployee.git # Clone KnowEmployee repository as local branch

python -m venv ~/env/knowemployee # Create python virtual environment
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
cd msfonts/
cabextract *.exe
rm -rf *.exe

