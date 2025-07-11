provider "aws" {
    region = var.aws_region
}

resource "aws_ecr_repository" "ecr_repo" {
    name = var.ecr_repo_name
    
    force_delete = true
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_role" "lambda_exec_role" {
    name = "${var.ecr_repo_name}_lambda_role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [{
            Action = "sts:AssumeRole",
            Effect = "Allow",
            Principal = {
                Service = "lambda.amazonaws.com"
            }
        }]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy" {
  role = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service_role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "main_lambda" {
  function_name = "${var.ecr_repo_name}-lambda"

  package_type = "Image"
  image_uri = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repo_name}:latest"

  role = aws_iam_role.lambda_exec_role.arn
  timeout = 30
  memory_size = 512

  depends_on = [aws_iam_role_policy_attachment.lambda_logs_policy]
}