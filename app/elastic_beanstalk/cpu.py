import boto3



class CPU_Usage:
    def __init__(self, aws_access_key, aws_secret_access_key, region_name='us-east-1'):
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.client = boto3.client(
                        'elasticbeanstalk',
                        region_name=self.region_name,
                        aws_access_key_id=self.aws_access_key,
                        aws_secret_access_key=self.aws_secret_access_key
                    )
    
    def get_cpu_usage(self):
        metrics = []
        for environment in self.client.describe_environments()['Environments']:
            try:
                environment_desc = self.client.describe_instances_health(
                    EnvironmentId=environment['EnvironmentId'],
                    AttributeNames=[
                        'All'
                    ])
                
                tags = {
                    "region": self.region_name,
                    "application": environment['ApplicationName'],
                    "environment_name": environment['EnvironmentName'],
                    "environment_id": environment['EnvironmentId']
                }

                for health in environment_desc['InstanceHealthList']:
                    cpu_utilization = health['System']['CPUUtilization']
                    env_name = environment['EnvironmentName']
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='user'} %s" % (env_name, cpu_utilization['User']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='nice'} %s" % (env_name, cpu_utilization['Nice']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='system'} %s" % (env_name, cpu_utilization['System']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='idle'} %s" % (env_name, cpu_utilization['Idle']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='iowait'} %s" % (env_name, cpu_utilization['IOWait']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='irq'} %s" % (env_name, cpu_utilization['IRQ']))
                    metrics.append("awsebs_system_cpu_percentage_average{chart='system.cpu',family='cpu%s',dimension='softirq'} %s" % (env_name, cpu_utilization['SoftIRQ']))
            except Exception as e:
                pass

        return metrics

