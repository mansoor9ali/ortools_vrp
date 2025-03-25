"""Vehicle Routing Problem (VRP) with Capacity Constraints."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt
import numpy as np

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    # Store locations in (x, y) coordinates
    data['locations'] = [
        (0, 0),     # depot
        (2, 4),     # customer 1
        (-3, 2),    # customer 2
        (4, -1),    # customer 3
        (-1, -3),   # customer 4
        (3, 5),     # customer 5
    ]
    
    # Add customer demands (package volumes)
    data['demands'] = [
        0,  # depot has no demand
        4,  # customer 1 demands 4 units
        3,  # customer 2 demands 3 units
        6,  # customer 3 demands 6 units
        2,  # customer 4 demands 2 units
        5,  # customer 5 demands 5 units
    ]
    
    # Time windows (in minutes) for each location
    data['time_windows'] = [
        (0, 120),    # depot
        (10, 30),    # customer 1
        (15, 45),    # customer 2
        (45, 75),    # customer 3
        (30, 60),    # customer 4
        (50, 80),    # customer 5
    ]
    
    data['num_vehicles'] = 2
    data['vehicle_capacities'] = [10, 15]  # Vehicle 0 can carry 10 units, Vehicle 1 can carry 15 units
    data['depot'] = 0
    data['vehicle_speed'] = 1  # units per minute
    data['time_per_stop'] = 10  # minutes per delivery
    return data


def compute_manhattan_distance(position_1, position_2):
    """Computes the Manhattan distance between two points."""
    return abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1])


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    
    # Get problem dimensions
    time_dimension = routing.GetDimensionOrDie('Time')
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    total_time = 0
    total_load = 0
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Route for vehicle {vehicle_id}:\n'
        route_time = 0
        route_load = 0
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            load_var = capacity_dimension.CumulVar(index)
            
            # Get the time window for this location
            time_min, time_max = data['time_windows'][node]
            
            # Add location and time information
            plan_output += f' Location {node}'
            plan_output += f' Load({solution.Value(load_var)})'
            plan_output += f' Time({solution.Min(time_var)},{solution.Max(time_var)})'
            plan_output += f' Window({time_min},{time_max})\n'
            
            route_load = solution.Value(load_var)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # End location
        node = manager.IndexToNode(index)
        time_var = time_dimension.CumulVar(index)
        load_var = capacity_dimension.CumulVar(index)
        
        plan_output += f' Location {node}'
        plan_output += f' Load({solution.Value(load_var)})'
        plan_output += f' Time({solution.Min(time_var)},{solution.Max(time_var)})\n'
        
        plan_output += f'Time of the route: {route_time}min\n'
        plan_output += f'Load of the route: {route_load}\n'
        print(plan_output)
        
        total_time += route_time
        total_load += route_load
        
    print(f'Total time of all routes: {total_time}min')
    print(f'Total load of all routes: {total_load}')


def plot_locations(locations, demands, time_windows, title="Delivery Locations"):
    """Plot the locations on a 2D map with demand information."""
    locations = np.array(locations)
    plt.figure(figsize=(10, 10))
    
    # Plot depot in red
    plt.plot(locations[0, 0], locations[0, 1], 'rs', markersize=15, label='Depot')
    
    # Plot other locations in blue
    plt.plot(locations[1:, 0], locations[1:, 1], 'bo', markersize=10, label='Customers')
    
    # Add location labels with demands
    for i, (x, y) in enumerate(locations):
        plt.annotate(f'Location {i}\nDemand: {demands[i]}\n{time_windows[i]}', (x, y), 
                    xytext=(10, 10), textcoords='offset points')
    
    plt.grid(True)
    plt.legend()
    plt.title(title)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    return plt.gcf()


def plot_solution(data, manager, routing, solution):
    """Plots the solution on a 2D map."""
    locations = np.array(data['locations'])
    demands = data['demands']
    plt.figure(figsize=(10, 10))
    
    # Plot depot in red
    plt.plot(locations[0, 0], locations[0, 1], 'rs', markersize=15, label='Depot')
    
    # Plot other locations in blue
    plt.plot(locations[1:, 0], locations[1:, 1], 'bo', markersize=10, label='Customers')
    
    # Get capacity dimension
    capacity_dimension = routing.GetDimensionOrDie('Capacity')
    
    # Plot routes for each vehicle with different colors
    colors = ['g-', 'm-', 'c-', 'y-', 'b-']  # Add more colors if needed
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        route_loads = []
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            load_var = capacity_dimension.CumulVar(index)
            route.append(locations[node])
            route_loads.append(solution.Value(load_var))
            index = solution.Value(routing.NextVar(index))
            
        node = manager.IndexToNode(index)
        load_var = capacity_dimension.CumulVar(index)
        route.append(locations[node])
        route_loads.append(solution.Value(load_var))
        route = np.array(route)
        
        # Plot the route
        plt.plot(route[:, 0], route[:, 1], colors[vehicle_id % len(colors)], 
                linewidth=2, label=f'Route {vehicle_id} (Cap: {data["vehicle_capacities"][vehicle_id]})')
    
    # Add location labels with demands
    for i, (x, y) in enumerate(locations):
        plt.annotate(f'Location {i}\nDemand: {demands[i]}\n{data["time_windows"][i]}', (x, y), 
                    xytext=(10, 10), textcoords='offset points')
    
    plt.grid(True)
    plt.legend()
    plt.title('Vehicle Routes with Capacity Constraints')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    return plt.gcf()


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Plot initial locations
    initial_plot = plot_locations(data['locations'], data['demands'], data['time_windows'])
    initial_plot.savefig('2-initial_locations_capacity.png')
    plt.close()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['locations']),
        data['num_vehicles'],
        data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return compute_manhattan_distance(
            data['locations'][from_node], data['locations'][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Add Time Windows constraint.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Get the distance between the two locations
        travel_time = compute_manhattan_distance(
            data['locations'][from_node], data['locations'][to_node])
        # Convert to travel time based on vehicle speed
        travel_time = travel_time / data['vehicle_speed']
        # Add service time at delivery location
        if to_node != data['depot']:
            travel_time += data['time_per_stop']
        return travel_time

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    dimension_name = 'Time'
    routing.AddDimension(
        time_callback_index,
        30,  # allow waiting time
        120,  # maximum time per vehicle
        False,  # Don't force start cumul to zero
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    depot_idx = data['depot']
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
        # Plot the solution
        solution_plot = plot_solution(data, manager, routing, solution)
        solution_plot.savefig('2-solution_routes_capacity.png')
        plt.close()
    else:
        print('No solution found!')


if __name__ == '__main__':
    main()
