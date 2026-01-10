// background.js
console.log("Agentic Auto-fill: Background script loaded.");

const BACKEND_URL = "http://localhost:8000";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "FILL_FORM_REQUEST") {
        handleFillFormRequest(message.payload)
            .then(data => sendResponse({ success: true, data }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Keep message channel open for async response
    }
});

async function handleFillFormRequest(payload) {
    console.log("Forwarding request to backend:", payload);
    const response = await fetch(`${BACKEND_URL}/agent/fill-form`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`Backend request failed with status ${response.status}`);
    }

    return await response.json();
}
