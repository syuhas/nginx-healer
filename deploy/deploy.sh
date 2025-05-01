#!/bin/bash

set -x

# if [ "$1" == "--dns" ]; then
#   echo "Running with DNS configuration"
#   # Add your DNS-specific commands here
# elif [ "$1" == "--non-dns" ]; then
#   echo "Running with non-DNS configuration"
#   # Add your non-DNS-specific commands here
# fi

# get IP addresses from terraform outputs
AIP="${ANSIBLE_IP}"
PIP="${PROMETHEUS_IP}"
NIP="${NGINX_IP}"

if [ -z "$AIP" ] || [ -z "$PIP" ] || [ -z "$NIP" ]; then
  echo "Error: One or more IP addresses are not set. Please check your Terraform outputs."
  exit 1
fi

cd ..
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

python3 retrieve_key.py

if [ $? -ne 0 ]; then
  echo "Error: Failed to retrieve the key."
  exit 1
fi
python3 generate_configs.py gall $NIP $AIP

if [ $? -ne 0 ]; then
  echo "Error: Failed to generate configs."
  exit 1
fi

cd ..
cd deploy


ssh -o StrictHostKeyChecking=no "$USER@$AIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../ansible "$USER@$AIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$AIP:/home/$USER/app"
ssh -o StrictHostKeyChecking=no "$USER@$NIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../nginx "$USER@$NIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$NIP:/home/$USER/app"
ssh -o StrictHostKeyChecking=no "$USER@$PIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../prometheus "$USER@$PIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$PIP:/home/$USER/app"

# build ansible server
ssh -o StrictHostKeyChecking=no "$USER@$AIP" << EOF
    cd /home/$USER/app
    chmod +x build.sh
    ./build.sh
EOF

# build nginx server
ssh -o StrictHostKeyChecking=no "$USER@$NIP" << EOF
    cd /home/$USER/app
    chmod +x build.sh
    ./build.sh
EOF

# build prometheus server
ssh -o StrictHostKeyChecking=no "$USER@$PIP" << EOF
    cd /home/$USER/app
    chmod +x build.sh
    ./build.sh
    sudo dnf install -y nginx
    sudo cp nginx/default.conf /etc/nginx/conf.d/default.conf
    sudo cp nginx/index.html /usr/share/nginx/html/index.html
    sudo systemctl enable nginx
    sudo systemctl start nginx
    sudo systemctl status nginx
EOF

echo "Yay!!!!"

