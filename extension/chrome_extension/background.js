// background.js
console.log("Agentic Auto-fill: Background script loaded.");

// Using 127.0.0.1 is often more reliable than localhost for Extensions
const BACKEND_URL = "http://127.0.0.1:8001";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "FILL_FORM_REQUEST") {
        handleFillFormRequest(message.payload)
            .then(data => sendResponse({ success: true, data }))
            .catch(error => {
                console.error("Agentic Fill Error:", error);
                sendResponse({ success: false, error: error.message });
            });
        return true; // Keep message channel open for async response
    }
});

async function handleFillFormRequest(payload) {
    console.log(`Forwarding request to backend: ${BACKEND_URL}/agent/fill-form`, payload);
    
    try {
        const response = await fetch(`${BACKEND_URL}/agent/fill-form`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Server responded with ${response.status}: ${errText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch failed details:", error);
        if (error.message.includes("Failed to fetch")) {
            // Detailed helpful error
            throw new Error(`Connection refused to ${BACKEND_URL}. Ensure 'web_interface.py' is running on port 8001.`);
        }
        throw error;
    }
}