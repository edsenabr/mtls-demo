#!/usr/bin/env python3
import json
import sys
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--envoy_ec2', 
    action='store_true',
    dest='envoy_ec2'
  )
  parser.add_argument(
    '--envoy_eks', 
    action='store_true',
    dest='envoy_eks'
  )
  parser.add_argument(
    '--ingress', 
    action='store_true',
    dest='ingress'
  )
  parser.add_argument(
    '--prefix', 
    nargs=1,
    required=True
  )
  args = parser.parse_args()

  with open('cdk.json', 'r') as f:
    cdk = json.load(f)
  cdk["context"]["envoy_ec2"] = args.envoy_ec2
  cdk["context"]["envoy_eks"] = args.envoy_eks
  cdk["context"]["ingress"] = args.ingress
  cdk["context"]["prefix"] = args.prefix[-1]

  with open('cdk.json', 'w') as outfile:
    json.dump(cdk, outfile, indent=2)

