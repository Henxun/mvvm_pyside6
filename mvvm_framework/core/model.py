"""
Model base class for MVVM framework.
Represents the data layer of the application.
"""

from typing import Any, Dict, Optional
from PySide6.QtCore import QObject

from .observable import ObservableObject


class Model(ObservableObject):
    """
    Base class for models in the MVVM pattern.
    
    Models represent the data and business logic of the application.
    They should be independent of the UI and contain only data-related logic.
    
    Example:
        class Person(Model):
            def __init__(self, name: str = "", age: int = 0):
                super().__init__()
                self._name = name
                self._age = age
            
            @property
            def name(self) -> str:
                return self._name
            
            @name.setter
            def name(self, value: str):
                if self._name != value:
                    self._name = value
                    self.notify_property_changed("name")
            
            @property
            def age(self) -> int:
                return self._age
            
            @age.setter
            def age(self, value: int):
                if self._age != value:
                    self._age = value
                    self.notify_property_changed("age")
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._validation_errors: Dict[str, str] = {}
    
    def validate(self, property_name: Optional[str] = None) -> bool:
        """
        Validate the model or a specific property.
        
        Args:
            property_name: Specific property to validate, or None for all
            
        Returns:
            True if validation passes, False otherwise
        """
        if property_name:
            # Clear existing error for this property
            self._validation_errors.pop(property_name, None)
            
            # Call specific validator if it exists
            validator_name = f"validate_{property_name}"
            if hasattr(self, validator_name):
                validator = getattr(self, validator_name)
                error = validator(getattr(self, property_name))
                if error:
                    self._validation_errors[property_name] = error
                    return False
            
            return len(self._validation_errors) == 0
        else:
            # Validate all properties
            self._validation_errors.clear()
            
            # Find all validator methods
            for attr_name in dir(self):
                if attr_name.startswith("validate_"):
                    prop_name = attr_name[9:]  # Remove "validate_" prefix
                    if hasattr(self, prop_name):
                        validator = getattr(self, attr_name)
                        value = getattr(self, prop_name)
                        error = validator(value)
                        if error:
                            self._validation_errors[prop_name] = error
            
            return len(self._validation_errors) == 0
    
    def get_validation_error(self, property_name: str) -> Optional[str]:
        """
        Get validation error for a specific property.
        
        Args:
            property_name: Name of the property
            
        Returns:
            Error message or None if no error
        """
        return self._validation_errors.get(property_name)
    
    def has_validation_errors(self) -> bool:
        """Check if the model has any validation errors."""
        return len(self._validation_errors) > 0
    
    def get_validation_errors(self) -> Dict[str, str]:
        """Get all validation errors."""
        return self._validation_errors.copy()
    
    def clear_validation_errors(self) -> None:
        """Clear all validation errors."""
        self._validation_errors.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                attr = getattr(self, attr_name)
                if not isinstance(attr, (classmethod, staticmethod)):
                    result[attr_name] = attr
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            New model instance
        """
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance
    
    def update(self, other: 'Model') -> None:
        """
        Update this model with values from another model.
        
        Args:
            other: Another model of the same type
        """
        for attr_name in dir(other):
            if not attr_name.startswith('_') and not callable(getattr(other, attr_name)):
                if hasattr(self, attr_name):
                    current_value = getattr(self, attr_name)
                    new_value = getattr(other, attr_name)
                    if current_value != new_value:
                        setattr(self, attr_name, new_value)
