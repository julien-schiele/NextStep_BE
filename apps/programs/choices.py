from django.db import models
from django.utils.translation import gettext_lazy as _


class Resolution(models.TextChoices):
    REPETITION = "repetition", _("Repetition")
    DURATION = "duration", _("Duration")


class PracticeZone(models.TextChoices):
    EVERYWHERE = "everywhere", _("Everywhere")
    CLIMBING_GYM = "climbing_gym", _("Climbing Gym")


class Focus(models.TextChoices):
    GENERAL_FITNESS = "general_fitness", _("General fitness")
    CLIMBING_PERFORMANCE = "climbing_performance", _("Climbing performance")


class Level(models.TextChoices):
    BEGINNER = "beginner", _("Beginner")
    INTERMEDIATE = "intermediate", _("Intermediate")
    ADVANCED = "advanced", _("Advanced")


class FocusAxis(models.TextChoices):
    # Climbing – Technique / Tactics
    TECHNICAL_BOULDERING = "technical_bouldering", _("Technical bouldering")
    PROJECT_BOULDERING = "project_bouldering", _("Project bouldering")
    ROUTE_TECHNIQUE = "route_technique", _("Route technique")
    MOVEMENT_QUALITY = "movement_quality", _("Movement quality")
    COORDINATION = "coordination", _("Coordination")
    FOOTWORK = "footwork", _("Footwork")

    # Climbing – Performance
    POWER = "power", _("Power")
    MAX_STRENGTH = "max_strength", _("Max strength")
    POWER_ENDURANCE = "power_endurance", _("Power endurance")
    ENDURANCE_CONTINUITY = "endurance_continuity", _("Endurance / continuity")
    CLIMBING_VOLUME = "climbing_volume", _("Climbing volume")

    # Specific training
    FINGER_STRENGTH = "finger_strength", _("Finger strength")
    UPPER_BODY_STRENGTH = "upper_body_strength", _("Upper body strength")
    CORE_TENSION = "core_tension", _("Core tension")
    LOCK_OFF_STRENGTH = "lock_off_strength", _("Lock-off strength")
    PULLING_STRENGTH = "pulling_strength", _("Pulling strength")

    # GPP
    GENERAL_STRENGTH = "general_strength", _("General strength")
    MOBILITY = "mobility", _("Mobility")
    STABILITY = "stability", _("Stability")
    BALANCE = "balance", _("Balance")
    CONDITIONING = "conditioning", _("Conditioning")

    # Recovery / Health
    ACTIVE_RECOVERY = "active_recovery", _("Active recovery")
    INJURY_PREVENTION = "injury_prevention", _("Injury prevention")
    ANTAGONIST_TRAINING = "antagonist_training", _("Antagonist training")

    # Methodology
    PROGRESSIVE_OVERLOAD = "progressive_overload", _("Progressive overload")
    DELOAD = "deload", _("Deload / recovery")
    MOVEMENT_EFFICIENCY = "movement_efficiency", _("Movement efficiency")
