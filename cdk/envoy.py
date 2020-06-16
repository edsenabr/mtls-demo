#!/usr/bin/env python3
class Envoy:
  def __init__(self, cluster, stack) -> None:

    app_label = {"app": "mtls-demo-envoy"}

    deployment = {
      "apiVersion": "apps/v1",
      "kind": "Deployment",
      "metadata": { "labels": app_label,
        "name": "mtls-demo-envoy"
      },
      "spec": {
        "replicas": 1,
        "selector": { "matchLabels": app_label },
        "template": {
          "metadata": { "labels": app_label },
          "spec": {
            "containers": [{
              "name": "mtls-demo-proxy",
              "image": "%s/mtls-demo-proxy:latest" % stack.node.try_get_context("prefix"),
              "ports": [
                {"containerPort": 9901},
                {"containerPort": 8081},
                {"containerPort": 8082},
                {"containerPort": 8083}
              ],
              "imagePullPolicy": "Always"
            },{
              "name": "mtls-demo-web",
              "image": "%s/mtls-demo-web:latest" % stack.node.try_get_context("prefix"),
              "ports": [{"containerPort": 8080}],
              "imagePullPolicy": "Always"
            }],
          }
        }
      }
    }

    # see https://kubernetes.io/docs/tutorials/services/source-ip/#source-ip-for-services-with-type-loadbalancer
    # see https://kubernetes.io/docs/concepts/services-networking/service/#aws-nlb-support
    envoy_http_service = {
      "apiVersion": "v1",
      "kind": "Service",
      "metadata": {
        "name": "mtls-demo-envoy-http",
        "annotations": {
          "service.beta.kubernetes.io/aws-load-balancer-type": "nlb"
        }
      },
      "spec": {
        "externalTrafficPolicy": "Local",
        "type": "LoadBalancer",
        "ports": [{"port": 80, "targetPort": 8081}],
        "selector": app_label
      }
    }

    envoy_mtls_service = {
      "apiVersion": "v1",
      "kind": "Service",
      "metadata": {
        "name": "mtls-demo-envoy-mtls",
        "annotations": {
          "service.beta.kubernetes.io/aws-load-balancer-type": "nlb"
        }
      },
      "spec": {
        "externalTrafficPolicy": "Local",
        "type": "LoadBalancer",
        "ports": [{"port": 443, "targetPort": 8083}],
        "selector": app_label
      }
    }

    cluster.add_resource(
      "envoy",
      deployment,
      envoy_http_service, 
      envoy_http_service, 
      envoy_mtls_service
    )