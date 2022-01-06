from enum import Enum


class GenericGameStateEnum(Enum):
    undefined = -1
    running = 0
    won = 1
    lost = 2
