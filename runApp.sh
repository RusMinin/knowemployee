#!/bin/bash
sudo apt update -y # Update server to latest stable version

git clone git@github.com:KnowEmploee/KnowEmploee.git # Clone KnowEmployee repository as local branch

python -m venv ~/env/KnowEmployee # Create python virtual environment
sleep 3 # it may take time, so let's give it 3 seconds :)
source ~/env/KnowEmployee/bin/activate # Connect to python virtual environment

pip  install deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt # Install needed dependencies 

sudo apt install sqlite3 sqlitebrowser -y # We need SQLite
sudo apt autoremove -y # Remove all tails (if there are any)