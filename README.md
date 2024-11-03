# typed_classproperties

Typed decorators for classproperty and cached_classproperty.

Python 3 compatible only. No dependencies.

## Installation

This package is hosted on PYPI and can be installed using `uv` or `pip`. E.g.

```bash
uv add typed_classproperties
```

```bash
pip install typed_classproperties
```

## Example usage

```python
from typing import override

from typed_classproperties import classproperty, cached_classproperty


class Foo:
    @override
    def __init__(self, bar: str) -> None:
        self.bar: str = bar

    @classproperty
    def BAR(cls) -> int:
        return 1


assert Foo.BAR == 1
assert Foo(bar="one").BAR == 1


class CachedFoo:
    @override
    def __init__(self, bar: str) -> None:
        self.bar: str = bar

    @cached_classproperty
    def BAR(cls) -> int:
        print("This will be executed only once")
        return 1


assert CachedFoo.BAR == 1
assert CachedFoo(bar="bar").FOO == 1
```

## Tests

See [`tests.py`](tests.py) for usage examples and expected behaviour.

To run tests:

```bash
uv run --group test pytest
```

## Credits

Credits to Denis Ryzhkov on Stackoverflow for the implementation of classproperty:
https://stackoverflow.com/a/13624858/1280629
