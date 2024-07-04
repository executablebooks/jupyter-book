"""Plugin aware click command Group."""
from typing import Any, Iterable, List, Set

import click

if __import__("sys").version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def get_entry_point_names(group: str) -> List[str]:
    return [ep.name for ep in entry_points(group=group)]


def load_entry_point(group: str, name: str) -> Any:
    eps = [ep for ep in entry_points(group=group) if ep.name == name]
    if not eps:
        raise KeyError(f"Entry-point {group}:{name}")
    return eps[0].load()


class PluggableGroup(click.Group):
    """A click command group that finds and loads plugin commands lazily."""

    def __init__(self, *, entry_point_group: str, **kwargs: Any):
        """Initialize with entry point group."""
        self.exclude_external_plugins = False
        self._entry_point_group: str = entry_point_group
        self._use_internal: Set[str] = kwargs.pop("use_internal", set())
        super().__init__(**kwargs)

    def list_commands(self, ctx: click.Context) -> Iterable[str]:
        """Add entry point names of available plugins to the command list."""
        subcommands = super().list_commands(ctx)

        if not self.exclude_external_plugins:
            subcommands.extend(get_entry_point_names(self._entry_point_group))

        return subcommands

    def get_command(self, ctx: click.Context, name: str) -> click.BaseCommand:
        """Try to load a subcommand from entry points, else defer to super."""
        command = None
        if self.exclude_external_plugins or name in self._use_internal:
            command = super().get_command(ctx, name)
        else:
            try:
                command = load_entry_point(self._entry_point_group, name)
            except KeyError:
                command = super().get_command(ctx, name)
        return command
