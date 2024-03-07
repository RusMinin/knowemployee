#!/bin/bash
cd ~
python -m venv ~/venv/knowemployee
timeout -5s
source ~/env/knowemployee/bin/activate
pip -y install deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt
sudo apt -y install sqlite3 sqlitebrowser
sudo apt -y autoremove