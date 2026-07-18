import { DOM } from "../dom.js";

// =====================================================
// Live Event Console
// =====================================================

let totalEvents = 0;

export function addEvent(event) {

    if (totalEvents === 0) {
        DOM.events.innerHTML = "";
    }

    const li = document.createElement("li");

    li.textContent =
        `[${new Date(event.timestamp).toLocaleTimeString()}] ${event.type}`;

    DOM.events.prepend(li);

    totalEvents++;

}