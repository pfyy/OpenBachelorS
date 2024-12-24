from flask import Flask


from .bp.bp_account import bp_account
from .bp.bp_app import bp_app
from .bp.bp_char import bp_char
from .bp.bp_charBuild import bp_charBuild
from .bp.bp_charRotation import bp_charRotation
from .bp.bp_config import bp_config
from .bp.bp_general import bp_general
from .bp.bp_quest import bp_quest
from .bp.bp_shop import bp_shop
from .bp.bp_u8 import bp_u8
from .bp.bp_user import bp_user


app = Flask(__name__)


app.register_blueprint(bp_account)
app.register_blueprint(bp_app)
app.register_blueprint(bp_char)
app.register_blueprint(bp_charBuild)
app.register_blueprint(bp_charRotation)
app.register_blueprint(bp_config)
app.register_blueprint(bp_general)
app.register_blueprint(bp_quest)
app.register_blueprint(bp_shop)
app.register_blueprint(bp_u8)
app.register_blueprint(bp_user)
