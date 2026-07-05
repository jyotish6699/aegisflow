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

document.getElementById("start").onclick = () => {
    addEvent("Session Started");
};

document.getElementById("end").onclick = () => {
    addEvent("Session Ended");
};