#!/usr/bin/env python3

import os
import time

import boto3
from pygrok import Grok

from message import send_message as send_to_slack


DATA_FILE=os.getenv(
    "DATA_FILE",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/message.txt")
)

def terminate_instance(**kwargs):
    client = boto3.client(
                    'ec2',
                    aws_access_key_id=kwargs.get("aws_access_key_id"),
                    aws_secret_access_key=kwargs.get("aws_secret_access_key"),
                    region_name=kwargs.get("region_name", "us-east-1"),
                )
    print("Terminating instance")
    return client.terminate_instances(
            InstanceIds=kwargs.get("instance_list"),
            DryRun=kwargs.get("dry_run", True)
        )
    


class Retriever:
    def process_message(self):
        with open(file=DATA_FILE, mode='r') as f:
            data = f.read().splitlines(True)
            data_size = len(data)
            for d in data:
                try:
                    pattern = "%{WORD:instance_id}\* %{WORD:environment_name} health status: %{WORD:status} Reason: %{GREEDYDATA:reason}"
                    grok = Grok(pattern)
                    parsed_data = grok.match(d)

                    d_reformat = d.split('Reason:')
                    d_reformat = "\nReason:".join(d_reformat)

                    slack_url = None

                    if parsed_data.get('status') in ["Degraded", "Severe"]:
                        send_to_slack(d_reformat, slack_url=slack_url)

                    status = [True for i in eval(parsed_data.get('reason')) if "root file system is in use." in i]
                    instance_id = f"i-{parsed_data.get('instance_id')}"
                    
                    if status and status[0] and parsed_data.get('status') == "Degraded":
                        send_to_slack(f":warning: <!channel> *{instance_id}* of environment *{parsed_data.get('environment_name')}* might cause problem", slack_url=slack_url)
                        terminate_instance(
                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                            instance_list=[instance_id]
                        )

                except Exception as e:
                    print(e)
                    with open(file=os.path.join(os.path.dirname(DATA_FILE), "fault_message.txt"), mode="a") as f:
                        f.write(d)


        with open(file=DATA_FILE, mode='w') as f:
            return f.writelines(data[data_size:])

if __name__ == "__main__":
    Retriever().process_message()
