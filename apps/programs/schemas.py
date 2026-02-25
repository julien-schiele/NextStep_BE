from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field


# ----------------- Choices -----------------

PracticeZoneLiteral = Literal["everywhere", "climbing_gym"]
FocusLiteral = Literal["general_fitness", "climbing_performance"]

FocusAxisLiteral = Literal[
    "technical_bouldering",
    "project_bouldering",
    "route_technique",
    "movement_quality",
    "coordination",
    "footwork",
    "power",
    "max_strength",
    "power_endurance",
    "endurance_continuity",
    "climbing_volume",
    "finger_strength",
    "upper_body_strength",
    "core_tension",
    "lock_off_strength",
    "pulling_strength",
    "general_strength",
    "mobility",
    "stability",
    "balance",
    "conditioning",
    "active_recovery",
    "injury_prevention",
    "antagonist_training",
    "progressive_overload",
    "deload",
    "movement_efficiency",
]

LevelLiteral = Literal["beginner", "intermediate", "advanced"]


# ----------------- Core Schemas -----------------


class ExerciseProgression(BaseModel):
    increment: int
    per_cycle: int


class Repeat(BaseModel):
    cycles: int = 1
    progression: Optional[Dict[str, ExerciseProgression]] = Field(default_factory=dict)


class ExerciseItem(BaseModel):
    exercise: str
    value: float
    practice_zone: Optional[PracticeZoneLiteral] = (
        None  # obligatoire: everywhere/climbing_gym
    )


class Session(BaseModel):
    session: int
    focus: FocusLiteral
    sequences: List[List[ExerciseItem]]
    zone: Optional[PracticeZoneLiteral] = None  # fallback zone


class ProgramContent(BaseModel):
    version: int
    sessions: List[Session]
    repeat: Optional[Repeat] = Field(default_factory=Repeat)
