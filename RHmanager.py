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

    def sync_pilots(self, args):
        self.log("syncing pilot info")
        
        for pilot in self.api.db.pilots:
            self.sync_pilot(pilot)

        self.log("pilot info synced")
        self.api.ui.message_alert("pilot info sync complete")

    def sync_pilot(self, rhPilot):
        self.log("syncing pilot info")

        slPilotId = self.api.db.pilot_attribute_value(rhPilot.id, self.uiManager.SL_PILOT_ID_ATTR, None)
        
        if(slPilotId!=None):
            self.log("getting info for pilot "+slPilotId)
            slPilotInfo = self.getSLPilot(slPilotId)
            slPilotCallsign = slPilotInfo["username"] or rhPilot.callsign
            slPilotName = slPilotInfo["full_name"] or rhPilot.name
            slPilotColor = slPilotInfo["color"] or rhPilot.color

            #try:
            url = "https://aonarvdztgwamwnzuysy.supabase.co/storage/v1/object/public/avatars/"+slPilotId
            response = requests.get(url)
            if response.status_code == 200:
                with open("plugins/streetleague_rotorhazard_plugin/static/img/pilotPhotos/"+slPilotId+".png", 'wb') as f:
                    f.write(response.content)
                
                self.api.db.pilot_alter(rhPilot.id, callsign=slPilotCallsign, name=slPilotName, color=slPilotColor, attributes={"PilotDetailPhotoURL": "http://"+RHUtils.getLocalIPAddress()+PILOT_PHOTO_URL+slPilotId+".png"})
            else:
                self.setPilotPhotoBlank(rhPilot.id)
            #except:
            #    self.log("failed to get pilot photo")
        else:
            self.setPilotPhotoBlank(rhPilot.id)
        self.api.ui.broadcast_pilots()

    def import_race(self, args):
        self.log("importing race")
        slRaceId = self.api.db.option(self.uiManager.SETTINGS_RACE_ID_FIELD_VALUE, default = None)
    
        if(slRaceId==None):
            self.log("no race id provided")
            self.api.ui.message_alert("No race id provided. You can find the race id in the url for a desired race page on streetleague.io")
            return

        url = SLAPI_URL+"race/"+slRaceId
        response = self.makeGetRequest(url)
        self.log(response.json())
        slPilots = response.json()["pilot_ids"] if response != None else []
        rhPilots = self.api.db.pilots
        rhSlPilotMap = {}
        for pilot in rhPilots:
            slId = self.api.db.pilot_attribute_value(pilot.id, self.uiManager.SL_PILOT_ID_ATTR, None)
            if(slId!=None):
                rhSlPilotMap[self.api.db.pilot_attribute_value(pilot.id, self.uiManager.SL_PILOT_ID_ATTR)] = pilot.id

        for slPilot in slPilots:
            self.log(slPilot)
            #find the rh pilot with the same sl id
            rhPilotId = rhSlPilotMap.get(slPilot["id"], None) if slPilot["id"] in rhSlPilotMap else None
            #if rh already has a pilot with that sl id, create a new one
            if(rhPilotId==None):
                rhPilotId = self.api.db.pilot_add(name="", callsign="", phonetic=None, team=None, color="#000000").id
                self.api.db.pilot_alter(rhPilotId, attributes={self.uiManager.SL_PILOT_ID_ATTR: slPilot["id"]})

            self.sync_pilot(self.api.db.pilot_by_id(rhPilotId))

        self.log("race pilots imported")
        self.api.ui.message_alert("Pilots imported successfully")
    
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
        
    def makeGetRequest(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            return None

    def update_plugin(self, args):
        self.log("updating Street League plugin")
        current_dir = os.getcwd()
        self.log("current directory: "+current_dir)
        plugin_relative_path = "plugins/streetleague_rotorhazard_plugin"
        plugin_path = os.path.join(current_dir, plugin_relative_path)
        # try:
        #     # Pull the latest code from the main branch
        #     self.log("git reset --hard HEAD"])
        #     result = subprocess.run(
        #         ["git", "reset", "--hard", "HEAD"],
        #         check=True,
        #         cwd=plugin_path,
        #         stdout=subprocess.PIPE,
        #         stderr=subprocess.PIPE,
        #         text=True
        #     )
        #     self.log(result.stdout)
        # except subprocess.CalledProcessError as e:
        #     self.log(e.output)
        #     self.log(e.stderr)
        #     self.log(f"An error occurred while updating the plugin: {e}")
        #     self.api.ui.message_alert("An error occurred while updating the plugin. Please check logs.")

        # Pull the latest code from the main branch
        try:
            self.log(["git fetch"])
            result = subprocess.run(
                ["git", "fetch"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.log(result.stdout)

            self.log(["git pull"])
            result = subprocess.run(
                ["git", "pull"],
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

