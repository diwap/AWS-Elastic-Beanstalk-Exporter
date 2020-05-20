import os

from flask import Flask, request, make_response

from queuer import Queuer


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "OK"

@app.route('/message', methods=['POST'])
def message_queuer():
    def send_response(status, code):
        response = make_response("{\"status\": \"%s\"" % (status), code)
        response.mimetype = "application/json"
        return response

    if request.method == 'POST':
        try:
            data = request.args.get("data")
            if not data:
                return send_response("Failure", 400)
            
            Queuer(data).set_queue()

            return send_response("Success", 200)
        except Exception as e:
            print(e)
            return send_response("Failure", 400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001")
