"""
Observable Object and List implementations for MVVM framework.
Provides property change notification system based on PySide6 signals.
"""

from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar
from PySide6.QtCore import QObject, Signal


T = TypeVar('T')


class ObservableObject(QObject):
    """
    Base class for observable objects in the MVVM pattern.
    
    Provides property change notification through Qt signals.
    Subclasses should use the @property decorator with notify_signal
    to create observable properties.
    
    Example:
        class Person(ObservableObject):
            def __init__(self):
                super().__init__()
                self._name = ""
                self._age = 0
            
            @property
            def name(self) -> str:
                return self._name
            
            @name.setter
            def name(self, value: str):
                if self._name != value:
                    self._name = value
                    self.propertyChanged.emit("name")
            
            @property
            def age(self) -> int:
                return self._age
            
            @age.setter
            def age(self, value: int):
                if self._age != value:
                    self._age = value
                    self.propertyChanged.emit("age")
    """
    
    # Signal emitted when any property changes, passes the property name
    propertyChanged = Signal(str)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._suppress_notifications = False
        self._computed_property_cache: Dict[str, Any] = {}
        self._property_dependencies: Dict[str, Set[str]] = {}
        self._suppressed_property_changes: Set[str] = set()
    
    def notify_property_changed(self, property_name: str) -> None:
        """
        Notify that a property has changed.
        
        Args:
            property_name: Name of the changed property
        """
        # Always invalidate dependent properties regardless of suppression
        self._invalidate_dependent_properties(property_name)
        
        if not self._suppress_notifications:
            self.propertyChanged.emit(property_name)
            # Emit notifications for dependent properties
            self._emit_dependent_notifications(property_name)
        else:
            # Track suppressed changes for later emission
            self._suppressed_property_changes.add(property_name)
    
    def _emit_dependent_notifications(self, property_name: str) -> None:
        """Emit notifications for dependent properties if not suppressed."""
        if property_name in self._property_dependencies and not self._suppress_notifications:
            for dependent_prop in self._property_dependencies[property_name]:
                if dependent_prop in self._computed_property_cache or \
                   dependent_prop in self._suppressed_property_changes:
                    self.propertyChanged.emit(dependent_prop)
    
    def suppress_notifications(self) -> None:
        """Temporarily suppress property change notifications."""
        self._suppress_notifications = True
    
    def resume_notifications(self, notify_changes: bool = False) -> None:
        """
        Resume property change notifications.
        
        Args:
            notify_changes: If True, emit notifications for all properties
                            that changed while suppressed
        """
        self._suppress_notifications = False
        if notify_changes:
            # Emit for both computed properties and tracked suppressed changes
            all_props = self._computed_property_cache.keys() | self._suppressed_property_changes
            for prop_name in all_props:
                self.propertyChanged.emit(prop_name)
            self._suppressed_property_changes.clear()
    
    def register_dependency(self, dependent_property: str, depends_on: str) -> None:
        """
        Register a property dependency for computed properties.
        
        Args:
            dependent_property: The computed property name
            depends_on: The property it depends on
        """
        if depends_on not in self._property_dependencies:
            self._property_dependencies[depends_on] = set()
        self._property_dependencies[depends_on].add(dependent_property)
    
    def _invalidate_dependent_properties(self, property_name: str) -> None:
        """Invalidate cached values of properties that depend on the changed property."""
        if property_name in self._property_dependencies:
            for dependent_prop in self._property_dependencies[property_name]:
                if dependent_prop in self._computed_property_cache:
                    del self._computed_property_cache[dependent_prop]
                    # Don't emit signal here - let notify_property_changed handle it
    
    def get_cached_value(self, property_name: str, compute_func: Callable[[], Any]) -> Any:
        """
        Get a cached value for a computed property.
        
        Args:
            property_name: Name of the computed property
            compute_func: Function to compute the value if not cached
            
        Returns:
            The cached or newly computed value
        """
        if property_name not in self._computed_property_cache:
            self._computed_property_cache[property_name] = compute_func()
        return self._computed_property_cache[property_name]
    
    def invalidate_cache(self, property_name: Optional[str] = None) -> None:
        """
        Invalidate the computed property cache.
        
        Args:
            property_name: Specific property to invalidate, or None for all
        """
        if property_name:
            self._computed_property_cache.pop(property_name, None)
        else:
            self._computed_property_cache.clear()
    
    def bind(self, property_name: str, callback: Callable[[Any], None]) -> object:
        """
        Bind a callback to property changes.
        
        Args:
            property_name: Name of the property to bind to
            callback: Function to call when property changes
            
        Returns:
            Connection object that can be used to disconnect the handler.
            The returned Connection is from self.propertyChanged.connect(handler),
            so callers must use conn.disconnect() to remove the binding.
            
        Example:
            conn = observable.bind("name", lambda v: print(v))
            # Later: conn.disconnect()
        """
        def handler(name: str):
            if name == property_name:
                callback(getattr(self, property_name))
        
        return self.propertyChanged.connect(handler)


