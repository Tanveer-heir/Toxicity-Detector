// Highlight toxic words inline with tooltip
function highlightToxicWords(text, toxicWords) {
    if (!toxicWords || toxicWords.length === 0) return text;

    // Escape regex special characters in toxic words
    const escapedWords = toxicWords.map(w => w.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
    const pattern = new RegExp(`\\b(${escapedWords.join('|')})\\b`, 'gi');

    // Wrap matched toxic words in span with highlight class
    return text.replace(pattern, match => `<span class="toxic-highlight" title="Marked as toxic word">${match}</span>`);
}

// Display toxic words as separate badges below analyzed text
function displayToxicWordLabels(toxicWords) {
    const container = document.getElementById("toxic-words-labels");
    if (!toxicWords || toxicWords.length === 0) {
        container.innerHTML = "<i>None</i>";
        return;
    }
    container.innerHTML = toxicWords
        .map(word => `<span class="label-badge toxic-word">${word}</span>`)
        .join(" ");
}

function checkToxicity() {
    const text = document.getElementById("tox-input").value;
    const resultDiv = document.getElementById("tox-result");

    if (!text.trim()) {
        resultDiv.innerHTML = '<p style="color: #ff6b6b;">Please enter some text to analyze.</p>';
        resultDiv.style.display = 'block';
        displayToxicWordLabels([]);
        return;
    }

    resultDiv.innerHTML = '<p style="color: #00d4ff;">Analyzing text...</p>';
    resultDiv.style.display = 'block';

    fetch("http://localhost:8000/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(result => {
        const highlightedText = highlightToxicWords(text, result.toxic_words);
        displayToxicWordLabels(result.toxic_words);

        const labels = result.toxic_labels.length ? result.toxic_labels.join(", ") : "None";
        const confPercent = (result.confidence * 100).toFixed(1);

        resultDiv.innerHTML = `
            <div class="highlighted-text">${highlightedText}</div>
            <div class="result-header">
                <div class="toxicity-indicator ${result.is_toxic ? "toxic" : "safe"}">
                    <div class="indicator-icon">${result.is_toxic ? "⚠" : "✅"}</div>
                    <div class="indicator-text">
                        <div class="indicator-label">${result.is_toxic ? "Toxic Content Detected" : "Content is Safe"}</div>
                        <div class="confidence-score">Confidence: ${confPercent}%</div>
                    </div>
                </div>
            </div>

            <div class="confidence-bar">
                <div class="confidence-label">Overall Confidence</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${confPercent}%; background: ${
                        result.is_toxic
                            ? "linear-gradient(90deg, #ff6b6b, #ff8e8e)"
                            : "linear-gradient(90deg, #90ee90, #a8f5a8)"
                    }"></div>
                </div>
                <div class="confidence-value">${result.confidence.toFixed(3)}</div>
            </div>

            <div class="labels-section">
                <div class="section-title">Detected Labels</div>
                <div class="labels-container">
                    ${
                        result.toxic_labels
                            .map(label => `
                                <span class="label-badge ${label}">${label.charAt(0).toUpperCase() + label.slice(1)}</span>
                            `)
                            .join("")
                    }
                </div>
            </div>

            <div class="scores-section">
                <div class="section-title">Detailed Analysis</div>
                <div class="scores-grid">
                    ${
                        Object.entries(result.scores)
                            .map(([label, score]) => {
                                const percentage = score * 100;
                                const isHigh = score > 0.5;
                                const color = isHigh ? "#ff6b6b" : score > 0.2 ? "#ffa500" : "#90ee90";
                                return `
                                    <div class="score-item">
                                        <div class="score-label">${label.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</div>
                                        <div class="score-bar">
                                            <div class="score-fill" style="width: ${percentage}%; background: ${color}"></div>
                                        </div>
                                        <div class="score-value" style="color: ${color}">${score.toFixed(3)}</div>
                                    </div>
                                `;
                            })
                            .join("")
                    }
                </div>
            </div>
        `;
    })
    .catch(error => {
        resultDiv.innerHTML = '<p style="color: #ff6b6b;">Error analyzing text. Please try again.</p>';
        resultDiv.style.display = 'block';
        displayToxicWordLabels([]);
        console.error("Error:", error);
    });
}

function detoxifyText() {
    const toxicText = document.getElementById("tox-input").value;
    const detoxOutput = document.getElementById("detox-output");

    if (!toxicText.trim()) {
        if (detoxOutput.tagName === "TEXTAREA" || detoxOutput.tagName === "INPUT") {
            detoxOutput.value = "Please enter some text to detoxify.";
        } else {
            detoxOutput.innerText = "Please enter some text to detoxify.";
        }
        return;
    }

    if (detoxOutput.tagName === "TEXTAREA" || detoxOutput.tagName === "INPUT") {
        detoxOutput.value = "Detoxifying text...";
    } else {
        detoxOutput.innerText = "Detoxifying text...";
    }

    fetch("http://localhost:8000/api/detoxify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: toxicText }),
    })
    .then(res => res.json())
    .then(result => {
        if (detoxOutput.tagName === "TEXTAREA" || detoxOutput.tagName === "INPUT") {
            detoxOutput.value = result.detoxified_text || "No output generated";
        } else {
            detoxOutput.innerText = result.detoxified_text || "No output generated";
        }
    })
    .catch(error => {
        if (detoxOutput.tagName === "TEXTAREA" || detoxOutput.tagName === "INPUT") {
            detoxOutput.value = "Error detoxifying text. Please try again.";
        } else {
            detoxOutput.innerText = "Error detoxifying text. Please try again.";
        }
        console.error("Error:", error);
    });
}

function askBot() {
    const question = document.getElementById("qa-input").value;
    fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("qa-result").innerText = data.answer;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const textInput = document.getElementById("tox-input");
    if (textInput) {
        textInput.addEventListener("keydown", e => {
            if (e.ctrlKey && e.key === "Enter") {
                checkToxicity();
            }
        });
        textInput.addEventListener("input", () => {
            const resultDiv = document.getElementById("tox-result");
            if (resultDiv && resultDiv.innerHTML.includes("Analyzing")) {
                resultDiv.innerHTML = "";
                resultDiv.style.display = 'none';
            }
            displayToxicWordLabels([]); // clear toxic word labels on input change
        });
    }
});
