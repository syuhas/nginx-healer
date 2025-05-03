variable "project_name" {
  default = "self-healer"
}
variable "aws_region" {
  default = "us-east-1"
}
variable "aws_account_id" {
  default = "123456789012"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "key_name" {
  description = "Key pair name for SSH access to the EC2 instance"
  default     = "ec2"
}
variable "ami" {
  description = "AMI ID for the EC2 instance"
  default     = "ami-00a929b66ed6e0de6"
}
variable "security_group" {
  description = "Security group for the EC2 instance"
  default = "sg-00d9ca388301c93a9"
}

variable "subnet_ids" {
  description = "List of subnets to use for EC2 instances"
  type = list(string)
  default = ["subnet-0823df6c43b1a0ea4", "subnet-057dcb202796ed034"]
}
