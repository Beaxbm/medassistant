# medassistant/backend/app/infra/outputs.tf

# VPC and Subnets
output "vpc_id" {
  description = "ID of the main VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

# RDS Postgres
output "rds_endpoint" {
  description = "Endpoint address of the RDS Postgres instance"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
  description = "Port of the RDS Postgres instance"
  value       = aws_db_instance.postgres.port
}

# ECR Repository
output "ecr_repository_url" {
  description = "URL of the ECR repository for the backend image"
  value       = aws_ecr_repository.app.repository_url
}

# ECS Cluster & Task Execution Role
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution"
  value       = aws_iam_role.ecs_task_execution.arn
}

# Security Groups
output "ecs_security_group_id" {
  description = "Security Group ID for the ECS service"
  value       = aws_security_group.ecs_sg.id
}

output "rds_security_group_id" {
  description = "Security Group ID for the RDS instance"
  value       = aws_security_group.rds_sg.id
}
