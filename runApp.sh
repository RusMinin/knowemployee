#!/bin/bash
cd ~
python -m venv ~/env/KnowEmployee
sleep 3
source ~/env/KnowEmployee/bin/activate
pip  install -y deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt
sudo apt install -y sqlite3 sqlitebrowser
sudo apt autoremove -y