from flask import Flask


app = Flask(__name__)


# if u import db im cmd import it form here

from views_dashboard import *
from views_loging import *



if __name__ == "__main__":
    app.run(debug=True)