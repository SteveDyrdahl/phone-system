#!/bin/bash
S3_BUCKET=?
AWS_PROFILE=?

rm phonesystem.zip
rm -rf dist
mkdir dist
cp -rf phonesystem dist
cp -rf env/lib/python3.6/site-packages/* dist
cd dist
zip -r ../phonesystem.zip .
cd ..
aws s3 cp phonesystem.zip s3://"$S3_BUCKET"/phonesystem.zip --profile $AWS_PROFILE

