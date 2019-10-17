import json

def lambda_handler(event, context):
  print(json.dumps(event))

  expect_code = event.get('params').get('expect_code', '200')
  if expect_code == '400':
    raise Exception("Requested response code is 400")
  elif expect_code == '200':
    return {
      "statusCode": 200,
      "body": json.dumps({
        "message": "hello world"
      })
    }
  else:
    raise Exception("Unsupported code was specified")
