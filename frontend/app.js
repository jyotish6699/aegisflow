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

    dispatch(event){
        addEvent(event.type);
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