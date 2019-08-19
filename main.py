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
    eventTypeCategory = event["detail"]["eventTypeCategory"]
    eventDescription = event['detail'][
        'eventDescription'][0]['latestDescription']
    affectedResources = event['resources']

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
