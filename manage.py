import os
import unittest

# from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import admin_blue, products_blue, recom_blue, user_blue, fb_blue, dashboard_blue, page_blue
from app.main import create_app # , db
from app.main.services import admin, user, recom, product, dashboard

DEBUG = True
HOST = "0.0.0.0"
PORT = 8000

app = create_app(os.getenv('ENV') or 'dev')
app.register_blueprint(admin_blue, url_prefix="/admin")
app.register_blueprint(products_blue, url_prefix="/api/1.0/products")
app.register_blueprint(recom_blue, url_prefix="/api/1.0/products")
app.register_blueprint(user_blue, url_prefix="/api/1.0/user")
app.register_blueprint(dashboard_blue, url_prefix="/api/1.0/dashboard")
app.register_blueprint(fb_blue)
app.register_blueprint(page_blue)
app.config['JSON_AS_ASCII'] = False

app.app_context().push()

manager = Manager(app)

# migrate = Migrate(app, db)

# manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run(debug=DEBUG, host=HOST, port=PORT)

@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()