import os
import logging
import boto3
import jinja2
import json
import io

from base64 import b64decode

slackChannel = boto3.client('ssm').get_parameter(
    Name="/tvlk-secret/tsiaihn/tsi/slack_channel",
    WithDecryption=True
)['Parameter']['Value']

slackToken = boto3.client('ssm').get_parameter(
    Name="/tvlk-secret/tsiaihn/tsi/slack_token",
    WithDecryption=True
)['Parameter']['Value']

print slackChannel

print slackToken
