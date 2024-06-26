import os
import subprocess
from eventmanager import Evt
from HeatGenerator import HeatGenerator, HeatPlan, HeatPlanSlot, SeedMethod
from RHUI import QuickButton, UIField, UIFieldType, UIFieldSelectOption
from Results import RaceClassRankMethod
from Database import HeatAdvanceType
import logging
import math
logger = logging.getLogger(__name__)

#Logging
DEBUG_LOGGING = True

#FieldNames
HEAT_STAGE_ATTR_NAME = "HeatStage"
STAGE_COUNT_FIELD_NAME = "stage_count"
STAGE_POINTS_RANKING_METHOD_NAME = "Total Stage Points"

def log(message):
    if(DEBUG_LOGGING):
        logging.info(str(message))
    else:
        logging.debug(str(message))

def getPilotsInClass(rhapi, classId):
    if classId:
        race_class = rhapi.db.raceclass_by_id(classId)
        class_results = rhapi.db.raceclass_results(race_class)
        if class_results and type(class_results) == dict:
            # fill from available results and convert to list of pilot objects
            byRaceTime = []
            for pilot in class_results['by_race_time']:
                byRaceTime.append(rhapi.db.pilot_by_id(pilot["pilot_id"]))
            pilotsInClass = byRaceTime
        else:
            # fall back to all pilots
            pilotsInClass = rhapi.db.pilots
    else:
        # use total number of pilots
        pilotsInClass = rhapi.db.pilots
    return pilotsInClass

def StreetLeagueElite8(rhapi, args):

    generatedHeatPlans = [
        HeatPlan(
            "Semifinal B - Heat 1/2",
            [
                HeatPlanSlot(SeedMethod.INPUT, 2),
                HeatPlanSlot(SeedMethod.INPUT, 4),
                HeatPlanSlot(SeedMethod.INPUT, 6),
                HeatPlanSlot(SeedMethod.INPUT, 8)
            ]
        ),
        
        HeatPlan(
            "Semifinal A - Heat 1/2",
            [
                HeatPlanSlot(SeedMethod.INPUT, 1),
                HeatPlanSlot(SeedMethod.INPUT, 3),
                HeatPlanSlot(SeedMethod.INPUT, 5),
                HeatPlanSlot(SeedMethod.INPUT, 7)
            ]
        ),
        HeatPlan(
            "Semifinal B - Heat 2/2",
            [
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 2, 0),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 3, 0),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 4, 0)
            ]
        ),
        
        HeatPlan(
            "Semifinal A - Heat 2/2",
            [
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 2, 1),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 3, 1),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 4, 1)
            ]
        ),
        HeatPlan(
            "Next 4 - Finals",
            [
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 2, 2),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 3, 2),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 2, 3),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 3, 3)
            ]
        ),
        HeatPlan(
            "Top 4 -Finals",
            [
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 0),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 1),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 2),
                HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 3)
            ]
        )
    ]
    return generatedHeatPlans

def getClassIndex(rhapi, classId):
    outputClassIndex = 0
    if classId==None:
        outputClassIndex = len(rhapi.db.raceclasses)+1
    else:
        outputClassIndex = 0
        for i in range(0,len(rhapi.db.raceclasses)):
            raceClass = rhapi.db.raceclasses[i]
            if(classId==raceClass.id):
                outputClassIndex = i
    return outputClassIndex

def getStageHeatsByClassId(rhapi, raceClass):
    stageHeats = {}
    classHeats = rhapi.db.heats_by_class(raceClass.id)
    for heat in classHeats:
        stage = int(rhapi.db.heat_attribute_value(heat, HEAT_STAGE_ATTR_NAME, default_value=0))
        if(not stage in stageHeats):
            stageHeats[stage] = []
        heatResult = rhapi.db.heat_results(heat)
        if(heatResult!=None):
            stageHeats[stage].append(heatResult)
    return stageHeats

def handleDidNotStart(rhapi, stageLeaderboard, raceClassId):
    pilotsInClass = getPilotsInClass(rhapi, raceClassId)
    log("adding did not starts to leaderboard")
    for pilot in pilotsInClass:
        dns = True
        for pilotResult in stageLeaderboard:
            if(str(pilotResult["pilot_id"])==str(pilot.id)):
                dns = False
                break
        if(dns==True):
            stageLeaderboard.append({"pilot_id": pilot.id, "callsign": pilot.callsign, "laps": None, "total_time_raw": None, "total_time":None, "points": 0})
            log("- pilot did not start the race: "+str(pilot.callsign))
        else:
            log("- pilot started the race: "+str(pilot.callsign))
    return stageLeaderboard

def sortByPoints(leaderboard):
    sorted_leaderboard = sorted(leaderboard, key=lambda x: (-x["points"]))
    for i in range(0, len(sorted_leaderboard)):
        sorted_leaderboard[i]["position"] = i+1
    return sorted_leaderboard

