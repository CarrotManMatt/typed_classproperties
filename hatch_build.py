"""Project build script to convert this project's AsciiDoc README file to Markdown format."""

import inspect
import os
import shutil
import subprocess
import sys
import warnings
from collections.abc import Collection, Iterable
from pathlib import Path
from typing import TYPE_CHECKING

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from hatchling.metadata.plugin.interface import MetadataHookInterface

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import Final

    if sys.version_info >= (3, 11):
        from typing import LiteralString
    else:
        from typing_extensions import LiteralString

__all__: "Sequence[str]" = ("DowndocCustomReadmeMetadataHook",)


class DowndocCustomReadmeMetadataHook(MetadataHookInterface):
    """Hatchling metadata hook to convert this project's AsciiDoc file to Markdown format."""

    @classmethod
    def _get_readme_path(cls, config: "Mapping[str, object]", root: "Path") -> "Path":
        readme_path: str = ""

        config_name: LiteralString
        for config_name in ("readme-path", "path"):
            try:
                raw_readme_path: object = config[config_name]
            except KeyError:
                continue

            if not isinstance(raw_readme_path, str):
                INVALID_PATH_TYPE_MESSAGE: str = (
                    f"{cls.PLUGIN_NAME}.{config_name} must be a string."
                )
                raise TypeError(INVALID_PATH_TYPE_MESSAGE)

            readme_path = raw_readme_path
            break

        return root / (readme_path if readme_path else "README.adoc")

    @classmethod
    def _is_project_misconfigured(cls, metadata: "Mapping[str, object]") -> bool:
        if "readme" in metadata:
            return True

        dynamic: object | Collection[object] = metadata.get("dynamic", [])
        if not isinstance(dynamic, Collection):
            INVALID_DYNAMIC_TYPE_MESSAGE: Final[str] = (
                "'dynamic' field within `[project]` must be an array."
            )
            raise TypeError(INVALID_DYNAMIC_TYPE_MESSAGE)

        return "readme" not in dynamic

    @classmethod
    def _perform_conversion(cls, readme_path: "Path") -> str:
        downdoc_executable: str | None = shutil.which("downdoc")
        if downdoc_executable is None:
            DOWNDOC_NOT_INSTALLED_MESSAGE: Final[str] = (
                "The downdoc executable could not be found. "
                "It can be installed with `uv tool install Pydowndoc-bin`)."
            )
            raise OSError(DOWNDOC_NOT_INSTALLED_MESSAGE)

        return subprocess.run(
            (downdoc_executable, "--output", "-", "--", str(readme_path)),
            capture_output=True,
            check=True,
            text=True,
        ).stdout

    @override
    def update(self, metadata: dict[str, object]) -> None:
        if (
            ("update", __file__)
            in ((frame.function, frame.filename) for frame in inspect.stack()[1:])
        ):  # SOURCE: https://github.com/flying-sheep/hatch-docstring-description/blob/2dfbfba2c48e112825fdd0cb7c37035d5598224c/src/hatch_docstring_description/read_description.py#L21
            return

        if self._is_project_misconfigured(metadata):
            MISSING_DYNAMIC_MESSAGE: Final[str] = (
                "You must add 'readme' to your `dynamic` fields and not to `[project]`."
            )
            raise TypeError(MISSING_DYNAMIC_MESSAGE)

        readme_path: Path = self._get_readme_path(self.config, Path(self.root))

        if not readme_path.is_file():
            raise FileNotFoundError(str(readme_path))

        try:
            metadata["readme"] = {
                "content-type": "text/markdown",
                "text": self._perform_conversion(readme_path),
            }
        except OSError as e:
            if (
                "/renovate/" not in os.environ["PWD"]
                and os.getenv("SKIP_MISSING_DOWNDOC", "False") != "True"
            ):
                raise e from e

            warnings.warn(
                (
                    f"{e} "
                    "This package will be built without any README content, "
                    "it MUST NOT BE UPLOADED to any package distribution platform "
                    "(E.g. PyPI)."
                ),
                stacklevel=1,
            )
            metadata["readme"] = {
                "content-type": "text/plain",
                "text": (
                    "Missing README content. "
                    "DO NOT UPLOAD this package to any distribution platform (E.g. PyPI).\n\n"
                    "If you are seeing this message on a package distribution platform, "
                    "please contact the project's maintainer."
                ),
            }

        if isinstance(metadata["dynamic"], Iterable):
            metadata["dynamic"] = [value for value in metadata["dynamic"] if value != "readme"]
