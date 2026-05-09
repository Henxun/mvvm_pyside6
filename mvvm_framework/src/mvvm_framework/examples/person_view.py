"""
Example: Person View for MVVM Framework Demo

A complete PySide6 view demonstrating data binding with the MVVM framework.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox,
    QCheckBox, QGroupBox, QComboBox, QListWidget,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from mvvm_framework.core import Binding
from mvvm_framework.examples.person_viewmodel import PersonViewModel, PersonCollectionViewModel


class PersonView(QWidget):
    """
    View for displaying and editing a Person.
    
    Demonstrates various data binding techniques including:
    - Two-way text binding
    - Value binding for spinboxes
    - Checked state binding
    - Command binding
    - Label binding for computed properties
    - Visibility binding
    """
    
    def __init__(self, viewmodel: PersonViewModel, parent: QWidget | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("Person Editor - MVVM Example")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Person Information")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Form group
        form_group = QGroupBox("Details")
        form_layout = QFormLayout(form_group)
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter name...")
        form_layout.addRow("Name:", self.name_edit)
        
        # Age field
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 150)
        form_layout.addRow("Age:", self.age_spin)
        
        # Email field
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email...")
        form_layout.addRow("Email:", self.email_edit)
        
        # Active checkbox
        self.active_check = QCheckBox("Is Active")
        form_layout.addRow("", self.active_check)
        
        layout.addWidget(form_group)
        
        # Display group
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        
        # Display name label (computed property)
        self.display_name_label = QLabel()
        self.display_name_label.setStyleSheet("font-style: italic; color: #555;")
        display_layout.addWidget(self.display_name_label)
        
        # Save status label
        self.save_status_label = QLabel()
        self.save_status_label.setStyleSheet("color: #888; font-size: 12px;")
        display_layout.addWidget(self.save_status_label)
        
        layout.addWidget(display_group)
        
        # Buttons group
        buttons_group = QGroupBox("Actions")
        buttons_layout = QHBoxLayout(buttons_group)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save changes")
        buttons_layout.addWidget(self.save_button)
        
        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Discard changes")
        buttons_layout.addWidget(self.reset_button)
        
        # Increment age button
        self.increment_button = QPushButton("+1 Age")
        self.increment_button.setToolTip("Increment age by 1")
        buttons_layout.addWidget(self.increment_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.setToolTip("Delete this person")
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        layout.addWidget(buttons_group)
        
        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        layout.addStretch()
    
    def _setup_bindings(self) -> None:
        """Set up data bindings between ViewModel and View."""
        vm = self.viewmodel
        
        # Two-way text bindings
        Binding.bind_text(vm, "name", self.name_edit, two_way=True)
        Binding.bind_text(vm, "email", self.email_edit, two_way=True)
        
        # One-way label binding for computed property
        Binding.bind_label(vm, "display_name", self.display_name_label)
        
        # Value binding for spinbox
        Binding.bind_value(vm, "age", self.age_spin)
        
        # Checked state binding
        Binding.bind_checked(vm, "is_active", self.active_check)
        
        # Status label binding
        Binding.bind_label(vm, "save_status", self.save_status_label)
        
        # Command bindings
        Binding.bind_command(vm, "save_command", self.save_button)
        Binding.bind_command(vm, "reset_command", self.reset_button)
        Binding.bind_command(vm, "increment_age_command", self.increment_button)
        Binding.bind_command(vm, "delete_command", self.delete_button)
        
        # Validation error binding
        Binding.bind_validation_error(vm, "name", self.name_edit, self.error_label)
        Binding.bind_validation_error(vm, "email", self.email_edit)
        
        # Subscribe to validation changes to show/hide error summary
        vm.propertyChanged.connect(self._on_validation_changed)
    
    def _on_validation_changed(self, property_name: str) -> None:
        """Handle validation changes."""
        if property_name in ("name", "email"):
            error = self.viewmodel.model.get_validation_error(property_name) if self.viewmodel.model else None
            if error:
                self.error_label.setText(error)
                self.error_label.show()
            else:
                # Only hide if no other errors
                has_errors = self.viewmodel.has_errors()
                if not has_errors:
                    self.error_label.hide()
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if self.viewmodel.has_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()


class PersonCollectionView(QWidget):
    """
    View for managing a collection of Persons.
    
    Demonstrates list binding and master-detail pattern.
    """
    
    def __init__(self, viewmodel: PersonCollectionViewModel, parent: QWidget | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("Person Collection - MVVM Example")
        self.setMinimumSize(600, 500)
        
        self._person_views: dict[int, PersonView] = {}
        self._current_person_view: PersonView | None = None
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        
        # Left panel - List
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        list_group = QGroupBox("People")
        list_layout = QVBoxLayout(list_group)
        
        self.people_list = QListWidget()
        list_layout.addWidget(self.people_list)
        
        # List buttons
        list_buttons = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        list_buttons.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setEnabled(False)
        list_buttons.addWidget(self.remove_button)
        
        list_buttons.addStretch()
        list_layout.addLayout(list_buttons)
        
        left_layout.addWidget(list_group)
        
        layout.addWidget(left_panel, stretch=1)
        
        # Right panel - Detail
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.detail_container = QFrame()
        self.detail_container.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        detail_layout = QVBoxLayout(self.detail_container)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        
        self.no_selection_label = QLabel("Select a person to edit\nor add a new one.")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setStyleSheet("color: #888; padding: 50px;")
        detail_layout.addWidget(self.no_selection_label)
        
        right_layout.addWidget(self.detail_container)
        
        layout.addWidget(right_panel, stretch=2)
    
    def _setup_bindings(self) -> None:
        """Set up data bindings."""
        vm = self.viewmodel
        
        # Command bindings
        Binding.bind_command(vm, "add_command", self.add_button)
        Binding.bind_command(vm, "remove_command", self.remove_button)
        
        # Connect to list selection changes
        self.people_list.currentRowChanged.connect(self._on_selection_changed)
        
        # Listen to collection changes
        vm.people.itemAdded.connect(self._on_item_added)
        vm.people.itemRemoved.connect(self._on_item_removed)
        vm.people.listCleared.connect(self._on_list_cleared)
        
        # Initial population
        self._refresh_list()
    
    def _refresh_list(self) -> None:
        """Refresh the people list."""
        self.people_list.clear()
        for person in self.viewmodel.people:
            self.people_list.addItem(str(person))
    
    def _on_selection_changed(self, index: int) -> None:
        """Handle selection change in the list."""
        if index < 0 or index >= len(self.viewmodel.people):
            self.viewmodel.selected_person = None
            self._show_no_selection()
            return
        
        person = self.viewmodel.people[index]
        person_vm = PersonViewModel(person)
        
        # Update the collection ViewModel's selected person
        # In a real app, you'd want a better way to track this
        self.viewmodel.selected_person = person_vm
        
        self._show_person_detail(person_vm)
    
    def _show_no_selection(self) -> None:
        """Show the no-selection placeholder."""
        self._clear_detail()
        self.no_selection_label.show()
    
    def _show_person_detail(self, viewmodel: PersonViewModel) -> None:
        """Show the detail view for a person."""
        self._clear_detail()
        self.no_selection_label.hide()
        
        person_view = PersonView(viewmodel)
        self._current_person_view = person_view
        
        # Embed the view
        person_view.setParent(self.detail_container)
        person_view.layout().setContentsMargins(0, 0, 0, 0)
        
        # Add to container layout
        container_layout = self.detail_container.layout()
        if container_layout:
            container_layout.addWidget(person_view)
    
    def _clear_detail(self) -> None:
        """Clear the detail view."""
        if self._current_person_view:
            self._current_person_view.deleteLater()
            self._current_person_view = None
    
    def _on_item_added(self, index: int, person) -> None:
        """Handle item added to collection."""
        self.people_list.insertItem(index, str(person))
        self._refresh_list()
    
    def _on_item_removed(self, index: int, person) -> None:
        """Handle item removed from collection."""
        self._refresh_list()
    
    def _on_list_cleared(self) -> None:
        """Handle list cleared."""
        self._refresh_list()
        self.viewmodel.selected_person = None
        self._show_no_selection()


def main():
    """Run the example application."""
    import sys
    from PySide6.QtWidgets import QApplication
    
    # Import Person model at function runtime to avoid NameError when called from elsewhere
    from mvvm_framework.examples.person_model import Person
    
    app = QApplication(sys.argv)
    
    # Create sample data
    person = Person(
        name="John Doe",
        age=30,
        email="john@example.com",
        is_active=True
    )
    
    # Create ViewModel
    viewmodel = PersonViewModel(person)
    
    # Create and show View
    view = PersonView(viewmodel)
    view.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
