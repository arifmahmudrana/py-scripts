"""
Retry Utilities Module.

This module provides a robust decorator for implementing
exponential backoff retry logic. This is particularly
useful for operations that might fail transiently, such as
network requests, API calls, or database connections. The
decorator is configurable, allowing customization of the
number of retries, delay timings, and the specific
exceptions that should trigger a retry.

Main component:
- exponential_backoff_retry: A decorator to automatically
  retry a function upon failure.
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Tuple, Type, TypeVar

# Configure a basic logger for the module.
# The user of this module can configure their own logging setup.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Define a TypeVar to represent the return type of the decorated function.
# This allows us to preserve the original function's return type signature.
_ReturnType = TypeVar("_ReturnType")


def exponential_backoff_retry(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions_to_retry: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., _ReturnType]], Callable[..., _ReturnType]]:
    """
    A decorator that retries a function with an exponential backoff strategy.

    This decorator will re-execute the decorated function if it raises one of
    the specified exceptions. The delay between retries increases exponentially
    and includes a random "jitter" to prevent multiple instances from retrying
    simultaneously (thundering herd problem).

    Args:
        max_retries (int): The maximum number of times to retry the function.
        base_delay (float): The base delay in seconds for the first retry.
        max_delay (float): The maximum possible delay between retries, capping
            the exponential growth.
        exceptions_to_retry (Tuple[Type[Exception], ...]): A tuple of exception
            classes that should trigger a retry. Defaults to `(Exception,)`
            which catches all standard exceptions. It's recommended to specify
            more granular exceptions (e.g., `ConnectionError`).

    Returns:
        Callable: The wrapped function with retry logic.

    Raises:
        The last caught exception if `max_retries` is exceeded.
    """

    def decorator(
        func: Callable[..., _ReturnType],
    ) -> Callable[..., _ReturnType]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> _ReturnType:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_retry as e:
                    retries += 1
                    if retries >= max_retries:
                        logging.error(
                            "Function '%s' failed after %d retries. "
                            "Final exception: %s: %s",
                            func.__name__,
                            max_retries,
                            type(e).__name__,
                            e,
                        )
                        raise

                    backoff_delay = base_delay * (2 ** (retries - 1))
                    jitter = random.uniform(0, 0.5)
                    current_delay = min(backoff_delay + jitter, max_delay)

                    logging.warning(
                        "Exception caught: %s: %s. "
                        "Retrying '%s' in %.2f seconds "
                        "(retry %d/%d).",
                        type(e).__name__,
                        e,
                        func.__name__,
                        current_delay,
                        retries,
                        max_retries,
                    )

                    time.sleep(current_delay)

            raise RuntimeError("Exited retry loop unexpectedly.")

        return wrapper

    return decorator


# --- Example Usage ---
if __name__ == "__main__":

    def make_flaky_api():
        """Factory that returns a flaky API function with internal counter."""
        call_counter = {"count": 0}

        @exponential_backoff_retry(
            max_retries=4,
            exceptions_to_retry=(ValueError,),
        )
        def fetch_data_from_flaky_api():
            """
            Simulates fetching data from an API
            that fails before succeeding.
            """
            call_counter["count"] += 1
            print(
                f"Attempt {call_counter['count']}: Trying to fetch data from API..."  # noqa: E501
            )
            if call_counter["count"] < 4:
                raise ValueError("API is not available right now.")
            print("Success! API returned data.")
            return {"data": "some important information"}

        return fetch_data_from_flaky_api

    print("--- Running example that should succeed after a few retries ---")
    try:
        result = make_flaky_api()()
        print(f"\nFinal result received: {result}")
    except ValueError as e:
        print(f"\nFunction failed unexpectedly: {e}")

    print("\n" + "-" * 60 + "\n")

    def make_permanent_fail():
        """Factory that returns a permanently failing function."""
        call_counter = {"count": 0}

        @exponential_backoff_retry(
            max_retries=3,
            base_delay=0.5,
            exceptions_to_retry=(OSError,),
        )
        def read_file_that_never_exists():
            """Simulates trying to read a file that will always fail."""
            call_counter["count"] += 1
            print(f"Attempt {call_counter['count']}: Trying to read file...")
            raise OSError("Permanent file access error.")

        return read_file_that_never_exists

    print("--- Running example that is expected to fail permanently ---")
    try:
        make_permanent_fail()()
    except OSError as e:
        print(
            f"\nFunction failed after all retries as expected. Final error: {e}"  # noqa: E501
        )
