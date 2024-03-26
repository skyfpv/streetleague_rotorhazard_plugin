# streetleague_rotorhazard_plugin
This plugin adds a heat generator for the Street League points format. It also adds a ranking method called Total Stage Points. Currently, it requires that you be on the main branch of RotorHazard core.

## how the points format works
Similar to Mario Kart, pilots earn points by setting the fastest time they can in each stage; 1pt for every competitor they beat. After each stage, the next stage is seeded based on pilots' total points, keeping rivals in the same heat. The pilot who earns the most points after all stages are complete wins.

***IMPORTANT***: Please remember to seed all heats in the next stage once the current stage is complete. Otherwise, some pilots may be skipped.

**screenshot**
![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/15ac967e-3c79-41d2-9cf5-cb511bc29816)


## Known issues
https://github.com/RotorHazard/RotorHazard/issues/882

### workaround
make the following changes to RotorHazard core
### addition to RHData.py (line 114)
    def merge(self, obj):
        try:
            Database.DB_session.merge(obj)
            return True
        except Exception as ex:
            logger.error('Error writing to database: ' + str(ex))
            return False

### replace heat_automation.py (line 149-154)
            logger.debug('Slot {} Pilot is {}'.format(slot.id, slot.pilot_id if slot.pilot_id else None))

        self._racecontext.rhdata.commit()
        return result

### with
            logger.debug('Slot {} Pilot is {}'.format(slot.id, slot.pilot_id if slot.pilot_id else None))
            self._racecontext.rhdata.merge(slot)
            self._racecontext.rhdata.commit()        
        return result
