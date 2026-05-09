"""
MVVM Framework for PySide6
A general-purpose MVVM framework based on PySide6 property system
"""

from .core.observable import ObservableObject, ObservableList
from .core.model import Model
from .core.viewmodel import ViewModel
from .core.command import Command
from .core.binding import Binding

__all__ = [
    'ObservableObject',
    'ObservableList',
    'Model',
    'ViewModel',
    'Command',
    'Binding',
]

__version__ = '1.0.0'
