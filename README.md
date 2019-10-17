# AnyResponseCodeDemo

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


```sh
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket ${S3BUCKET}
```


```sh
sam deploy \
    --template-file packaged.yaml \
    --stack-name any-response-code-demo \
    --capabilities CAPABILITY_IAM
```
