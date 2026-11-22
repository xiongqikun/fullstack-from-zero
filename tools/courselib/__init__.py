"""courselib: the library behind ``tools/course.py``.

Standard library only; runs unchanged on Python 3.9 through 3.14.

Layout (one concern per module):

- ``errors``     exception types and exit codes
- ``ui``         console output, prompts, colours, CJK-aware padding
- ``app``        the per-run ``App`` object (paths, clock, environment)
- ``store``      atomic state store (state.json, log.jsonl, last-result.json)
- ``catalog``    lesson discovery and safe loading
- ``syllabus``   the fixed syllabus of the plan (lessons, stations, rules, gates)
- ``normalize``  normalisation of learner answers
- ``gitread``    read-only Git access for checks
- ``gitwrite``   Git for scenario builders (isolated, signing switched off)
- ``context``    the check context handed to lesson check functions
- ``runner``     the guarded check runner and the three outcomes
- ``progress``   station records, sessions, ordering
- ``hints``      the four hint levels
- ``schedule``   Leitner boxes for review items
- ``review``     what a review session serves (order, cap, return routine, redos)
- ``scenario``   the scenario builder context and safe build/reset
- ``status``     the status report and PROGRESS.md
- ``journal``    journal entries
- ``rulecards``  parser for rules.md
- ``validate``   the builders' validator
- ``cmdkit``     helpers for command plug-ins
- ``cli``        argument parsing, plug-in discovery, top-level error handling
- ``commands/``  one plug-in module per command

The lesson-facing API is documented in ``docs/authoring/tool-api.md``; the
plug-in protocol in ``docs/authoring/command-plugins.md``.
"""

__version__ = "1.0.0"

#: Version of the lesson-facing API described in docs/authoring/tool-api.md.
API_VERSION = 1
