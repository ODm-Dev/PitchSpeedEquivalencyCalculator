import numpy as np

def calculate_reaction_time(speed, distance):
    """Calculate reaction time given speed (mph) and distance (ft)"""
    # Convert mph to ft/s (1 mph = 1.467 ft/s)
    speed_ft_per_sec = speed * 1.467
    return distance / speed_ft_per_sec

def calculate_equivalent_speeds(target_time, distances):
    """Calculate speeds that produce the same reaction time at different distances"""
    # Convert back to mph from ft/s
    return (distances / target_time) / 1.467

def generate_distance_range():
    """Generate distance range from 15ft to 60.5ft in 0.5ft increments"""
    return np.arange(15, 61, 0.5)

def validate_inputs(speed, distance):
    """Validate user inputs"""
    errors = []
    
    if not isinstance(speed, (int, float)) or speed <= 0:
        errors.append("Speed must be a positive number")
    
    if not isinstance(distance, (int, float)) or distance < 15 or distance > 60.5:
        errors.append("Distance must be between 15 and 60.5 feet")
        
    return errors
