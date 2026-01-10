// content.js
console.log("Agentic Auto-fill: Content script loaded.");

// Inject the floating button immediately
createFloatingButton();

function createFloatingButton() {
    if (document.getElementById('agentic-floating-action-btn')) return;

    const btn = document.createElement('button');
    btn.id = 'agentic-floating-action-btn';
    btn.className = 'agentic-floating-btn';
    btn.innerHTML = '<span class="agentic-icon">✨</span> Apply with Agent';
    btn.type = 'button';

    btn.onclick = async () => {
        btn.classList.add('loading');
        btn.innerHTML = '<span class="agentic-icon">🧬</span> Analyze & Fill';
        
        try {
            // Find the best form to fill
            const forms = document.querySelectorAll('form');
            if (forms.length === 0) {
                showToast("⚠️ No forms found on this page.");
                return;
            }

            // Heuristic: Pick the form with the most inputs
            let bestForm = forms[0];
            let maxInputs = 0;
            forms.forEach(f => {
                const count = f.querySelectorAll('input:not([type="hidden"]), textarea, select').length;
                if (count > maxInputs) {
                    maxInputs = count;
                    bestForm = f;
                }
            });

            console.log("Targeting form:", bestForm);
            await handleAutoFill(bestForm);
            showToast("✅ Form filled successfully!");
            
        } catch (e) {
            console.error("Auto-fill error:", e);
            if (e.message.includes("Failed to fetch")) {
                showToast("❌ Error: Cannot connect to Agent. Is 'web_interface.py' running on port 8001?");
            } else {
                showToast(`❌ Error: ${e.message}`);
            }
        } finally {
            btn.classList.remove('loading');
            btn.innerHTML = '<span class="agentic-icon">✨</span> Apply with Agent';
        }
    };

    document.body.appendChild(btn);
}

function showToast(text) {
    let container = document.getElementById('agentic-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'agentic-toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'agentic-toast';
    toast.innerText = text;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

async function handleAutoFill(form) {
    // 1. Scrape fields
    const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
    
    if (inputs.length === 0) {
        throw new Error("No fillable fields found in the target form.");
    }

    const fields = inputs.map(input => {
        // Find label
        let labelText = "";
        const id = input.id;
        if (id) {
            const label = document.querySelector(`label[for="${id}"]`);
            if (label) labelText = label.innerText;
        }
        
        // Fallback: Check parent
        if (!labelText && input.parentElement.tagName === 'LABEL') {
            labelText = input.parentElement.innerText;
        }
        // Fallback: Check previous sibling
        if (!labelText && input.previousElementSibling && input.previousElementSibling.tagName === 'LABEL') {
            labelText = input.previousElementSibling.innerText;
        }

        return {
            id: input.id || "",
            name: input.name || "",
            label: labelText.trim(),
            placeholder: input.placeholder || "",
            type: input.type || "text"
        };
    });

    console.log("Scraped fields:", fields);

    // 2. Send to Background Script (MV3 Message Passing)
    const data = await new Promise((resolve, reject) => {
        try {
            chrome.runtime.sendMessage({
                type: "FILL_FORM_REQUEST",
                payload: { fields }
            }, (response) => {
                if (chrome.runtime.lastError) {
                    const msg = chrome.runtime.lastError.message;
                    if (msg.includes("Receiving end does not exist") || msg.includes("Extension context invalidated")) {
                        return reject(new Error("Extension disconnected. Please reload the page and the extension."));
                    }
                    return reject(new Error(msg));
                }
                if (!response) {
                    return reject(new Error("No response from background agent. Is the background script running?"));
                }
                if (response.success) {
                    resolve(response.data);
                } else {
                    reject(new Error(response.error || "Unknown error from background script"));
                }
            });
        } catch (e) {
            reject(new Error("Extension context invalid. Please reload the page."));
        }
    });

    const mapping = data.filled_fields || {};
    const logs = data.reasoning_logs || [];

    console.log("Agentic Reasoning:", logs);

    // 3. Fill Form & Highlight
    let filledCount = 0;
    inputs.forEach(input => {
        const key = input.id || input.name;
        
        // Try exact match first, then check if we mapped the other attribute
        let val = mapping[input.id] || mapping[input.name];
        
        if (val !== undefined && val !== null) {
            input.value = val;
            input.classList.add('agentic-filled');
            
            // Dispatch events to satisfy frameworks like React/Angular
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
            
            filledCount++;
        }
    });
    
    if (filledCount === 0) {
        showToast("⚠️ Analyzed form but couldn't confidently match any fields.");
    }
}

// Observe for dynamic forms (SPA support) to keep button on top if needed
// Actually, since it's fixed, we don't need to re-inject, but we might check if it was removed
const observer = new MutationObserver((mutations) => {
    if (!document.getElementById('agentic-floating-action-btn')) {
        createFloatingButton();
    }
});
observer.observe(document.body, { childList: true, subtree: true });