def sortByLapsThenTime(leaderboard):
    leaderboard = sorted(leaderboard, key=lambda x: (-x["laps"], x["total_time_raw"]))
    return leaderboard

#ranking method for points race
#NEEDS OPTIMIZATION
def pointsRanking(rhapi, raceClass, args):
    log("running points ranking method")
    log("args"+str(args))
    log("race_class")
    log("- id: "+str(raceClass.id))
    log("- name: "+str(raceClass.name))
    log("- description: "+str(raceClass.description))
    log("- format_id: "+str(raceClass.format_id))
    log("- win_condition: "+str(raceClass.win_condition))
    #log("- results: "+str(raceClass.results))
    log("- _cache_status: "+str(raceClass._cache_status))
    log("- ranking: "+str(raceClass.ranking))
    log("- rank_settings: "+str(raceClass.rank_settings))
    log("- _rank_status: "+str(raceClass._rank_status))
    log("- rounds: "+str(raceClass.rounds))
    log("- heat_advance_type: "+str(raceClass.heat_advance_type))
    log("- order: "+str(raceClass.order))
    log("- active: "+str(raceClass.active))
    classPilots = getPilotsInClass(rhapi, raceClass.id)
    stageLeaderboards = {} #contains stage lists which have pilots sorted by race time
    stagePointsByPilotId = {}
    heatsByStage = getStageHeatsByClassId(rhapi, raceClass)
    totalPointsByPilotId = {}
    leaderboard = []

    #initialize the leaderboard for all pilots
    for i in range(0,len(classPilots)):
        pilot = classPilots[i]
        totalPointsByPilotId[pilot.id] = 0
        stagePointsByPilotId[pilot.id] = []

    #create a list of leaderboards seperated by stage
    for stage in heatsByStage:
        stageLeaderboard = []
        #add all the pilot laps and times to the stage leaderboard
        for heatResult in heatsByStage[stage]:
            for pilotResult in heatResult["by_race_time"]:
                laps = pilotResult.get("laps")
                totalTimeRaw = pilotResult.get("total_time_raw")
                totalTime = pilotResult.get("total_time")
                pilotId = pilotResult.get("pilot_id")
                callsign = pilotResult.get("callsign")
                stageLeaderboard.append({"pilot_id": pilotId, "callsign": callsign, "laps": laps, "total_time_raw": totalTimeRaw, "total_time":totalTime})
        
        #sort this stage leaderboard so that we can easily award points
        stageLeaderboard = sortByLapsThenTime(stageLeaderboard)

        #award points for the stage
        for i in range(0,len(stageLeaderboard)):
            stageLeaderboard[i]["points"] = len(stageLeaderboard)-i

        #add the stage leaderboard to the dict of stage leaderboards
        stageLeaderboards[stage] = stageLeaderboard

    #sum up each pilot's stage points to get their total points
    for stage in stageLeaderboards:
        stageLeaderboard = stageLeaderboards[stage]
        stageLeaderboard = handleDidNotStart(rhapi,stageLeaderboard,raceClass.id)
        for pilotResult in stageLeaderboard:
            #if the pilot never started the race
            if(pilotResult.get("points")==0):
                #mark them as a DNS
                stagePointsByPilotId[pilotResult.get("pilot_id")].append("dns")
            #otherwise
            else:
                #add their stage points to their total points and mark the points for this stage
                totalPointsByPilotId[pilotResult.get("pilot_id")]+=pilotResult.get("points")
                stagePointsByPilotId[pilotResult.get("pilot_id")].append(pilotResult.get("points"))

    #fill leaderboard with pilot entries
    for pilotId in totalPointsByPilotId:
        pilot = rhapi.db.pilot_by_id(pilotId)
        points = totalPointsByPilotId[pilotId]
        leaderboardResult = {"position": 0, "points": points, "pilot_id": pilot.id, "callsign": pilot.callsign}
        
        #add each stage column to the leaderboard so pilot points can be viewed for each stage
        for stageIndex in range(0,len(stagePointsByPilotId[pilot.id])):
            leaderboardResult["stage "+str(stageIndex+1)] = stagePointsByPilotId[pilot.id][stageIndex]

        leaderboard.append(leaderboardResult)

    #sort the leaderboard by pilots total points
    leaderboard = sortByPoints(leaderboard)

    rankFields = []
    for stage in stageLeaderboards:
        rankFields.append({"name": "stage "+str(stage), "label":"Stage "+str(stage)})
    rankFields.append({"name": "points", "label":"Total Points"})
    return (leaderboard, {"method_label": "Total Stage Points", "rank_fields": rankFields})

