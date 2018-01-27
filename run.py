import battlecode as bc
import random
import sys
import traceback
import time
import os
from copy import copy, deepcopy
from collections import deque
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
    for direct in random_directions:
        #print(str(unit.location.map_location().add(dir).clone()) + " ;P" )
        if unit.location.map_location().add(direct):
            loc = unit.location.map_location().add(direct)
        else:
            continue
        loc_map = gc.starting_map(loc.planet)

        if (loc.x < loc_map.width and loc.x >= 0 and loc.y < loc_map.height and loc.y >= 0
            and gc.is_occupiable(unit.location.map_location().add(direct))):
            #if gc.can_move(unit.id, dir) and gc.is_occupiable(unit.location.map_location().add(dir)):
            return direct
    return None

def worker_can_harvest(unit_id):
    for direct in directions:
        if gc.can_harvest(unit_id, direct):
             return direct
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

# Teams
my_team = gc.team()
enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
print("Enemey team: " + str(enemy_team))
# Keep the track of the number of units_earth we have

units_earth = {bc.UnitType.Worker: len(gc.my_units()), bc.UnitType.Factory: 0, bc.UnitType.Knight: 0,
         bc.UnitType.Ranger: 0, bc.UnitType.Mage: 0, bc.UnitType.Healer: 0, bc.UnitType.Rocket: 0}
# Hash table for unit missions
unit_mission = {}
print("Initial number of workers: " + str(units_earth[bc.UnitType.Worker]))

# Get the map of the Earth
loc_map = gc.starting_map(bc.Planet.Earth)

# Create a matrix for the Earth's terrain, 0 - passable, 1 - impassable
map_matrix = [[0]*loc_map.height for i in range(loc_map.width)]
print("WIDTH = " + str(loc_map.width))
print("HEIGHT = " + str(loc_map.height))
for x in range(loc_map.width):
    for y in range(loc_map.height):
        if loc_map.is_passable_terrain_at(bc.MapLocation(bc.Planet.Earth, x, y)):
            map_matrix[x][y] = 0
        else:
            map_matrix[x][y] = 1
#print("Map:")
#print(map_matrix)

# Current phase
phase = 0
built_rockets = 0
# phase 1 ends in round 94
'''
# Find an empty corner
distance = 0
for unit in gc.my_units():
    # Check each corner

'''

def worker_behaviour(unit):
    d = random.choice(directions)
    bot_can_harvest = worker_can_harvest(unit.id)
    bot_occupiable = find_occupiable(unit)

    if phase == 0:
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            print("Blueprint: Factory")
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)
            # Increase the number of known factories
            units_earth[bc.UnitType.Factory] += 1
        # replicate
        elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            print("Worker replicated!")
            gc.replicate(unit.id, bot_occupiable)
            # Increase the number of known workers
            units_earth[bc.UnitType.Worker] += 1
        # harvest
        elif bot_can_harvest:
            #print("Harvested")
            #print(gc.karbonite_at(unit.location.map_location().add(bot_can_harvest)))
            gc.harvest(unit.id, bot_can_harvest)
        # and if that fails, try to move
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            #print("Moved")
            gc.move_robot(unit.id, d)

    elif phase == 1:
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and bot_occupiable and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            print("Blueprint: Factory")
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)
            # Increase the number of known factories
            units_earth[bc.UnitType.Factory] += 1
        # harvest
        elif bot_can_harvest:
            #print("Harvested")
            #print(gc.karbonite_at(unit.location.map_location().add(bot_can_harvest)))
            gc.harvest(unit.id, bot_can_harvest)
        # and if that fails, try to move
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            #print("Moved")
            gc.move_robot(unit.id, d)
    elif phase == 2 or phase == 3 or phase > 4:
        # harvest
        if bot_can_harvest:
            #print("Harvested")
            #print(gc.karbonite_at(unit.location.map_location().add(bot_can_harvest)))
            gc.harvest(unit.id, bot_can_harvest)
        # and if that fails, try to move
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            #print("Moved")
            gc.move_robot(unit.id, d)
    elif phase == 4:
        if units_earth[bc.UnitType.Rocket] < 2 and gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and bot_occupiable and gc.can_blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable):
            print("Blueprint: Rocket")
            gc.blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable)
            # Increase the number of known rockets
            units_earth[bc.UnitType.Rocket] += 1
    # elif phase == 3:

    # first, let's look for nearby blueprints to work on
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units(location.map_location(), 2)
        for other in nearby:
            if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                gc.build(unit.id, other.id)
                #print('built a factory!')
                continue
    return

