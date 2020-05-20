import os


DATA_FILE=os.getenv(
    "DATA_FILE",
    os.path.join(os.path.abspath(""), "data/message.txt")
)

class Queuer:
    def __init__(self, data):
        self.data = str(data)
    
    def set_queue(self):
        with open(file=DATA_FILE, mode="a") as f:
            return f.write(f"{self.data}\n")
