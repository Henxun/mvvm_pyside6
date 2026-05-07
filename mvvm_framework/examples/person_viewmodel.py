"""
Example: Person ViewModel for MVVM Framework Demo
"""

from mvvm_framework.core import ViewModel, Command, ObservableList
from mvvm_framework.examples.person_model import Person


class PersonViewModel(ViewModel[Person]):
    """
    Example ViewModel for Person model.
    
    Demonstrates command implementation, computed properties,
    and data binding patterns.
    """
    
    def __init__(self, model: Person | None = None):
        if model is None:
            model = Person()
        
        super().__init__(model)
        
        # Initialize commands
        self._save_command = Command(
            execute=self.save,
            can_execute=self.can_save
        )
        
        self._reset_command = Command(
            execute=self.reset,
            can_execute=self.can_reset
        )
        
        self._delete_command = Command(
            execute=self.delete,
            can_execute=self.can_delete
        )
        
        self._increment_age_command = Command(
            execute=self.increment_age
        )
        
        # Track original values for reset functionality
        self._original_name = model.name
        self._original_age = model.age
        self._original_email = model.email
        
        # Subscribe to model changes for command state updates
        self.propertyChanged.connect(self._on_property_changed)
    
    #region Properties
    
    @property
    def name(self) -> str:
        """Get the person's name."""
        return self.model.name if self.model else ""
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the person's name."""
        if self.model:
            self.model.name = value
            self.notify_property_changed("name")
            self._save_command.notify_can_execute_changed()
    
    @property
    def age(self) -> int:
        """Get the person's age."""
        return self.model.age if self.model else 0
    
    @age.setter
    def age(self, value: int) -> None:
        """Set the person's age."""
        if self.model:
            self.model.age = value
            self.notify_property_changed("age")
            self._save_command.notify_can_execute_changed()
    
    @property
    def email(self) -> str:
        """Get the person's email."""
        return self.model.email if self.model else ""
    
    @email.setter
    def email(self, value: str) -> None:
        """Set the person's email."""
        if self.model:
            self.model.email = value
            self.notify_property_changed("email")
            self._save_command.notify_can_execute_changed()
    
    @property
    def is_active(self) -> bool:
        """Check if the person is active."""
        return self.model.is_active if self.model else False
    
    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set the active status."""
        if self.model:
            self.model.is_active = value
            self.notify_property_changed("is_active")
    
    @property
    def display_name(self) -> str:
        """Get the formatted display name."""
        return self.model.display_name if self.model else ""
    
    @property
    def has_changes(self) -> bool:
        """Check if there are unsaved changes."""
        if not self.model:
            return False
        return (
            self.model.name != self._original_name or
            self.model.age != self._original_age or
            self.model.email != self._original_email
        )
    
    @property
    def save_status(self) -> str:
        """Get the current save status message."""
        if self.has_changes:
            return "Unsaved changes"
        return "All changes saved"
    
    #endregion
    
    #region Commands
    
    @property
    def save_command(self) -> Command:
        """Get the save command."""
        return self._save_command
    
    @property
    def reset_command(self) -> Command:
        """Get the reset command."""
        return self._reset_command
    
    @property
    def delete_command(self) -> Command:
        """Get the delete command."""
        return self._delete_command
    
    @property
    def increment_age_command(self) -> Command:
        """Get the increment age command."""
        return self._increment_age_command
    
    #endregion
    
    #region Command Handlers
    
    def can_save(self) -> bool:
        """Check if save command can execute."""
        return self.has_changes and not self.has_errors()
    
    def can_reset(self) -> bool:
        """Check if reset command can execute."""
        return self.has_changes
    
    def can_delete(self) -> bool:
        """Check if delete command can execute."""
        return True  # Always allow delete in this example
    
    def save(self) -> None:
        """Save the current changes."""
        if self.model and self.validate():
            # Update original values
            self._original_name = self.model.name
            self._original_age = self.model.age
            self._original_email = self.model.email
            
            # Notify UI of status change
            self.notify_property_changed("has_changes")
            self.notify_property_changed("save_status")
            
            print(f"Saved: {self.model}")
    
    def reset(self) -> None:
        """Reset to original values."""
        if self.model:
            self.model.name = self._original_name
            self.model.age = self._original_age
            self.model.email = self._original_email
            
            # Notify all changed properties
            self.notify_property_changed("name")
            self.notify_property_changed("age")
            self.notify_property_changed("email")
            self.notify_property_changed("has_changes")
            self.notify_property_changed("save_status")
    
    def delete(self) -> None:
        """Delete the person (in a real app, would remove from collection)."""
        print(f"Deleting: {self.model}")
        # In a real application, you would notify a parent ViewModel
        # to remove this item from a collection
    
    def increment_age(self) -> None:
        """Increment the person's age by 1."""
        if self.model:
            self.age = self.model.age + 1
    
    #endregion
    
    #region Internal Methods
    
    def _on_property_changed(self, property_name: str) -> None:
        """Handle property changes."""
        if property_name in ("name", "age", "email"):
            self.notify_property_changed("has_changes")
            self.notify_property_changed("save_status")
            self._save_command.notify_can_execute_changed()
            self._reset_command.notify_can_execute_changed()
    
    def set_person(self, person: Person) -> None:
        """Set a new person model."""
        self.model = person
        self._original_name = person.name
        self._original_age = person.age
        self._original_email = person.email
        
        # Notify all properties
        self.notify_property_changed("name")
        self.notify_property_changed("age")
        self.notify_property_changed("email")
        self.notify_property_changed("is_active")
        self.notify_property_changed("display_name")
        self.notify_property_changed("has_changes")
        self.notify_property_changed("save_status")


