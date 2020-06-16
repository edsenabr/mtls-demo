#!/bin/bash

__ask () {
  echo $1
  select yn in Yes No; do
      case $yn in
          Yes) 
            export $2=True
            break
          ;; 
          No)
            break
          ;;
      esac
  done
}

cat<<EOF
In order to deploy this stack, you need to inform the Docker Hub prefix where the images
  were deployed. If you didn't build the application, just hit <enter> and the default, 
  pre-built images will be used. Since the repositories are named as:
    prefix/mtls-demo-web
    prefix/mtls-demo-proxy
  .. you need to inform only the "prefix" part:
EOF
read -er -p "Enter the prefix:" PREFIX

cat<<EOF
  The CDK stack will lookup the latest AMI available for the Envoy@EC2 scenario. It'll need
    the AWS account and the AWS region where you'll deployu the stack.
EOF
#deploy aws environment
read -er -p "Enter your account number:" CDK_DEFAULT_ACCOUNT
read -er -p "Enter the region you want to use:" CDK_DEFAULT_REGION

__ask "Do you want to deploy the Envoy@EKS scenario ?" "envoy_eks"
__ask "Do you want to deploy the Envoy@EC2 scenario ?" "envoy_ec2"
__ask "Do you want to deploy the Ingress@EKS scenario ?" "ingress"

cat<<EOF
  PREFIX: $PREFIX
  CDK_DEFAULT_ACCOUNT: $CDK_DEFAULT_ACCOUNT
  CDK_DEFAULT_REGION: $CDK_DEFAULT_REGION
  Envoy@EKS: $envoy_eks
  Envoy@EC2: $envoy_ec2
  Ingress: $ingress
EOF

pushd cdk
if [[ ! -d .env ]]; then
  python3 -m venv .env
fi
. .env/bin/activate
pip install -r requirements.txt
cdk synth -c repository_prefix=${PREFIX:-edsena} -c envoy_ec2=$envoy_ec2 -c envoy_eks=$envoy_eks -c ingress=$ingress
cdk deploy -c repository_prefix=${PREFIX:-edsena} -c envoy_ec2=$envoy_ec2 -c envoy_eks=$envoy_eks -c ingress=$ingress --outputs-file outputs.json
deactivate
popd

echo "now you must wait a few minutes (usually 5) before running your tests, while the resources are loading"