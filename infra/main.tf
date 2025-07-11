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
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_managed_policy" {
  role = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_lambda_function" "main_lambda" {
  function_name = "${var.ecr_repo_name}-lambda"

  package_type = "Image"
  image_uri = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repo_name}:latest"

  role = aws_iam_role.lambda_exec_role.arn
  timeout = 30
  memory_size = 512

  environment {
    variables = {
        BOT_TOKEN = var.discord_bot_token
        CACHE_TOKEN = var.cache_token
        CACHE_ENDPOINT = var.cache_endpoint
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_logs_policy]
}

resource "aws_apigatewayv2_api" "http_api" {
  name = "lambda-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri = aws_lambda_function.main_lambda.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /"
  target = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.http_api.id
  name = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}