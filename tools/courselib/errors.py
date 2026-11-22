"""Exception types and exit codes shared by every command.

Exit codes follow plan I4:

- 0   passed / ok
- 1   not yet (also: the learner cancelled a prompt)
- 2   checker problem (the tool, a lesson module or the environment is broken)
- 64  usage error
"""

EXIT_OK = 0
EXIT_NOT_YET = 1
EXIT_PROBLEM = 2
EXIT_USAGE = 64


class CourseError(Exception):
    """Base class of every error the tool raises on purpose."""


class Cancelled(CourseError):
    """The learner pressed Ctrl+C or sent end-of-file at a prompt."""


class UsageProblem(CourseError):
    """The command was called in a way that cannot work (exit code 64).

    ``message`` is a complete Chinese sentence for the learner.
    """

    def __init__(self, message, suggestion=""):
        CourseError.__init__(self, message)
        self.message = message
        self.suggestion = suggestion


class Refused(CourseError):
    """The tool declined to do something (exit code 1).

    Used for safety refusals, for example a practice folder that would have
    to be deleted but does not carry the tool's marker.  ``message`` is a
    complete Chinese explanation that names what to do instead.
    """

    def __init__(self, message):
        CourseError.__init__(self, message)
        self.message = message


class ToolTrouble(CourseError):
    """The tool, a lesson module or the environment is broken (exit code 2).

    The learner is never blamed for this.  ``summary`` is one Chinese
    sentence; ``detail`` is technical text for the tutor (may be English);
    ``recovery`` is an optional Chinese instruction that the learner or the
    tutor can follow; ``where`` names a file and line when known.
    """

    def __init__(self, summary, detail="", recovery="", where=""):
        CourseError.__init__(self, summary)
        self.summary = summary
        self.detail = detail
        self.recovery = recovery
        self.where = where


class StateTrouble(ToolTrouble):
    """A state file under learner/ is corrupt or unreadable."""


class CheckStop(Exception):
    """Internal control flow: a check asked to stop early (``ctx.stop()``).

    Deliberately not a CourseError: only the check runner catches it.
    """
