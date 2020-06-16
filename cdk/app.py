#!/usr/bin/env python3
from ec2 import EC2
from eks import EKS
import os

from aws_cdk import (
  aws_ec2 as ec2,
  core
)

class Stack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)


    VPC = ec2.Vpc(
      self, 
      "vpc",
      cidr="10.0.0.0/22",
      max_azs=2,
      nat_gateways=1
    )
    if bool(self.node.try_get_context("envoy_ec2")):
      print ("Will deploy the Envoy@EC2 stack")
      EC2(self,VPC)

    if bool(self.node.try_get_context("envoy_eks")) or bool(self.node.try_get_context("ingress")):
      print ("Will create the EKS Cluster")
      EKS(self,VPC)

app = core.App()

Stack(
	app, 
	"mtls-demo",
    env={
          'account': os.environ['CDK_DEFAULT_ACCOUNT'], 
          'region': os.environ['CDK_DEFAULT_REGION']
    },
    tags={
      "stack": "mtls-demo"
    }
)
app.synth()