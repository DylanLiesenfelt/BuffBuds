from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

#---------------------------------------------
# Schemas for workout log - data validation
#---------------------------------------------
class Exercise(BaseModel):
    name: str
    type: str
    sets: int
    reps: int
    exercise_weight: float

    @field_validator('sets', 'reps')
    # where cls is the class and v is the value
    def positive_int(cls, v):
        if v <= 0:
            raise ValueError('must be positive')
        return v

    @field_validator('exercise_weight')
    def non_negative_weight(cls, v):
        if v < 0:
            raise ValueError('must be non-negative')
        return v

class WorkoutPlan(BaseModel):
    name: str
    description: Optional[str]
    exercises: List[Exercise]

class WorkoutCreate(BaseModel):
    session_date: str
    notes: Optional[str]
    workoutPlan: WorkoutPlan

    @field_validator('session_date')
    def valid_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d") # can be changed to whatever date format
        except ValueError:
            raise ValueError('date must be in YYYY-MM-DD format')
        return v