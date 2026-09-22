#!/usr/bin/env zsh

zmodload zsh/datetime

_aegisflow_command_id=""
_aegisflow_command=""
_aegisflow_cwd=""
_aegisflow_started_at=""
_aegisflow_internal=1


_aegisflow_emit_started() {
    if [[ "$_aegisflow_internal" == "1" ]]; then
        return
    fi

    _aegisflow_internal=1

    _aegisflow_command="$1"
    _aegisflow_command_id="${EPOCHREALTIME}-${RANDOM}"
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


_aegisflow_emit_completed() {
    if [[ -z "$_aegisflow_command_id" ]]; then
        return
    fi

    _aegisflow_internal=1

    local exit_code="$1"
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
}


_aegisflow_preexec() {
    if [[ "$_aegisflow_internal" == "1" ]]; then
        return
    fi

    _aegisflow_emit_started "$1"
}


_aegisflow_precmd() {
    local exit_code="$?"

    if [[ -n "$_aegisflow_command_id" ]]; then
        _aegisflow_emit_completed "$exit_code"
    fi
}


autoload -Uz add-zsh-hook

add-zsh-hook preexec _aegisflow_preexec
add-zsh-hook precmd _aegisflow_precmd

_aegisflow_internal=0