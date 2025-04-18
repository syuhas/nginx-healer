provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "terraform-lock-bucket/"
    key            = "terraform/state/healer/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock-table"
    
  }
}

resource "aws_instance" "prometheus" {
  ami = var.ami
  instance_type = var.instance_type
  subnet_id = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group]
  associate_public_ip_address = true
  tags = {
    Name = "${var.project}-prometheus"
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
    Name = "${var.project}-prometheus"
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
    Name = "${var.project}-prometheus"
  }
  key_name = var.key_name

  lifecycle {
    create_before_destroy = true
  }
}