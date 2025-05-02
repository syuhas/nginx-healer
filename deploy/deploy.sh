#!/bin/bash

set -x

# I want to pass in a parameter, redeploy and deploy
if [ "$1" == "redeploy" ]; then
  echo "Redeploying..."
  # Add your redeploy logic here
elif [ "$1" == "deploy" ]; then
  echo "Deploying..."
else
  echo "Invalid argument. Use 'redeploy' or 'deploy'."
  exit 1
fi

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

if [ "$1" == "redeploy" ]; then
  sed -i 's|sudo docker-compose build|sudo docker-compose down\nsudo docker-compose build|' build.sh
fi

###### Ansible server ######
ssh -o StrictHostKeyChecking=no "$USER@$AIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../ansible "$USER@$AIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$AIP:/home/$USER/app"
# build ansible server
ssh -o StrictHostKeyChecking=no "$USER@$AIP" << EOF
    cd /home/$USER/app
    chmod +x build.sh
    ./build.sh
EOF


###### Nginx server ######
ssh -o StrictHostKeyChecking=no "$USER@$NIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../nginx "$USER@$NIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$NIP:/home/$USER/app"
# build nginx server
ssh -o StrictHostKeyChecking=no "$USER@$NIP" << EOF
    cd /home/$USER/app
    chmod +x build.sh
    ./build.sh
EOF


###### Prometheus server ######
ssh -o StrictHostKeyChecking=no "$USER@$PIP" << EOF
    rm -Rf /home/$USER/app
EOF
scp -o StrictHostKeyChecking=no -r ../prometheus "$USER@$PIP:/home/$USER/app"
scp -o StrictHostKeyChecking=no build.sh "$USER@$PIP:/home/$USER/app"
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

