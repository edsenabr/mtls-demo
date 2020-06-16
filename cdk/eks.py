#!/usr/bin/env python3
from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)

from ingress import Ingress
from envoy import Envoy

class EKS:

  def __init__(self, stack: core.Stack, VPC: ec2.Vpc) -> None:

    cluster_admin = iam.Role(stack, "AdminRole",
      assumed_by=iam.AccountRootPrincipal()
    )

    cluster = eks.Cluster(
      stack, 
      "cluster", 
      default_capacity=1,
      vpc=VPC,
      masters_role=cluster_admin
    )

    #see https://github.com/kubernetes/kubernetes/issues/61486?#issuecomment-635169272
    eks.KubernetesPatch(
      stack,
      "patch",
      cluster=cluster,
      resource_name="daemonset/kube-proxy",
      resource_namespace="kube-system",
      apply_patch = {
        "spec": {
          "template": {
            "spec": {
              "containers": [{
                "name": "kube-proxy",
                "command": [
                    "kube-proxy",
                    "--v=2",
                    "--hostname-override=$(NODE_NAME)",
                    "--config=/var/lib/kube-proxy-config/config",
                ],
                "env": [{
                  "name": "NODE_NAME",
                  "valueFrom": {
                    "fieldRef": {
                      "apiVersion": "v1",
                      "fieldPath": "spec.nodeName"
                    }
                  }
                }]
              }]
            }
          }
        }
      },
      restore_patch={
        "spec": {
          "template": {
            "spec": {
              "containers": [{
                "name": "kube-proxy",
                "command": [
                  "kube-proxy",
                  "--v=2",
                  "--config=/var/lib/kube-proxy-config/config"
                ]
              }]
            }
          }
        }
      }
    )

    if stack.node.try_get_context("ingress"):
      print ("Will deploy the Ingress stack")
      Ingress (cluster, stack)

    if stack.node.try_get_context("envoy_eks"):
      print ("Will deploy the Envoy@EKS stack")
      Envoy(cluster, stack)