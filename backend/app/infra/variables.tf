# medassistant/backend/app/infra/variables.tf

variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
}

variable "db_instance_class" {
  description = "Instance class for the RDS Postgres database"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage (in GB) for the RDS Postgres database"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Name of the Postgres database"
  type        = string
  default     = "medassistant"
}

variable "db_username" {
  description = "Master username for the Postgres database"
  type        = string
}

variable "db_password" {
  description = "Master password for the Postgres database"
  type        = string
  sensitive   = true
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository for the backend Docker image"
  type        = string
}
