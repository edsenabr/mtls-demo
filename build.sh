#!/bin/bash

#build the java app
pushd web
./mvnw clean package
popd

./generate-certs.sh

docker-compose build

#push images to docker.hub
docker login
docker push edsena/mtls-demo-web:latest
docker push edsena/mtls-demo-proxy:latest


#deploy aws environment
read -er -p "Enter your account number:" CDK_DEFAULT_ACCOUNT
read -er -p "Enter the region you want to use:" CDK_DEFAULT_REGION
pushd cdk
python3 -m venv .env
. .env/bin/activate
pip install -r requirements.txt
cdk synth
cdk deploy --outputs-file outputs.json
deactivate
popd

echo "now you must wait a few minutes (usually 5) before running your tests, while the resources are loading"