import json
import random
import os

# ------------------------------
# Automatic Workout Generator
# ------------------------------

def load_exercises(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        return json.load(f)

def generate_workout(day: str, exercises_data: dict) -> dict:
    """
    current workout days: 'push', 'pull', 'legs', or 'push_pull'
    
    generator function: will select at random 2 compound, 2 functional,
                        and 3 isolated exercises to complete a simple full
                        body workout. Logic can be changed to include or remove
                        to create a different workout design. 

    future additions: 
        1. cardio/stretching addition to complete workout
        2. ability to customize the ratio of compound, func, iso exercises
        3. limitations to the list (preference/injury measures)
        4. user added exercises
     """
    
    # handles the combination of push pull
    if day == 'push_pull':
        # generate both push and pull workouts
        push_cat = exercises_data['exercises']['push_pull_split']['push_day']
        pull_cat = exercises_data['exercises']['push_pull_split']['pull_day']

        push_workout = {
            "day": "push_day",
            "exercises": {
                "compound": random.sample(push_cat["compound"], 2),
                "functional": random.sample(push_cat["functional"], 2),
                "isolated": random.sample(push_cat["isolated"], 3)
            }
        }

        pull_workout = {
            "day": "pull_day",
            "exercises": {
                "compound": random.sample(pull_cat["compound"], 2),
                "functional": random.sample(pull_cat["functional"], 2),
                "isolated": random.sample(pull_cat["isolated"], 3)
            }
        }

        return {
            "push_day": push_workout,
            "pull_day": pull_workout
        }

    # creates the workouts for push, pull, legs
    else:
        category = exercises_data['exercises'][day]
        workout = {
            "day": day,
            "exercises": {
                "compound": random.sample(category["compound"], 2),
                "functional": random.sample(category["functional"], 2),
                "isolated": random.sample(category["isolated"], 3)
            }
        }
        return workout


# load JSON file
base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'workout_gen_data.json')
exercises_data = load_exercises(json_path)

# uncomment for testing:
'''
print("Push workout:")
print(generate_workout('push', exercises_data))

print("\nPull workout:")
print(generate_workout('pull', exercises_data))

print("\nLegs workout:")
print(generate_workout('legs', exercises_data))

print("\nPush/Pull workout:")
print(generate_workout('push_pull', exercises_data))
'''