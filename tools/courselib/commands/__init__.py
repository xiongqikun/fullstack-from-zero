"""Command plug-ins: one module per command.

Each module ``<name>.py`` exposes ``register(subparsers)`` and
``run(args) -> int``.  ``courselib.cli`` discovers the modules of this package
at start-up; adding a command means adding a file here, nothing else.

See docs/authoring/command-plugins.md.
"""
