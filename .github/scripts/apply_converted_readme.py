# noqa: D100
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "tomlkit",
# ]
# ///

from pathlib import Path
from typing import TYPE_CHECKING

from tomlkit.items import AbstractTable
from tomlkit.toml_file import TOMLFile

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

    from tomlkit.container import Container
    from tomlkit.items import Item
    from tomlkit.toml_document import TOMLDocument

__all__: "Sequence[str]" = ()

PYPROJECT_FILE_PATH: "Final[TOMLFile]" = TOMLFile(
    Path(__file__).parent.parent.parent / "pyproject.toml"
)
README_FILE_PATH: "Final[Path]" = Path(__file__).parent.parent.parent / "README.md"


def main() -> int:
    project_config: TOMLDocument = PYPROJECT_FILE_PATH.read()

    project_table: Item | Container = project_config["project"]
    if not isinstance(project_table, AbstractTable):
        raise TypeError

    readme_table: Item | Container = project_table["readme"]
    if not isinstance(readme_table, AbstractTable):
        raise TypeError

    readme_table["text"] = f"{README_FILE_PATH.read_text().strip()}\n"

    PYPROJECT_FILE_PATH.write(project_config)

    README_FILE_PATH.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
