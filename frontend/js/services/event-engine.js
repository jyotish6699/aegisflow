import { addEvent } from "../ui/events.js";

// =====================================================
// Event Engine
// =====================================================

export const EventEngine = {

    async emit(type, payload) {

        const event = {

            event_id: crypto.randomUUID(),

            type,

            timestamp: new Date().toISOString(),

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