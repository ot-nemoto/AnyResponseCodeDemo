import json

def lambda_handler(event, context):
  print(json.dumps(event))

  expect_code = event.get('params').get('expect_code', '200')
  if expect_code == '200':
    return {
      "statusCode": 200,
      "body": {
        "message": "hello world"
      }
    }
  elif expect_code == '400':
    raise Exception("Bad Request")
  elif expect_code == '401':
    return {
      "stackTrace": [],
      "errorType": "Exception",
      "errorMessage": "Unauthorixed"
    }
  else:
    raise Exception("Internal Server Error")