def factory_produce(unit, unit_type, bot_occupiable):
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        if bot_occupiable and gc.can_unload(unit.id, bot_occupiable):
            print('unloaded a unit!')
            gc.unload(unit.id, bot_occupiable)
    elif gc.can_produce_robot(unit.id, unit_type):
        gc.produce_robot(unit.id, unit_type)
        units_earth[unit_type] += 1
        print('produced a ' + str(unit_type))

def random_unit_type():
    unit_types = [bc.UnitType.Knight, bc.UnitType.Ranger, bc.UnitType.Mage, bc.UnitType.Healer]
    return random.choice(unit_types)

def number_of_units_all_types():
    return (units_earth[bc.UnitType.Knight] + units_earth[bc.UnitType.Ranger]
        + units_earth[bc.UnitType.Mage] +units_earth[bc.UnitType.Healer])

def factory_behaviour(unit):
    # first, factory logic
    bot_occupiable = find_occupiable(unit)
    if phase == 0:
        factory_produce(unit, bc.UnitType.Worker, bot_occupiable)
    elif phase == 1:
        factory_produce(unit, bc.UnitType.Knight, bot_occupiable)
    elif phase == 2:
        factory_produce(unit, bc.UnitType.Knight, bot_occupiable)
    elif phase == 3:
        factory_produce(unit, random_unit_type(), bot_occupiable)
    elif phase > 3:
        if gc.karbonite() >= 95:
            factory_produce(unit, random_unit_type(), bot_occupiable)
    # elif phase == 3:
    return

def knight_behaviour(unit):
    # Find an empty space
    bot_occupiable = find_occupiable(unit)

    if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
        gc.move_robot(unit.id, bot_occupiable)
    # Move
    if unit_mission[unit.id] and gc.is_move_ready(unit.id) and gc.can_move(unit.id, unit_mission[unit.id]):
        gc.move_robot(unit.id, unit_mission[unit.id])
    # Check whether there is something to attack
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
        for other in nearby:
            if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                print('Knight attacked a thing!')
                gc.attack(unit.id, other.id)
                continue
    return

def ranger_behaviour(unit):
    # Find an empty space
    bot_occupiable = find_occupiable(unit)

    if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
        gc.move_robot(unit.id, bot_occupiable)
    # Move
    if unit_mission[unit.id] and gc.is_move_ready(unit.id) and gc.can_move(unit.id, unit_mission[unit.id]):
        gc.move_robot(unit.id, unit_mission[unit.id])
    # Check whether there is something to attack
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 70, enemy_team)
        for other in nearby:
            if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                print('Ranger attacked a thing!')
                gc.attack(unit.id, other.id)
                continue
    return

def mage_behaviour(unit):
    # Find an empty space
    bot_occupiable = find_occupiable(unit)

    if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
        gc.move_robot(unit.id, bot_occupiable)
    # Move
    if unit_mission[unit.id] and gc.is_move_ready(unit.id) and gc.can_move(unit.id, unit_mission[unit.id]):
        gc.move_robot(unit.id, unit_mission[unit.id])
    # Check whether there is something to attack
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 30, enemy_team)
        for other in nearby:
            if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                print('Mage attacked a thing!')
                gc.attack(unit.id, other.id)
                continue
    return

def healer_behaviour(unit):
    # Find an empty space
    bot_occupiable = find_occupiable(unit)
    # Move
    if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
        gc.move_robot(unit.id, bot_occupiable)
    # Check whether there is something to attack
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, my_team)
        for other in nearby:
            if other.team == my_team and gc.is_heal_ready(unit.id) and gc.can_heal(unit.id, other.id):
                # print('Healed a thing!')
                gc.heal(unit.id, other.id)
                continue
    return

def rocket_behaviour(unit):
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 9, my_team)
        for other in nearby:
            if other.team == my_team and gc.can_load(unit.id, other.id):
                # print('Loaded a ' + other.unit_type + ' into rocket!')
                gc.load(unit.id, other.id)
                continue
    destination = rocket_destination(unit.id)
    if gc.can_launch_rocket(unit.id, destination) and (len(unit.structure_garrison()) >= 6 or gc.round() >= 400):
        gc.launch_rocket(unit.id, destination)
    if unit.location.map_location().planet == bc.Planet.Mars:
        bot_occupiable = find_occupiable(unit)
        if bot_occupiable:
            gc.unload(unit.id, find_occupiable(unit))
    return

def rocket_destination(unit_id):
    x = random.randint(0, gc.starting_map(bc.Planet.Mars).width)
    y = random.randint(0, gc.starting_map(bc.Planet.Mars).height)
    location = bc.MapLocation(bc.Planet.Mars, x, y)
    if gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(location):
        return bc.MapLocation(bc.Planet.Mars, x, y)
    else:
        return rocket_destination(unit_id)

