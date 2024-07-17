import os
import subprocess

from .FormatManager import FormatManager
from .UImanager import UImanager
from .EventManager import EventManager

from flask import templating
from HeatGenerator import HeatGenerator, HeatPlan, HeatPlanSlot, SeedMethod
from RHUI import QuickButton, UIField, UIFieldType, UIFieldSelectOption
from Results import RaceClassRankMethod
import logging
import math
logger = logging.getLogger(__name__)

class RHmanager():
    def __init__(self, rhapi, debugging=False):
        self.api = rhapi
        self.debugging = debugging

        self.uiManager = UImanager(self)
        self.formatManager = FormatManager(self)
        self.eventManager = EventManager(self)

    def log(self, message, warning=False):
        if(self.debugging):
            if(warning):
                logging.warning(str(message))
            else:
                logging.info(str(message))
        else:
            logging.debug(str(message))
            
    def update_plugin(self, args):
        self.log("updating Street League plugin")
        current_dir = os.getcwd()
        self.log("current directory: "+current_dir)
        plugin_relative_path = "plugins/streetleague_rotorhazard_plugin"
        plugin_path = os.path.join(current_dir, plugin_relative_path)
        try:
            # Pull the latest code from the main branch
            self.log(["git", "reset", "--hard", "HEAD"])
            result = subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.log(result.stdout)

            self.log(["git", "checkout", "main"])
            result = subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.log(result.stdout)

            self.log(["git", "pull", "origin", "main"])
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.log(result.stdout)
            
            self.log("Street League plugin updated successfully. Please restart RotorHazard to see the changes.")
            self.api.ui.message_alert("Street League plugin updated successfully. Please restart RotorHazard to see the changes.")
        except subprocess.CalledProcessError as e:
            self.log(e.output)
            self.log(e.stderr)
            self.log(f"An error occurred while updating the plugin: {e}")
            self.api.ui.message_alert("An error occurred while updating the plugin. Please check logs.")

