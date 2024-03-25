# streetleague_rotorhazard_plugin

Requires the following additions to RotorHazard core (otherwise seeding wont work)
# addition to RHData.py (line 114)
    def merge(self, obj):
        try:
            Database.DB_session.merge(obj)
            return True
        except Exception as ex:
            logger.error('Error writing to database: ' + str(ex))
            return False

# replace heat_automation.py (line 149-154)
                    logger.debug("Ignoring null class as seed source")

            logger.debug('Slot {} Pilot is {}'.format(slot.id, slot.pilot_id if slot.pilot_id else None))

        self._racecontext.rhdata.commit()
        return result

# with
                    logger.debug("Ignoring null class as seed source")
            self._racecontext.rhdata.merge(slot)
            self._racecontext.rhdata.commit()
            logger.debug('Slot {} Pilot is {}'.format(slot.id, slot.pilot_id if slot.pilot_id else None))
        
        return result

See https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#merging for why this is necessary. 
