"""Dependency Injection Container for Syngex.

Provides centralized component registration and lifecycle management
with support for singleton and scoped lifetimes.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

T = TypeVar("T")


class ComponentRegistration:
    """Represents a registered component in the container."""

    def __init__(
        self,
        cls: Type[Any],
        singleton: bool = True,
        dependencies: Optional[List[str]] = None,
        factory: Optional[Callable[..., Any]] = None,
    ):
        """Initialize component registration.

        Args:
            cls: The class to register
            singleton: If True, only one instance is created and reused
            dependencies: List of component names this component depends on
            factory: Optional factory function to create instances
        """
        self.cls = cls
        self.singleton = singleton
        self.dependencies = dependencies or []
        self.factory = factory
        self.instance: Optional[Any] = None


class SyngexContainer:
    """
    Dependency Injection Container for Syngex.

    Provides centralized component registration and lifecycle management.

    Example:
        ```python
        container = SyngexContainer()
        container.register(GEXCalculator, singleton=True)
        container.register(StrategyEngine, dependencies=['GEXCalculator'])
        orchestrator = container.resolve(SyngexOrchestrator)
        ```
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the container.

        Args:
            logger: Optional logger for container events
        """
        self._registrations: Dict[str, ComponentRegistration] = {}
        self._instances: Dict[str, Any] = {}
        self._logger = logger or logging.getLogger(__name__)

    def register(
        self,
        cls: Type[T],
        name: Optional[str] = None,
        singleton: bool = True,
        dependencies: Optional[List[str]] = None,
        factory: Optional[Callable[..., T]] = None,
        **kwargs: Any,
    ) -> "SyngexContainer":
        """Register a component with the container.

        Args:
            cls: The class to register
            name: Optional name for the registration (defaults to class name)
            singleton: If True, only one instance is created and reused
            dependencies: List of component names this component depends on
            factory: Optional factory function to create instances
            **kwargs: Additional keyword arguments for the class/factory

        Returns:
            Self for method chaining

        Example:
            ```python
            container.register(GEXCalculator, singleton=True)
            container.register(StrategyEngine, dependencies=['GEXCalculator'])
            ```
        """
        reg_name = name or cls.__name__
        self._registrations[reg_name] = ComponentRegistration(
            cls=cls,
            singleton=singleton,
            dependencies=dependencies or [],
            factory=factory,
        )
        # Store any additional kwargs
        if kwargs:
            self._registrations[reg_name]._kwargs = kwargs  # type: ignore

        self._logger.debug(f"Registered component: {reg_name} (singleton={singleton})")
        return self

    def register_instance(
        self,
        name: str,
        instance: Any,
        dependencies: Optional[List[str]] = None,
    ) -> "SyngexContainer":
        """Register a pre-created instance with the container.

        Args:
            name: Name for the registration
            instance: The instance to register
            dependencies: List of component names this instance depends on

        Returns:
            Self for method chaining
        """
        reg = ComponentRegistration(
            cls=type(instance),
            singleton=True,
            dependencies=dependencies or [],
        )
        reg.instance = instance
        self._registrations[name] = reg
        self._instances[name] = instance

        self._logger.debug(f"Registered instance: {name}")
        return self

    def unregister(self, name: str) -> bool:
        """Unregister a component.

        Args:
            name: Name of the component to unregister

        Returns:
            True if component was unregistered, False if not found
        """
        if name in self._registrations:
            del self._registrations[name]
            if name in self._instances:
                del self._instances[name]
            self._logger.debug(f"Unregistered component: {name}")
            return True
        return False

    def resolve(
        self,
        cls: Type[T],
        name: Optional[str] = None,
        dependencies: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> T:
        """Resolve a component from the container.

        Args:
            cls: The class to resolve
            name: Optional name override
            dependencies: Optional dict of pre-resolved dependencies
            **kwargs: Additional keyword arguments

        Returns:
            Resolved instance of the class

        Raises:
            ValueError: If component is not registered
        """
        reg_name = name or cls.__name__

        if reg_name not in self._registrations:
            raise ValueError(f"Component not registered: {reg_name}")

        registration = self._registrations[reg_name]

        # Return cached singleton if available
        if registration.singleton and reg_name in self._instances:
            self._logger.debug(f"Returning cached instance: {reg_name}")
            return self._instances[reg_name]  # type: ignore

        # Resolve dependencies
        resolved_deps = self._resolve_dependencies(registration, dependencies or {}, **kwargs)

        # Create instance
        if registration.factory:
            instance = registration.factory(**resolved_deps)
        else:
            instance = registration.cls(**resolved_deps)

        # Cache singleton
        if registration.singleton:
            self._instances[reg_name] = instance

        self._logger.debug(f"Resolved component: {reg_name}")
        return instance  # type: ignore

    def resolve_all(self) -> Dict[str, Any]:
        """Resolve all registered components.

        Returns:
            Dict of all resolved components by name
        """
        results: Dict[str, Any] = {}
        for name in self._registrations:
            try:
                reg = self._registrations[name]
                results[name] = self.resolve(reg.cls, name=name)
            except Exception as e:
                self._logger.error(f"Failed to resolve {name}: {e}")
        return results

    def _resolve_dependencies(
        self,
        registration: ComponentRegistration,
        explicit_deps: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Resolve dependencies for a component.

        Args:
            registration: The component registration
            explicit_deps: Pre-resolved dependencies
            **kwargs: Additional keyword arguments

        Returns:
            Dict of resolved dependencies
        """
        resolved: Dict[str, Any] = {}

        # Get constructor signature
        import inspect
        sig = inspect.signature(registration.cls.__init__)

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Check for explicit dependency override
            if param_name in explicit_deps:
                resolved[param_name] = explicit_deps[param_name]
                continue

            # Check for kwargs override
            if param_name in kwargs:
                resolved[param_name] = kwargs[param_name]
                continue

            # Check if this is a registered dependency
            if param_name in self._registrations:
                resolved[param_name] = self.resolve(
                    self._registrations[param_name].cls,
                    name=param_name,
                )
                continue

            # Check for default value
            if param.default is not inspect.Parameter.empty:
                resolved[param_name] = param.default
                continue

            # Required parameter with no default - try to resolve from dependencies list
            if registration.dependencies and param_name in registration.dependencies:
                if param_name in self._registrations:
                    resolved[param_name] = self.resolve(
                        self._registrations[param_name].cls,
                        name=param_name,
                    )

        return resolved

    def get(self, name: str) -> Optional[Any]:
        """Get a registered component by name.

        Args:
            name: Name of the component

        Returns:
            The component instance or None if not found
        """
        if name in self._instances:
            return self._instances[name]

        if name in self._registrations:
            reg = self._registrations[name]
            if reg.singleton and reg.instance:
                return reg.instance

        return None

    def has(self, name: str) -> bool:
        """Check if a component is registered.

        Args:
            name: Name of the component

        Returns:
            True if registered
        """
        return name in self._registrations

    def clear(self) -> None:
        """Clear all registrations and instances."""
        self._registrations.clear()
        self._instances.clear()
        self._logger.debug("Container cleared")

    @property
    def registrations(self) -> Dict[str, ComponentRegistration]:
        """Get all registrations."""
        return self._registrations.copy()

    @property
    def instances(self) -> Dict[str, Any]:
        """Get all cached instances."""
        return self._instances.copy()
