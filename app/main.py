import os

from flask import Flask, make_response

from elastic_beanstalk.cpu import CPU_Usage


app = Flask(__name__)

def generate_metrics():
    metrics = ""
    cpu_usage = CPU_Usage(os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'))
    for usage in cpu_usage.get_cpu_usage():
        metrics += f"{usage}\n"
    return metrics


@app.route('/')
def index():
    return "Ok"


@app.route('/prometheus/metrics')
def prom_metrics():
    response = make_response(generate_metrics(), 200)
    response.mimetype = "text/plain"
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')