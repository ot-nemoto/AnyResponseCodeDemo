# AnyResponseCodeDemo

## 概要

- API Gateway - Lambdaの構成で、デフォルトでは、Lambdaでエラーが発生した場合でも、API Gatewayではレスポンスコードは200として返却する
- これはAPI Gateway自体では問題は発生しておらず、Lambda側のエラーはLambda側で処理し、API Gatewayとしては、API Gatewayのレスポンスコードを返す
- 但し、ケース（要件）によっては、Lambdaで指定したレスポンスコードをAPI Gatewayのレスポンスコードとして返却したい場合がある
- その場合のデモ

## 構成

- クエリパラメータ *expect_code* で指定したレスポンスコードを指定します。
- 未指定の場合は、デフォルトでは **200** を返します。
- *expect_code*=**200**

```py
# json を return
return {
  "statusCode": 200,
  "body": {
    "message": "hello world"
  }
}
```

API Gateway ではHTTPレスポンスコードを200で、Lambda側のレスポンスをそのまま（パススルー）返却する。

```json
{
  "body": {
    "message": "hello world"
  },
  "statusCode": 200
}
```

- *expect_code*=**400**

```py
# Exceptionを発生
raise Exception("Bad Request")
```

Lambdaではreturnせずに、Exceptionを発生させる。通常、API Gateway側は、Lambdaのレスポンス（エラーメッセージのJSON）をHTTPレスポンスコードを 200 で返却する。
このデモでは、API Gateway のレスポンス統合で、**errorMessage** が `Bad Request` のレスポンスを正規表現でひっかけ、HTTPレスポンスコードを 400 で返却する。

```json
{
  "statusCode": 400,
  "body": {
    "message": "Bad Request"
  }
}
```

- 上記以外（e.g. *expect_code*=**50x**）

```py
# Exceptionを発生
raise Exception("Internal Server Error")
```
400 ケースと同様に、上記で触れていない *expect_code* が指定された場合には、Exceptionを発生させる。
API Gateway のレスポンス統合で、**errorMessage** が `Internal Server Error` のレスポンスを正規表現でひっかけ、HTTPレスポンスコードを 500 で返却する。

```json
{
  "statusCode": 500,
  "body": {
    "message": "Internal Server Error"
  }
}
```

---

- *expect_code*=**401**

このケースは、Exceptionから生成されるJSONと同様のパラメータを return した場合の**挙動検証**を備忘録として残す。

```py
# json を return
return {
  "stackTrace": [],
  "errorType": "Exception",
  "errorMessage": "Unauthorixed"
}
```

API Gateway では、400と同様に、レスポンス統合で、**errorMessage** が `Unauthorixed` を正規表現でひっかけ、HTTPレスポンスコードを 401 で返却することを想定したが、結果として、return されたものは、正規表現には引っかからず、正常なHTTPレスポンスコード 200 として返却する。（なのでレスポンス内容はパススルー）

```json
{
  "stackTrace": [],
  "errorMessage": "Unauthorixed",
  "errorType": "Exception"
}
```

*expect_code*が**400**と、**401**のケースで、LambdaからAPI Gateway へのレスポンスを比較してみると、

**400**の場合

*Endpoint response headers:*
```
{
  Date=Thu, 17 Oct 2019 23:47:36 GMT, Content-Type=application/json,
  Content-Length=153,
  Connection=keep-alive,
  x-amzn-RequestId=42eef5fc-569c-4dda-b2d1-d7740ed9e811,
  X-Amz-Function-Error=Unhandled,
  x-amzn-Remapped-Content-Length=0,
  X-Amz-Executed-Version=$LATEST,
  X-Amzn-Trace-Id=root=1-5da8fd98-31bcdfca8b188442316886fe;sampled=0
}
```
*Endpoint response body before transformations:*
```
{
  "stackTrace": [["/var/task/app.py", 15, "lambda_handler", "raise Exception(\"Bad Request\")"]],
  "errorType": "Exception",
  "errorMessage": "Bad Request"
}
```

**401**の場合

*Endpoint response headers:*
```
{
  Date=Thu, 17 Oct 2019 23:48:34 GMT, Content-Type=application/json,
  Content-Length=76,
  Connection=keep-alive,
  x-amzn-RequestId=c125f451-6e58-4eaf-910c-8bcb03f18f2e,
  x-amzn-Remapped-Content-Length=0,
  X-Amz-Executed-Version=$LATEST,
  X-Amzn-Trace-Id=root=1-5da8fdd2-1a32a21d1a1bcca9eaeda4ec;sampled=0
}
```
*Endpoint response body before transformations:*
```
{
  "stackTrace": [],
  "errorMessage": "Unauthorixed",
  "errorType": "Exception"
}
```

結果、`X-Amz-Function-Error` が含まれるかどうかの違いがあり、
API Gatewayでは、Lambdaでreturn処理されたものは正常系とし処理され、HTTPレスポンスコードは**200**で処理し、API GatewayでHTTPレスポンスコードを操作したい場合は、例外で返す必要ある。

## デプロイ

ソースコードをアップロードするS3バケットを作成

```sh
S3BUCKET=any-response-code-demo-bucket-`date +%Y%m%d%H%M%S`
echo ${S3BUCKET}
  # any-response-code-demo-bucket-01234567890123

aws s3 mb s3://${S3BUCKET}
  # make_bucket: any-response-code-demo-bucket-01234567890123
```

パッケージ

```sh
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket ${S3BUCKET}
```

デプロイ

```sh
sam deploy \
    --template-file packaged.yaml \
    --stack-name any-response-code-demo \
    --capabilities CAPABILITY_IAM
```

## 使い方

URLを取得

```sh
INVOKE_URL=$(aws cloudformation describe-stacks \
    --stack-name any-response-code-demo \
    --query 'Stacks[].Outputs[?OutputKey==`InvokeUrl`].OutputValue' \
    --output text)
echo ${INVOKE_URL}
  #
```

正常なレスポンスコードを返すリクエスト

```sh
curl -s ${INVOKE_URL} | jq
  # {
  #   "body": {
  #     "message": "hello world"
  #   },
  #   "statusCode": 200
  # }
curl -s ${INVOKE_URL} -o /dev/null -w '%{http_code}\n'
  # 200
```

*expect_code* で期待するHTTPレスポンスコードを指定するリクエスト

```sh
curl -s ${INVOKE_URL}?expect_code=400 | jq
  # {
  #   "statusCode": 400,
  #   "body": {
  #     "message": "Bad Request"
  #   }
  # }
curl -s ${INVOKE_URL}?expect_code=400 -o /dev/null -w '%{http_code}\n'
  # 400
```

## お掃除

```sh
aws cloudformation delete-stack \
    --stack-name any-response-code-demo

aws s3 rb s3://${S3BUCKET} --force
  # ...
  # delete: s3://any-response-code-demo-bucket-01234567890123/...
  # remove_bucket: any-response-code-demo-bucket-01234567890123
```
