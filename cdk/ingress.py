#!/usr/bin/env python3
from pathlib import Path
from base64 import b64encode
from aws_cdk import (
    aws_eks as eks,
)

class Ingress:
  def readCert(self, file_name):
    return str(
      b64encode(
        Path(file_name)
          .read_text()
            .encode("utf-8")
      ), 
      "utf-8"
    )

  def __init__(self, cluster, stack) -> None:
    ca_cert = self.readCert('../certs/ca.pem')
    tls_cert = self.readCert('../certs/server.pem')
    tls_key = self.readCert('../certs/server.key')

    app_label = {"app": "mtls-demo-ingress"}

    deployment = {
      "apiVersion": "apps/v1",
      "kind": "Deployment",
      "metadata": { "labels": app_label,
        "name": "mtls-demo-ingress"
      },
      "spec": {
        "replicas": 1,
        "selector": { "matchLabels": app_label },
        "template": {
          "metadata": { "labels": app_label },
          "spec": {
            "containers": [{
              "name": "mtls-demo-web",
              "image": "%s/mtls-demo-web:latest" % stack.node.try_get_context("repository_prefix"),
              "ports": [{"containerPort": 8080}]
            }]
          }
        }
      }
    }

    mtls_ingress = {
      "apiVersion": "networking.k8s.io/v1beta1",
      "kind": "Ingress",
      "metadata": {
        "name": "mtls-demo-ingress",
        "annotations": {
          "nginx.ingress.kubernetes.io/ssl-redirect": "false",
          "nginx.ingress.kubernetes.io/force-ssl-redirect": "false",
          "nginx.ingress.kubernetes.io/auth-tls-verify-client": "on",
          "nginx.ingress.kubernetes.io/auth-tls-secret": "default/mtls-demo-ingresss",
          "nginx.ingress.kubernetes.io/auth-tls-verify-depth": "1",
          "nginx.ingress.kubernetes.io/auth-tls-error-page": "http://aws.amazon.com",
          "nginx.ingress.kubernetes.io/auth-tls-pass-certificate-to-upstream": "true"
        }
      },
      "spec": {
        "rules": [{
            "host": "*.amazonaws.com",
            "http": {
              "paths": [{
                "backend": {
                  "serviceName": "mtls-demo-ingress",
                  "servicePort": 8080
                },
                "path": "/"
              }]
            }
          }
        ],
        "tls": [{
          "hosts": [
            "*.amazonaws.com"
          ],
          "secretName": "mtls-demo-ingresss"
        }]
      }
    }

    service = {
      "apiVersion": "v1",
      "kind": "Service",
      "metadata": {
        "name": "mtls-demo-ingress",
      },
      "spec": {
        "type": "ClusterIP",
        "ports": [{"port": 8080, "targetPort": 8080}],
        "selector": app_label
      }
    }

    secret = {
      "apiVersion": "v1",
      "kind": "Secret",
      "metadata": {
        "name": "mtls-demo-ingresss"
      },
      "data": {
        "ca.crt": ca_cert,
        "tls.crt": tls_cert,
        "tls.key": tls_key
      }
    }

    namespace = {
      "apiVersion": "v1",
      "kind": "Namespace",
      "metadata": {
        "name": "ingress-nginx",
        "labels": {
          "app.kubernetes.io/name": "ingress-nginx",
          "app.kubernetes.io/instance": "ingress-nginx"
        }
      }
    }

    ingress_namespace = eks.KubernetesResource(
      stack, 
      "namespace",
      cluster=cluster,
      manifest=[namespace]
    )

    #see https://kubernetes.io/docs/tutorials/services/source-ip/#source-ip-for-services-with-type-loadbalancer
    #see https://kubernetes.io/docs/concepts/services-networking/service/#aws-nlb-support
    eks.HelmChart(
      stack, 
      "chart",
      cluster=cluster,
      chart="ingress-nginx",
      repository="https://kubernetes.github.io/ingress-nginx",
      namespace=namespace.get("metadata").get("name"),
      values={
        "controller": {
          "name": "mtls-demo-ingress",
          "logLevel": 5,
          "healthStatus": "true",
          "healthStatusURI": "/health",
          "service": {
            "externalTrafficPolicy": "Local",
            "annotations": {
              "service.beta.kubernetes.io/aws-load-balancer-type" :"nlb",
            }
          }
        }
      }
    ).node.add_dependency(ingress_namespace)

    cluster.add_resource(
      "secret",
      secret
    )

    cluster.add_resource(
      "deployment",
      deployment
    )

    cluster.add_resource(
      "ingress",
      service,
      mtls_ingress
    )