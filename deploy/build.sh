#!/bin/bash
set -x

sudo dnf update
sudo dnf install -y docker
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo groupadd docker
sudo usermod -aG docker ec2-user
sudo systemctl enable docker
sudo systemctl start docker
sudo chmod 777 /var/run/docker.sock
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash


echo ' '
echo 'Working directory: '
pwd
echo ' '


echo 'Spinning up all containers...'
echo ' '
sudo docker-compose build
sudo docker-compose up -d

echo ' '
echo 'Success.'
echo ' '

echo 'Containers Running: '
docker ps