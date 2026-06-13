"""
Data binding utilities for MVVM framework.
Provides tools for binding UI elements to ViewModel properties.
"""

import logging
from typing import Any, Callable, Optional, Union
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QAction


logger = logging.getLogger(__name__)


class _BindingHandler(QObject):
    """
    Internal helper class to manage binding connections without lambda expressions.
    This prevents wild pointer issues when objects are destroyed.
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._connections = []
    
    def _disconnect_all(self):
        """Disconnect all managed connections."""
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
            except RuntimeError:
                pass
        self._connections.clear()
    
    def _track_connection(self, signal, slot):
        """Track a connection for cleanup."""
        self._connections.append((signal, slot))
    
    def deleteLater(self):
        """Clean up connections before deletion."""
        self._disconnect_all()
        super().deleteLater()


class _TextBindingHandler(_BindingHandler):
    """Handler for text binding."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        two_way: bool = True,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        
        self._update_widget(getattr(viewmodel, property_name))
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
        
        if two_way:
            if hasattr(widget, 'textEdited'):
                widget.textEdited.connect(self._on_text_edited)
                self._track_connection(widget.textEdited, self._on_text_edited)
            elif hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self._on_text_changed)
                self._track_connection(widget.textChanged, self._on_text_changed)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_widget(getattr(self._viewmodel, self._property_name))
    
    @Slot(str)
    def _on_text_edited(self, text: str) -> None:
        if hasattr(self._viewmodel, self._property_name):
            setattr(self._viewmodel, self._property_name, text)
    
    @Slot(str)
    def _on_text_changed(self, text: str) -> None:
        if hasattr(self._viewmodel, self._property_name):
            setattr(self._viewmodel, self._property_name, text)
    
    def _update_widget(self, value: Any) -> None:
        if hasattr(self._widget, 'setText'):
            if hasattr(self._widget, 'blockSignals'):
                was_blocked = self._widget.blockSignals(True)
                try:
                    self._widget.setText(str(value) if value is not None else "")
                finally:
                    self._widget.blockSignals(was_blocked)
            else:
                self._widget.setText(str(value) if value is not None else "")


class _CheckedBindingHandler(_BindingHandler):
    """Handler for checked state binding."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        
        self._update_widget(getattr(viewmodel, property_name))
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
        
        if hasattr(widget, 'toggled'):
            widget.toggled.connect(self._on_toggled)
            self._track_connection(widget.toggled, self._on_toggled)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_widget(getattr(self._viewmodel, self._property_name))
    
    @Slot(bool)
    def _on_toggled(self, checked: bool) -> None:
        setattr(self._viewmodel, self._property_name, checked)
    
    def _update_widget(self, value: Any) -> None:
        if hasattr(self._widget, 'setChecked'):
            self._widget.setChecked(bool(value))


class _ValueBindingHandler(_BindingHandler):
    """Handler for value binding (spinbox, slider, etc.)."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        converter: Optional[Callable[[Any], Any]] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        self._converter = converter
        
        self._update_widget(getattr(viewmodel, property_name))
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
        
        if hasattr(widget, 'valueChanged'):
            widget.valueChanged.connect(self._on_value_changed)
            self._track_connection(widget.valueChanged, self._on_value_changed)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_widget(getattr(self._viewmodel, self._property_name))
    
    @Slot(int)
    def _on_value_changed(self, value: int) -> None:
        setattr(self._viewmodel, self._property_name, value)
    
    def _update_widget(self, value: Any) -> None:
        if self._converter:
            value = self._converter(value)
        if hasattr(self._widget, 'setValue'):
            self._widget.setValue(value)


