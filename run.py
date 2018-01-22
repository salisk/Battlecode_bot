import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

def find_occupiable(unit):
    if unit.location.is_in_garrison():
        return None
    # Create a random order of directions
    random_directions = directions
    random.shuffle(random_directions)
    # Iterate through each direction
    for dir in random_directions:
        #print(str(unit.location.map_location().add(dir).clone()) + " ;P" )
        if unit.location.map_location().add(dir):
            loc = unit.location.map_location().add(dir)
        else:
            continue
        loc_map = gc.starting_map(loc.planet)

        if (loc.x < loc_map.width and loc.x >= 0 and loc.y < loc_map.height and loc.y >= 0
            and gc.is_occupiable(unit.location.map_location().add(dir))):
            #if gc.can_move(unit.id, dir) and gc.is_occupiable(unit.location.map_location().add(dir)):
            return dir
    return None

def worker_can_harvest(unit_id):
    for dir in directions:
         if gc.can_harvest(unit_id, dir):
             return dir
    return None

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
# Keep the track of the number of units we have
workers_num = len(gc.my_units())
factory_num = 0
print(workers_num)

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        print("Money: " + str(gc.karbonite()))
        # walk through our units:
        for unit in gc.my_units():

            d = random.choice(directions)
            bot_can_harvest = worker_can_harvest(unit.id)
            bot_occupiable = find_occupiable(unit)
            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    if bot_occupiable and gc.can_unload(unit.id, bot_occupiable):
                        print('unloaded a unit!')
                        gc.unload(unit.id, bot_occupiable)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Worker):
                    gc.produce_robot(unit.id, bc.UnitType.Worker)
                    print('produced a worker!')
                    continue

            else:
                # or, try to build a factory:
                if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
                    print("Blueprint")
                    gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)
                    # Increase number of known factories
                    factory_num = factory_num + 1
                # replicate
                elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
                    print("Worker replicated!")
                    gc.replicate(unit.id, bot_occupiable)
                # harvest
                elif bot_can_harvest:
                    #print("Harvested")
                    print(gc.karbonite_at(unit.location.map_location().add(bot_can_harvest)))
                    gc.harvest(unit.id, bot_can_harvest)
                # and if that fails, try to move
                elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                    print("Moved")
                    gc.move_robot(unit.id, d)

                # first, let's look for nearby blueprints to work on
                location = unit.location
                if location.is_on_map():
                    nearby = gc.sense_nearby_units(location.map_location(), 2)
                    for other in nearby:
                        if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                            gc.build(unit.id, other.id)
                            print('built a factory!')
                            # move onto the next unit
                            continue
                        if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                            print('attacked a thing!')
                            gc.attack(unit.id, other.id)
                            continue

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
