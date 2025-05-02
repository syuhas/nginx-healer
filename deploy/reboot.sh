#!/bin/bash
set -x


echo "Rebooting Nginx Instance..."
aws ec2 reboot-instances --instance-ids ${NGINX_INSTANCE_ID} --region ${AWS_REGION}

echo "Waiting for Nginx instance to reboot..."
aws ec2 wait instance-status-ok --instance-ids ${NGINX_INSTANCE_ID} --region ${AWS_REGION}

echo "Nginx instance is back online."

echo "Waiting for services to fully restart..."
aws ec2 wait instance-status-ok --instance-ids ${NGINX_INSTANCE_ID} --region ${AWS_REGION}

echo "Nginx instance is healthy."

echo "Waiting for SSH to be available..."
retries=0
until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "ec2-user@${NGINX_IP}" "exit" 2>/dev/null || [ $retries -eq 12 ]; do
  echo "Still waiting... ($((retries+1))/12)"
  sleep 10
  ((retries++))
done

if [ $retries -eq 12 ]; then
  echo "ERROR: SSH did not become available. Exiting."
  exit 1
fi

echo "SSH Ready."
echo "Restarting Containers..."
echo ""
ssh -o StrictHostKeyChecking=no "ec2-user@${NGINX_IP}" << EOF
    cd /home/ec2-user/app
    docker-compose down
    docker-compose build
    docker-compose up -d
    docker ps
    docker logs nginx
EOF

echo "Containers restarted."