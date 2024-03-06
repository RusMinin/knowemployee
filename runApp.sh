#!/bin/bash
python -m venv ~/venv/knowemployee
source ~/venv/knowemployee/bin/activate
pip install deepgram-sdk Flask Flask-SQLAlchemy aiohttp Werkzeug PyJWT cryptography openai python-dotenv qrcode Pillow flask_migrate requests scrypt
sudo apt install sqlite3 sqlitebrowser