output "ubuntu_ami_id" {
  value = data.aws_ssm_parameter.ubuntu_ami.value
  sensitive = true
}

output "load_balancer_dns" {
  value = aws_lb.app_lb.dns_name
}

output "instance_1_public_ip" {
  value = aws_instance.influenceSearch_dev_1.public_ip
}

output "instance_2_public_ip" {
  value = aws_instance.influenceSearch_dev_2.public_ip
}
