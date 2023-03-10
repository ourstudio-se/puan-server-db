
from typing import Callable, List, Optional
from dataclasses import dataclass
from pydantic import BaseSettings, Field
from logging import Logger

from app.services import CommitService

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class ServiceConfiguration(metaclass=Singleton):

    """
        A ServiceConfiguration holds services needed to run application.
    """
    commit_service: CommitService