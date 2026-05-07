"""
Example: Person Model for MVVM Framework Demo
"""

from mvvm_framework.core import Model


class Person(Model):
    """
    Example model representing a person.
    
    Demonstrates property definition, validation, and change notification.
    """
    
    def __init__(
        self,
        name: str = "",
        age: int = 0,
        email: str = "",
        is_active: bool = True
    ):
        super().__init__()
        self._name = name
        self._age = age
        self._email = email
        self._is_active = is_active
    
    @property
    def name(self) -> str:
        """Get the person's name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the person's name."""
        if self._name != value:
            self._name = value
            self.notify_property_changed("name")
    
    @property
    def age(self) -> int:
        """Get the person's age."""
        return self._age
    
    @age.setter
    def age(self, value: int) -> None:
        """Set the person's age."""
        if self._age != value:
            self._age = value
            self.notify_property_changed("age")
    
    @property
    def email(self) -> str:
        """Get the person's email."""
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """Set the person's email."""
        if self._email != value:
            self._email = value
            self.notify_property_changed("email")
    
    @property
    def is_active(self) -> bool:
        """Check if the person is active."""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set the active status."""
        if self._is_active != value:
            self._is_active = value
            self.notify_property_changed("is_active")
    
    @property
    def display_name(self) -> str:
        """
        Computed property: Full display name.
        
        Returns:
            Formatted display name with age
        """
        return self.get_cached_value(
            "display_name",
            lambda: f"{self._name} ({self._age} years old)" if self._name else ""
        )
    
    # Register dependencies for computed properties
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # This would be called when Person is subclassed
    
    def validate_name(self, value: str) -> str | None:
        """Validate the name property."""
        if not value or not value.strip():
            return "Name cannot be empty"
        if len(value.strip()) < 2:
            return "Name must be at least 2 characters"
        return None
    
    def validate_age(self, value: int) -> str | None:
        """Validate the age property."""
        if value < 0:
            return "Age cannot be negative"
        if value > 150:
            return "Age cannot be greater than 150"
        return None
    
    def validate_email(self, value: str) -> str | None:
        """Validate the email property."""
        if value and '@' not in value:
            return "Invalid email format"
        return None
    
    def to_dict(self) -> dict:
        """Convert person to dictionary."""
        return {
            'name': self._name,
            'age': self._age,
            'email': self._email,
            'is_active': self._is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Person':
        """Create a Person from a dictionary."""
        return cls(
            name=data.get('name', ''),
            age=data.get('age', 0),
            email=data.get('email', ''),
            is_active=data.get('is_active', True)
        )
    
    def __str__(self) -> str:
        return f"Person(name={self._name}, age={self._age})"
    
    def __repr__(self) -> str:
        return self.__str__()
