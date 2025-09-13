function checkToxicity() {
    const text = document.getElementById("tox-input").value;
    fetch("http://localhost:5000/api/detect", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: text})
    })
    .then(res => res.json())
    .then(result => {
        let resDiv = document.getElementById("tox-result");
        resDiv.innerHTML =
            `<b>Is Toxic:</b> ${result.is_toxic ? "Yes" : "No"}<br>` +
            `<b>Confidence:</b> ${result.confidence}<br>` +
            `<b>Labels:</b> ${result.toxic_labels.length ? result.toxic_labels.join(", ") : "None"}<br>`;
    });
}

function askBot() {
    const question = document.getElementById("qa-input").value;
    fetch("http://localhost:5000/api/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: question})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("qa-result").innerText = data.answer;
    });
}
