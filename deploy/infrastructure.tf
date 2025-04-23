provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "terraform-lock-bucket"
    key            = "healer/terraform.tfstate"
    region         = "us-east-1"
    use_lockfile   = true
    workspace_key_prefix = "healer"
  }
}

resource "aws_instance" "prometheus" {
  ami = var.ami
  instance_type = var.instance_type
  subnet_id = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = true
  tags = {
    Name = "${var.project_name}-prometheus"
  }
  key_name = var.key_name

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_instance" "nginx" {
  ami = var.ami
  instance_type = var.instance_type
  subnet_id = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = true
  
  tags = {
    Name = "${var.project_name}-prometheus"
  }
  key_name = var.key_name

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_instance" "ansible" {
  ami = var.ami
  instance_type = var.instance_type
  subnet_id = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = true
  tags = {
    Name = "${var.project_name}-prometheus"
  }
  key_name = var.key_name

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "monitor" {
  zone_id = "Z02299283BLAIJGG9JHMK"
  name    = "monitor.digitalsteve.net"
  type    = "A"
  ttl     = 300
  records = [aws_instance.prometheus.public_ip]
  
}