from .RHmanager import RHmanager

#Logging
DEBUG_LOGGING = False

def initialize(rhapi):
    rotorhazard = RHmanager(rhapi, DEBUG_LOGGING)