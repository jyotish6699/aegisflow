import { DOM } from "../dom.js";

// =====================================================
// Wrap-up Validation
// =====================================================

export function validateWrapup() {

    if (DOM.summaryInput.value.trim() === "") {

        alert("Please write a session summary.");

        DOM.summaryInput.focus();

        return false;

    }

    if (DOM.nextStepInput.value.trim() === "") {

        alert("Please enter the next step.");

        DOM.nextStepInput.focus();

        return false;

    }

    return true;

}