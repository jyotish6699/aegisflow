import { DOM } from "../dom.js";

// =====================================================
// Wrap-up UI
// =====================================================

export const WrapupUI = {

    show() {

        DOM.workspacePanel.style.display = "none";

        DOM.wrapupPanel.style.display = "block";

    },

    hide() {

        DOM.workspacePanel.style.display = "block";

        DOM.wrapupPanel.style.display = "none";

    }

};