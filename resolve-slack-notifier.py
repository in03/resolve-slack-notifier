#!/usr/bin/env python
import os
import socket
import sys
from pydavinci import davinci
import dotenv

from loguru import logger

logger.add("renderbot_lastrun.log")

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

dotenv.load_dotenv(verbose=True)

TOKEN = os.getenv('RENDERBOT_SLACK_TOKEN')
CHANNEL_NAME = os.getenv('RENDERBOT_CHANNEL_NAME')

resolve = davinci.Resolve()
client = WebClient(token=TOKEN)

def get_job_info(project, job_id):
    jobList = project.GetRenderJobList()
    for jobDetail in jobList:
        if jobDetail["JobId"] == job_id:
            return jobDetail

    return ""

def notify_slack(message):
    try:
        _ = client.chat_postMessage(
            channel=CHANNEL_NAME,
            text=message
        )
    except SlackApiError as e:
        print(f"[red]Error sending slack message: {e.response['error']}")

def main():
    try:
        
        project = resolve.project
        detailed_status = project.render_status(job)
        message = f"Slack Message sent by hostname: {socket.gethostname()}, project name: {project.name}\n"
        message += f"Message initiated by: {sys.argv[0]}\n"
        message += f"job id: {job}, job status: {status}, error (if any) {error}\n"
        message += f"Detailed job status: {str(detailed_status)}"
        message += f"Job Details: {str(get_job_info(project, job))}\n"
        notify_slack(message)
        
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
