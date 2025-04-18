output "prometheus_ip" {
  value = aws_instance.prometheus.public_ip
}

output "nginx_ip" {
  value = aws_instance.nginx.public_ip
}

output "ansible_ip" {
  value = aws_instance.ansible.public_ip
}