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


sc = slack.WebClient(token=slackToken)


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
    try:
        response = sc.files_upload(
            channels=slackChannel,
            content=message,
            filetype="post",
            filename="Amazon " + service.upper() + " Scheduled Maintenance",
            title="Amazon " + service.upper() + " Scheduled Maintenance"
        )
        print(response['response_metadata'])

    except Exception as error:
        print(error)

# if __name__ == "__main__":
#    with open("event_example.json") as json_file:
#        data = json.load(json_file)
#        lambda_handler(data, "context")