#points race heat generator
def StreetLeaguePointsGenerator(rhapi, args):
    log("classes...")
    for raceClass in rhapi.db.raceclasses:
        log(" - "+str(raceClass.name)+": "+str(raceClass.id))
    inputClassId = args.get("input_class")
    inputClass = rhapi.db.raceclass_by_id(inputClassId)
    outputClassId = args.get("output_class")
    availableSeats = args.get("available_seats")
    stageCount = int(args.get(STAGE_COUNT_FIELD_NAME))

    outputClassIndex = getClassIndex(rhapi, outputClassId)

    log("input class ID: "+str(inputClassId))
    log("output class ID: "+str(outputClassId))
    log("available seats: "+str(availableSeats))
    log("stage count: "+str(stageCount))

    totalPilotsToSeed = len(getPilotsInClass(rhapi, inputClassId))
    

    if totalPilotsToSeed == 0:
        logger.warning("Unable to street league points race: no pilots available")
        return False

    heatLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    heatLetterStartIndex = math.ceil(totalPilotsToSeed/availableSeats)-1
    seatsToSkip = availableSeats-(totalPilotsToSeed % availableSeats)
    if(seatsToSkip>=availableSeats):
            seatsToSkip = 0
    log("Generate Points Race")
    generatedHeatPlans = []

    for stage in range(1,stageCount+1):
        log(" - Stage "+str(stage))
        pilotsLeftToSeed = totalPilotsToSeed
        seatsToSkip = availableSeats-(totalPilotsToSeed % availableSeats)
        if(seatsToSkip>=availableSeats):
            seatsToSkip = 0
        for h in range(0,len(heatLetters)):
            heat = heatLetters[heatLetterStartIndex-h]
            if(pilotsLeftToSeed>0):
                heatName = "Stage "+str(stage)+" - Heat "+heat
                log("  - Heat "+str(heatName))
                heatPlanSlots = []
                if(stage==1):
                    seedMethod = SeedMethod.INPUT
                else:
                    seedMethod = SeedMethod.CLASS_INDEX
                log("  - skipping "+str(seatsToSkip)+" seats. "+str(totalPilotsToSeed)+" pilots to seed")
                for node in range(seatsToSkip,availableSeats):
                    seatsToSkip = 0
                    if(seedMethod == SeedMethod.INPUT):
                        seedIndex = None
                    else:
                        seedIndex = outputClassIndex
                    heatPlanSlot = HeatPlanSlot(method=seedMethod, seed_rank=pilotsLeftToSeed, seed_index=seedIndex)
                    heatPlanSlots.append(heatPlanSlot)
                    pilotsLeftToSeed=pilotsLeftToSeed-1
                    if(pilotsLeftToSeed<=0):
                        break

                generatedHeatPlans.append(HeatPlan(heatName, heatPlanSlots))
            else:
                break

    log("heats generated!!!!")
    return generatedHeatPlans


def register_generator_handlers(args):
    


    #register elite 8
    #stageCount = UIField(name = STAGE_COUNT_FIELD_NAME, label = 'Number of Stages', field_type = UIFieldType.CHECKBOX, value = True)
    EliteEightSettings = []
    args['register_fn'](
        HeatGenerator("Street League Elite 8", generator_fn=StreetLeagueElite8, settings=EliteEightSettings)
    )

    #register points race
    stageCount = UIField(name = STAGE_COUNT_FIELD_NAME, label = 'Number of Stages', field_type = UIFieldType.BASIC_INT, value = 8)
    pointsSettings = [stageCount]
    
    #register street league points
    args['register_fn'](
        
        HeatGenerator(label="Street League Points", generator_fn=StreetLeaguePointsGenerator, settings=pointsSettings)
    )

def register_ranking_handlers(args):
    args['register_fn'](
        RaceClassRankMethod(STAGE_POINTS_RANKING_METHOD_NAME, pointsRanking, default_args=None, settings=None, name=None)
    )

def getRaceFormatByName(rhapi, formatName):
    raceFormatByName = None
    for raceFormat in rhapi.db.raceformats:
        log(raceFormat.name)
        if(raceFormat.name==formatName):
            raceFormatByName = raceFormat.id
    return raceFormatByName

def getClassRankMethodByName(rhapi, rankMethodName):
    rankMethodByname = None
    for rankMethod in rhapi.classrank.methods:
        
        if(rankMethod==rankMethodName):
            rankMethodByName = rankMethod
    return rankMethodByName

def applyElite8ClassDefaults(args):
    rhapi = args.get("rhapi")
    classId = args.get("output_class_id")

    #set the class ranking method to ...TO-DO: create a new class ranking method for finals
    pointsDescription = "The top 8 pilots are grouped into semifinals A and B. Each seminfinal group races twice. The winning pilot from each of those races advances into the Top 4 where they will race for positions 1-4. Pilots who fail to win a semifinal are knocked into the Next 4 race to compete for positions 5-8."
    rhapi.db.raceclass_alter(classId, rounds=1, raceformat=getRaceFormatByName(rhapi, "First to 3 Laps"), heat_advance_type=HeatAdvanceType.NEXT_HEAT, description=pointsDescription, win_condition=getClassRankMethodByName(rhapi, "Last_Heat_Position"))
    rhapi.ui.broadcast_raceclasses()
