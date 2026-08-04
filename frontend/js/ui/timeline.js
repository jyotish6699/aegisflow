import { DOM } from "../dom.js";
import { TimelineLabels } from "../constants/timeline-labels.js";

// =====================================================
// Timeline UI
// =====================================================

function formatTime(timestamp) {

    return new Date(timestamp).toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );

}

function createTimelineItem(event) {

    const li = document.createElement("li");

    li.textContent =
        `[${formatTime(event.occurred_at)}] ${
            TimelineLabels[event.event_type] ?? event.event_type
        }`;

    return li;

}

export function renderTimeline(timeline) {

    DOM.events.innerHTML = "";

    DOM.timelineTitle.textContent = "Timeline";

    const totalEvents = timeline.events.length;

    DOM.timelineCount.textContent =
        `${totalEvents} ${totalEvents === 1 ? "Event" : "Events"}`;

    if (totalEvents === 0) {

        const li = document.createElement("li");

        li.textContent = "No events recorded.";

        DOM.events.appendChild(li);

        return;

    }

    for (const event of timeline.events) {

        DOM.events.appendChild(
            createTimelineItem(event)
        );

    }

}