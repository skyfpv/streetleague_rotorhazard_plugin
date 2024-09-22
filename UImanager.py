from flask.blueprints import Blueprint
from flask import Flask, templating
from RHUI import UIField, UIFieldType, UIFieldSelectOption
import logging
logger = logging.getLogger(__name__)

class UImanager():
    SETTINGS_PANEL_VALUE = "sl_settings_panel"
    SETTINGS_PANEL_LABEL = "Street League"
    SETTINGS_UPDATE_BUTTON_VALUE = "sl_update_plugin"
    SETTINGS_UPDATE_BUTTON_LABEL = "Update Plugin"
    SETTINGS_SYNC_BUTTON_VALUE = "sl_sync_plugin"
    SETTINGS_SYNC_BUTTON_LABEL = "Sync Pilot Info"
    SETTINGS_IMPORT_BUTTON_VALUE = "sl_import_race"
    SETTINGS_IMPORT_BUTTON_LABEL = "Import Race"
    SETTINGS_RACE_ID_FIELD_VALUE = "sl_race_id"
    SETTINGS_RACE_ID_FIELD_LABEL = "Race ID"
    SL_RACE_ID_VALUE = "sl_race_id"
    SL_PILOT_ID_ATTR = "sl_pilot_id"
    PILOT_CHECKED_IN_ATTR = "sl_checked_in"
    def __init__(self, rhManager):
        self.rh = rhManager

        #register UI panels
        self.rh.api.ui.register_panel(self.SETTINGS_PANEL_VALUE, self.SETTINGS_PANEL_LABEL, "settings", order=0)

        #settings panel items
        self.rh.api.ui.register_quickbutton(self.SETTINGS_PANEL_VALUE, self.SETTINGS_UPDATE_BUTTON_VALUE, self.SETTINGS_UPDATE_BUTTON_LABEL, self.rh.update_plugin)
        self.rh.api.ui.register_quickbutton(self.SETTINGS_PANEL_VALUE, self.SETTINGS_SYNC_BUTTON_VALUE, self.SETTINGS_SYNC_BUTTON_LABEL, self.rh.sync_pilots)
        self.rh.api.ui.register_quickbutton(self.SETTINGS_PANEL_VALUE, self.SETTINGS_IMPORT_BUTTON_VALUE, self.SETTINGS_IMPORT_BUTTON_LABEL, self.rh.import_race)

        raceIDField = UIField(name=self.SL_RACE_ID_VALUE, label="Race ID", desc="The ID of the race to import on streetleague.io.", field_type=UIFieldType.TEXT)
        self.rh.api.fields.register_option(raceIDField, self.SETTINGS_PANEL_VALUE)

        #register pilot attributes
        pilotIDField = UIField(name=self.SL_PILOT_ID_ATTR, label="SL Pilot ID", desc="The ID of the pilot on streetleague.io.", field_type=UIFieldType.TEXT)
        self.rh.api.fields.register_pilot_attribute(pilotIDField)

        pilotCheckinField = UIField(name=self.SL_PILOT_ID_ATTR, label="Check-In", field_type=UIFieldType.CHECKBOX, value=False)
        self.rh.api.fields.register_pilot_attribute(pilotCheckinField)

        #register blueprints
        self.fpvOverlayBlueprint = Blueprint(
            'fpvoverlay',
            __name__,
            template_folder='pages',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.autopilotBlueprint = Blueprint(
            'autopilot',
            __name__,
            template_folder='pages',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.leaderboardBlueprint = Blueprint(
            'leaderboard',
            __name__,
            template_folder='pages',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.rankOverlayBlueprint = Blueprint(
            'rankoverlay',
            __name__,
            template_folder='pages',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.preCheckBlueprint = Blueprint(
            'precheck',
            __name__,
            template_folder='pages',
            static_folder='static',
            static_url_path='/sl/static'
        )

        self.setup_routes()
        self.rh.api.ui.blueprint_add(self.preCheckBlueprint)
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
        
        @self.leaderboardBlueprint.route('/sl/leaderboard')
        def bp_leaderboard_page():
            return self.render_template('leaderboard.html')
        
        @self.rankOverlayBlueprint.route('/sl/rankoverlay')
        def bp_rankoverlay_page():
            return self.render_template('rank_overlay.html')
        
        @self.preCheckBlueprint.route('/sl/precheck')
        def bp_rankoverlay_page():
            return self.render_template('pre_check.html')
