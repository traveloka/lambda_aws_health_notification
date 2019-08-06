from __future__ import print_function

import os
import logging
import boto3
import jinja2
import json

# setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get SNS ARN from environment variable
snsTargetArn = os.environ['SNS_TARGET_ARN']


def publish_to_sns(message, subject):
    client = boto3.client("sns")
    try:
        response = client.publish(
            TargetArn=snsTargetArn,
            Message=message,
            Subject=subject,
            MessageStructure="string"
        )
    except Exception as error:
        print(error)


def lambda_handler(event, context):
    """
    main lambda function for handling events of AWS infrastructure health notification
    """
    logger.info('Event: ' + str(event))

    service = event["detail"]["service"]

    event_description = event['detail'][
        'eventDescription'][0]['latestDescription']
    affected_resources = event['resources']

    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./")
    ).get_template("email_template.j2")
    message = template.render(
        eventDescription=event_description,
        resources=affected_resources
    )
    subject = "[Amazon " + service + " Maintenance] " + \
        event['detail']['eventTypeCode']
    #publish_to_sns(message, subject)

if __name__ == "__main__":
    with open("event_example.json") as json_file:
        data = json.load(json_file)
        lambda_handler(data, "context")
