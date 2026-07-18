import { DOM } from "../dom.js";
import { SessionState } from "../state/session.js";
import { setWorkspaceLocked } from "../utils/workspace-reset.js";

// =====================================================
// Workspace UI
// =====================================================

export const WorkspaceUI = {

    startSession() {

        SessionState.active = true;

        DOM.sessionStatus.textContent =
            "🟢 Session Active";

        DOM.startButton.style.display =
            "none";

        DOM.endButton.style.display =
            "inline-block";

        setWorkspaceLocked(true);

    },

    endSession() {

        SessionState.active = false;

    }

};