import os
import logging
import boto3
import jinja2
import json
import io

with open("event_example.json") as json_file:
    event = json.load(json_file)

service = event["detail"]["service"]
eventTypeCategory = event["detail"]["eventTypeCategory"]
eventDescription = event['detail'][
    'eventDescription'][0]['latestDescription']
affectedResources = event['resources']
template = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./")
).get_template("postTemplate.j2")
message = template.render(
    eventDescription=eventDescription,
    resources=affectedResources
)
print(eventDescription)
print(message)
