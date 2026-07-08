const events = document.getElementById("events");
const count = document.getElementById("count");

let totalEvents = 0;

function addEvent(message){
    
    if(totalEvents === 0){
        events.innerHTML = "";
    }

    const li = document.createElement("li");
    li.textContent = message;

    events.prepend(li);

    totalEvents++;
    count.textContent = totalEvents;
}

const EventEngine = {

    emit(type, payload){

        const event = {

            id: crypto.randomUUID(),
            type: type,
            timestamp: new Date().toISOString(),
            payload: payload
        };

        this.dispatch(event);
    },

    async dispatch(event){
        
        try {

            // Send the event to the backend and receive response
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

            // Convert backend response to JavaScript object
            const result = await response.json();

            // Check whether backend accepted the event
            if(result.status === "success") {

                addEvent(event.type);
            }else {

                console.error("Backend rejected event:", result);
            }

        } catch (error) {
            console.error("Failed to send event:", error);
        }
    }
};

document.getElementById("start").onclick = () => {
    EventEngine.emit(
        "session.started",
        {}
    );
};

document.getElementById("end").onclick = () => {
    EventEngine.emit(
        "session.ended",
        {}
    );
};