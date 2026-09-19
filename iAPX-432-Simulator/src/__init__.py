"""
Intel iAPX 432 Educational Simulator

A simplified educational simulator of the Intel iAPX 432
General Data Processor (GDP), implementing core concepts
of capability-based security and object-oriented hardware.
"""

__version__ = "1.0.0"
__author__ = "UntestedFeasibility"

from .cpu import CPU
from .memory import Memory
from .decoder import InstructionDecoder
from .execution import ExecutionUnit
from .objects import AccessDescriptor, Domain, Context
from .capabilities import CapabilityChecker
from .simulator import Simulator

__all__ = [
    'CPU',
    'Memory',
    'InstructionDecoder',
    'ExecutionUnit',
    'AccessDescriptor',
    'Domain',
    'Context',
    'CapabilityChecker',
    'Simulator',
]
