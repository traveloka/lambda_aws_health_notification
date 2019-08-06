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
#logger = logging.getLogger()
# logger.setLevel(logging.INFO)

#slackChannel = os.environ["SLACK_CHANNEL"]
#slackToken = os.environ["SLACK_TOKEN"]


sc = slack.WebClient(token=slackToken)


def lambda_handler(event, context):
    """
    main lambda function for handling events of AWS infrastructure health notification
    """
    #logger.info('Event: ' + str(event))

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
            filename="Amazon " + service + " Scheduled Maintenance",
            title="Amazon " + service + " Scheduled Maintenance"
        )
        print(response)

    except Exception as error:
        print(error)

if __name__ == "__main__":
    with open("event_example.json") as json_file:
        data = json.load(json_file)
        lambda_handler(data, "context")
