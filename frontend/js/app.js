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

function saveSession() {

    if (!validateWrapup()) {

        return;

    }

    SessionState.currentSession.summary =
        DOM.summaryInput.value.trim();

    SessionState.currentSession.nextStep =
        DOM.nextStepInput.value.trim();

    SessionState.currentSession.endedAt =
        new Date();

    SessionState.previousSession =
        SessionState.currentSession;

    SessionState.currentSession = null;

    renderPreviousSession();

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
            "session.started",
            {

                project: DOM.projectInput.value,

                task: DOM.taskInput.value,

                note: DOM.noteInput.value

            }

        );

    }
);

DOM.endButton.addEventListener(
    "click",
    async () => {

        WrapupUI.show();

        await EventEngine.emit(
            "session.ended",
            {

                project: DOM.projectInput.value

            }

        );

    }
);

DOM.saveSessionButton.addEventListener(
    "click",
    saveSession
);