class _CommandBindingHandler(_BindingHandler):
    """Handler for command binding."""
    
    def __init__(
        self,
        command,
        widget: Union[QWidget, QAction],
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._command = command
        self._widget = widget
        
        self._update_enabled()
        
        if hasattr(command, 'canExecuteChanged'):
            command.canExecuteChanged.connect(self._on_can_execute_changed)
            self._track_connection(command.canExecuteChanged, self._on_can_execute_changed)
        
        if hasattr(widget, 'clicked'):
            widget.clicked.connect(self._on_clicked)
            self._track_connection(widget.clicked, self._on_clicked)
        elif hasattr(widget, 'triggered'):
            widget.triggered.connect(self._on_triggered)
            self._track_connection(widget.triggered, self._on_triggered)
        elif hasattr(widget, 'pressed'):
            widget.pressed.connect(self._on_pressed)
            self._track_connection(widget.pressed, self._on_pressed)
    
    @Slot(bool)
    def _on_can_execute_changed(self, _: bool) -> None:
        self._update_enabled()
    
    @Slot()
    def _on_clicked(self) -> None:
        self._command.execute()
    
    @Slot()
    def _on_triggered(self) -> None:
        self._command.execute()
    
    @Slot()
    def _on_pressed(self) -> None:
        self._command.execute()
    
    def _update_enabled(self) -> None:
        enabled = self._command.can_execute()
        if hasattr(self._widget, 'setEnabled'):
            self._widget.setEnabled(enabled)


class _VisibilityBindingHandler(_BindingHandler):
    """Handler for visibility binding."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        inverse: bool = False,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        self._inverse = inverse
        
        self._update_visibility(getattr(viewmodel, property_name))
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_visibility(getattr(self._viewmodel, self._property_name))
    
    def _update_visibility(self, value: Any) -> None:
        visible = bool(value) != self._inverse
        self._widget.setVisible(visible)


class _ItemsBindingHandler(_BindingHandler):
    """Handler for items binding (combobox, listwidget)."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        display_member: Optional[str] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        self._display_member = display_member
        
        self._update_items()
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
        
        from .observable import ObservableList
        items = getattr(viewmodel, property_name, [])
        if isinstance(items, ObservableList):
            items.itemAdded.connect(self._on_item_added)
            self._track_connection(items.itemAdded, self._on_item_added)
            
            items.itemRemoved.connect(self._on_item_removed)
            self._track_connection(items.itemRemoved, self._on_item_removed)
            
            items.itemChanged.connect(self._on_item_changed)
            self._track_connection(items.itemChanged, self._on_item_changed)
            
            items.listReset.connect(self._on_list_reset)
            self._track_connection(items.listReset, self._on_list_reset)
            
            items.listCleared.connect(self._on_list_cleared)
            self._track_connection(items.listCleared, self._on_list_cleared)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_items()
    
    @Slot(int, object)
    def _on_item_added(self, index: int, item) -> None:
        self._update_items()
    
    @Slot(int, object)
    def _on_item_removed(self, index: int, item) -> None:
        self._update_items()
    
    @Slot(int, object)
    def _on_item_changed(self, index: int, item) -> None:
        self._update_items()
    
    @Slot()
    def _on_list_reset(self) -> None:
        self._update_items()
    
    @Slot()
    def _on_list_cleared(self) -> None:
        self._update_items()
    
    def _update_items(self) -> None:
        items = getattr(self._viewmodel, self._property_name, [])
        
        if hasattr(self._widget, 'clear'):
            self._widget.clear()
        
        for item in items:
            if self._display_member and hasattr(item, self._display_member):
                display_value = getattr(item, self._display_member)
            else:
                display_value = str(item)
            
            if hasattr(self._widget, 'addItem'):
                self._widget.addItem(display_value, item)


class _ValidationBindingHandler(_BindingHandler):
    """Handler for validation error binding."""
    
    def __init__(
        self,
        viewmodel: QObject,
        property_name: str,
        widget: QWidget,
        error_label: Optional[QWidget] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._property_name = property_name
        self._widget = widget
        self._error_label = error_label
        
        self._update_validation()
        
        if hasattr(viewmodel, 'propertyChanged'):
            viewmodel.propertyChanged.connect(self._on_property_changed)
            self._track_connection(viewmodel.propertyChanged, self._on_property_changed)
    
    @Slot(str)
    def _on_property_changed(self, name: str) -> None:
        if name == self._property_name:
            self._update_validation()
    
    def _update_validation(self) -> None:
        if hasattr(self._viewmodel, 'get_validation_error'):
            error = self._viewmodel.get_validation_error(self._property_name)
            
            if error:
                self._widget.setProperty("error", True)
                self._widget.style().unpolish(self._widget)
                self._widget.style().polish(self._widget)
                
                if self._error_label and hasattr(self._error_label, 'setText'):
                    self._error_label.setText(error)
                    self._error_label.show()
            else:
                self._widget.setProperty("error", False)
                self._widget.style().unpolish(self._widget)
                self._widget.style().polish(self._widget)
                
                if self._error_label and hasattr(self._error_label, 'hide'):
                    self._error_label.hide()


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
        class _PropertyBindingHandler(_BindingHandler):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._source = source
                self._source_property = source_property
                self._target = target
                self._target_property = target_property
                self._converter = converter
                
                self._update_target(getattr(source, source_property))
                
                if hasattr(source, 'propertyChanged'):
                    source.propertyChanged.connect(self._on_property_changed)
                    self._track_connection(source.propertyChanged, self._on_property_changed)
            
            @Slot(str)
            def _on_property_changed(self, name: str) -> None:
                if name == self._source_property:
                    self._update_target(getattr(self._source, self._source_property))
            
            def _update_target(self, value: Any) -> None:
                if self._converter:
                    value = self._converter(value)
                setattr(self._target, self._target_property, value)
        
        _PropertyBindingHandler()
    
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
        _TextBindingHandler(viewmodel, property_name, widget, two_way)
    
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
        _CheckedBindingHandler(viewmodel, property_name, widget)
    
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
        _ValueBindingHandler(viewmodel, property_name, widget, converter)
    
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
        if command is not None:
            _CommandBindingHandler(command, widget)
    
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
        _VisibilityBindingHandler(viewmodel, property_name, widget, inverse)
    
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
        _ItemsBindingHandler(viewmodel, property_name, widget, display_member)
    
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
        _ValidationBindingHandler(viewmodel, property_name, widget, error_label)