import datetime
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    time = str(datetime.datetime.now())
    return f"Hello from EC2 automated deployment! - {time}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
