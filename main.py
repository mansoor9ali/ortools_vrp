#https://github.com/NVIDIA/cuOpt-Resources/blob/1314da8b4236afb5f8da9f7eb80fdd2622afebfa/notebooks/routing/managed_service/cpdptw-reoptmization.ipynb

cuopt_problem_data = {}

 # Processes input data, communicates data to cuOpt server and returns Optimized routes
def get_optimized_route(data):
    
    cuopt_problem_data = {"task_data":{},"fleet_data":{}}
    
    print(cuopt_problem_data)
    print("********************************************************************")
    # Set cost matrix
    if "cost_matrices" in data:
        cuopt_problem_data["cost_matrix_data"] = {
        "data": data["cost_matrices"]
    }
        
    
    # Set/Update Transit time matrix    
    if "transit_time_matrices" in data:
        cuopt_problem_data["travel_time_matrix_data"] = {
        "data": data["transit_time_matrices"]
    }
            
    print(cuopt_problem_data)
    print("********************************************************************")
    
    
    # Set/Update Task data
    if "task_locations" in data:
        cuopt_problem_data["task_data"]["task_locations"] = data["task_locations"]
        
    if "pickup_indices" in data and "delivery_indices" in data:
        cuopt_problem_data["task_data"]["pickup_and_delivery_pairs"] = [
            [pickup_idx, delivery_idx] for pickup_idx, delivery_idx in zip(
                data["pickup_indices"], data["delivery_indices"]
            )
        ]
    elif "pickup_indices" in data or "delivery_indices" in data:
        raise ValueError("Pick indices or Delivery indices are missing, both should be provided")
        
    print(data["pickup_indices"])
    print(data["delivery_indices"])
    print(cuopt_problem_data)
    print("********************************************************************")        
    
    if "task_earliest_time" in data and "task_latest_time" in data and "task_service_time" in data:
        cuopt_problem_data["task_data"]["task_time_windows"] = [
            [earliest, latest] for earliest, latest in zip(data["task_earliest_time"], data["task_latest_time"])
        ]
        cuopt_problem_data["task_data"]["service_times"] =  data["task_service_time"]
    elif "task_earliest_time" in data or "task_latest_time" in data or "task_service_time" in data:
        raise ValueError("Earliest, Latest and Service time should be provided, one or more are missing")
    
    print(cuopt_problem_data)
    print("********************************************************************")      
        
    if "demand" in data:
        cuopt_problem_data["task_data"]["demand"] = data["demand"]
    
    print(cuopt_problem_data)
    print("********************************************************************")    
    
    
    if "order_vehicle_match" in data:
        cuopt_problem_data["task_data"]["order_vehicle_match"] = data["order_vehicle_match"]

        
    # Set/Update Fleet data
    if "vehicle_locations" in data:
        cuopt_problem_data["fleet_data"]["vehicle_locations"] = data["vehicle_locations"]
        
    if "capacity" in data:
        cuopt_problem_data["fleet_data"]["capacities"] = data["capacity"]
        
    if "vehicle_earliest" in data and "vehicle_latest" in data:
        cuopt_problem_data["fleet_data"]["vehicle_time_windows"] = [
            [earliest, latest] for earliest, latest in zip(data["vehicle_earliest"], data["vehicle_latest"])
        ]
    elif "vehicle_earliest" in data or "vehicle_latest" in data:
        raise ValueError("vehicle_earliest and vehicle_latest both should be provided, one of them is missing")
       
    
    # Set Solver settings
    cuopt_problem_data["solver_config"] = {
        "time_limit": 5
    }  
    
    # Get optimized route
     
    return  cuopt_problem_data

# Input data - 1

input_data_1 = {}

input_data_1["cost_matrices"] = {0:[
    [0, 1, 2, 3, 4],
    [1, 0, 2, 3, 4],
    [2, 3, 0, 4, 1],
    [3, 4, 1, 0, 2],
    [4, 1, 2, 3, 0]
]}

input_data_1["transit_time_matrices"] = {0:[
    [0, 1, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 0, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 0]
]}
       
# Task data
input_data_1["task_locations"] = [1, 2, 3, 4, 3, 2, 1, 3]
input_data_1["pickup_indices"]   = [0, 2, 4, 6]
input_data_1["delivery_indices"] = [1, 3, 5, 7]
input_data_1["task_earliest_time"] = [0, 2, 1, 2, 0, 0,  2, 1]
input_data_1["task_latest_time"]   = [5, 4, 5, 5, 7, 7, 10, 9]
input_data_1["task_service_time"]  = [1, 1, 1, 1, 1, 1,  1, 1]
input_data_1["demand"] = [[1, -1, 1, -1, 1, -1, 1, -1]]

# Vehicle data
input_data_1["vehicle_locations"] = [[0, 0]] * 4 
input_data_1["vehicle_earliest"] = [0.0, 0.0,  2.0,  2.0]
input_data_1["vehicle_latest"]   = [8.0, 8.0, 15.0, 15.0]
input_data_1["capacity"] = [[3, 3, 3, 3]]

# Solve for optimized route
resp = get_optimized_route(input_data_1)
print(resp)
    