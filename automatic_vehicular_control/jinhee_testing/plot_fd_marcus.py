import os
import traci
import matplotlib.pyplot as plt
import sys

# or "sumo-gui"
sumo_binary = "sumo"

# params
circumference = 1000.2
half_circumference = circumference / 2  # 
simulation_time = 500
warmup_time = 200
vehicle_numbers = range(3, 138, 8)

# results
densities = []
flows = []
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

def run_simulation(vehicle_count):
    config_path = os.path.abspath('circles.sumocfg')

    traci.start([sumo_binary, "-c", config_path, "--step-length", "1"])
    #total_length = sum(traci.lane.getLength(edge_id + "_0") for edge_id in traci.edge.getIDList())
    # passed_vehicles = []

    # add vehicles and place them
    for i in range(vehicle_count):
        vehicle_id = f"car_{i}"

        # find position to place them
        d = (circumference / vehicle_count)
        if d <= 5:
            break
        # depart_position = (i * (circumference / vehicle_count)) % circumference
        depart_position = i * d
        # on edge 1
        if depart_position < half_circumference:
            route_id = "ring_route"
            traci.vehicle.add(vehicle_id, route_id, depart="0", departPos=depart_position, departSpeed = 0)
        # on edge 2
        else:
            route_id = "ring_route2"
            depart_position = depart_position - half_circumference
            traci.vehicle.add(vehicle_id, route_id, depart="0", departPos=depart_position, departSpeed = 0)

        # start with all vehicles stopped
        traci.vehicle.setSpeed(vehicle_id, 0) 

    # let vehicles be placed
    for _ in range(10):
        traci.simulationStep()

    #start all vehicles
    for i in range(vehicle_count):
        vehicle_id = f"car_{i}"
        traci.vehicle.setSpeed(vehicle_id, -1)  # speed is -1 for SUMO starting control

    # warm-up time
    for i in range(warmup_time):
        traci.simulationStep()

    # calculating density and flow
    step = 0
    # last_vehicle = ""

    average_speed_list = []
    while step < simulation_time:
        traci.simulationStep() 
        step += 1
        average_speed_list.append(sum(traci.vehicle.getSpeed(id) for id in traci.vehicle.getIDList()) / vehicle_count)
        
        # get vehicle IDs that are currently on the "left" edge and add them to the set
        # vehicle_ids_on_left = traci.edge.getLastStepVehicleIDs("left")

        # # if new vehicle on left edge, add to detected; won't work when vehicle_numbers is 1
        # if len(vehicle_ids_on_left) != 0:     
        #     if vehicle_ids_on_left[0] != last_vehicle:
        #         last_vehicle = vehicle_ids_on_left[0]
        #         passed_vehicles.append(last_vehicle)

    traci.close()

    # calculate density
    density = vehicle_count / (circumference / 1000)  # in vehicles per kilometer
    # calculate avg speed
    v = sum(average_speed_list) / len(average_speed_list) #km / hour

    # calculate flow
    flow = density * v
    
    return density, flow

# test with diff number of vehicles
run_simulation(25)
for n_vehicles in vehicle_numbers:
    density, flow = run_simulation(n_vehicles)
    densities.append(density)
    flows.append(flow)

# fundamental diagram plotting
plt.figure(figsize=(8, 6))
plt.plot(densities, flows, '-o')
plt.xlabel('Density (vehicles per kilometer)')
plt.ylabel('Flow (vehicles per hour)')
plt.title('Fundamental Diagram for Ring Road')
plt.grid(True)
plt.show()
