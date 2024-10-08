import json
from time import monotonic
from eventmanager import Evt
import gevent.monkey
from Database import ProgramMethod

from .FormatManager import Formats # type: ignore
gevent.monkey.patch_all()
class EventManager():
    def __init__(self, rhManager):
        self.rh = rhManager
        self.tasks = []

        #autopilot trigger events
        self.rh.api.events.on(Evt.CROSSING_ENTER, self.send_autopilot_trigger, default_args={"event_name": "crossing_enter"} )
        self.rh.api.events.on(Evt.CROSSING_EXIT, self.send_autopilot_trigger, default_args={"event_name": "crossing_exit"} )
        #self.rh.api.events.on(Evt.RACE_STAGE, self.send_autopilot_trigger, default_args={"event_name": "race_stage"})
        self.rh.api.events.on(Evt.RACE_START, self.send_autopilot_trigger, default_args={"event_name": "race_start"})
        self.rh.api.events.on(Evt.RACE_STOP, self.send_autopilot_trigger, default_args={"event_name": "race_stop"})
        self.rh.api.events.on(Evt.RACE_FINISH, self.send_autopilot_trigger, default_args={"event_name": "race_finish"})
        #self.rh.api.events.on(Evt.RACE_FIRST_PASS, self.send_autopilot_trigger, default_args={"event_name": "race_first_pass"})
        self.rh.api.events.on(Evt.LAPS_SAVE, self.send_autopilot_trigger, default_args={"event_name": "laps_save"})
        self.rh.api.events.on(Evt.LAPS_CLEAR, self.send_autopilot_trigger, default_args={"event_name": "laps_clear"})
        self.rh.api.events.on(Evt.LAPS_DISCARD, self.send_autopilot_trigger, default_args={"event_name": "laps_discard"})
        self.rh.api.events.on(Evt.HEAT_SET, self.handle_heat_set, default_args={"event_name": "heat_set"})
        #self.rh.api.events.on(Evt.RACE_PILOT_DONE, self.send_autopilot_trigger, default_args={"event_name": "pilot_done"})
        #self.rh.api.events.on(Evt.RACE_WIN, self.send_autopilot_trigger, default_args={"event_name": "race_win"})
        #self.rh.api.events.on(Evt.RACE_LAP_RECORDED, self.send_autopilot_trigger, default_args={"event_name": "lap_record"})
        self.rh.api.events.on(Evt.RACE_SCHEDULE, self.handle_race_schedule)
        self.rh.api.events.on(Evt.RACE_SCHEDULE_CANCEL, self.handle_race_schedule_cancel)

        #overlay events
        self.rh.api.events.on(Evt.LAP_DELETE, self.handle_race_timing)

        #overloaded events
        self.rh.api.events.on(Evt.RACE_LAP_RECORDED, self.handle_race_lap_recorded)
        self.rh.api.events.on(Evt.RACE_PILOT_DONE, self.handle_race_pilot_done)
        self.rh.api.events.on(Evt.RACE_WIN, self.handle_race_win)
        self.rh.api.events.on(Evt.RACE_STAGE, self.handle_race_stage)
        self.rh.api.events.on(Evt.RACE_FIRST_PASS, self.handle_first_pass)

        #websocket listeners
        self.rh.api.ui.socket_listen("sl_get_seat_info", self.handle_get_seat_info)
        self.rh.api.ui.socket_listen("sl_leaderboard", self.handle_get_leaderboard)
        self.rh.api.ui.socket_listen("sl_schedule_race", self.handle_sl_schedule_race)
        self.rh.api.ui.socket_listen("sl_schedule_race", self.handle_sl_schedule_race)
        # self.rh.api.ui.socket_listen("sl_get_current_stage_times", self.get_current_race_times)
        self.rh.api.ui.socket_listen("sl_get_current_stage_times", self.get_current_stage_times)
        self.rh.api.ui.socket_listen("sl_get_pilot_colors", self.get_pilot_colors)
        self.rh.api.ui.socket_listen("sl_get_current_heat_results", self.handle_current_heat_results)
        self.rh.api.ui.socket_listen("sl_pre_check_pilot", self.handle_pre_check_pilot)
        self.rh.api.ui.socket_listen("sl_pre_check_get_pilot_info", self.handle_pre_check_get_pilot_info)



    def handle_race_lap_recorded(self, data):
        self.handle_race_timing(data)
        self.send_autopilot_trigger({"event_name": "lap_record"})

    def handle_race_pilot_done(self, data):
        self.handle_race_timing(data)
        self.send_autopilot_trigger({"event_name": "pilot_done"})

    def handle_race_win(self, data):
        self.handle_race_timing(data)
        self.send_autopilot_trigger({"event_name": "race_win"})

    def handle_race_stage(self, data):
        self.handle_race_timing(data)
        self.send_autopilot_trigger({"event_name": "race_stage"})

    def handle_first_pass(self, data):
        self.handle_race_timing(data)
        self.send_autopilot_trigger({"event_name": "race_first_pass"})

    def get_pilot_colors(self):
        self.rh.log(self.rh.api.interface.seats)
        self.rh.log("get_pilot_colors()")
        pilotColors = {}
        for pilot in self.rh.api.db.pilots:
            pilotColors[pilot.id] = pilot.color
        self.rh.api.ui.socket_broadcast("sl_pilot_colors", pilotColors)

    def get_current_stage_times(self):
        self.rh.log("get_current_stage_times()")
        currentHeatId = self.rh.api.race.heat
        if(currentHeatId!=None):
            currentHeat = self.rh.api.db.heat_by_id(currentHeatId)
            #check if we aren't in practice mode
            if(currentHeat!=None):
                #check if this heat is classified or not
                if(currentHeat.class_id!=None):
                    currentStageNumber = self.rh.api.db.heat_attribute_value(currentHeat, Formats.HEAT_STAGE_ATTR_NAME, default_value=None)
                    if(currentStageNumber==None):
                        self.rh.api.ui.socket_broadcast("sl_current_stage_times", [])
                    else:
                        currentClass = self.rh.api.db.raceclass_by_id(currentHeat.class_id)
                        classStages = self.rh.formatManager.getStageHeatsByClassId(currentClass)
                        self.rh.api.ui.socket_broadcast("sl_current_stage_times", classStages[int(currentStageNumber)])
                        self.handle_race_timing(None)
            else:
                self.rh.api.ui.socket_broadcast("sl_current_stage_times", [])
                self.handle_race_timing(None)

    def handle_race_timing(self, data):
        raceTiming = self.rh.api.race.results
        raceTiming["race_start_time"] = str(self.rh.api.race.start_time)
        #if we're in practice mode
        if(self.rh.api.db.heat_by_id(self.rh.api.race.heat)==None):
            for i in range(0,len(raceTiming["by_race_time"])):
                raceTiming["by_race_time"][i]["pilot_id"] = raceTiming["by_race_time"][i]["callsign"]
                raceTiming["by_consecutives"][i]["pilot_id"] = raceTiming["by_race_time"][i]["callsign"]
                raceTiming["by_fastest_lap"][i]["pilot_id"] = raceTiming["by_race_time"][i]["callsign"]
        self.rh.log("handle_race_timing() "+str(self.rh.api.race.heat))
        self.send_ui_event("sl_race_timing", raceTiming)
        #self.send_autopilot_trigger(data)

    def handle_current_heat_results(self):
        self.send_ui_event("sl_current_heat_results", self.rh.api.race.results)

    def handle_sl_schedule_race(self, data):
        self.rh.api.race.schedule(data["start_delay"])

    def handle_speak(self, data):
        self.rh.api.ui.message_speak(data)

    def handle_heat_set(self, data):
        self.send_autopilot_trigger(data)
        self.handle_get_seat_info()

    def handle_get_leaderboard(self, data):
        raceRanks = self.rh.api.eventresults.results["classes"][int(data["classId"])]
        self.rh.api.ui.socket_broadcast("sl_leaderboard", raceRanks)

    def handle_get_seat_info(self, data=None):
        self.rh.log("handle_get_seat_info()")
        frequencies = json.loads(self.rh.api.race.frequencyset.frequencies)
        self.rh.log(frequencies)
        seats = {}
        if(self.rh.api.race.heat != 0):
            for index in self.rh.api.race.pilots:
                pilot = self.rh.api.db.pilot_by_id(self.rh.api.race.pilots[index])
                #seatColor = self.rh.api.race.seat_colors[index]
                if(pilot != None):
                    seatColor = pilot.color
                else:
                    seatColor = "#555555"
                seatActive = (frequencies['b'][index] != None)
                if pilot == None:
                    pilotDictItem = {
                        "id": 0,
                        "name": "",
                        "callsign": "",
                        "team": None,
                        "color": None,
                        "used_frequencies": "[]",
                        "active_seat": seatActive,
                        "active_color": seatColor
                    }
                else:
                    pilotDictItem = {
                        "id": pilot.id,
                        "name": pilot.name,
                        "callsign": pilot.callsign,
                        "team": pilot.team,
                        "color": pilot.color,
                        "used_frequencies": pilot.used_frequencies,
                        "active_seat": seatActive,
                        "active_color": seatColor
                    }
                seats[index] = pilotDictItem
        else:
            self.rh.log("practice mode")
            for index in range(0, len(self.rh.api.race.results["by_race_time"])):
                seats[index] = {
                    "id": self.rh.api.race.results["by_race_time"][index]["callsign"],
                    "name": "",
                    "callsign": self.rh.api.race.results["by_race_time"][index]["callsign"],
                    "team": None,
                    "color": None,
                    "used_frequencies": "[]",
                    "active_seat": True,
                    "active_color": self.rh.api.race.seat_colors[index]
                }
        

        self.rh.log(self.rh.api.race.heat)
        self.rh.api.ui.socket_broadcast("sl_seat_info", {"seat_info": seats})

    def send_autopilot_trigger(self, data):
        self.rh.log(data["event_name"])
        self.rh.api.ui.socket_broadcast("autopilot_trigger", data)

    def send_ui_event(self, subject, body):
        self.rh.api.ui.socket_broadcast(subject, body)

    def handle_shutdown(self):
        self.running = False

    def handle_race_schedule_cancel(self, args=None):
        for g in self.tasks:
            g.kill()
        self.tasks = []

    def handle_race_schedule(self, args):
        args["event_name"] = "race_schedule"
        self.send_autopilot_trigger(args)

        #kill any extra greenlets from previous schedules
        self.handle_race_schedule_cancel()

        #TO-DO allow front user to specify trigger conditions
        #send race start warnings at 15m, 10m, 9m, 8m, 7m, 6m, 5m, 4m, 3m, 2m, 1m, 30s, 15s, 10s, 5s, 4s, 3s, 2s, 1s
        self.set_race_countdown_warning(args["scheduled_at"], 60*15)
        self.set_race_countdown_warning(args["scheduled_at"], 60*10)
        self.set_race_countdown_warning(args["scheduled_at"], 60*9)
        self.set_race_countdown_warning(args["scheduled_at"], 60*8)
        self.set_race_countdown_warning(args["scheduled_at"], 60*7)
        self.set_race_countdown_warning(args["scheduled_at"], 60*6)
        self.set_race_countdown_warning(args["scheduled_at"], 60*5)
        self.set_race_countdown_warning(args["scheduled_at"], 60*4)
        self.set_race_countdown_warning(args["scheduled_at"], 60*3)
        self.set_race_countdown_warning(args["scheduled_at"], 60*2)
        self.set_race_countdown_warning(args["scheduled_at"], 60)
        self.set_race_countdown_warning(args["scheduled_at"], 30)
        self.set_race_countdown_warning(args["scheduled_at"], 15)
        self.set_race_countdown_warning(args["scheduled_at"], 10)
        self.set_race_countdown_warning(args["scheduled_at"], 5)
        self.set_race_countdown_warning(args["scheduled_at"], 4)
        self.set_race_countdown_warning(args["scheduled_at"], 3)
        self.set_race_countdown_warning(args["scheduled_at"], 2)
        self.set_race_countdown_warning(args["scheduled_at"], 1)

    def set_race_countdown_warning(self, scheduledAt, warningScheduleTime):
        notification_delay = scheduledAt-monotonic()-warningScheduleTime
        self.rh.log("notification will occur in "+str(notification_delay)+" seconds")
        if(notification_delay>0):
            self.tasks.append(gevent.spawn_later(notification_delay, self.send_race_countdown_warning, "race_in_"+str(warningScheduleTime)))

    def send_race_countdown_warning(self, eventName):
        self.send_autopilot_trigger({"event_name": eventName})
            
    def handle_pre_check_get_pilot_info(self, args):
        pilot = self.getPilotByUUID(args["slPilotId"])
        if(pilot!=None):
            self.rh.api.ui.socket_broadcast("sl_pre_check_pilot_info", {"requestId": args["requestId"], "pilot": {"id": pilot.id, "slPilotId": args["slPilotId"], "name": pilot.name, "callsign": pilot.callsign, "team": pilot.team, "color": pilot.color, "used_frequencies": pilot.used_frequencies}})
        else:
            self.rh.api.ui.socket_broadcast("sl_pre_check_pilot_info", {"requestId": args["requestId"], "pilot": None})

    def handle_pre_check_pilot(self, args):
        classId = self.rh.api.db.heat_by_id(self.rh.api.race.heat).class_id
        heats = self.rh.api.db.heats_by_class(classId)
        self.rh.log("handle_pre_check_pilot: "+str(args))
        slotFound = False
        activeNodes = self.getActiveNodes()
        for heat in heats:
            if(slotFound):
                break
            self.rh.log(heat)
            heatSlots = self.rh.api.db.slots_by_heat(heat.id)
            #check if this pilot is already in the heat
            pilotInHeat = self.pilotInHeatSlots(heatSlots, args["slPilotId"])
            
            #ensure the heat hasn't already been run. Can't use status as it's unreliable
            if(self.rh.api.db.heat_max_round(heat.id)<1 and heat.id!=self.rh.api.race.heat):
                for heatSlot in heatSlots:
                    if(slotFound):
                        break
                    self.rh.log(heatSlot)
                    
                    #check if this particular node is active in the frequency set
                    nodeActive = False
                    if(heatSlot.node_index!=None):
                        if(len(activeNodes)>=heatSlot.node_index):
                            nodeActive = activeNodes[heatSlot.node_index]

                    self.rh.log("slot: "+str(heatSlot.node_index)+", pilot: "+str(heatSlot.pilot_id)+" enabled: "+str(nodeActive))
                    if(heatSlot.pilot_id==0 and heatSlot.method == ProgramMethod.ASSIGN and nodeActive and pilotInHeat==False):
                        self.rh.log("FOUND A SLOT!")
                        self.rh.log("heat status is "+str(heat.status))
                        slotFound = True
                        self.addSLPilotToSlotIdByUUID(heat, heatSlot, args["slPilotId"], args["requestId"])
                        break
        if(slotFound==False):
            self.rh.log("No free slot found. Creating new heat")
            heat = self.rh.api.db.heat_add(name=None, raceclass=classId, auto_frequency=False)
            newHeatSlots = self.rh.api.db.slots_by_heat(heat.id)
            self.addSLPilotToSlotIdByUUID(heat, newHeatSlots[0], args["slPilotId"], args["requestId"])
        self.rh.api.ui.broadcast_heats()

    
    def getPilotByUUID(self, slPilotId):
        matchingPilots = self.rh.api.db.pilot_ids_by_attribute(self.rh.uiManager.SL_PILOT_ID_ATTR, slPilotId)
        self.rh.log(matchingPilots)
        #if we couldn't find a pilot with a matching SL ID, import a new user
        if(matchingPilots==[]):
            self.rh.log("SL pilot "+str(slPilotId)+" not found in db. Importing from streetleague.io")
            pilotId = self.rh.api.db.pilot_add(name="", callsign="", phonetic=None, team=None, color="#000000").id
            self.rh.api.db.pilot_alter(pilotId, attributes={self.rh.uiManager.SL_PILOT_ID_ATTR: slPilotId})
            self.rh.sync_pilot(self.rh.api.db.pilot_by_id(pilotId))
            if(self.rh.api.db.pilot_by_id(pilotId).callsign==""):
                self.rh.log("unable to find pilot with SL id: "+slPilotId)
                self.rh.api.db.pilot_delete(pilotId)
                return None
            self.rh.log("callsign: \""+self.rh.api.db.pilot_by_id(pilotId).callsign+"\"")
        else:
            self.rh.log("SL pilot "+str(slPilotId)+" found with ID "+str(matchingPilots[0]))
            pilotId = matchingPilots[0]
        return self.rh.api.db.pilot_by_id(pilotId)

    def pilotInHeatSlots(self, heatSlots, slPilotId):
        pilotId = self.getPilotByUUID(slPilotId).id
        for slot in heatSlots:
            if(slot.pilot_id==pilotId):
                return True
        return False
            
    def addSLPilotToSlotIdByUUID(self, heat, slot, slPilotId, requestId):
        self.rh.log("Adding SL pilot "+str(slPilotId)+" to slot ID "+str(slot.id))
        pilot = self.getPilotByUUID(slPilotId)
        self.rh.api.db.slot_alter(slot.id, method=ProgramMethod.ASSIGN, pilot=pilot.id, seed_heat_id=None, seed_raceclass_id=None, seed_rank=None)
        pilotInfo = {"id": pilot.id, "slPilotId": slPilotId, "name": pilot.name, "callsign": pilot.callsign, "team": pilot.team, "color": pilot.color}
        heatInfo = {"id": heat.id, "name": heat.name, "class_id": heat.class_id, "results": heat.results, "status": heat.status}
        self.rh.api.ui.socket_broadcast("sl_pre_check_join_confirm", {"requestId": requestId, "heat": heatInfo, "pilot": pilotInfo, "channelInfo": self.getSlotChannel(slot)})


    def getActiveNodes(self):
        activeNodes = []
        frequencySet = self.rh.api.race.frequencyset
        self.rh.log("frequencySet -> "+str(frequencySet.id))
        profile = self.rh.api.db.frequencyset_by_id(frequencySet.id)
        self.rh.log("proifle -> "+str(profile))
        self.rh.log("frequencies -> "+str(profile.frequencies))
        self.rh.log("f -> "+str(profile.frequencies))
        freqs = json.loads(profile.frequencies)["f"]
        for freq in freqs:
            activeNodes.append(freq!=0)
        self.rh.log(activeNodes)
        return activeNodes

    def getSlotChannel(self, slot):
        frequencySet = self.rh.api.race.frequencyset
        profile = self.rh.api.db.frequencyset_by_id(frequencySet.id)
        freq = json.loads(profile.frequencies)["f"][slot.node_index]
        band = json.loads(profile.frequencies)["b"][slot.node_index]
        channel = json.loads(profile.frequencies)["c"][slot.node_index]
        return {"frequency": freq, "band": band, "channel": channel}
