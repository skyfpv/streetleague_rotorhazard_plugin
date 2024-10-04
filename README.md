# Street League RotorHazard Plugin
This plugin adds a heat generator for the Street League points format. It also adds a ranking method called Total Stage Points.

## How Points Format Works
Similar to Mario Kart, pilots earn points by setting the fastest time they can in each stage; 1pt for every competitor they beat. After each stage, the next stage is seeded based on pilots' total points, keeping rivals in the same heat. The pilot who earns the most points after all stages are complete wins.

## Installation Instructions
1. ssh into your rotorhazard

    ```ssh pi@YOUR_ROTORHAZARD_IP_ADDRESS```
2. Navigate to the plugins directory

    ```cd RotorHazard/src/server/plugins/```
4. Download/Update the plugin
    - If you are updating run

        ```rm -rf streetleague_rotorhazard_plugin```
    - Download the latest plugin

        ```sudo git clone https://github.com/skyfpv/streetleague_rotorhazard_plugin.git```

5. Restart your rotorhazard

    ```sudo reboot now```
7. Verify plugin installation
    - Navigate to rotorhazard.local/settings > plugins
    - You should see
  ![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/e5f5ea00-088d-48cc-a76e-dd0023c7f405)


## Setup A Race

### Generate Heats
***Format > Generators***

- Once you've added all of your pilots, start by selecting "Street League Points" for your generator.
- If you've already run qualifying you can use that class as your input.
- There's no need to select an output class.
- Hit generate and select how many stages you would like to run. Each stage means 1 pack for your pilots. If you aren't sure how much time you'll have, air on the side of having too many rounds. You can always delete stages later.
![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/09dedc1b-4404-4cbe-acf1-f15de9d7c420)


- You should now see your new class under ***Format > Classes and Heats***
![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/d68d6669-6356-4313-ae5f-f15a9a4bbb2b)

### Run Stages
- Start by running all of the heats in stage 1. Typically you'll want to run Heat A last since it's easy to remember that the fastest pilots race last.
- Once all heats in stage 1 are complete, it's time to seed stage 2. This will place pilots in heats with their closest rivals based on the current race standings (more on that later).
  - If you want to reduice the number of channel changes that occur during your event, you can seed multiple stages at a time. But typically it's fun for pilots to always be racing their rivals
***IMPORTANT***: Please remember to seed all heats in the stage before running the first heat. Otherwise, some pilots may be skipped.
- Rinse and repeat. Keep seeding and then running stages until you've finish the last stage

***E.G. Stage 2 is complete. Time to seed all the heats for Stage 3***
![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/4b3a0e23-d8db-4624-8ff1-9e84cdd166c2)


# Results
- As stages are completed, pilots will earn points for each stage based on their stage time (relavitve to all the pilots in that stage)
- Those stage points add up to equal their total score

***E.G. 4 stages have been run so far. Callsign 11 is in the lead with 37 points.
![image](https://github.com/skyfpv/streetleague_rotorhazard_plugin/assets/45609851/15ac967e-3c79-41d2-9cf5-cb511bc29816)