class PersonCollectionViewModel(ViewModel):
    """
    ViewModel for managing a collection of Person objects.
    
    Demonstrates working with ObservableList and collection operations.
    """
    
    def __init__(self):
        super().__init__()
        
        self._people = ObservableList[Person]()
        self._selected_person: PersonViewModel | None = None
        
        self._add_command = Command(
            execute=self.add_person,
            can_execute=lambda: True
        )
        
        self._remove_command = Command(
            execute=self.remove_selected,
            can_execute=self.can_remove_selected
        )
    
    @property
    def people(self) -> ObservableList[Person]:
        """Get the collection of people."""
        return self._people
    
    @property
    def selected_person(self) -> PersonViewModel | None:
        """Get the currently selected person ViewModel."""
        return self._selected_person
    
    @selected_person.setter
    def selected_person(self, value: PersonViewModel | None) -> None:
        """Set the selected person."""
        if self._selected_person != value:
            self._selected_person = value
            self.notify_property_changed("selected_person")
            self._remove_command.notify_can_execute_changed()
    
    @property
    def add_command(self) -> Command:
        """Get the add command."""
        return self._add_command
    
    @property
    def remove_command(self) -> Command:
        """Get the remove command."""
        return self._remove_command
    
    @property
    def count(self) -> int:
        """Get the number of people."""
        return len(self._people)
    
    def can_remove_selected(self) -> bool:
        """Check if selected person can be removed."""
        return self._selected_person is not None
    
    def add_person(self) -> None:
        """Add a new person to the collection."""
        person = Person(name="New Person", age=25)
        self._people.append(person)
        self.notify_property_changed("count")
        print(f"Added person: {person}")
    
    def remove_selected(self) -> None:
        """Remove the selected person."""
        if self._selected_person and self._selected_person.model:
            person = self._selected_person.model
            if person in self._people:
                self._people.remove(person)
                self.notify_property_changed("count")
                self.selected_person = None
                print(f"Removed person: {person}")
    
    def load_sample_data(self) -> None:
        """Load sample data for demonstration."""
        self._people.clear()
        self._people.extend([
            Person(name="Alice", age=30, email="alice@example.com"),
            Person(name="Bob", age=25, email="bob@example.com"),
            Person(name="Charlie", age=35, email="charlie@example.com"),
        ])
        self.notify_property_changed("count")
