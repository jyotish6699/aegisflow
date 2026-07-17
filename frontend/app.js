// =====================================================
// DOM Elements
// =====================================================

const events = document.getElementById("events");

const projectInput = document.getElementById("project");
const taskInput = document.getElementById("task");
const noteInput = document.getElementById("note");

const sessionStatus = document.getElementById("status");

const startButton = document.getElementById("start-session");
const endButton = document.getElementById("end-session");

const wrapupPanel = document.getElementById("session-wrapup");

const summaryInput = document.getElementById("summary-input");

const nextStepInput = document.getElementById("next-step-input");

const saveSessionButton =
    document.getElementById("save-session-btn");

const workspacePanel =
    document.getElementById("workspace-panel");

let totalEvents = 0;

// =====================================================
// Session State
// =====================================================

const SessionState = {

    active: false,

    currentSession: null,

    previousSession: null

};


// =====================================================
// Live Event Console
// =====================================================

function addEvent(event) {

    if (totalEvents === 0) {
        events.innerHTML = "";
    }

    const li = document.createElement("li");

    li.textContent =
        `[${new Date(event.timestamp).toLocaleTimeString()}] ${event.type}`;

    events.prepend(li);

    totalEvents++;
}

// =====================================================
// Workspace Validation
// =====================================================

function validateWorkspace() {

    // Project is required
    if(projectInput.value.trim() === "") {

        alert("Please enter a project name.");

        projectInput.focus();

        return false;
    }

    // Current task is required
    if(taskInput.value.trim() === "") {

        alert("Please enter the current task.");

        taskInput.focus();

        return false;
    }

    return true;
}


// =====================================================
// Workspace UI
// =====================================================

const WorkspaceUI = {

    startSession() {

        SessionState.active = true;

        SessionState.currentSession = {

            project: projectInput.value.trim(),

            task: taskInput.value.trim(),

            notes: noteInput.value.trim(),

            startedAt: new Date(),

            endedAt: null,

            summary: "",

            nextStep: ""

        };

        sessionStatus.textContent = "🟢 Session Active";

        startButton.style.display = "none";

        endButton.style.display = "inline-block";

        setWorkspaceLocked(true);
    },

    endSession() {

        SessionState.active = false;

    }
    

};

// =====================================================
// Wrap-up UI
// =====================================================

const WrapupUI = {

    show() {

        workspacePanel.style.display = "none";

        wrapupPanel.style.display = "block";

    },

    hide() {

        workspacePanel.style.display = "block";

        wrapupPanel.style.display = "none";

    }

};

// =====================================================
// Wrap-up Validation
// =====================================================

function validateWrapup() {

    if (summaryInput.value.trim() === "") {

        alert("Please write a session summary.");

        summaryInput.focus();

        return false;
    }

    if (nextStepInput.value.trim() === "") {

        alert("Please enter the next step.");

        nextStepInput.focus();

        return false;
    }

    return true;

}

// =====================================================
// SaveSession
// =====================================================

function saveSession() {

    if (!validateWrapup()) {
        return;
    }

    SessionState.currentSession.summary =
        summaryInput.value.trim();

    SessionState.currentSession.nextStep =
        nextStepInput.value.trim();

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
// Previous Session UI
// =====================================================

function renderPreviousSession() {

    if (!SessionState.previousSession) {
        return;
    }

    const previousPanel =
        document.getElementById("previous-session");

    previousPanel.style.display = "block";

    document.getElementById("previous-project").textContent =
        SessionState.previousSession.project;

    document.getElementById("previous-task").textContent =
        SessionState.previousSession.task;

    document.getElementById("summary").textContent =
        SessionState.previousSession.summary || "No summary.";

    document.getElementById("next-step").textContent =
        SessionState.previousSession.nextStep;



}

// =====================================================
// Workspace Lock
// =====================================================

function setWorkspaceLocked(locked) {

    projectInput.disabled = locked;

    taskInput.disabled = locked;

    noteInput.disabled = locked;

}

// =====================================================
// Workspace Reset
// =====================================================

function resetWorkspace() {

    // Clear workspace inputs
    projectInput.value = "";

    taskInput.value = "";

    noteInput.value = "";

    // Clear wrap-up inputs
    summaryInput.value = "";

    nextStepInput.value = "";

    // Unlock workspace
    setWorkspaceLocked(false);

    // Reset session state
    SessionState.active = false;

    // Restore UI
    WrapupUI.hide();

    sessionStatus.textContent = "⚪ Workspace Ready";

    startButton.style.display = "inline-block";

    endButton.style.display = "none";

    // Ready for next session
    projectInput.focus();

}


// =====================================================
// Event Engine
// =====================================================

const EventEngine = {

    emit(type, payload) {

        const event = {

            event_id: crypto.randomUUID(),

            type: type,

            timestamp: new Date().toISOString(),

            payload: payload

        };

        return this.dispatch(event);
    },

    async dispatch(event) {

        try {

            const response = await fetch(
                "http://localhost:8000/events",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(event)
                }
            );

            const result = await response.json();

            if (result.status === "success") {

                addEvent(event);

                console.log("Event Stored Successfully");

                console.log(result);

            } else {

                console.error("Backend rejected event");

                console.error(result);

            }

        } catch (error) {

            console.error("Failed to send event");

            console.error(error);

        }

    }

};


// =====================================================
// Button Events
// =====================================================


startButton.addEventListener("click", async () => {

        // Validate workspace
        if (!validateWorkspace()) {
            return;
        }

        WorkspaceUI.startSession();

        await EventEngine.emit(
            "session.started",
            {
                project: projectInput.value,
                task: taskInput.value,
                note: noteInput.value
            }
        );

    });



endButton.addEventListener("click", async () => {

        WrapupUI.show();

        await EventEngine.emit(
            "session.ended",
            {
                project: projectInput.value
            }
        );

    });

saveSessionButton.addEventListener(
    "click",
    saveSession
);