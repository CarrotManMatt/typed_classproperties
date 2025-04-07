"""Full test suite for 'typed_classproperties' library."""

import abc
import sys
from typing import TYPE_CHECKING

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from typed_classproperties import cached_classproperty, classproperty

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

__all__: "Sequence[str]" = ("TestCachedClassProperty", "TestClassProperty")


class BaseTestClassProperty(abc.ABC):  # noqa: B024
    """Abstract base class for all test classes."""

    @classmethod
    def _get_cls_definition(cls, test_value: object) -> "Any":  # noqa: ANN401
        class _HolderClass:
            cached_prop_exec_count = 0

            @classproperty
            def held_value(cls) -> object:
                return test_value

            @cached_classproperty
            def cached_held_value(cls):  # noqa: ANN202
                cls.cached_prop_exec_count += 1
                return test_value

        return _HolderClass


class TestClassProperty(BaseTestClassProperty):
    """Test the `classproperty` decorator."""

    def test_classproperty_class(self) -> None:
        """Test that a classproperty correctly returns its value from a class."""
        assert self._get_cls_definition(1000).held_value == 1000

    def test_classproperty_instance(self) -> None:
        """Test that a classproperty correctly returns its value from an instance."""
        assert self._get_cls_definition(2000)().held_value == 2000

    def test_typed_subclasses(self) -> None:
        """Test that subclasses can override classproperties."""

        class _BaseClass(abc.ABC):
            @classproperty
            @abc.abstractmethod
            def base_method(cls) -> str:
                pass

        class _SubClass(_BaseClass):
            @classproperty
            @override
            def base_method(cls) -> str:
                return ""


class TestCachedClassProperty(BaseTestClassProperty):
    """Test the `cached_classproperty` decorator."""

    def test_cached_classproperty_class(self) -> None:
        """Test that a `cached_classproperty` correctly returns its value from a class."""
        created_class: Any = self._get_cls_definition(3000)
        assert created_class.cached_prop_exec_count == 0
        assert created_class.cached_held_value == 3000
        assert created_class.cached_prop_exec_count == 1

    def test_cached_classproperty_executed_once(self) -> None:
        """Test that a `cached_classproperty` correctly returns the cached value."""
        created_class: Any = self._get_cls_definition(4000)
        assert created_class.cached_prop_exec_count == 0
        assert created_class.cached_held_value == 4000
        assert created_class.cached_prop_exec_count == 1
        assert created_class.cached_held_value == 4000
        assert created_class.cached_prop_exec_count == 1

    def test_cached_classproperty_delete_cache(self) -> None:
        """Test that removing a `cached_classproperty`'s cached value functions correctly."""
        created_class: Any = self._get_cls_definition(5000)
        assert created_class.cached_prop_exec_count == 0
        assert created_class.cached_held_value == 5000
        assert created_class.cached_prop_exec_count == 1
        cached_classproperty.remove_cached_value(created_class, "cached_held_value")
        assert created_class.cached_held_value == 5000
        assert created_class.cached_prop_exec_count == 2

    def test_cached_classproperty_instance(self) -> None:
        """Test that a `cached_classproperty` returns the correct value from an instance."""
        created_instance: Any = self._get_cls_definition(6000)()
        assert created_instance.cached_prop_exec_count == 0
        assert created_instance.cached_held_value == 6000
        assert created_instance.cached_prop_exec_count == 1

    def test_cached_classproperty_instance_with_deletion(self) -> None:
        """Test that a `cached_classproperty` can delete its cached value from an instance."""
        created_class: Any = self._get_cls_definition(7000)
        created_instance: Any = created_class()
        assert created_instance.cached_prop_exec_count == 0
        assert created_instance.cached_held_value == 7000

        created_instance.cached_held_value = 750
        assert created_class.cached_held_value == 7000
        assert created_instance.cached_held_value == 750

        del created_instance.cached_held_value
        assert created_class.cached_held_value == 7000
        assert created_class.cached_prop_exec_count == 1

    def test_cached_classproperty_executed_once_instance(self) -> None:
        """Test that a `cached_classproperty` returns its value from an instance only once."""
        created_instance: Any = self._get_cls_definition(8000)()
        assert created_instance.cached_prop_exec_count == 0
        assert created_instance.cached_held_value == 8000
        assert created_instance.cached_prop_exec_count == 1
        assert created_instance.cached_held_value == 8000
        assert created_instance.cached_prop_exec_count == 1

    def test_cached_classproperty_executed_once_instance_cls_share_same_cached_val(
        self,
    ) -> None:
        """Test that a `cached_classproperty` returns its value from a shared class once."""
        created_class: Any = self._get_cls_definition(9000)
        created_instance: Any = created_class()
        assert created_instance.cached_prop_exec_count == 0
        assert created_instance.cached_held_value == 9000
        assert created_instance.cached_prop_exec_count == 1
        assert created_instance.cached_held_value == 9000
        assert created_instance.cached_prop_exec_count == 1

        assert created_class.cached_prop_exec_count == 1
        assert created_class.cached_held_value == 9000
        assert created_class.cached_prop_exec_count == 1

        created_instance = created_class()
        assert created_instance.cached_prop_exec_count == 1
        assert created_instance.cached_held_value == 9000
        assert created_instance.cached_prop_exec_count == 1
