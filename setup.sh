#!/bin/bash
# Update package lists and install dependencies
apt-get update
apt-get install -y libxrender1 

# Install python dependencies
pip install -r requirements.txt
