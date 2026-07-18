import { DOM } from "../dom.js";
import { SessionState } from "../state/session.js";

// =====================================================
// Previous Session UI
// =====================================================

export function renderPreviousSession() {

    if (!SessionState.previousSession) {

        return;

    }

    DOM.previousPanel.style.display =
        "block";

    DOM.previousProject.textContent =
        SessionState.previousSession.project;

    DOM.previousTask.textContent =
        SessionState.previousSession.task;

    DOM.previousSummary.textContent =
        SessionState.previousSession.summary ||
        "No summary.";

    DOM.previousNextStep.textContent =
        SessionState.previousSession.nextStep;

}