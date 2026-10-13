#!/usr/bin/env bash

_aegisflow_command_id=""
_aegisflow_command=""
_aegisflow_cwd=""
_aegisflow_started_at=""
_aegisflow_internal=1
_aegisflow_last_debug_command=""
_aegisflow_skip_next_debug=1
_aegisflow_session_id="${AEGISFLOW_SESSION_ID:-bash-${BASHPID}-${RANDOM}}"


_aegisflow_emit_started() {
    if [[ "$_aegisflow_internal" == "1" ]]; then
        return
    fi

    if [[ "$_aegisflow_skip_next_debug" == "1" ]]; then
        _aegisflow_skip_next_debug=0
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
        aegisflow_capture\ *|_aegisflow_capture\ *)
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
        "$_aegisflow_cwd" >&3 <<'PY'
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


aegisflow_capture() {
    local command="$*"

    if [[ -z "${AEGISFLOW_TERMINAL_CAPTURE_ENDPOINT:-}" ]]; then
        printf '%s\n' \
            "aegisflow_capture: AEGISFLOW_TERMINAL_CAPTURE_ENDPOINT is not set" \
            >&2
        return 2
    fi

    if [[ -z "$command" ]]; then
        printf '%s\n' \
            "aegisflow_capture: expected a command string" \
            >&2
        return 2
    fi

    local shell_executable
    shell_executable="$(command -v bash)" || return 127

    _aegisflow_internal=1
    python3 -m observation.providers.terminal.capture.helper \
        --endpoint "$AEGISFLOW_TERMINAL_CAPTURE_ENDPOINT" \
        --session-id "$_aegisflow_session_id" \
        --command-id "${BASHPID}-${RANDOM}" \
        --shell "$shell_executable" \
        --cwd "$PWD" \
        "$command"
    local exit_code=$?
    _aegisflow_internal=0
    return "$exit_code"
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
        "$duration" >&3 <<'PY'
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

_aegisflow_internal=0