"""
Data binding utilities for MVVM framework.
Provides tools for binding UI elements to ViewModel properties.
"""

from typing import Any, Callable, Optional, Union
from PySide6.QtCore import QObject, QMetaObject, Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QAction


class Binding:
    """
    Utility class for creating data bindings between ViewModels and Views.
    
    Supports one-way and two-way bindings for various widget types.
    
    Example:
        # One-way binding (ViewModel -> View)
        Binding.bind_label(viewmodel, "name", label_widget)
        
        # Two-way binding (ViewModel <-> View)
        Binding.bind_text(viewmodel, "name", line_edit)
        
        # Command binding
        Binding.bind_command(viewmodel, "save_command", button)
    """
    
    @staticmethod
    def bind_property(
        source: QObject,
        source_property: str,
        target: QObject,
        target_property: str,
        converter: Optional[Callable[[Any], Any]] = None,
        reverse_converter: Optional[Callable[[Any], Any]] = None
    ) -> None:
        """
        Create a one-way binding from source property to target property.
        
        Args:
            source: Source object (usually ViewModel)
            source_property: Name of the source property
            target: Target object (usually Widget)
            target_property: Name of the target property
            converter: Optional function to convert source value to target value
            reverse_converter: Optional function for reverse conversion (two-way)
        """
        def update_target(value: Any):
            if converter:
                value = converter(value)
            setattr(target, target_property, value)
        
        # Initial update
        update_target(getattr(source, source_property))
        
        # Connect to property changes
        if hasattr(source, 'propertyChanged'):
            source.propertyChanged.connect(lambda name: update_target(getattr(source, source_property)) if name == source_property else None)
    
    @staticmethod
    def bind_text(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        two_way: bool = True
    ) -> None:
        """
        Bind a ViewModel property to a widget's text property.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the property to bind
            widget: Widget to bind to (QLineEdit, QLabel, etc.)
            two_way: If True, create a two-way binding
        """
        # ViewModel -> Widget
        def update_widget(value: Any):
            if hasattr(widget, 'setText'):
                widget.setText(str(value) if value is not None else "")
        
        # Initial update
        update_widget(getattr(viewmodel, property_name))
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_widget(getattr(viewmodel, property_name)) if name == property_name else None
            )
        
        # Widget -> ViewModel (two-way binding)
        if two_way:
            # Prefer textEdited to avoid redundant updates from programmatic setText
            if hasattr(widget, 'textEdited'):
                widget.textEdited.connect(
                    lambda text: setattr(viewmodel, property_name, text) if hasattr(viewmodel, property_name) else None
                )
            elif hasattr(widget, 'textChanged'):
                widget.textChanged.connect(
                    lambda text: setattr(viewmodel, property_name, text) if hasattr(viewmodel, property_name) else None
                )
    
    @staticmethod
    def bind_label(
        viewmodel: QObject,
        property_name: str,
        label: QWidget
    ) -> None:
        """
        Bind a ViewModel property to a QLabel's text (one-way).
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the property to bind
            label: QLabel widget
        """
        Binding.bind_text(viewmodel, property_name, label, two_way=False)
    
    @staticmethod
    def bind_checked(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget
    ) -> None:
        """
        Bind a ViewModel property to a widget's checked state.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the property to bind
            widget: Checkable widget (QCheckBox, QRadioButton, etc.)
        """
        # ViewModel -> Widget
        def update_widget(value: Any):
            if hasattr(widget, 'setChecked'):
                widget.setChecked(bool(value))
        
        # Initial update
        update_widget(getattr(viewmodel, property_name))
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_widget(getattr(viewmodel, property_name)) if name == property_name else None
            )
        
        # Widget -> ViewModel
        if hasattr(widget, 'toggled'):
            widget.toggled.connect(
                lambda checked: setattr(viewmodel, property_name, checked)
            )
    
    @staticmethod
    def bind_value(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        converter: Optional[Callable[[Any], Any]] = None
    ) -> None:
        """
        Bind a ViewModel property to a spinbox/slider value.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the property to bind
            widget: Value widget (QSpinBox, QSlider, etc.)
            converter: Optional value converter
        """
        # ViewModel -> Widget
        def update_widget(value: Any):
            if converter:
                value = converter(value)
            if hasattr(widget, 'setValue'):
                widget.setValue(int(value) if value is not None else 0)
        
        # Initial update
        update_widget(getattr(viewmodel, property_name))
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_widget(getattr(viewmodel, property_name)) if name == property_name else None
            )
        
        # Widget -> ViewModel
        if hasattr(widget, 'valueChanged'):
            widget.valueChanged.connect(
                lambda value: setattr(viewmodel, property_name, value)
            )
    
    @staticmethod
    def bind_command(
        viewmodel: QObject,
        command_name: str,
        widget: Union[QWidget, QAction]
    ) -> None:
        """
        Bind a ViewModel command to a widget's click/trigger action.
        
        Args:
            viewmodel: The ViewModel instance
            command_name: Name of the command property
            widget: Widget to bind to (QPushButton, QAction, etc.)
        """
        command = getattr(viewmodel, command_name, None)
        
        if command is None:
            return
        
        # Enable/disable widget based on command's can_execute
        def update_enabled():
            enabled = command.can_execute()
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(enabled)
        
        # Initial state
        update_enabled()
        
        # Connect to command's canExecuteChanged
        if hasattr(command, 'canExecuteChanged'):
            command.canExecuteChanged.connect(lambda _: update_enabled())
        
        # Connect widget click to command execution
        if hasattr(widget, 'clicked'):
            widget.clicked.connect(lambda: command.execute())
        elif hasattr(widget, 'triggered'):
            widget.triggered.connect(lambda: command.execute())
        elif hasattr(widget, 'pressed'):
            widget.pressed.connect(lambda: command.execute())
    
    @staticmethod
    def bind_visibility(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        inverse: bool = False
    ) -> None:
        """
        Bind a ViewModel boolean property to widget visibility.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the boolean property
            widget: Widget to bind to
            inverse: If True, hide when True, show when False
        """
        def update_visibility(value: Any):
            visible = bool(value) != inverse
            widget.setVisible(visible)
        
        # Initial update
        update_visibility(getattr(viewmodel, property_name))
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_visibility(getattr(viewmodel, property_name)) if name == property_name else None
            )
    
    @staticmethod
    def bind_items(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        display_member: Optional[str] = None
    ) -> None:
        """
        Bind a ViewModel list property to a combobox/listwidget.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the list property
            widget: ComboBox or ListWidget
            display_member: Property name to display for each item
        """
        from .observable import ObservableList
        
        def update_items():
            items = getattr(viewmodel, property_name, [])
            
            if hasattr(widget, 'clear'):
                widget.clear()
            
            for item in items:
                if display_member and hasattr(item, display_member):
                    display_value = getattr(item, display_member)
                else:
                    display_value = str(item)
                
                if hasattr(widget, 'addItem'):
                    widget.addItem(display_value, item)
        
        # Initial update
        update_items()
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_items() if name == property_name else None
            )
        
        # Also listen to ObservableList changes
        items = getattr(viewmodel, property_name, [])
        if isinstance(items, ObservableList):
            items.itemAdded.connect(lambda _: update_items())
            items.itemRemoved.connect(lambda _: update_items())
            items.listCleared.connect(update_items)
    
    @staticmethod
    def bind_validation_error(
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        error_label: Optional[QWidget] = None
    ) -> None:
        """
        Bind validation errors to widget styling and error label.
        
        Args:
            viewmodel: The ViewModel instance
            property_name: Name of the property
            widget: Widget to style on error
            error_label: Optional label to show error message
        """
        def update_validation():
            if hasattr(viewmodel, 'get_validation_error'):
                error = viewmodel.get_validation_error(property_name)
                
                if error:
                    widget.setProperty("error", True)
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    
                    if error_label and hasattr(error_label, 'setText'):
                        error_label.setText(error)
                        error_label.show()
                else:
                    widget.setProperty("error", False)
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    
                    if error_label and hasattr(error_label, 'hide'):
                        error_label.hide()
        
        # Initial update
        update_validation()
        
        # Connect to property changes
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(
                lambda name: update_validation() if name == property_name else None
            )
