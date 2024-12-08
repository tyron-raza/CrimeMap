from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)
bcrypt = Bcrypt(app)

from routes import *
if __name__ == "__main__":
    app.run(debug=True)
