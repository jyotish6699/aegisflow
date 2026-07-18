import { DOM } from "../dom.js";

// =====================================================
// Workspace Validation
// =====================================================

export function validateWorkspace() {

    if (DOM.projectInput.value.trim() === "") {

        alert("Please enter a project name.");

        DOM.projectInput.focus();

        return false;

    }

    if (DOM.taskInput.value.trim() === "") {

        alert("Please enter the current task.");

        DOM.taskInput.focus();

        return false;

    }

    return true;

}