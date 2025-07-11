output "lambda_function_name" {
  value = aws_lambda_function.main_lambda.function_name
}

output "lambda_image_uri" {
  value = aws_lambda_function.main_lambda.image_uri
}

output "ecr_repo_url" {
  value = aws_ecr_repository.ecr_repo.repository_url
}