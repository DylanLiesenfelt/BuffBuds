from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

#---------------------------------------------
# Schemas for workout log - data validation
#---------------------------------------------

class Set(BaseModel):
    weight: float
    reps: int

    @field_validator("weight")
    def non_negative_weight(cls, v):
        if v < 0:
            raise ValueError("weight must be non-negative")
        return v

    @field_validator("reps")
    def positive_reps(cls, v):
        if v <= 0:
            raise ValueError("reps must be positive")
        return v


class Exercise(BaseModel):
    name: str
    type: str
    sets: List[Set]  # now a list of sets with reps/weight per set


class WorkoutPlan(BaseModel):
    name: str
    description: Optional[str]
    exercises: List[Exercise]


class WorkoutCreate(BaseModel):
    notes: Optional[str]
    total_volume: Optional[float] = 0.0
    workoutPlan: WorkoutPlan

