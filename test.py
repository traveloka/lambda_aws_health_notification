import os
import logging
import boto3
import jinja2
import json
import io

ec2_client = boto3.client('ec2')


def get_ec2_tags(instanceIds):
    instance_tags = []
    try:
        reservations = ec2_client.describe_instances(
            InstanceIds=instanceIds
        )
        for reservation in reservations['Reservations']:
            for instances in reservation['Instances']:
                tag = {}
                tag['InstanceId'] = instances['InstanceId']
                for instance_tag in instances['Tags']:
                    if instance_tag['Key'] == "ProductDomain":
                        tag['ProductDomain'] = instance_tag['Value']
                    if instance_tag['Key'] == "Service":
                        tag['Service'] = instance_tag['Value']
                instance_tags.append(tag)
    except Exception as e:
        print(e)
    return instance_tags

if __name__ == "__main__":
    tag = get_ec2_tags(["i-038e508b1a2953d90", "i-0bdc3aca2f790e40d"])
    print(tag)
