import os, datetime

import boto3
from dotenv import load_dotenv
from influxdb import InfluxDBClient


load_dotenv()

client = boto3.client(
    'elasticbeanstalk',
    region_name=os.getenv('AWS_REGION_NAME'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

influx_client = InfluxDBClient(
    host=os.getenv('INFLUX_HOST'),
    database=os.getenv('INFLUX_DBNAME'),
    use_udp=True,
    udp_port=4444
    )

response = client.describe_environments()

for environment in response['Environments']:
    try:
        now = datetime.datetime.now()
        environment_desc = client.describe_instances_health(
            EnvironmentId=environment['EnvironmentId'],
            AttributeNames=[
                'All'
            ])

        tags = {
            "region": os.getenv('AWS_REGION_NAME'),
            "application": environment['ApplicationName'],
            "environment_name": environment['EnvironmentName'],
            "environment_id": environment['EnvironmentId']
        }

        json_body = [
            {
                "measurement": "awseb_instance_count",
                "tags": tags,
                "time": now,
                "fields": {
                    "value": environment_desc['InstanceHealthList'].__len__()
                }
            }
        ]

        for health in environment_desc['InstanceHealthList']:
            json_body.append({
                "measurement": "awseb_instance_health",
                "tags": {
                    "region": os.getenv('AWS_REGION_NAME'),
                    "application": environment['ApplicationName'],
                    "environment_name": environment['EnvironmentName'],
                    "environment_id": environment['EnvironmentId']
                },
                "time": now,
                "fields": {
                    "value": health['HealthStatus']
                }
            })
            json_body += [{
                "measurement": "awseb_instance_cpu_utilization",
                "tags": {
                    "region": os.getenv('AWS_REGION_NAME'),
                    "application": environment['ApplicationName'],
                    "environment_name": environment['EnvironmentName'],
                    "environment_id": environment['EnvironmentId'],
                    "dimension": "User"
                },
                "time": now,
                "fields": {
                    "value": health['System']['CPUUtilization']['User'],
                }
            },{
                "measurement": "awseb_instance_cpu_utilization",
                "tags": {
                    "region": os.getenv('AWS_REGION_NAME'),
                    "application": environment['ApplicationName'],
                    "environment_name": environment['EnvironmentName'],
                    "environment_id": environment['EnvironmentId'],
                    "dimension": "Idle"
                },
                "time": now,
                "fields": {
                    "value": health['System']['CPUUtilization']['Idle'],
                }
            }]

        influx_client.write_points(json_body)
    except Exception as e:
        pass
