# checkin_system/api/__init__.py

from .team import team_api
from .login_api import login_api
from .checkin_api import checkin_api
from .record_api import record_api
from .report_api import report_api

def register_api_blueprints(app):
    app.register_blueprint(team_api)
    app.register_blueprint(login_api)
    app.register_blueprint(checkin_api)
    app.register_blueprint(record_api)
    app.register_blueprint(report_api)
