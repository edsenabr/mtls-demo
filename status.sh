#!/bin/bash

while true; do 
	status="$(aws elbv2 describe-target-groups --query 'TargetGroups[].[TargetGroupArn]' --output text | xargs -i aws elbv2 describe-target-health --target-group-arn {} --query 'TargetHealthDescriptions[].[TargetHealth.State, Target.Id] ' --output text )"
	healthy=$(grep -Ev 'initial|unhealthy' <<<$status | sed -e '/^$/d' )
	unhealthy=$(grep -E 'initial|unhealthy' <<<$status | sed -e '/^$/d' )
	if [[ -z $unhealthy ]]; then
		echo "all healthy!"
		exit;
	fi
	echo -e "healthy: $(wc -l <<<$healthy); waiting for: ($(wc -l <<<$unhealthy))\n$unhealthy"
	sleep 5;
done;