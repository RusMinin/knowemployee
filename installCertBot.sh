#!/bin/bash
sudo apt remove certbot -y ## Just to make sure there is no old version of Certbot

sudo apt install snapd -y ## Install snapd 

sudo snap install --classic certbot ## Install latest classic flavored certbot

sudo ln -s /snap/bin/certbot /usr/bin/certbot 

sudo certbot --nginx ## Install certificate/s