import { addEvent } from "../ui/events.js";
import { SessionState } from "../state/session.js";

// =====================================================
// Event Engine
// =====================================================

export const EventEngine = {

    async emit(event_type, payload) {

        const event = {

            session_id: SessionState.currentSession.id,

            event_type,

            occurred_at: new Date().toISOString(),

            payload

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

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const savedEvent = await response.json();

            addEvent(savedEvent);

            console.log("Event stored successfully");

            console.log(savedEvent);

        } catch (error) {

            console.error("Failed to send event");

            console.error(error);

        }

    }

};