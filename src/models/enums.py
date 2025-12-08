from enum import Enum


class EmotionName(str, Enum):
    HAPPY = "happy"
    CALM = "calm"
    EXCITED = "excited"
    PLAYFUL = "playful"
    NO_PROBLEM = "no_problem"
    ENCOURAGING = "encouraging"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    PROUD = "proud"
    IDLE = "idle"
    SAD = "sad"
    THATS_RIGHT = "thats_right"
    WORRY = "worry"
    THINKING = "thinking"


class CelebrateDecision(str, Enum):
    YES = "yes"
    NO = "no"

