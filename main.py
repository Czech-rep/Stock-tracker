from flask import Flask


app = Flask(__name__)


# if u import db im cmd import it form here

from views import *
from loging import *



if __name__ == "__main__":
    app.run(debug=True)