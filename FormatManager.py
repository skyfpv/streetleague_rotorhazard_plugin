import math
from HeatGenerator import HeatGenerator, HeatPlan, HeatPlanSlot, SeedMethod
from RHUI import QuickButton, UIField, UIFieldType, UIFieldSelectOption
from Database import HeatAdvanceType
from Results import RaceClassRankMethod
from eventmanager import Evt



#FieldNames

class Formats:
    HEAT_STAGE_ATTR_NAME = "HeatStage"
    STAGE_COUNT_FIELD_NAME = "stage_count"
    STAGE_POINTS_RANKING_METHOD_NAME = "Total Stage Points"

class FormatManager():

    def __init__(self, rhManager):
        self.rh = rhManager

        #register the heat generators
        #points race
        self.rh.api.events.on(Evt.HEAT_GENERATOR_INITIALIZE, self.register_generator_handlers)
        self.rh.api.events.on(Evt.CLASS_RANK_INITIALIZE, self.register_ranking_handlers)
        self.rh.api.events.on(Evt.HEAT_GENERATE, self.generate_complete_handler)

        #register the stage attribute
        heatStage = UIField(name = Formats.HEAT_STAGE_ATTR_NAME, label = 'Stage', field_type = UIFieldType.BASIC_INT, value = 0)
        self.rh.api.fields.register_heat_attribute(heatStage)

    #returns a list of pilots who have results in the class. If no class is passed, or no results are available, all pilots are returned
    def getPilotsFromClassResults(self, classId):
        if classId:
            race_class = self.rh.api.db.raceclass_by_id(classId)
            class_results = self.rh.api.db.raceclass_results(race_class)
            if class_results and type(class_results) == dict:
                # fill from available results and convert to list of pilot objects
                byRaceTime = []
                for pilot in class_results['by_race_time']:
                    byRaceTime.append(self.rh.api.db.pilot_by_id(pilot["pilot_id"]))
                pilotsInClass = byRaceTime
            else:
                # fall back to all pilots
                pilotsInClass = self.rh.api.db.pilots
        else:
            # use total number of pilots
            pilotsInClass = self.rh.api.db.pilots
        return pilotsInClass

    def getPilotsInClass(self, classId):
        if classId:
            class_heats = self.rh.api.db.heats_by_class(classId)
            classPilots = []
            if class_heats == []:
                # fill from available results and convert to list of pilot objects
                for heat in class_heats:
                    heat_slots = self.rh.api.db.slots_by_heat(heat.id)
                    for slot in heat_slots:
                        if(slot.pilot_id!=None):
                            classPilots[slot.pilot_id] = self.rh.api.db.pilot_by_id(slot.pilot_id)
            else:
                # fall back to all pilots
                pilotsInClass = self.rh.api.db.pilots
        else:
            # use total number of pilots
            pilotsInClass = self.rh.api.db.pilots
        return pilotsInClass

    def StreetLeagueElite8(self, rhapi, args):

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
                "Top 4 - Finals",
                [
                    HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 0),
                    HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 1),
                    HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 2),
                    HeatPlanSlot(SeedMethod.HEAT_INDEX, 1, 3)
                ]
            )
        ]
        return generatedHeatPlans

    def getClassIndex(self, classId):
        outputClassIndex = 0
        if classId==None:
            outputClassIndex = len(self.rh.api.db.raceclasses)+1
        else:
            outputClassIndex = 0
            for i in range(0,len(self.rh.api.db.raceclasses)):
                raceClass = self.rh.api.db.raceclasses[i]
                if(classId==raceClass.id):
                    outputClassIndex = i
        return outputClassIndex

    def getStageHeatsByClassId(self, raceClass):
        stageHeats = {}
        classHeats = self.rh.api.db.heats_by_class(raceClass.id)
        for heat in classHeats:
            stage = int(self.rh.api.db.heat_attribute_value(heat, Formats.HEAT_STAGE_ATTR_NAME, default_value=0))
            if(not stage in stageHeats):
                stageHeats[stage] = []
            heatResult = self.rh.api.db.heat_results(heat)
            if(heatResult!=None):
                stageHeats[stage].append(heatResult)
        return stageHeats

    def handleDidNotStart(self, stageLeaderboard, raceClassId):
        pilotsInClass = self.getPilotsInClass(raceClassId)
        for pilot in pilotsInClass:
            dns = True
            for pilotResult in stageLeaderboard:
                if(str(pilotResult["pilot_id"])==str(pilot.id)):
                    dns = False
                    break
            if(dns==True):
                stageLeaderboard.append({"pilot_id": pilot.id, "callsign": pilot.callsign, "laps": None, "total_time_raw": None, "total_time":None, "points": 0})
        return stageLeaderboard

    def sortByPoints(self, leaderboard):
        sorted_leaderboard = sorted(leaderboard, key=lambda x: (-x["points"]))
        for i in range(0, len(sorted_leaderboard)):
            sorted_leaderboard[i]["position"] = i+1
        return sorted_leaderboard

    def sortByLapsThenTime(self, leaderboard):
        leaderboard = sorted(leaderboard, key=lambda x: (-x["laps"], x["total_time_raw"]))
        return leaderboard

    #ranking method for points race
    #NEEDS OPTIMIZATION
    def pointsRanking(self, rhapi, raceClass, args):
        self.rh.log("running points ranking method")
        self.rh.log("args"+str(args))
        self.rh.log("race_class")
        self.rh.log("- id: "+str(raceClass.id))
        self.rh.log("- name: "+str(raceClass.name))
        self.rh.log("- description: "+str(raceClass.description))
        self.rh.log("- format_id: "+str(raceClass.format_id))
        self.rh.log("- win_condition: "+str(raceClass.win_condition))
        #self.rh.log("- results: "+str(raceClass.results))
        self.rh.log("- _cache_status: "+str(raceClass._cache_status))
        self.rh.log("- ranking: "+str(raceClass.ranking))
        self.rh.log("- rank_settings: "+str(raceClass.rank_settings))
        self.rh.log("- _rank_status: "+str(raceClass._rank_status))
        self.rh.log("- rounds: "+str(raceClass.rounds))
        self.rh.log("- heat_advance_type: "+str(raceClass.heat_advance_type))
        self.rh.log("- order: "+str(raceClass.order))
        self.rh.log("- active: "+str(raceClass.active))
        classPilots = self.getPilotsInClass(raceClass.id)
        self.rh.log(classPilots)
        stageLeaderboards = {} #contains stage lists which have pilots sorted by race time
        stagePointsByPilotId = {}
        heatsByStage = self.getStageHeatsByClassId(raceClass)
        totalPointsByPilotId = {}
        leaderboard = []

        #initialize the leaderboard for all pilots
        for pilot in classPilots:
            totalPointsByPilotId[pilot.id] = 0
            stagePointsByPilotId[pilot.id] = []

        #create a list of leaderboards seperated by stage
        for stage in heatsByStage:
            stageLeaderboard = []
            #add all the pilot laps and times to the stage leaderboard
            for heatResult in heatsByStage[stage]:
                for pilotResult in heatResult["by_race_time"]: #TO-DO: THERE'S PROBLY A BUG HERE. PILOTS WITH NO HOLESHOT ARE NOT INCLUDED IN THE HEAT RESULTS
                    laps = pilotResult.get("laps")
                    totalTimeRaw = pilotResult.get("total_time_raw")
                    totalTime = pilotResult.get("total_time")
                    pilotId = pilotResult.get("pilot_id")
                    callsign = pilotResult.get("callsign")
                    stageLeaderboard.append({"pilot_id": pilotId, "callsign": callsign, "laps": laps, "total_time_raw": totalTimeRaw, "total_time":totalTime})
            
            #sort this stage leaderboard so that we can easily award points
            stageLeaderboard = self.sortByLapsThenTime(stageLeaderboard)

            #award points for the stage
            for i in range(0,len(stageLeaderboard)):
                stageLeaderboard[i]["points"] = len(stageLeaderboard)-i

            #add the stage leaderboard to the dict of stage leaderboards
            stageLeaderboards[stage] = stageLeaderboard

        #sum up each pilot's stage points to get their total points
        for stage in stageLeaderboards:
            stageLeaderboard = stageLeaderboards[stage]
            stageLeaderboard = self.handleDidNotStart(stageLeaderboard,raceClass.id)
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
            pilot = self.rh.api.db.pilot_by_id(pilotId)
            points = totalPointsByPilotId[pilotId]
            leaderboardResult = {"position": 0, "points": points, "pilot_id": pilot.id, "callsign": pilot.callsign}
            
            #add each stage column to the leaderboard so pilot points can be viewed for each stage
            for stageIndex in range(0,len(stagePointsByPilotId[pilot.id])):
                leaderboardResult["stage "+str(stageIndex+1)] = stagePointsByPilotId[pilot.id][stageIndex]

            leaderboard.append(leaderboardResult)

        #sort the leaderboard by pilots total points
        leaderboard = self.sortByPoints(leaderboard)

        rankFields = []
        for stage in stageLeaderboards:
            rankFields.append({"name": "stage "+str(stage), "label":"Stage "+str(stage)})
        rankFields.append({"name": "points", "label":"Total Points"})
        return (leaderboard, {"method_label": "Total Stage Points", "rank_fields": rankFields})

    #points race heat generator
    def StreetLeaguePointsGenerator(self, rhapi, args):
        self.rh.log("classes...")
        for raceClass in self.rh.api.db.raceclasses:
            self.rh.log(" - "+str(raceClass.name)+": "+str(raceClass.id))
        inputClassId = args.get("input_class")
        inputClass = self.rh.api.db.raceclass_by_id(inputClassId)
        outputClassId = args.get("output_class")
        availableSeats = args.get("available_seats")
        stageCount = int(args.get(Formats.STAGE_COUNT_FIELD_NAME))

        outputClassIndex = self.getClassIndex(outputClassId)

        self.rh.log("input class ID: "+str(inputClassId))
        self.rh.log("output class ID: "+str(outputClassId))
        self.rh.log("available seats: "+str(availableSeats))
        self.rh.log("stage count: "+str(stageCount))

        totalPilotsToSeed = len(self.getPilotsFromClassResults(inputClassId))
        

        if totalPilotsToSeed == 0:
            self.rh.log("Unable to street league points race: no pilots available", True)
            return False

        heatLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        heatLetterStartIndex = math.ceil(totalPilotsToSeed/availableSeats)-1
        seatsToSkip = availableSeats-(totalPilotsToSeed % availableSeats)
        if(seatsToSkip>=availableSeats):
                seatsToSkip = 0
        self.rh.log("Generate Points Race")
        generatedHeatPlans = []

        for stage in range(1,stageCount+1):
            self.rh.log(" - Stage "+str(stage))
            pilotsLeftToSeed = totalPilotsToSeed
            seatsToSkip = availableSeats-(totalPilotsToSeed % availableSeats)
            if(seatsToSkip>=availableSeats):
                seatsToSkip = 0
            for h in range(0,len(heatLetters)):
                heat = heatLetters[heatLetterStartIndex-h]
                if(pilotsLeftToSeed>0):
                    heatName = "Stage "+str(stage)+" - Heat "+heat
                    self.rh.log("  - Heat "+str(heatName))
                    heatPlanSlots = []
                    if(stage==1):
                        seedMethod = SeedMethod.INPUT
                    else:
                        seedMethod = SeedMethod.CLASS_INDEX
                    self.rh.log("  - skipping "+str(seatsToSkip)+" seats. "+str(totalPilotsToSeed)+" pilots to seed")
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

        self.rh.log("heats generated!!!!")
        return generatedHeatPlans


    def register_generator_handlers(self, args):
        #register elite 8
        #stageCount = UIField(name = STAGE_COUNT_FIELD_NAME, label = 'Number of Stages', field_type = UIFieldType.CHECKBOX, value = True)
        EliteEightSettings = []
        args['register_fn'](
            HeatGenerator("Street League Elite 8", generator_fn=self.StreetLeagueElite8, settings=EliteEightSettings)
        )

        #register points race
        stageCount = UIField(name = Formats.STAGE_COUNT_FIELD_NAME, label = 'Number of Stages', field_type = UIFieldType.BASIC_INT, value = 8)
        pointsSettings = [stageCount]
        args['register_fn'](
            
            HeatGenerator(label="Street League Points", generator_fn=self.StreetLeaguePointsGenerator, settings=pointsSettings)
        )

    def register_ranking_handlers(self, args):
        args['register_fn'](
            RaceClassRankMethod(Formats.STAGE_POINTS_RANKING_METHOD_NAME, self.pointsRanking, default_args=None, settings=None, name=None)
        )

    def getRaceFormatByName(self, formatName):
        raceFormatByName = None
        for raceFormat in self.rh.api.db.raceformats:
            self.rh.log(raceFormat.name)
            if(raceFormat.name==formatName):
                raceFormatByName = raceFormat.id
        return raceFormatByName

    def getClassRankMethodByName(self, rankMethodName):
        rankMethodByname = None
        for rankMethod in self.rh.api.classrank.methods:
            
            if(rankMethod==rankMethodName):
                rankMethodByName = rankMethod
        return rankMethodByName

    def applyElite8ClassDefaults(self, args):
        rhapi = args.get("rhapi")
        classId = args.get("output_class_id")

        #set the class ranking method to ...TO-DO: create a new class ranking method for finals
        pointsDescription = "The top 8 pilots are grouped into semifinals A and B. Each seminfinal group races twice. The winning pilot from each of those races advances into the Top 4 where they will race for positions 1-4. Pilots who fail to win a semifinal are knocked into the Next 4 race to compete for positions 5-8."
        self.rh.api.db.raceclass_alter(classId, rounds=1, raceformat=self.getRaceFormatByName("First to 3 Laps"), heat_advance_type=HeatAdvanceType.NEXT_HEAT, description=pointsDescription, win_condition=self.getClassRankMethodByName("Last_Heat_Position"))
        self.rh.api.ui.broadcast_raceclasses()
    #apply class defaults as well as appropriate stage attribute to each of the generated heats
    def applyPointsClassDefaults(self, args):
        generate_args = args.get("generate_args")
        generatorStageCount = int(generate_args.get(Formats.STAGE_COUNT_FIELD_NAME))
        available_seats = int(generate_args.get("available_seats"))
        classId = args.get("output_class_id")
        self.rh.log("apply stages...")
        rhapi = args.get("rhapi")

        #set the class ranking method to Total Stage Points
        pointsDescription = "Similar to Mario Kart, pilots earn points by setting the fastest time they can in each stage; 1pt for every competitor they beat. After each stage, the next stage is seeded based on pilots' total points, keeping rivals in the same heat. The pilot who earns the most points after all stages are complete wins.\nIMPORTANT: Please remember to seed all heats in the next stage after the current stage is complete."
        self.rh.api.db.raceclass_alter(classId, rounds=1, raceformat=self.getRaceFormatByName("First to 3 Laps"), heat_advance_type=HeatAdvanceType.NEXT_HEAT, description=pointsDescription, win_condition=self.getClassRankMethodByName("Total_Stage_Points"))

        self.rh.log(str(args))
        
        classHeats = self.rh.api.db.heats_by_class(classId)
        self.rh.log("class has "+str(len(classHeats))+" heats")
        totalPilots = len(self.getPilotsInClass(classId))
        heatsPerStage = math.ceil(totalPilots/available_seats)

        classHeatIndex = 0
        for stage in range(0,generatorStageCount):
            self.rh.log("- stage: "+str(stage))
            for stageHeatIndex in range(0,heatsPerStage):
                self.rh.log(" - stage heat index: "+str(stageHeatIndex))
                self.rh.log(" - class heat index: "+str(classHeatIndex))
                heat = classHeats[classHeatIndex]
                self.rh.log(" - setting heat "+str(heat.name)+" stage attr to "+str(stage+1))

                self.rh.api.db.heat_alter(heat.id, attributes={Formats.HEAT_STAGE_ATTR_NAME:int(stage+1)})
                classHeatIndex+=1
        self.rh.api.ui.broadcast_raceclasses()

    def generate_complete_handler(self, args):
        self.rh.log("generate points complete handler")
        self.rh.log(args)
        if(args["generator"]=="Street_League_Points"):
            self.applyPointsClassDefaults(args)
        if(args["generator"]=="Street_League_Elite_8"):
            self.applyElite8ClassDefaults(args)
        