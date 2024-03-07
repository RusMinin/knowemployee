#!/bin/bash
python -m venv ~/env/KnowEmployee
sleep 3
source ~/env/KnowEmployee/bin/activate
pip  install deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt
sudo apt install sqlite3 sqlitebrowser -y
sudo apt autoremove -y