# ref: https://docs.python.org/es/3/library/functools.html
import functools
import contextlib
import nucleus.core.exceptions as exceptions

from nucleus.core.types import Callable, Any, Optional, T
from .constants import DB_ISOLATION_LEVEL
from .database import connect
from .types import Connection


class Atomic(contextlib.ContextDecorator):
    """A base class that enables a context manager to also be used as a decorator.

    ref: https://docs.python.org/3/library/contextlib.html
    """

    conn: Connection

    def __enter__(self):
        # Set connection with isolation level to turn off auto commit
        # ref: https://docs.python.org/3.4/library/sqlite3.html
        self.conn = connect(isolation_level=DB_ISOLATION_LEVEL)
        return self.conn

    def __call__(self, f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def _wrapper(*args: Any, **kwargs: Any):
            with self._recreate_cm():  # type: ignore
                # Get extra settings passed to decorator
                return f(self.conn, *args, **kwargs)

        return _wrapper

    def __exit__(self, *_: Any):

        try:
            # If context execution goes fine return results
            self.conn.commit()
        except Exception as e:
            # In case of any issue we should rollback
            self.conn.rollback()
            # Raise an exception to "alert" about the issue.
            # Error should never pass silently.
            # When you raise without arguments, the interpreter looks for the last exception raised and handled.
            # It then acts the same as if you used raise with the most recent
            # exception type, value and traceback.
            raise exceptions.DatabaseTransactionError(
                f"error while trying to commit database transaction: {str(e)}"
            )
        finally:
            # After everything is done we should commit transactions and close
            # the connection.
            self.conn.close()


def connected(f: Optional[Callable[..., Any]] = None) -> Any:
    """Decorate a method call with database.

    :param f: a function to execute in wrapper
    :return: wrapper function
    :rtype: Callable[..., T]
    """

    if not callable(f):
        return Atomic()

    @functools.wraps(f)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get connection a pass it to func call
        return f(connect(), *args, **kwargs)

    # Return wrapper function
    return _wrapper


def atomic(f: Optional[Callable[..., Any]] = None) -> Any:
    """Decorate executions made to database.
    This method enhance the execution of queries/transactions to database adding extra atomic capabilities.

    :param f: This function should contain any query or transaction to db.
    :: decorated function/context for atomic transaction
    :rtype: Callable[..., T]
    :raises DatabaseTransactionError: if database transaction fail
    """
    if callable(f):
        # If atomic is called as decorator
        return Atomic()(f)
    # If atomic is called as context manager
    return Atomic()


__all__ = ["connected", "atomic"]
