import { DOM } from "../dom.js";
import { SessionState } from "../state/session.js";
import { WrapupUI } from "../ui/wrapup.js";

// =====================================================
// Workspace Lock
// =====================================================

export function setWorkspaceLocked(locked) {

    DOM.projectInput.disabled = locked;

    DOM.taskInput.disabled = locked;

    DOM.noteInput.disabled = locked;

}

// =====================================================
// Workspace Reset
// =====================================================

export function resetWorkspace() {

    // Clear workspace inputs

    DOM.projectInput.value = "";

    DOM.taskInput.value = "";

    DOM.noteInput.value = "";

    // Clear wrap-up

    DOM.summaryInput.value = "";

    DOM.nextStepInput.value = "";

    // Unlock workspace

    setWorkspaceLocked(false);

    // Reset session state

    SessionState.active = false;

    // Restore UI

    WrapupUI.hide();

    DOM.sessionStatus.textContent =
        "⚪ Workspace Ready";

    DOM.startButton.style.display =
        "inline-block";

    DOM.endButton.style.display =
        "none";

    // Ready for next session

    DOM.projectInput.focus();

}