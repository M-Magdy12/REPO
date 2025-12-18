terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = "us-east-1"
}


resource "aws_security_group" "mediscan_sg" {
  name        = "mediscan-security-group"
  description = "Security group for MediScan application"


  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

 
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

 
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Flask API"
  }

 
  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Streamlit UI"
  }

 
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "mediscan-sg"
  }
}


resource "aws_instance" "mediscan_server" {

  instance_type = "t3.micro"


  ami = "ami-0c7217cdde317cfec"


  key_name = "mediscan-key"


  vpc_security_group_ids = [aws_security_group.mediscan_sg.id]

 
  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }


  user_data = <<-EOF
              #!/bin/bash
              # Update system
              yum update -y
              
              # Install Docker
              yum install docker -y
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              
              # Install Docker Compose
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              # Install Git
              yum install git -y
              
              echo "Docker installation completed!"
              EOF

  
  tags = {
    Name        = "mediscan-server"
    Environment = "production"
    Application = "MediScan"
  }
}


output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.mediscan_server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.mediscan_server.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.mediscan_server.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i mediscan-key.pem ec2-user@${aws_instance.mediscan_server.public_ip}"
}

output "streamlit_url" {
  description = "URL to access Streamlit UI"
  value       = "http://${aws_instance.mediscan_server.public_ip}:8501"
}

output "flask_api_url" {
  description = "URL to access Flask API"
  value       = "http://${aws_instance.mediscan_server.public_ip}:5000"
}
