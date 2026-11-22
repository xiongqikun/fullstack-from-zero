"""The state store: learner/state.json, learner/log.jsonl, learner/last-result.json.

Rules (plan I5):

- Every write of state.json and last-result.json is atomic: the text goes to a
  temporary file in the same folder, is flushed to disk, and is then renamed
  over the target.  A crash leaves either the old file or the new one.
- log.jsonl is append-only: one JSON object per line, each with a ``ts``.
- A missing state.json is created.  If log.jsonl holds earlier records the
  state is rebuilt from them, because every change of state is also written to
  the log as a small patch (an event of type ``state``).
- A corrupt state.json is never overwritten.  Loading raises ``StateTrouble``
  with an instruction the learner can follow.

State schema, version 1::

    {
      "schema": 1,
      "stations":  {"1.6a": {"status": "open|passed|assisted", "attempts": 0,
                             "first_pass": null, "last_pass": null,
                             "last_attempt": null, "highest_hint": 0,
                             "last_hint": null, "confidence": null,
                             "redo": {"after": "YYYY-MM-DD",
                                      "before": "YYYY-MM-DD", "done": null}}},
      "review":    {"1.6-r1": {"box": 1, "due": "YYYY-MM-DD", "history": []}},
      "exams":     {"gate-b": {"1.6-x1": {"form": "A", "result": "pass",
                                           "date": "YYYY-MM-DD"}}},
      "sessions":  [{"date": "YYYY-MM-DD", "minutes": 0,
                     "start": "...", "last": "..."}],
      "decisions": {"commit_signing": "off"}
    }

Unknown keys are preserved, so later versions can add fields.
"""

import copy
import json
import os

from .errors import StateTrouble, ToolTrouble

SCHEMA = 1
SECTIONS = (("stations", dict), ("review", dict), ("exams", dict),
            ("sessions", list), ("decisions", dict))

TEXT = {
    "corrupt": "进度文件 learner/state.json 读不出来了（{reason}）。",
    "corrupt_recovery": (
        "先别删这个文件。在学习工作区里运行 mv learner/state.json learner/state.json.bad"
        "（把它改名为 state.json.bad），然后再运行一次 python3 tools/course.py status："
        "工具会按 learner/log.jsonl 里的记录重建进度。"
    ),
    "newer": "进度文件 learner/state.json 是更新版本的工具写的（schema {found}，这个工具只认到 {known}）。",
    "newer_recovery": "请导师把 tools/ 更新到最新版本，再运行一次。不要手动改这个文件。",
    "unreadable": "读不了 {name}（{reason}）。",
    "unwritable": "写不了 {name}（{reason}）。",
    "unwritable_recovery": "检查 learner 文件夹是不是还在、有没有写入权限、磁盘有没有满，然后再运行一次。",
    "read_only": "进度文件 {name} 被设成了只读，工具不会替换它。",
    "read_only_recovery": "这个文件是工具自己管的。把这一段发给导师，确认没问题后再把它改回可写。",
    "reason_json": "不是合法的 JSON",
    "reason_shape": "内容的结构不对：{what}",
}

_MISSING = object()


def empty_state():
    """A fresh state: nothing passed, nothing scheduled."""
    return {"schema": SCHEMA, "stations": {}, "review": {}, "exams": {},
            "sessions": [], "decisions": {}}


# ---------------------------------------------------------------------------
# Patches: the difference between two states, small enough to log
# ---------------------------------------------------------------------------
def diff_state(old, new):
    """Operations that turn ``old`` into ``new`` (two levels deep)."""
    ops = []
    for key in sorted(set(old) | set(new)):
        if key not in new:
            ops.append({"path": [key], "delete": True})
            continue
        before = old.get(key, _MISSING)
        after = new[key]
        if before is not _MISSING and before == after:
            continue
        if isinstance(before, dict) and isinstance(after, dict):
            for sub in sorted(set(before) | set(after)):
                if sub not in after:
                    ops.append({"path": [key, sub], "delete": True})
                elif sub not in before or before[sub] != after[sub]:
                    ops.append({"path": [key, sub], "value": copy.deepcopy(after[sub])})
        elif isinstance(before, list) and isinstance(after, list):
            if len(after) < len(before):
                ops.append({"path": [key], "length": len(after)})
            for index, item in enumerate(after):
                if index >= len(before) or before[index] != item:
                    ops.append({"path": [key, index], "value": copy.deepcopy(item)})
        else:
            ops.append({"path": [key], "value": copy.deepcopy(after)})
    return ops


