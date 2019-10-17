# AnyResponseCodeDemo

## 概要

- API Gateway - Lambdaの構成で、デフォルトでは、Lambdaでエラーが発生した場合でも、API Gatewayではレスポンスコードは200として返却する
- これはAPI Gateway自体では問題は発生しておらず、Lambda側のエラーはLambda側で処理し、API Gatewayとしては、API Gatewayのレスポンスコードを返す
- 但し、ケース（要件）によっては、Lambdaで指定したレスポンスコードをAPI Gatewayのレスポンスコードとして返却したい場合がある
- その場合のデモ

## 構成

## デプロイ

ソースコードをアップロードするS3バケットを作成

```sh
aws cloudformation create-stack \
    --stack-name any-response-code-demo-bucket \
    --template-body file://bucket_template.yaml

S3BUCKET=$(aws cloudformation describe-stacks \
    --stack-name any-response-code-demo-bucket \
    --query 'Stacks[].Outputs[?OutputKey==`S3Bucket`].OutputValue' \
    --output text)
echo ${S3BUCKET}
  #
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

レスポンスコードが200のケース

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

レスポンスコードが400のケース

```sh
curl -s ${INVOKE_URL}?expect_code=400 | jq
  # {
  #   "statusCode": 400,
  #   "body": {
  #     "message": "Requested response code is 400"
  #   }
  # }
curl -s ${INVOKE_URL}?expect_code=400 -o /dev/null -w '%{http_code}\n'
  # 400
```

レスポンスコードが500のケース

```sh
curl -s ${INVOKE_URL}?expect_code=50x | jq
  # {
  #   "statusCode": 500,
  #   "body": {
  #     "message": "Unsupported code was specified"
  #   }
  # }
curl -s ${INVOKE_URL}?expect_code=50x -o /dev/null -w '%{http_code}\n'
  # 500
```

## お掃除

```sh
aws cloudformation delete-stack \
    --stack-name any-response-code-demo

aws cloudformation delete-stack \
    --stack-name any-response-code-demo-bucket
```