#apply class defaults as well as appropriate stage attribute to each of the generated heats
def applyPointsClassDefaults(args):
    generate_args = args.get("generate_args")
    generatorStageCount = int(generate_args.get(STAGE_COUNT_FIELD_NAME))
    available_seats = int(generate_args.get("available_seats"))
    classId = args.get("output_class_id")
    log("apply stages...")
    rhapi = args.get("rhapi")

    #set the class ranking method to Total Stage Points
    pointsDescription = "Similar to Mario Kart, pilots earn points by setting the fastest time they can in each stage; 1pt for every competitor they beat. After each stage, the next stage is seeded based on pilots' total points, keeping rivals in the same heat. The pilot who earns the most points after all stages are complete wins.\nIMPORTANT: Please remember to seed all heats in the next stage after the current stage is complete."
    rhapi.db.raceclass_alter(classId, rounds=1, raceformat=getRaceFormatByName(rhapi, "First to 3 Laps"), heat_advance_type=HeatAdvanceType.NEXT_HEAT, description=pointsDescription, win_condition=getClassRankMethodByName(rhapi, "Total_Stage_Points"))

    log(str(args))
    
    classHeats = rhapi.db.heats_by_class(classId)
    log("class has "+str(len(classHeats))+" heats")
    totalPilots = len(getPilotsInClass(rhapi, classId))
    heatsPerStage = math.ceil(totalPilots/available_seats)

    classHeatIndex = 0
    for stage in range(0,generatorStageCount):
        log("- stage: "+str(stage))
        for stageHeatIndex in range(0,heatsPerStage):
            log(" - stage heat index: "+str(stageHeatIndex))
            log(" - class heat index: "+str(classHeatIndex))
            heat = classHeats[classHeatIndex]
            log(" - setting heat "+str(heat.name)+" stage attr to "+str(stage+1))

            rhapi.db.heat_alter(heat.id, attributes={HEAT_STAGE_ATTR_NAME:int(stage+1)})
            classHeatIndex+=1
    rhapi.ui.broadcast_raceclasses()

def generate_complete_handler(args):
    log("generate points complete handler")
    log(args)
    if(args["generator"]=="Street_League_Points"):
        applyPointsClassDefaults(args)
    if(args["generator"]=="Street_League_Elite_8"):
        applyElite8ClassDefaults(args)
    
class RHmanager():
    def __init__(self, rhapi):
        self._rhapi = rhapi
        #register the heat generators

        #points race
        rhapi.events.on(Evt.HEAT_GENERATOR_INITIALIZE, register_generator_handlers)
        rhapi.events.on(Evt.CLASS_RANK_INITIALIZE, register_ranking_handlers)
        rhapi.events.on(Evt.HEAT_GENERATE, generate_complete_handler, default_args={"rhapi":rhapi})

        #register the stage attribute
        heatStage = UIField(name = HEAT_STAGE_ATTR_NAME, label = 'Stage', field_type = UIFieldType.BASIC_INT, value = 0)
        rhapi.fields.register_heat_attribute(heatStage)

        #register UI panels
        settingsPanel = rhapi.ui.register_panel("street_league_plugin", "Street League", "settings", order=0)
        #register panel
        #register buttons
        rhapi.ui.register_quickbutton('street_league_plugin', 'update_plugin', 'Update Plugin', self.update_plugin)

    def update_plugin(self, args):
        log("updating Street League plugin")
        current_dir = os.getcwd()
        log("current directory: "+current_dir)
        plugin_relative_path = "plugins/streetleague_rotorhazard_plugin"
        plugin_path = os.path.join(current_dir, plugin_relative_path)
        try:
            # Pull the latest code from the main branch
            log(["git", "fetch"])
            result = subprocess.run(
                ["git", "fetch"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            log(result.stdout)

            log(["git", "pull", "origin", "main"])
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                cwd=plugin_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            log(result.stdout)
            
            log("Street League plugin updated successfully. Please RotorHazard to see the changes.")
            self._rhapi.ui.message_alert("Street League plugin updated successfully.")
        except subprocess.CalledProcessError as e:
            log(e.output)
            log(e.stderr)
            log(f"An error occurred while updating the plugin: {e}")
            self._rhapi.ui.message_alert("An error occurred while updating the plugin. Please check logs.")

def initialize(rhapi):
    log(str(rhapi.API_VERSION_MAJOR)+"."+str(rhapi.API_VERSION_MINOR))
    RHmanager(rhapi)