from __future__ import print_function

import os
import logging
import boto3
import jinja2
import json
import slack
import io

from base64 import b64decode


# setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

slackChannel = boto3.client('ssm').get_parameter(
    Name="/tvlk-secret/tsiaihn/tsi/slack_channel",
    WithDecryption=True
)['Parameter']['Value']

slackToken = boto3.client('ssm').get_parameter(
    Name="/tvlk-secret/tsiaihn/tsi/slack_token",
    WithDecryption=True
)['Parameter']['Value']

ec2_client = boto3.client('ec2')

sc = slack.WebClient(token=slackToken)


def get_ec2_tags(instanceIds):
    print("Getting EC2 Instances Tags")
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
    print(instance_tags)
    return instance_tags


# def get_rds_tags(dbInstanceIds):


def lambda_handler(event, context):
    """
    main lambda function for handling events of AWS infrastructure health notification
    """
    logger.info('Event: ' + str(event))

    service = event["detail"]["service"]
    eventTypeCategory = event["detail"]["eventTypeCategory"]
    eventDescription = event['detail'][
        'eventDescription'][0]['latestDescription']
    resources = event['resources']
    affectedResources = resources
    if service == "EC2":
        affectedResources = get_ec2_tags(resources)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./")
    ).get_template("postTemplate.j2")
    message = template.render(
        eventDescription=eventDescription.replace("\\n", "\n"),
        resources=affectedResources
    )
    postFileandTitle = "Amazon " + service.upper()
    if eventTypeCategory == "scheduledChange":
        postFileandTitle = postFileandTitle + " Scheduled Maintenance"
    elif eventTypeCategory == "issue":
        postFileandTitle = postFileandTitle + " Issue"
    elif eventTypeCategory == "accountNotification":
        postFileandTitle = postFileandTitle + " Account Notification"
    try:
        response = sc.files_upload(
            channels=slackChannel,
            content=message,
            filetype="post",
            filename=postFileandTitle,
            title=postFileandTitle
        )
        print(response['response_metadata'])

    except Exception as error:
        print(error)

# if __name__ == "__main__":
#    with open("event_example.json") as json_file:
#        data = json.load(json_file)
#        lambda_handler(data, "context")
