import os
import subprocess

from .FormatManager import FormatManager
from .UImanager import UImanager
from .EventManager import EventManager
import requests
import RHUtils

from flask import templating
from HeatGenerator import HeatGenerator, HeatPlan, HeatPlanSlot, SeedMethod
from RHUI import QuickButton, UIField, UIFieldType, UIFieldSelectOption
from Results import RaceClassRankMethod
import logging
import math
logger = logging.getLogger(__name__)

PILOT_PHOTO_URL = "/sl/static/img/pilotPhotos/"
SLAPI_URL = "https://api.streetleague.io/v1/"

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

    def sync_pilot_info(self, args):
        self.log("syncing pilot info")
        
        for pilot in self.api.db.pilots:
            rhPilotId = pilot.id
            slPilotId = self.api.db.pilot_attribute_value(rhPilotId, self.uiManager.sl_pilot_id_attr, None)
            
            if(slPilotId!=None):
                self.log("getting info for pilot "+slPilotId)
                slPilotInfo = self.getSLPilot(slPilotId)
                slPilotCallsign = slPilotInfo["username"] or pilot.callsign
                slPilotName = slPilotInfo["full_name"] or pilot.name
                slPilotColor = slPilotInfo["color"] or pilot.color

                #try:
                url = "https://aonarvdztgwamwnzuysy.supabase.co/storage/v1/object/public/avatars/"+slPilotId
                response = requests.get(url)
                if response.status_code == 200:
                    with open("plugins/streetleague_rotorhazard_plugin/static/img/pilotPhotos/"+slPilotId+".png", 'wb') as f:
                        f.write(response.content)
                    
                    self.api.db.pilot_alter(rhPilotId, callsign=slPilotCallsign, name=slPilotName, color=slPilotColor, attributes={"PilotDetailPhotoURL": "http://"+RHUtils.getLocalIPAddress()+PILOT_PHOTO_URL+slPilotId+".png"})
                else:
                    self.setPilotPhotoBlank(rhPilotId)
                #except:
                #    self.log("failed to get pilot photo")
            else:
                self.setPilotPhotoBlank(rhPilotId)

        self.log("pilot info synced")
        self.api.ui.message_alert("pilot info sync complete")
    
    def setPilotPhotoBlank(self, pilotId):
        self.api.db.pilot_alter(pilotId, attributes={"PilotDetailPhotoURL": "http://"+RHUtils.getLocalIPAddress()+PILOT_PHOTO_URL+"blank-user.png"})

    def getSLPilot(self, slPilotId):
        url = SLAPI_URL+"user/"+slPilotId
        response = requests.get(url)
        if response.status_code == 200:
            self.log("got slapi response:\n "+str(response.json()))
            return response.json()
        else:
            return {"username": None, "full_name": None, "color": None}

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