class ObservableList(QObject, Generic[T]):
    """
    A list that notifies when items are added, removed, or changed.
    
    Example:
        numbers = ObservableList([1, 2, 3])
        numbers.itemAdded.connect(lambda idx, val: print(f"Added {val} at {idx}"))
        numbers.append(4)
    """
    
    # Signals for list operations
    itemAdded = Signal(int, object)  # index, value
    itemRemoved = Signal(int, object)  # index, value
    itemChanged = Signal(int, object)  # index, new_value
    itemPropertyChanged = Signal(int, object, str)  # index, item, property_name
    listCleared = Signal()
    listReset = Signal()
    
    def __init__(self, initial_data: Optional[List[T]] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._data: List[T] = list(initial_data) if initial_data else []
        self._item_connections: Dict[int, T] = {}
        for i, item in enumerate(self._data):
            self._subscribe_to_item(i, item)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __getitem__(self, index: int) -> T:
        return self._data[index]
    
    def _subscribe_to_item(self, index: int, item: T) -> None:
        """Subscribe to property changes for an ObservableObject item."""
        if isinstance(item, ObservableObject):
            def handler(prop_name, idx=index, itm=item):
                # Look up the current index of the item in case it has moved
                try:
                    current_index = self._data.index(itm)
                except ValueError:
                    current_index = idx
                self._on_item_property_changed(current_index, itm, prop_name)
            self._item_connections[index] = (item, handler)
            item.propertyChanged.connect(handler)
    
    def _unsubscribe_from_item(self, index: int) -> None:
        """Unsubscribe from property changes for an item at given index."""
        if index in self._item_connections:
            item, handler = self._item_connections.pop(index)
            if isinstance(item, ObservableObject):
                try:
                    item.propertyChanged.disconnect(handler)
                except Exception:
                    pass
    
    def _reindex_subscriptions(self, start_index: int) -> None:
        """Reindex subscriptions after items are inserted or removed."""
        old_connections = dict(self._item_connections)
        self._item_connections.clear()
        
        # Re-subscribe all items from start_index onwards
        # The items before start_index remain unchanged
        for i, item in enumerate(self._data):
            if i < start_index and i in old_connections:
                old_item, handler = old_connections[i]
                if old_item is item:
                    # Item hasn't moved, keep the old handler
                    self._item_connections[i] = (item, handler)
                else:
                    # Item has changed, create new subscription
                    self._subscribe_to_item(i, item)
            else:
                # Items from start_index onwards or not in old connections
                # Need to create new subscriptions with updated indices
                self._subscribe_to_item(i, item)
    
    def _on_item_property_changed(self, index: int, item: T, property_name: str) -> None:
        """Handle property changes in items and emit itemPropertyChanged signal."""
        self.itemPropertyChanged.emit(index, item, property_name)
    
    def __setitem__(self, index: int, value: T) -> None:
        self._unsubscribe_from_item(index)
        self._data[index] = value
        self._subscribe_to_item(index, value)
        self.itemChanged.emit(index, value)
    
    def __delitem__(self, index: int) -> None:
        """Remove item at index or slice of items."""
        if isinstance(index, slice):
            indices = range(*index.indices(len(self._data)))
            removed_items = [(i, self._data[i]) for i in sorted(indices, reverse=True)]
            for i, _ in removed_items:
                self._unsubscribe_from_item(i)
            del self._data[index]
            for i, value in reversed(removed_items):
                self.itemRemoved.emit(i, value)
            self._reindex_subscriptions(index.start or 0)
        else:
            self._unsubscribe_from_item(index)
            value = self._data.pop(index)
            self.itemRemoved.emit(index, value)
            self._reindex_subscriptions(index)
    
    def __iter__(self):
        return iter(self._data)
    
    def __contains__(self, item: T) -> bool:
        return item in self._data
    
    def __repr__(self) -> str:
        return f"ObservableList({self._data})"
    
    def append(self, item: T) -> None:
        """Add an item to the end of the list."""
        index = len(self._data)
        self._data.append(item)
        self._subscribe_to_item(index, item)
        self.itemAdded.emit(index, item)
    
    def insert(self, index: int, item: T) -> None:
        """Insert an item at the specified index."""
        self._data.insert(index, item)
        self._subscribe_to_item(index, item)
        self._reindex_subscriptions(index + 1)
        self.itemAdded.emit(index, item)
    
    def remove(self, item: T) -> None:
        """Remove the first occurrence of an item."""
        try:
            index = self._data.index(item)
            self._unsubscribe_from_item(index)
            self._data.pop(index)
            self.itemRemoved.emit(index, item)
            self._reindex_subscriptions(index)
        except ValueError:
            pass
    
    def pop(self, index: int = -1) -> T:
        """Remove and return item at index."""
        # Validate bounds before normalization
        if index >= len(self._data) or index < -len(self._data):
            raise IndexError("pop index out of range")
        
        # Normalize negative index
        if index < 0:
            index = len(self._data) + index
        
        self._unsubscribe_from_item(index)
        value = self._data.pop(index)
        self.itemRemoved.emit(index, value)
        self._reindex_subscriptions(index)
        return value
    
    def clear(self) -> None:
        """Remove all items from the list."""
        for i in list(self._item_connections.keys()):
            self._unsubscribe_from_item(i)
        self._data.clear()
        self.listCleared.emit()
    
    def extend(self, items: List[T]) -> None:
        """Extend the list by appending elements from the iterable."""
        items_list = list(items)
        start_index = len(self._data)
        self._data.extend(items_list)
        for i, item in enumerate(items_list):
            self._subscribe_to_item(start_index + i, item)
            self.itemAdded.emit(start_index + i, item)
    
    def reset(self, new_data: List[T]) -> None:
        """
        Atomically replace the internal storage with new data and emit listReset.
        
        Args:
            new_data: New list data to replace existing data
        """
        for i in list(self._item_connections.keys()):
            self._unsubscribe_from_item(i)
        self._data = list(new_data)
        for i, item in enumerate(self._data):
            self._subscribe_to_item(i, item)
        self.listReset.emit()
    
    def to_list(self) -> List[T]:
        """Return a copy of the underlying list."""
        return self._data.copy()
    
    def index(self, item: T, start: int = 0, end: Optional[int] = None) -> int:
        """Return the index of the first occurrence of item."""
        if end is None:
            end = len(self._data)
        return self._data.index(item, start, end)
    
    def count(self, item: T) -> int:
        """Return the number of occurrences of item."""
        return self._data.count(item)
