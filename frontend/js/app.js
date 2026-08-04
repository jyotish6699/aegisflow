import { DOM } from "./dom.js";

import { SessionState } from "./state/session.js";

import { WorkspaceUI } from "./ui/workspace.js";
import { WrapupUI } from "./ui/wrapup.js";
import { renderPreviousSession } from "./ui/previous-session.js";

import { validateWorkspace } from "./validation/workspace.js";
import { validateWrapup } from "./validation/wrapup.js";

import { EventEngine } from "./services/event-engine.js";

import { resetWorkspace } from "./utils/workspace-reset.js";

import { SessionService } from "./services/session-service.js";

import { EventTypes } from "./constants/event-types.js";

import { TimelineService } from "./services/timeline-service.js";
import { renderTimeline } from "./ui/timeline.js";

// =====================================================
// Session Service
// =====================================================

async function createSession() {

    const session = await SessionService.create({

        project_name: DOM.projectInput.value.trim(),

        task_name: DOM.taskInput.value.trim(),

        notes: DOM.noteInput.value.trim()

    });

    SessionState.currentSession = {

        id: session.id,

        project: session.project_name,

        task: session.task_name,

        notes: session.notes,

        startedAt: session.started_at,

        endedAt: null,

        summary: "",

        nextStep: ""

    };

}

// =====================================================
// Save Session
// =====================================================

async function saveSession() {

    if (!validateWrapup()) {

        return;

    }

    SessionState.currentSession.summary =
        DOM.summaryInput.value.trim();

    SessionState.currentSession.nextStep =
        DOM.nextStepInput.value.trim();

    await EventEngine.emit(
        EventTypes.SESSION_SUMMARY_UPDATED,
        {
            summary: SessionState.currentSession.summary
        }
    );

    await EventEngine.emit(
        EventTypes.SESSION_NEXT_STEP_UPDATED,
        {
            next_step: SessionState.currentSession.nextStep
        }
    );

    await EventEngine.emit(
        EventTypes.SESSION_COMPLETED,
        {}
    );

    SessionState.currentSession.endedAt =
        new Date();

    const sessionId = SessionState.currentSession.id;

    SessionState.previousSession =
        SessionState.currentSession;

    SessionState.currentSession = null;

    renderPreviousSession();

    const timeline = await TimelineService.get(sessionId);

    renderTimeline(timeline);

    WorkspaceUI.endSession();

    resetWorkspace();

}

// =====================================================
// Event Listeners
// =====================================================

DOM.startButton.addEventListener(
    "click",
    async () => {

        if (!validateWorkspace()) {

            return;

        }

        await createSession();

        WorkspaceUI.startSession();

        await EventEngine.emit(
            EventTypes.SESSION_STARTED,
            {}
        );

        await EventEngine.emit(
            EventTypes.WORKSPACE_PROJECT_UPDATED,
            {
                project_name: SessionState.currentSession.project
            }
        );

        await EventEngine.emit(
            EventTypes.WORKSPACE_TASK_UPDATED,
            {
                task_name: SessionState.currentSession.task
            }
        );

        await EventEngine.emit(
            EventTypes.WORKSPACE_NOTE_UPDATED,
            {
                notes: SessionState.currentSession.notes
            }
        );

    }
);

DOM.endButton.addEventListener(
    "click",
    async () => {

        WrapupUI.show();

    }
);

DOM.saveSessionButton.addEventListener(
    "click",
    saveSession
);