#!/bin/bash

sudo dnf update
sudo dnf install -y docker
sudo groupadd docker
sudo usermod -aG docker ec2-user
sudo systemctl enable docker
sudo systemctl start docker
sudo chmod 777 /var/run/docker.sock
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash

cd app
sudo docker-compose up -d

docker ps