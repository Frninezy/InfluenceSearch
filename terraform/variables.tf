variable "region" {
	description = "AWS region"
  	type        = string
  	default     = "eu-central-1"
}

variable "ami" {
	description = "AMI"
  	type        = string
  	default     = "ami-0fd9576cca965bd19"
}

variable "t3" {
	description = "t3 micro"
  	type        = string
  	default     = "t3.micro"
}

variable "ssh" {
	description = "ssh key"
  	type        = string
  	default     = "frninezy"
}

variable "security-group" {
	description = "security group"
  	type        = string
  	default     = "sg-05cb1b5e9e6715c98"
}