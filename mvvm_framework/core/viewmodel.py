"""
ViewModel base class for MVVM framework.
Acts as an intermediary between Model and View.
"""

from typing import Any, Dict, Generic, Optional, Type, TypeVar
from PySide6.QtCore import QObject

from .observable import ObservableObject
from .model import Model


M = TypeVar('M', bound=Model)


class ViewModel(ObservableObject, Generic[M]):
    """
    Base class for ViewModels in the MVVM pattern.
    
    ViewModels expose data from models to views and handle UI logic.
    They implement commands that views can bind to for user actions.
    
    Example:
        class PersonViewModel(ViewModel[Person]):
            def __init__(self, model: Person):
                super().__init__()
                self._model = model
                self._save_command = Command(self.save)
            
            @property
            def name(self) -> str:
                return self._model.name
            
            @name.setter
            def name(self, value: str):
                if self._model.name != value:
                    self._model.name = value
                    self.notify_property_changed("name")
            
            @property
            def save_command(self) -> Command:
                return self._save_command
            
            def save(self):
                # Save logic here
                pass
    """
    
    def __init__(self, model: Optional[M] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._model = model
        self._commands: Dict[str, Any] = {}
        
        if model:
            # Bind to model property changes
            model.propertyChanged.connect(self._on_model_property_changed)
    
    @property
    def model(self) -> Optional[M]:
        """Get the underlying model."""
        return self._model
    
    @model.setter
    def model(self, value: M) -> None:
        """Set a new model."""
        if self._model:
            self._model.propertyChanged.disconnect(self._on_model_property_changed)
        
        self._model = value
        
        if self._model:
            self._model.propertyChanged.connect(self._on_model_property_changed)
    
    def _on_model_property_changed(self, property_name: str) -> None:
        """
        Handle property changes from the model.
        
        Args:
            property_name: Name of the changed property
        """
        # By default, propagate all model changes to the view
        self.notify_property_changed(property_name)
    
    def get_property(self, property_name: str) -> Any:
        """
        Get a property value from the model.
        
        Args:
            property_name: Name of the property
            
        Returns:
            The property value
        """
        if self._model and hasattr(self._model, property_name):
            return getattr(self._model, property_name)
        return None
    
    def set_property(self, property_name: str, value: Any) -> None:
        """
        Set a property value on the model.
        
        Args:
            property_name: Name of the property
            value: New value
        """
        if self._model and hasattr(self._model, property_name):
            setattr(self._model, property_name, value)
            self.notify_property_changed(property_name)
    
    def register_command(self, name: str, command: Any) -> None:
        """
        Register a command with the ViewModel.
        
        Args:
            name: Command name
            command: Command instance
        """
        self._commands[name] = command
    
    def get_command(self, name: str) -> Any:
        """
        Get a registered command.
        
        Args:
            name: Command name
            
        Returns:
            The command instance or None
        """
        return self._commands.get(name)
    
    def validate(self) -> bool:
        """
        Validate the underlying model.
        
        Returns:
            True if validation passes, False otherwise
        """
        if self._model:
            return self._model.validate()
        return True
    
    def has_errors(self) -> bool:
        """Check if the model has validation errors."""
        if self._model:
            return self._model.has_validation_errors()
        return False
    
    def get_errors(self) -> Dict[str, str]:
        """Get all validation errors from the model."""
        if self._model:
            return self._model.get_validation_errors()
        return {}
    
    def get_validation_error(self, property_name: str) -> Optional[str]:
        """
        Get validation error for a specific property.
        
        Args:
            property_name: Name of the property
            
        Returns:
            Error message or None if no error
        """
        if self._model and hasattr(self._model, 'get_validation_error'):
            return self._model.get_validation_error(property_name)
        # Fallback to get_errors()
        return self.get_errors().get(property_name)
    
    def refresh(self) -> None:
        """Refresh all properties by notifying changes."""
        if self._model:
            # Only iterate over instance attributes to avoid Qt internals
            for attr_name in vars(self._model):
                if not attr_name.startswith('_'):
                    self.notify_property_changed(attr_name)


def viewmodel_factory(model_class: Type[M]):
    """
    Decorator factory for creating ViewModel classes.
    
    Note: User-defined cls.__init__ implementations must use cooperative
    multiple-inheritance init by calling super().__init__(model, parent)
    so each __init__ in the MRO runs exactly once.
    
    Example:
        @viewmodel_factory(Person)
        class PersonViewModel:
            def __init__(self, model: Person, parent=None):
                super().__init__(model, parent)
                # ...
    """
    def decorator(cls):
        class GeneratedViewModel(cls, ViewModel[M]):
            def __init__(self, model: M, parent: Optional[QObject] = None):
                super().__init__(model, parent)
        
        return GeneratedViewModel
    
    return decorator
