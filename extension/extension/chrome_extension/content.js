// content.js
console.log("Agentic Auto-fill: Content script loaded.");


function injectApplyButton(form) {
    if (form.querySelector('.agentic-apply-btn')) return;

    const btn = document.createElement('button');
    btn.innerHTML = "✨ Apply with Agent";
    btn.className = "agentic-apply-btn";
    btn.type = "button";

    btn.onclick = async (e) => {
        e.preventDefault();
        btn.classList.add('loading');
        btn.innerHTML = "🧬 Thinking...";
        try {
            await handleAutoFill(form);
            showToast("✨ Form auto-filled. Please review.");
        } catch (e) {
            console.error(e);
            showToast("❌ Error filling form.");
        } finally {
            btn.classList.remove('loading');
            btn.innerHTML = "✨ Apply with Agent";
        }
    };

    // Layout-safe injection: search for submit button area
    const sub = form.querySelector('button[type="submit"], input[type="submit"]');
    if (sub) {
        const wrap = document.createElement('div');
        wrap.style.display = 'block';
        wrap.style.width = '100%';
        wrap.appendChild(btn);
        sub.parentNode.insertBefore(wrap, sub);
    } else {
        form.prepend(btn);
    }
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
    }, 3000);
}

async function handleAutoFill(form) {
    // 1. Scrape fields
    const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
    const fields = inputs.map(input => {
        // Find label
        let labelText = "";
        const label = document.querySelector(`label[for="${input.id}"]`);
        if (label) {
            labelText = label.innerText;
        } else if (input.parentElement.tagName === 'LABEL') {
            labelText = input.parentElement.innerText;
        } else if (input.previousElementSibling && input.previousElementSibling.tagName === 'LABEL') {
            labelText = input.previousElementSibling.innerText;
        }

        return {
            id: input.id || "",
            name: input.name || "",
            label: labelText,
            placeholder: input.placeholder || "",
            type: input.type || "text"
        };
    });

    // 2. Send to Background Script (MV3 Message Passing)
    const data = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({
            type: "FILL_FORM_REQUEST",
            payload: { fields }
        }, (response) => {
            if (chrome.runtime.lastError) {
                return reject(new Error(chrome.runtime.lastError.message));
            }
            if (response && response.success) {
                resolve(response.data);
            } else {
                reject(new Error(response.error || "Unknown error from background script"));
            }
        });
    });

    const mapping = data.filled_fields || {};
    const logs = data.reasoning_logs || [];

    console.log("Agentic Reasoning:", logs);

    // 3. Fill Form & Highlight
    inputs.forEach(input => {
        const key = input.id || input.name;
        if (mapping[key]) {
            input.value = mapping[key];
            // Green Highlighting
            input.classList.add('agentic-filled');

            // Trigger events
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
}

// Initial Injection
document.querySelectorAll('form').forEach(injectApplyButton);

// Observe for dynamic forms (SPA support)
const observer = new MutationObserver((mutations) => {
    document.querySelectorAll('form').forEach(injectApplyButton);
});
observer.observe(document.body, { childList: true, subtree: true });
