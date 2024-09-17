from .RHmanager import RHmanager

#Logging
DEBUG_LOGGING = True

def initialize(rhapi):
    rotorhazard = RHmanager(rhapi, DEBUG_LOGGING)