# Modified BFS algorithm from http://compsci.ca/v3/viewtopic.php?t=32571
def BFS(x,y,planet,target_x,target_y):
    grid = deepcopy(map_matrix)
    queue = deque( [(x,y,None)]) #create queue
    while len(queue)>0: #make sure there are nodes to check left
        node = queue.popleft() #grab the first node
        x = node[0] #get x and y
        y = node[1]

        if not (x < gc.starting_map(planet).width and x >= 0 and y < gc.starting_map(planet).height and y >= 0):
            continue
        if x == target_x and y == target_y: #check if it's an exit
            return GetPathFromNodes(node) #if it is then return the path
        if grid[x][y] != 0 or not gc.starting_map(planet).is_passable_terrain_at(bc.MapLocation(planet, x, y)) or gc.sense_nearby_units(bc.MapLocation(planet, x, y), 1):
            continue
        grid[x][y]= 2 #make this spot explored so we don't try again
        for i in [[x+1, y+1], [x+1, y-1], [x-1, y-1], [x-1, y+1], [x-1, y], [x+1, y], [x, y-1], [x, y+1]]:
            queue.append((i[0],i[1],node))#create the new spot, with node as the parent
    return []

def GetPathFromNodes(node):
    path = []
    while(node != None):
        path.append((node[0],node[1]))
        node = node[2]
    return path

def switch_phase():
    global phase
    if phase == 0 and units_earth[bc.UnitType.Worker] > 7:
        print("Phase 1 starting")
        phase = 1
    elif phase == 1 and units_earth[bc.UnitType.Factory] >= 6:
        print("Phase 2 starting")
        phase = 2
    elif phase == 2 and units_earth[bc.UnitType.Knight] >= 10:
        print("Phase 3 starting")
        phase = 3
    elif phase == 3 and gc.round() > 300:
        print("Phase 4 starting")
        phase = 4
    elif phase == 4 and built_rockets >= 2:
        print("Phase 5 starting")
        phase = 5
    else:
        return

#print(BFS(0, 0, bc.Planet.Earth, 19, 19))
while True:
    # Phase logic
    switch_phase()
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        print("Money: " + str(gc.karbonite()))

        # Sense nearby units, every 5 rounds
        if(units_earth[bc.UnitType.Knight] > 0 and gc.round() % 10 == 0):
            enemy_vec = gc.sense_nearby_units_by_team(
                bc.MapLocation(bc.Planet.Earth, int(loc_map.width / 2), int(loc_map.height / 2)),loc_map.width * loc_map.width, enemy_team)
            #print("Enemies found: " + str(len(enemy_vec)))

        # walk through our units_earth:
        for unit in gc.my_units():

            if unit.unit_type == bc.UnitType.Worker:
                worker_behaviour(unit)
                continue
            elif unit.unit_type == bc.UnitType.Factory:
                factory_behaviour(unit)
                continue
            elif unit.unit_type == bc.UnitType.Rocket:
                rocket_behaviour(unit)
                if unit.health == 200:
                    built_rockets += 1
                    print("Rocket built")
                continue

            # Assign a target
            closest_enemy_dist = 99999
            closest_enemy_id = None
            direction = None

            if gc.round() % 10 == 0 and not unit.location.is_in_garrison():
                for enemy in enemy_vec:
                    if unit.location.map_location().planet == enemy.location.map_location().planet and unit.location.map_location().distance_squared_to(enemy.location.map_location()) <= closest_enemy_dist:
                        closest_enemy_dist = unit.location.map_location().distance_squared_to(enemy.location.map_location())
                        closest_enemy_id = enemy.id
                        #print(closest_enemy_dist)

                if closest_enemy_id:
                    path = BFS(unit.location.map_location().x, unit.location.map_location().y, unit.location.map_location().planet,
                                gc.unit(closest_enemy_id).location.map_location().x, gc.unit(closest_enemy_id).location.map_location().y)
                    if path:
                        cordinate = path[len(path) - 2]
                        unit_mission[unit.id] = unit.location.map_location().direction_to(bc.MapLocation(unit.location.map_location().planet, cordinate[0], cordinate[1]))
                    else:
                        unit_mission[unit.id] = None
                else:
                    unit_mission[unit.id] = None
            else:
                unit_mission[unit.id] = None

            if unit.unit_type == bc.UnitType.Knight:
                knight_behaviour(unit)
            elif unit.unit_type == bc.UnitType.Ranger:
                ranger_behaviour(unit)
            elif unit.unit_type == bc.UnitType.Mage:
                mage_behaviour(unit)
            elif unit.unit_type == bc.UnitType.Healer:
                healer_behaviour(unit)

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
