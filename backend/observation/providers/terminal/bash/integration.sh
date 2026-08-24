#!/usr/bin/env bash

_aegisflow_command_id=""
_aegisflow_command=""
_aegisflow_cwd=""
_aegisflow_started_at=""
_aegisflow_internal=0
_aegisflow_last_debug_command=""


_aegisflow_emit_started() {
    if [[ "$_aegisflow_internal" == "1" ]]; then
        return
    fi

    if [[ "$BASH_COMMAND" == "$_aegisflow_last_debug_command" ]]; then
        _aegisflow_last_debug_command=""
        return
    fi

    case "$BASH_COMMAND" in
        trap\ *)
            return
            ;;
        _aegisflow_*)
            return
            ;;
    esac

    _aegisflow_internal=1
    _aegisflow_last_debug_command="$BASH_COMMAND"

    _aegisflow_command="$BASH_COMMAND"
    _aegisflow_command_id="${BASHPID}-${RANDOM}"
    _aegisflow_cwd="$PWD"
    _aegisflow_started_at="$EPOCHREALTIME"

    python3 - \
        "$_aegisflow_command_id" \
        "$_aegisflow_command" \
        "$_aegisflow_cwd" >&2 <<'PY'
import json
import sys

command_id, command, cwd = sys.argv[1:]

print(
    json.dumps(
        {
            "type": "command.started",
            "command_id": command_id,
            "command": command,
            "cwd": cwd,
        }
    ),
    flush=True,
)
PY

    _aegisflow_internal=0
}


_aegisflow_emit_completed() {
    local exit_code=$?

    if [[ -z "$_aegisflow_command_id" ]]; then
        return "$exit_code"
    fi

    _aegisflow_internal=1

    local duration

    duration="$(
        python3 - \
            "$_aegisflow_started_at" \
            "$EPOCHREALTIME" <<'PY'
import sys

started = float(sys.argv[1])
finished = float(sys.argv[2])

print(finished - started)
PY
    )"

    python3 - \
        "$_aegisflow_command_id" \
        "$_aegisflow_command" \
        "$_aegisflow_cwd" \
        "$exit_code" \
        "$duration" >&2 <<'PY'
import json
import sys

command_id, command, cwd, exit_code, duration = sys.argv[1:]

print(
    json.dumps(
        {
            "type": "command.completed",
            "command_id": command_id,
            "command": command,
            "cwd": cwd,
            "exit_code": int(exit_code),
            "duration": float(duration),
        }
    ),
    flush=True,
)
PY

    _aegisflow_command_id=""
    _aegisflow_command=""
    _aegisflow_cwd=""
    _aegisflow_started_at=""

    _aegisflow_internal=0

    return "$exit_code"
}


trap '_aegisflow_emit_started' DEBUG
trap '_aegisflow_emit_completed' EXIT