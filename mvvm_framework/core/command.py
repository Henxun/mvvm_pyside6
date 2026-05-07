"""
Command implementation for MVVM framework.
Implements the Command pattern for handling user actions.
"""

from typing import Any, Callable, Optional
from PySide6.QtCore import QObject, Signal


class Command(QObject):
    """
    Command class for MVVM pattern.
    
    Represents an action that can be executed, with optional
    enable/disable logic and execution state tracking.
    
    Example:
        save_command = Command(
            execute=lambda: save_data(),
            can_execute=lambda: not is_saving,
            executed=lambda: print("Saved!")
        )
        
        # In a ViewModel:
        self._save_command = Command(self.save, lambda: self.can_save)
        
        @property
        def save_command(self) -> Command:
            return self._save_command
    """
    
    # Signal emitted when command execution state changes
    canExecuteChanged = Signal(bool)
    # Signal emitted after command is executed
    executed = Signal()
    # Signal emitted before command execution
    executing = Signal()
    # Signal emitted if execution fails
    executionFailed = Signal(str)  # error message
    
    def __init__(
        self,
        execute: Callable[[], Any],
        can_execute: Optional[Callable[[], bool]] = None,
        parent: Optional[QObject] = None
    ):
        """
        Initialize a Command.
        
        Args:
            execute: Function to execute when command is invoked
            can_execute: Optional function to determine if command can execute
            parent: Parent QObject
        """
        super().__init__(parent)
        self._execute = execute
        self._can_execute = can_execute
        self._is_executing = False
        self._last_error: Optional[str] = None
    
    @property
    def is_executing(self) -> bool:
        """Check if the command is currently executing."""
        return self._is_executing
    
    @property
    def last_error(self) -> Optional[str]:
        """Get the last error message if execution failed."""
        return self._last_error
    
    def can_execute(self) -> bool:
        """
        Check if the command can be executed.
        
        Returns:
            True if the command can execute, False otherwise
        """
        if self._is_executing:
            return False
        
        if self._can_execute:
            try:
                return self._can_execute()
            except Exception as e:
                self._last_error = f"Error in can_execute: {e!s}"
                return False
        
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the command.
        
        Args:
            *args: Arguments to pass to the execute function
            **kwargs: Keyword arguments to pass to the execute function
            
        Returns:
            The result of the execute function, or None if execution failed
        """
        if not self.can_execute():
            return None
        
        self._is_executing = True
        self._last_error = None
        self.executing.emit()
        
        try:
            result = self._execute(*args, **kwargs)
            self.executed.emit()
            return result
        except Exception as e:
            self._last_error = f"{e!s}"
            self.executionFailed.emit(f"{e!s}")
            raise  # Re-raise the exception instead of silently returning
        finally:
            self._is_executing = False
            self.canExecuteChanged.emit(self.can_execute())
    
    def notify_can_execute_changed(self) -> None:
        """Notify that the can_execute state has changed."""
        self.canExecuteChanged.emit(self.can_execute())
    
    def refresh(self) -> None:
        """Refresh the command state by re-evaluating can_execute."""
        self.notify_can_execute_changed()


class AsyncCommand(Command):
    """
    Command that executes asynchronously.
    
    Useful for long-running operations that shouldn't block the UI.
    """
    
    # Signal emitted when async execution completes
    completed = Signal()
    
    def __init__(
        self,
        execute: Callable[[], Any],
        can_execute: Optional[Callable[[], bool]] = None,
        on_completed: Optional[Callable[[], None]] = None,
        on_failed: Optional[Callable[[str], None]] = None,
        parent: Optional[QObject] = None
    ):
        """
        Initialize an AsyncCommand.
        
        Args:
            execute: Async function to execute
            can_execute: Optional function to determine if command can execute
            on_completed: Optional callback for successful completion
            on_failed: Optional callback for failure
            parent: Parent QObject
        """
        super().__init__(execute, can_execute, parent)
        self._on_completed = on_completed
        self._on_failed = on_failed
    
    async def execute_async(self, *args, **kwargs) -> Any:
        """
        Execute the command asynchronously.
        
        Args:
            *args: Arguments to pass to the execute function
            **kwargs: Keyword arguments to pass to the execute function
            
        Returns:
            The result of the execute function
        """
        if not self.can_execute():
            return None
        
        self._is_executing = True
        self._last_error = None
        self.executing.emit()
        
        try:
            # Check if execute is a coroutine function
            import inspect
            if inspect.iscoroutinefunction(self._execute):
                result = await self._execute(*args, **kwargs)
            else:
                result = self._execute(*args, **kwargs)
            
            self.executed.emit()
            self.completed.emit()
            
            if self._on_completed:
                self._on_completed()
            
            return result
        except Exception as e:
            self._last_error = f"{e!s}"
            self.executionFailed.emit(f"{e!s}")
            
            if self._on_failed:
                self._on_failed(f"{e!s}")
            
            return None
        finally:
            self._is_executing = False
            self.canExecuteChanged.emit(self.can_execute())
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the async command by scheduling it on the event loop.
        
        This override ensures that when called via Command.execute (e.g., from bind_command),
        the coroutine actually runs on the event loop.
        
        Args:
            *args: Arguments to pass to the execute function
            **kwargs: Keyword arguments to pass to the execute function
            
        Returns:
            None (the coroutine is scheduled asynchronously)
        """
        import asyncio
        
        if not self.can_execute():
            return None
        
        # Schedule the async execution
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create and schedule the coroutine
        coro = self.execute_async(*args, **kwargs)
        asyncio.ensure_future(coro, loop=loop)
        return None


class ParameterizedCommand(Command):
    """
    Command that accepts a parameter during execution.
    
    Example:
        delete_command = ParameterizedCommand(
            execute=lambda item: delete_item(item),
            can_execute=lambda item: item is not None
        )
        
        # Execute with parameter
        delete_command.execute(selected_item)
    """
    
    def can_execute_with(self, parameter: Any) -> bool:
        """
        Check if the command can execute with the given parameter.
        
        Args:
            parameter: The parameter to check
            
        Returns:
            True if the command can execute with the parameter
        """
        if self._is_executing:
            return False
        
        if self._can_execute:
            try:
                return self._can_execute(parameter)
            except Exception as e:
                self._last_error = f"Error in can_execute: {str(e)}"
                return False
        
        return True
    
    def execute_with(self, parameter: Any) -> Any:
        """
        Execute the command with a parameter.
        
        Args:
            parameter: Parameter to pass to the execute function
            
        Returns:
            The result of the execute function
        """
        if not self.can_execute_with(parameter):
            return None
        
        self._is_executing = True
        self._last_error = None
        self.executing.emit()
        
        try:
            result = self._execute(parameter)
            self.executed.emit()
            return result
        except Exception as e:
            self._last_error = f"{e!s}"
            self.executionFailed.emit(f"{e!s}")
            raise
        finally:
            self._is_executing = False
            self.canExecuteChanged.emit(self.can_execute_with(parameter))
