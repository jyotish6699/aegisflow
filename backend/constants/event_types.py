# =====================================================
# Session Events
# =====================================================

class EventTypes:

    SESSION_STARTED = "session.started"

    SESSION_COMPLETED = "session.completed"

    # =================================================
    # Workspace Events
    # =================================================

    WORKSPACE_PROJECT_UPDATED = "workspace.project.updated"

    WORKSPACE_TASK_UPDATED = "workspace.task.updated"

    WORKSPACE_NOTE_UPDATED = "workspace.note.updated"

    # =================================================
    # Wrap-up Events
    # =================================================

    SESSION_SUMMARY_UPDATED = "session.summary.updated"

    SESSION_NEXT_STEP_UPDATED = "session.next_step.updated"

    # =================================================
    # Supported Event Types
    # =================================================

    ALL = {

        SESSION_STARTED,

        SESSION_COMPLETED,

        WORKSPACE_PROJECT_UPDATED,

        WORKSPACE_TASK_UPDATED,

        WORKSPACE_NOTE_UPDATED,

        SESSION_SUMMARY_UPDATED,

        SESSION_NEXT_STEP_UPDATED

    }