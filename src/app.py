from flask import Flask


from .bp.bp_account import bp_account
from .bp.bp_api import bp_api
from .bp.bp_app import bp_app
from .bp.bp_aprilFool import bp_aprilFool
from .bp.bp_assetbundle import bp_assetbundle
from .bp.bp_building import bp_building
from .bp.bp_businessCard import bp_businessCard
from .bp.bp_campaignV2 import bp_campaignV2
from .bp.bp_char import bp_char
from .bp.bp_charBuild import bp_charBuild
from .bp.bp_charRotation import bp_charRotation
from .bp.bp_config import bp_config
from .bp.bp_crisisV2 import bp_crisisV2
from .bp.bp_gacha import bp_gacha
from .bp.bp_general import bp_general
from .bp.bp_mail import bp_mail
from .bp.bp_pay import bp_pay
from .bp.bp_quest import bp_quest
from .bp.bp_rlv2 import bp_rlv2
from .bp.bp_sandboxPerm import bp_sandboxPerm
from .bp.bp_settings import bp_settings
from .bp.bp_shop import bp_shop
from .bp.bp_social import bp_social
from .bp.bp_storyreview import bp_storyreview
from .bp.bp_templateShop import bp_templateShop
from .bp.bp_tower import bp_tower
from .bp.bp_u8 import bp_u8
from .bp.bp_user import bp_user
from .bp.misc_bp import misc_bp


app = Flask(__name__)


app.register_blueprint(bp_account)
app.register_blueprint(bp_api)
app.register_blueprint(bp_app)
app.register_blueprint(bp_aprilFool)
app.register_blueprint(bp_assetbundle)
app.register_blueprint(bp_building)
app.register_blueprint(bp_businessCard)
app.register_blueprint(bp_campaignV2)
app.register_blueprint(bp_char)
app.register_blueprint(bp_charBuild)
app.register_blueprint(bp_charRotation)
app.register_blueprint(bp_config)
app.register_blueprint(bp_crisisV2)
app.register_blueprint(bp_gacha)
app.register_blueprint(bp_general)
app.register_blueprint(bp_mail)
app.register_blueprint(bp_pay)
app.register_blueprint(bp_quest)
app.register_blueprint(bp_rlv2)
app.register_blueprint(bp_sandboxPerm)
app.register_blueprint(bp_settings)
app.register_blueprint(bp_shop)
app.register_blueprint(bp_social)
app.register_blueprint(bp_storyreview)
app.register_blueprint(bp_templateShop)
app.register_blueprint(bp_tower)
app.register_blueprint(bp_u8)
app.register_blueprint(bp_user)
app.register_blueprint(misc_bp)

app.json.sort_keys = False

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8443,
        debug=True,
    )
