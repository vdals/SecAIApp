"""
Utilities for working with FastAPI dependencies
"""
from typing import Callable, Any, TypeVar, Generic, Type, cast
import inspect

T = TypeVar('T')

class Stub(Generic[T]):
    """    
    This solves the problem when FastAPI sees args/kwargs in the signature of the dependency
    and adds them as required parameters in the OpenAPI schema.
    """
    def __init__(self, dependency: Callable[..., T] | Type[T]) -> None:
        """Save our dependency."""
        self._dependency = dependency

    async def __call__(self, *args: Any, **kwargs: Any) -> T:  # type: ignore[override]
        """
        Returns the real dependency, but without analyzing its signature.
        Supports both synchronous and asynchronous dependencies.
        """
        # Remove parameters 'args' and 'kwargs' that may have come from the query string
        kwargs.pop("args", None)
        kwargs.pop("kwargs", None)

        if callable(self._dependency) and not isinstance(self._dependency, type):
            result = self._dependency(*args, **kwargs)
        else:
            result = cast(T, self._dependency(*args, **kwargs))

        if inspect.isawaitable(result):
            return await result
        return result 