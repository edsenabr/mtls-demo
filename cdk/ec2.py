#!/usr/bin/env python3

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

class EC2:

    def __init__(self, stack : core.Stack, VPC: ec2.Vpc) -> None:

        bastionSG = ec2.SecurityGroup(stack, "BastionSecurityGroup",
            vpc=VPC,
            description="Allow ssh access to the bastion host",
            allow_all_outbound=True            
        )

        bastionSG.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(22), ''
            "allow ssh access from the world"
        )

        bastionSG.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp_range(8081, 8083),
            "allow http(s) access from the world"
        )

        userData = ec2.UserData.for_linux()
        userData.add_commands("""
            set -v
            apt update
            apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common gdebi-core ec2-instance-connect
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
            add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu	$(lsb_release -cs)	stable"
            apt install -y docker-ce docker-ce-cli containerd.io
            usermod -a -G docker ubuntu
            curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            echo 'version: "3.8"' > /home/ubuntu/docker-compose.yaml
            echo 'services:' >> /home/ubuntu/docker-compose.yaml
            echo '  web:' >> /home/ubuntu/docker-compose.yaml
            echo '    image: edsena/mtls-demo-web' >> /home/ubuntu/docker-compose.yaml
            echo '    network_mode: "service:proxy"' >> /home/ubuntu/docker-compose.yaml
            echo '    depends_on:' >> /home/ubuntu/docker-compose.yaml
            echo '      - proxy' >> /home/ubuntu/docker-compose.yaml
            echo '    restart: unless-stopped' >> /home/ubuntu/docker-compose.yaml
            echo '  proxy:' >> /home/ubuntu/docker-compose.yaml
            echo '    image: edsena/mtls-demo-proxy' >> /home/ubuntu/docker-compose.yaml
            echo '    ports:' >> /home/ubuntu/docker-compose.yaml
            echo '      - "9901:9901"' >> /home/ubuntu/docker-compose.yaml
            echo '      - "8081:8081"' >> /home/ubuntu/docker-compose.yaml
            echo '      - "8082:8082"' >> /home/ubuntu/docker-compose.yaml
            echo '      - "8083:8083"' >> /home/ubuntu/docker-compose.yaml
            echo '      - "8084:8084"' >> /home/ubuntu/docker-compose.yaml
            echo '    restart: unless-stopped' >> /home/ubuntu/docker-compose.yaml
            echo 'networks:' >> /home/ubuntu/docker-compose.yaml
            echo '  public:' >> /home/ubuntu/docker-compose.yaml
            echo '    external: true' >> /home/ubuntu/docker-compose.yaml
            /usr/local/bin/docker-compose -f /home/ubuntu/docker-compose.yaml up
        """)

        # no key installed, use
        #
        #   aws ec2-instance-connect send-ssh-public-key 
        #
        # to install a temporary key and gain access to the vm
        bastion = ec2.Instance(stack, "Bastion",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, 
                ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.MachineImage.lookup(name="ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"),
            vpc=VPC,
            security_group=bastionSG,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            user_data=userData
        )
        core.CfnOutput(stack, "BastionIP",
            value=bastion.instance_public_ip
        )
        core.CfnOutput(stack, "BastionInstanceID",
            value=bastion.instance_id
        )
        core.CfnOutput(stack, "BastionSendSSHKeyCommand",
            value= "aws ec2-instance-connect send-ssh-public-key --instance-id %s --instance-os-user ubuntu --availability-zone %s --ssh-public-key file://~/.ssh/id_rsa.pub" % (
              bastion.instance_id,
              bastion.instance_availability_zone
            )
        )


        nlb = elbv2.NetworkLoadBalancer(
            stack, 
            "NLB",
            vpc=VPC,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
        core.CfnOutput(stack, "NLBAddress",
            value=nlb.load_balancer_dns_name
        )
        core.Tag.add(
            nlb,
            "stack",
            "ec2",
            apply_to_launched_instances=True
        )

        nlb.add_listener(
            "HTTP",
            port=80,
            default_target_groups=[elbv2.NetworkTargetGroup(
                stack,
                "HTTPDefaultTargetGroup",
                port=8081,
                vpc=VPC,
                targets=[
                    elbv2.InstanceTarget(
                        bastion.instance_id,
                        8081
                    )
                ]
            )]
        )

        nlb.add_listener(
            "mTLS",
            port=443,
            default_target_groups=[elbv2.NetworkTargetGroup(
                stack,
                "mTLSDefaultTargetGroup",
                port=8083,
                vpc=VPC,
                targets=[
                    elbv2.InstanceTarget(
                        bastion.instance_id,
                        8083
                    )
                ]
            )]
        )