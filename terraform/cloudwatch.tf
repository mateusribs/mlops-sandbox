# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "anomaly_classifier" {
  dashboard_name = local.dashboard_name

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["MLOpsSandbox", "AnomalyPrediction", { stat = "Sum" }],
            [".", "InferenceTime", { stat = "Average" }],
            [".", "ModelLoadTime", { stat = "Average" }],
            [".", "PredictionErrors", { stat = "Sum" }],
            ["AWS/Lambda", "Duration", { stat = "Average", dimensions = { FunctionName = aws_lambda_function.classify_anomaly.function_name } }],
            [".", "Errors", { stat = "Sum", dimensions = { FunctionName = aws_lambda_function.classify_anomaly.function_name } }],
            [".", "Throttles", { stat = "Sum", dimensions = { FunctionName = aws_lambda_function.classify_anomaly.function_name } }],
            [".", "ConcurrentExecutions", { stat = "Maximum", dimensions = { FunctionName = aws_lambda_function.classify_anomaly.function_name } }],
          ]
          period = 60
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Anomaly Classifier Metrics"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["MLOpsSandbox", "AnomalyPrediction", { stat = "SampleCount" }]
          ]
          period = 60
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Predictions Count (Last Hour)"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["MLOpsSandbox", "InferenceTime", { stat = "Average" }],
            [".", "ModelLoadTime", { stat = "Average" }]
          ]
          period = 60
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Latency Metrics (ms)"
        }
      }
    ]
  })
}
