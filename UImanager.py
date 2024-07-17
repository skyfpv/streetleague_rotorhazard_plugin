from flask.blueprints import Blueprint
from flask import Flask, templating
import logging
logger = logging.getLogger(__name__)

SETTINGS_PANEL_VALUE = "sl_settings_panel"
SETTINGS_PANEL_LABEL = "Street League"
SETTINGS_UPDATE_BUTTON_VALUE = "sl_update_plugin"
SETTINGS_UPDATE_BUTTON_LABEL = "Update Plugin"

class UImanager():

    def __init__(self, rhManager):
        self.rh = rhManager

        #register UI panels
        self.rh.api.ui.register_panel(SETTINGS_PANEL_VALUE, SETTINGS_PANEL_LABEL, "settings", order=0)
        #register buttons
        self.rh.api.ui.register_quickbutton(SETTINGS_PANEL_VALUE, SETTINGS_UPDATE_BUTTON_VALUE, SETTINGS_UPDATE_BUTTON_LABEL, self.rh.update_plugin)

        #register blueprints
        self.fpvOverlayBlueprint = Blueprint(
            'fpvoverlay',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.autopilotBlueprint = Blueprint(
            'autopilot',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.leaderboardBlueprint = Blueprint(
            'leaderboard',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.rankOverlayBlueprint = Blueprint(
            'rankoverlay',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.setup_routes()
        self.rh.api.ui.blueprint_add(self.fpvOverlayBlueprint)
        self.rh.api.ui.blueprint_add(self.autopilotBlueprint)
        self.rh.api.ui.blueprint_add(self.leaderboardBlueprint)
        self.rh.api.ui.blueprint_add(self.rankOverlayBlueprint)

    def render_template(self, template_name_or_list, **context):
        try:
            return templating.render_template(template_name_or_list, **context)
        except Exception:
            logger.exception("Exception in render_template")
        return "Error rendering template"
    
    def setup_routes(self):
        @self.fpvOverlayBlueprint.route('/sl/fpvoverlay')
        def bp_fpvoverlay_page():
            return self.render_template('fpv_overlay.html')
        

        @self.autopilotBlueprint.route('/sl/autopilot')
        def bp_autopilot_page():
            return self.render_template('autopilot.html')
        
        @self.autopilotBlueprint.route('/sl/leaderboard')
        def bp_leaderboard_page():
            return self.render_template('leaderboard.html')
        
        @self.autopilotBlueprint.route('/sl/rankoverlay')
        def bp_rankoverlay_page():
            return self.render_template('rank_overlay.html')
