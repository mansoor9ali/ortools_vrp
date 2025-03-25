"""Vehicle Routing Problem (VRP) with Multiple Depots."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt
import numpy as np

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    # Store locations in (x, y) coordinates
    data['locations'] = [
        (0, 0),     # depot 1
        (8, 4),     # depot 2
        (2, 4),     # customer 1
        (-3, 2),    # customer 2
        (4, -1),    # customer 3
        (-1, -3),   # customer 4
        (3, 5),     # customer 5
        (5, -2),    # customer 6
        (-2, 6),    # customer 7
        (7, 1),     # customer 8
    ]
    
    # Define which locations are depots
    data['depots'] = [0, 1]  # Locations 0 and 1 are depots
    
    # Define vehicle start and end depots
    data['starts'] = [0, 0, 1]  # Vehicles 0 and 1 start at depot 0, Vehicle 2 starts at depot 1
    data['ends'] = [0, 0, 1]    # Vehicles return to their starting depots
    
    # Time windows (in minutes) for each location
    data['time_windows'] = [
        (0, 120),    # depot 1
        (0, 120),    # depot 2
        (10, 30),    # customer 1
        (15, 45),    # customer 2
        (45, 75),    # customer 3
        (30, 60),    # customer 4
        (50, 80),    # customer 5
        (10, 40),    # customer 6
        (35, 65),    # customer 7
        (20, 50),    # customer 8
    ]
    
    data['num_vehicles'] = 3
    data['vehicle_speed'] = 1  # units per minute
    data['time_per_stop'] = 10  # minutes per delivery
    return data


def compute_manhattan_distance(position_1, position_2):
    """Computes the Manhattan distance between two points."""
    return abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1])


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        start_depot = manager.IndexToNode(index)
        plan_output = f'Route for vehicle {vehicle_id} starting at depot {start_depot}:\n'
        route_time = 0
        
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node = manager.IndexToNode(index)
            
            # Get the time window for this location
            time_min, time_max = data['time_windows'][node]
            
            plan_output += f' Location {node}'
            plan_output += f' Time({solution.Min(time_var)},{solution.Max(time_var)})'
            plan_output += f' Window({time_min},{time_max})\n'
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        time_var = time_dimension.CumulVar(index)
        node = manager.IndexToNode(index)
        plan_output += f' Location {node} (depot)'
        plan_output += f' Time({solution.Min(time_var)},{solution.Max(time_var)})\n'
        plan_output += f'Time of the route: {route_time}min\n'
        print(plan_output)
        total_time += route_time
    print(f'Total time of all routes: {total_time}min')


def plot_locations(locations, depots, time_windows, title="Delivery Locations with Multiple Depots"):
    """Plot the locations on a 2D map."""
    locations = np.array(locations)
    plt.figure(figsize=(12, 12))
    
    # Plot depots in red with different shapes
    depot_markers = ['rs', 'r^', 'rd']  # square, triangle, diamond
    for i, depot_idx in enumerate(depots):
        plt.plot(locations[depot_idx, 0], locations[depot_idx, 1], 
                 depot_markers[i % len(depot_markers)], markersize=15, 
                 label=f'Depot {depot_idx}')
    
    # Plot customers in blue
    customer_indices = [i for i in range(len(locations)) if i not in depots]
    customer_locations = locations[customer_indices]
    plt.plot(customer_locations[:, 0], customer_locations[:, 1], 'bo', markersize=10, label='Customers')
    
    # Add location labels
    for i, (x, y) in enumerate(locations):
        marker_text = f'Depot {i}' if i in depots else f'Cust {i}'
        plt.annotate(f'{marker_text}\n{time_windows[i]}', (x, y), 
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
    plt.figure(figsize=(12, 12))
    
    # Plot depots in red with different shapes
    depot_markers = ['rs', 'r^', 'rd']  # square, triangle, diamond
    for i, depot_idx in enumerate(data['depots']):
        plt.plot(locations[depot_idx, 0], locations[depot_idx, 1], 
                 depot_markers[i % len(depot_markers)], markersize=15, 
                 label=f'Depot {depot_idx}')
    
    # Plot customers in blue
    customer_indices = [i for i in range(len(locations)) if i not in data['depots']]
    customer_locations = locations[customer_indices]
    plt.plot(customer_locations[:, 0], customer_locations[:, 1], 'bo', markersize=10, label='Customers')
    
    # Plot routes for each vehicle with different colors
    colors = ['g-', 'm-', 'c-', 'y-', 'b-', 'k-']  # Add more colors if needed
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        start_node = manager.IndexToNode(index)
        route = []
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(locations[node])
            index = solution.Value(routing.NextVar(index))
            
        node = manager.IndexToNode(index)
        route.append(locations[node])
        route = np.array(route)
        
        # Plot the route
        plt.plot(route[:, 0], route[:, 1], colors[vehicle_id % len(colors)], 
                linewidth=2, label=f'Route {vehicle_id} (Depot {start_node})')
    
    # Add location labels
    for i, (x, y) in enumerate(locations):
        marker_text = f'Depot {i}' if i in data['depots'] else f'Cust {i}'
        plt.annotate(f'{marker_text}\n{data["time_windows"][i]}', (x, y), 
                    xytext=(10, 10), textcoords='offset points')
    
    plt.grid(True)
    plt.legend()
    plt.title('Vehicle Routes with Multiple Depots')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    return plt.gcf()


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Plot initial locations
    initial_plot = plot_locations(data['locations'], data['depots'], data['time_windows'])
    initial_plot.savefig('3-initial_locations_multi_depot.png')
    plt.close()

    # Create the routing index manager.
    # Use IndexManager for multiple depots with explicit start/end locations
    manager = pywrapcp.RoutingIndexManager(
        len(data['locations']),
        data['num_vehicles'],
        data['starts'],
        data['ends'])

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
        if to_node not in data['depots']:
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

    # Add time window constraints for each location except depots.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx in data['depots']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        start_depot = data['starts'][vehicle_id]
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][start_depot][0],
            data['time_windows'][start_depot][1])

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
        solution_plot.savefig('3-solution_routes_multi_depot.png')
        plt.close()
    else:
        print('No solution found!')


if __name__ == '__main__':
    main()