def apply_ops(state, ops):
    """Apply operations produced by ``diff_state``; malformed ones are skipped.

    Returns the number of operations applied.
    """
    applied = 0
    for op in ops if isinstance(ops, list) else []:
        if not isinstance(op, dict):
            continue
        path = op.get("path")
        if not isinstance(path, list) or not 1 <= len(path) <= 2:
            continue
        top = path[0]
        if not isinstance(top, str):
            continue
        if len(path) == 1:
            if op.get("delete"):
                state.pop(top, None)
            elif "length" in op and isinstance(state.get(top), list):
                del state[top][max(0, int(op["length"])):]
            elif "value" in op:
                state[top] = copy.deepcopy(op["value"])
            else:
                continue
            applied += 1
            continue
        sub = path[1]
        target = state.get(top)
        if isinstance(sub, bool):
            continue
        if isinstance(sub, int):
            if not isinstance(target, list) or "value" not in op:
                continue
            if 0 <= sub < len(target):
                target[sub] = copy.deepcopy(op["value"])
            elif sub == len(target):
                target.append(copy.deepcopy(op["value"]))
            else:
                continue
            applied += 1
        elif isinstance(sub, str):
            if target is None:
                target = state[top] = {}
            if not isinstance(target, dict):
                continue
            if op.get("delete"):
                target.pop(sub, None)
            elif "value" in op:
                target[sub] = copy.deepcopy(op["value"])
            else:
                continue
            applied += 1
    return applied


