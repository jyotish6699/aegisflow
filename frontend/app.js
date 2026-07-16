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

let totalEvents = 0;

// =====================================================
// Session State
// =====================================================

const SessionState = {

    active: false

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

        sessionStatus.active = true;

        sessionStatus.textContent = "🟢 Session Active";

        startButton.style.display = "none";

        endButton.style.display = "inline-block";

        setWorkspaceLocked(true);
    },

    endSession() {

        sessionStatus.active = false;

        sessionStatus.textContent = "⚪ Session Ended";

        startButton.style.display = "inline-block";

        endButton.style.display = "none";

        setWorkspaceLocked(false);
    }

};

// =====================================================
// Workspace Lock
// =====================================================

function setWorkspaceLocked(locked) {

    projectInput.disabled = locked;

    taskInput.disabled = locked;

    noteInput.disabled = locked;

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

document
    .getElementById("start-session")
    .addEventListener("click", async () => {

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


document
    .getElementById("end-session")
    .addEventListener("click", async () => {

        WorkspaceUI.endSession();

        await EventEngine.emit(
            "session.ended",
            {
                project: projectInput.value
            }
        );

    });