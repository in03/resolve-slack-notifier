#!/usr/bin/env python
import os
import time
import socket
from pydavinci import davinci
import chime
from tkinter import messagebox
from datetime import timedelta

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# For some reason, Resolve will fail to execute the script if certain libraries are used.
# For example, use of the 'logging' module will cause execution to fail with no errors.
# Maybe this has something to do with Resolve injecting its own stuff like it does with
# the job, status, error variables? Tkinter is your best best for showing errors, unfortunately.

TOKEN = "<PUT YOUR SLACK TOKEN HERE>"
CHANNEL_NAME = "renderbot"

client = WebClient(token=TOKEN)
resolve = davinci.Resolve()

chime.notify_exceptions()
chime.theme("material")
chime.info()

def get_job_info(job_id):
    jobs = resolve.project.render_jobs
    for job_info in jobs:
        if job_info["JobId"] == job_id:
            return job_info

    return ""

def notify_slack(message):
    try:
        _ = client.chat_postMessage(
            channel=CHANNEL_NAME,
            text=message
        )
    except SlackApiError as e:
        print(f"Error sending slack message: {e.response['error']}")

def main():
    
    try:
    
        
        host = socket.gethostname()
        project = resolve.project
        render_status = project.render_status(job)
        status = str(render_status["JobStatus"]).lower()
        
        job_info = get_job_info(job)
        job_name = job_info["RenderJobName"]
        
        output_dir = job_info["TargetDir"]
        output_filename = job_info["OutputFilename"]
        
        if status == "cancelled":
            chime.warning()
            return
            
        if status == "complete":
            
            render_time = timedelta(milliseconds=int(render_status["TimeTakenToRenderInMs"]))
        
            chime.success()
            message = (
                f"Huzzah! {host} finished rendering:\n\n"
                
                f"{output_filename}\n\n"
                
                f"Took {render_time}\n"
                f"See '{output_dir}'"
            )
            
            
        else:
        
            chime.theme("zelda")
            chime.error()
            message = (
                f"Uh oh! {host} FAILED rendering:\n\n"
                
                f"{output_filename}\n\n"
                
                f"Took {render_time}\n"
                f"Status '{status}'"
            )
            
        
        
        notify_slack(message)
        
    except Exception as e:
        chime.theme("mario")
        chime.error()
        
        message = f"Renderbot had a glitch on {host}!\n"
        message += f"Here's what went wrong:\n{e}"
        try:
            notify_slack(message)
        except Exception:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main()
    time.sleep(2)