def atomic_write_text(path, text):
    """Write ``text`` to ``path`` so that readers see the old or the new file."""
    path = os.fspath(path)
    folder = os.path.dirname(path) or "."
    tmp = os.path.join(folder, f".{os.path.basename(path)}.{os.getpid()}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def check_shape(state):
    """Return a description of what is wrong with ``state``, or ""."""
    if not isinstance(state, dict):
        return "最外层不是一个对象"
    schema = state.get("schema", SCHEMA)
    if not isinstance(schema, int) or isinstance(schema, bool):
        return "schema 不是整数"
    for name, kind in SECTIONS:
        if name in state and not isinstance(state[name], kind):
            return f"{name} 的类型不对"
    for name in ("stations", "review", "exams"):
        for key, value in state.get(name, {}).items():
            if not isinstance(value, dict):
                return f"{name}.{key} 不是一个对象"
    for item in state.get("sessions", []):
        if not isinstance(item, dict):
            return "sessions 里有一项不是对象"
    return ""


class Store:
    """Reads and writes the three tool-owned files under ``learner/``."""

    def __init__(self, folder, app=None):
        self.folder = os.fspath(folder)
        self.state_path = os.path.join(self.folder, "state.json")
        self.log_path = os.path.join(self.folder, "log.jsonl")
        self.result_path = os.path.join(self.folder, "last-result.json")
        self._app = app
        self._snapshot = None

    # -- helpers ------------------------------------------------------------
    def _stamp(self):
        if self._app is not None:
            return self._app.stamp()
        import datetime
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    def _scrub(self, value):
        """Keep the home directory (and so the user name) out of stored text."""
        if self._app is None:
            return value
        if isinstance(value, str):
            return self._app.scrub(value)
        if isinstance(value, list):
            return [self._scrub(item) for item in value]
        if isinstance(value, dict):
            return {key: self._scrub(item) for key, item in value.items()}
        return value

    def _ensure_folder(self):
        try:
            os.makedirs(self.folder, exist_ok=True)
        except OSError as exc:
            raise ToolTrouble(
                TEXT["unwritable"].format(name="learner/", reason=_reason(exc)),
                detail=repr(exc), recovery=TEXT["unwritable_recovery"])

    # -- state --------------------------------------------------------------
    def load(self):
        """Return the state as a dict.

        A missing file is created (and rebuilt from the log when the log has
        records).  A corrupt file raises ``StateTrouble`` and is left alone.
        """
        if not os.path.lexists(self.state_path):
            state, replayed, skipped = self._rebuild()
            self._ensure_folder()
            self._write_state(state)
            self._append({"type": "state-created", "replayed_events": replayed,
                          "unreadable_lines": skipped})
            self._snapshot = copy.deepcopy(state)
            return state
        state = self._read_state()
        self._snapshot = copy.deepcopy(state)
        return state

    def _read_state(self):
        try:
            with open(self.state_path, "r", encoding="utf-8") as handle:
                raw = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            raise StateTrouble(
                TEXT["corrupt"].format(reason=_reason(exc)),
                detail=repr(exc), recovery=TEXT["corrupt_recovery"],
                where="learner/state.json")
        try:
            state = json.loads(raw)
        except ValueError as exc:
            raise StateTrouble(
                TEXT["corrupt"].format(reason=TEXT["reason_json"]),
                detail=str(exc), recovery=TEXT["corrupt_recovery"],
                where="learner/state.json")
        problem = check_shape(state)
        if problem:
            raise StateTrouble(
                TEXT["corrupt"].format(reason=TEXT["reason_shape"].format(what=problem)),
                detail=problem, recovery=TEXT["corrupt_recovery"],
                where="learner/state.json")
        if state.get("schema", SCHEMA) > SCHEMA:
            raise StateTrouble(
                TEXT["newer"].format(found=state.get("schema"), known=SCHEMA),
                recovery=TEXT["newer_recovery"], where="learner/state.json")
        base = empty_state()
        base.update(state)
        return base

    def _rebuild(self):
        """Replay the ``state`` events of the log into a fresh state."""
        state = empty_state()
        replayed = 0
        skipped = 0
        for event in self.events(count_bad=True):
            if event is None:
                skipped += 1
                continue
            if event.get("type") == "state" and apply_ops(state, event.get("ops")):
                replayed += 1
        if check_shape(state):
            state = empty_state()
            replayed = 0
        state["schema"] = SCHEMA
        return state, replayed, skipped

    def ensure_writable(self):
        """Raise ``ToolTrouble`` now when the state could not be saved later.

        Commands that record an outcome call this before they do the work, so
        the learner never sees an outcome followed by 检查器出问题.
        """
        self._ensure_folder()
        if not os.access(self.folder, os.W_OK):
            raise ToolTrouble(
                TEXT["unwritable"].format(name="learner/", reason=_reason(PermissionError())),
                recovery=TEXT["unwritable_recovery"])
        for path, name in ((self.state_path, "learner/state.json"),
                           (self.log_path, "learner/log.jsonl")):
            if os.path.lexists(path) and not os.access(path, os.W_OK):
                raise ToolTrouble(TEXT["read_only"].format(name=name),
                                  recovery=TEXT["read_only_recovery"])

    def _write_state(self, state):
        text = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if os.path.lexists(self.state_path) and not os.access(self.state_path, os.W_OK):
            # The atomic rename would replace even a read-only file.
            raise ToolTrouble(TEXT["read_only"].format(name="learner/state.json"),
                              recovery=TEXT["read_only_recovery"])
        try:
            atomic_write_text(self.state_path, text)
        except OSError as exc:
            raise ToolTrouble(
                TEXT["unwritable"].format(name="learner/state.json", reason=_reason(exc)),
                detail=repr(exc), recovery=TEXT["unwritable_recovery"])

    def save(self, state, events=()):
        """Write ``state`` atomically and append ``events`` to the log.

        ``events`` is a list of dicts with at least a ``type``.  The change of
        state since the last ``load`` or ``save`` is logged as well, so the
        state can be rebuilt from the log alone.
        """
        problem = check_shape(state)
        if problem:
            raise ToolTrouble(f"工具要写入的进度数据结构不对：{problem}", detail=problem)
        state = self._scrub(state)
        state["schema"] = SCHEMA
        if self._snapshot is None:
            if os.path.lexists(self.state_path):
                self._snapshot = self._read_state()
            else:
                self._snapshot = empty_state()
        self._ensure_folder()
        ops = diff_state(self._snapshot, state)
        # state.json first: when it cannot be written, the log must not record
        # a change that state.json never got (a rebuild would replay it).
        self._write_state(state)
        self._snapshot = copy.deepcopy(state)
        for event in events:
            self._append(event)
        if ops:
            self._append({"type": "state", "ops": ops})
        return state

    # -- log ----------------------------------------------------------------
    def log(self, kind, **fields):
        """Append one event of type ``kind`` to the log (no change of state)."""
        self._ensure_folder()
        event = {"type": kind}
        event.update(fields)
        self._append(event)

    def _append(self, event):
        record = {"ts": self._stamp()}
        record.update(self._scrub(dict(event)))
        line = json.dumps(record, ensure_ascii=False, sort_keys=False)
        try:
            needs_newline = False
            if os.path.exists(self.log_path) and os.path.getsize(self.log_path) > 0:
                with open(self.log_path, "rb") as handle:
                    handle.seek(-1, os.SEEK_END)
                    needs_newline = handle.read(1) != b"\n"
            with open(self.log_path, "a", encoding="utf-8", newline="\n") as handle:
                handle.write(("\n" if needs_newline else "") + line + "\n")
        except OSError as exc:
            raise ToolTrouble(
                TEXT["unwritable"].format(name="learner/log.jsonl", reason=_reason(exc)),
                detail=repr(exc), recovery=TEXT["unwritable_recovery"])

    def events(self, count_bad=False):
        """Yield the events of the log in order.

        Unreadable lines are skipped; with ``count_bad`` they are yielded as
        None so the caller can count them.
        """
        if not os.path.exists(self.log_path):
            return
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
        except OSError as exc:
            raise ToolTrouble(
                TEXT["unreadable"].format(name="learner/log.jsonl", reason=_reason(exc)),
                detail=repr(exc))
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                event = None
            if not isinstance(event, dict):
                if count_bad:
                    yield None
                continue
            yield event

    # -- last result --------------------------------------------------------
    def write_result(self, data):
        """Store the result of the last check for the tutor to read."""
        self._ensure_folder()
        record = {"ts": self._stamp()}
        record.update(self._scrub(dict(data)))
        text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        try:
            atomic_write_text(self.result_path, text)
        except OSError as exc:
            raise ToolTrouble(
                TEXT["unwritable"].format(name="learner/last-result.json", reason=_reason(exc)),
                detail=repr(exc), recovery=TEXT["unwritable_recovery"])

    def read_result(self):
        """The last stored check result, or None when there is none."""
        try:
            with open(self.result_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) else None


def _reason(exc):
    """A short Chinese reason for an OSError (never an English class name)."""
    import errno
    if isinstance(exc, PermissionError):
        return "没有权限"
    if isinstance(exc, FileNotFoundError):
        return "找不到文件或文件夹"
    if isinstance(exc, IsADirectoryError):
        return "那里是一个文件夹，不是文件"
    if isinstance(exc, NotADirectoryError):
        return "路径中间有一项是文件，不是文件夹"
    if isinstance(exc, FileExistsError):
        return "那里已经有一个同名的文件，不是文件夹"
    if isinstance(exc, UnicodeDecodeError):
        return "不是 UTF-8 文本"
    code = getattr(exc, "errno", None)
    if code == errno.ENOSPC:
        return "磁盘满了"
    if code == errno.EROFS:
        return "这个位置是只读的"
    return "系统报了一个错误"


#: The public name of ``_reason`` for other modules.
reason = _reason
