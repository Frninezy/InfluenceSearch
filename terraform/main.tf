terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_instance" "influenceSearch-Dev-1" {
  ami                    = var.ami
  instance_type          = var.t3
  key_name               = var.ssh
  vpc_security_group_ids = ["${var.security-group}"]
}

resource "aws_instance" "influenceSearch-Dev-2" {
  ami                    = var.ami
  instance_type          = var.t3
  key_name               = var.ssh
  vpc_security_group_ids = ["${var.security-group}"]
}

resource "aws_lb" "app_lb" {
  name               = "influence-search-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = ["sg-0d3c34a09bf7896b8"]

  subnets = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "target-group" {
  name = "InfluenceSearch-targetGroup"
  port = 80
  protocol = "HTTP"
  vpc_id = data.aws_vpc.default.id
}

resource "aws_lb_target_group_attachment" "instance-1" {
  target_group_arn = aws_lb_target_group.target-group.arn
  target_id = aws_instance.influenceSearch-Dev-1.arn
  port = 80
}

resource "aws_lb_target_group_attachment" "instance-2" {
  target_group_arn = aws_lb_target_group.target-group.arn
  target_id = aws_instance.influenceSearch-Dev-2.arn
  port = 80
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target-group.arn
  }
}