from flask import Flask, render_template, request, url_for, session, g
from core import models
from views import users, admin, shop

app = Flask(__name__)
app.config.from_object('core.config.DevelopmentConfig')
app.register_blueprint(users.app)
app.register_blueprint(admin.app, url_prefix='/access')
app.register_blueprint(shop.app)

@app.before_request
def before_request():
    models.initialize()

@app.teardown_request
def teardown_request(exception):
    models.close()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)