variable "region" {
	description = "AWS region"
  	type        = string
  	default     = "eu-central-1"
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