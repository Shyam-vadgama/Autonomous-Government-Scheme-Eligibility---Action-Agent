// content.js
console.log("Agentic Auto-fill: Content script loaded (v1.2).");

let isLoggedIn = false;
let currentUser = null;

// Initialize
function init() {
    // Check if context is valid
    try {
        if (!chrome.runtime.id) {
            console.log("Agentic Auto-fill: Extension context invalid.");
            return;
        }
    } catch (e) {
        return;
    }

    if (document.body) {
        createFloatingButton();
        checkLoginStatus();
        startObserver();
    } else {
        window.addEventListener('DOMContentLoaded', () => {
            createFloatingButton();
            checkLoginStatus();
            startObserver();
        });
    }
}

function checkLoginStatus() {
    try {
        chrome.storage.local.get(['agenticUser'], (result) => {
            if (chrome.runtime.lastError) return;
            if (result.agenticUser) {
                isLoggedIn = true;
                currentUser = result.agenticUser;
                updateButtonState();
            }
        });
    } catch (e) {
        console.error("Agentic: Could not check login status (orphaned script?)", e);
    }
}

function startObserver() {
    const observer = new MutationObserver((mutations) => {
        if (!document.getElementById('agentic-btn-container')) {
            createFloatingButton();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

function createFloatingButton() {
    if (document.getElementById('agentic-floating-action-btn')) return;

    const btnContainer = document.createElement('div');
    btnContainer.id = 'agentic-btn-container';
    btnContainer.className = 'agentic-btn-container';

    const btn = document.createElement('button');
    btn.id = 'agentic-floating-action-btn';
    btn.className = 'agentic-floating-btn';
    btn.innerHTML = '<span class="agentic-icon">✨</span> Apply with Agent';
    btn.type = 'button';

    btn.onclick = async () => {
        if (!isLoggedIn) {
            showLoginModal();
            return;
        }
        
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

    btnContainer.appendChild(btn);

    // Add logout button if logged in
    if (isLoggedIn && currentUser) {
        const logoutBtn = document.createElement('button');
        logoutBtn.id = 'agentic-logout-btn';
        logoutBtn.className = 'agentic-logout-btn';
        logoutBtn.innerHTML = '🚪';
        logoutBtn.title = 'Logout';
        logoutBtn.onclick = () => {
            chrome.storage.local.remove(['agenticUser']);
            isLoggedIn = false;
            currentUser = null;
            updateButtonState();
            showToast("👋 Logged out successfully");
        };
        btnContainer.appendChild(logoutBtn);
    }

    document.body.appendChild(btnContainer);
    updateButtonState();
}

function updateButtonState() {
    const btn = document.getElementById('agentic-floating-action-btn');
    const container = document.getElementById('agentic-btn-container');
    if (!btn || !container) return;
    
    // Remove existing logout button
    const existingLogoutBtn = document.getElementById('agentic-logout-btn');
    if (existingLogoutBtn) {
        existingLogoutBtn.remove();
    }
    
    if (isLoggedIn && currentUser) {
        btn.innerHTML = `<span class="agentic-icon">✨</span> Apply as ${currentUser.name}`;
        btn.classList.remove('logged-out');
        btn.classList.add('logged-in');
        
        // Add logout button
        const logoutBtn = document.createElement('button');
        logoutBtn.id = 'agentic-logout-btn';
        logoutBtn.className = 'agentic-logout-btn';
        logoutBtn.innerHTML = '🚪';
        logoutBtn.title = 'Logout';
        logoutBtn.onclick = () => {
            chrome.storage.local.remove(['agenticUser']);
            isLoggedIn = false;
            currentUser = null;
            updateButtonState();
            showToast("👋 Logged out successfully");
        };
        container.appendChild(logoutBtn);
    } else {
        btn.innerHTML = '<span class="agentic-icon">🔐</span> Login to Apply';
        btn.classList.remove('logged-in');
        btn.classList.add('logged-out');
    }
}

function showLoginModal() {
    if (document.getElementById('agentic-login-modal')) return;
    
    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'agentic-login-modal';
    modalOverlay.className = 'agentic-modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'agentic-modal';
    modal.innerHTML = `
        <div class="agentic-modal-header">
            <h2>🔐 Login to Agentic Auto-fill</h2>
            <button class="agentic-close-btn" onclick="closeLoginModal()">&times;</button>
        </div>
        <div class="agentic-modal-body">
            <form id="agentic-login-form">
                <div class="agentic-form-group">
                    <label for="agentic-email">Email:</label>
                    <input type="email" id="agentic-email" required>
                </div>
                <div class="agentic-form-group">
                    <label for="agentic-password">Password:</label>
                    <input type="password" id="agentic-password" required>
                </div>
                <div class="agentic-form-actions">
                    <button type="submit" class="agentic-login-btn">Login</button>
                    <button type="button" class="agentic-signup-btn" onclick="showSignupModal()">Sign Up</button>
                </div>
            </form>
        </div>
    `;
    
    modalOverlay.appendChild(modal);
    document.body.appendChild(modalOverlay);
    
    // Add event listener for login form
    document.getElementById('agentic-login-form').onsubmit = async (e) => {
        e.preventDefault();
        const email = document.getElementById('agentic-email').value;
        const password = document.getElementById('agentic-password').value;
        
        try {
            const response = await fetch('http://127.0.0.1:8001/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            if (response.ok) {
                const userData = await response.json();
                chrome.storage.local.set({ agenticUser: userData.user });
                isLoggedIn = true;
                currentUser = userData.user;
                closeLoginModal();
                updateButtonState();
                showToast(`✅ Logged in as ${userData.user.name}`);
            } else {
                const error = await response.json();
                showToast(`❌ Login failed: ${error.detail}`);
            }
        } catch (e) {
            showToast(`❌ Login error: ${e.message}`);
        }
    };
    
    // Close modal when clicking outside
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeLoginModal();
        }
    };
}

function showSignupModal() {
    closeLoginModal();
    
    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'agentic-signup-modal';
    modalOverlay.className = 'agentic-modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'agentic-modal';
    modal.innerHTML = `
        <div class="agentic-modal-header">
            <h2>📝 Sign Up for Agentic Auto-fill</h2>
            <button class="agentic-close-btn" onclick="closeSignupModal()">&times;</button>
        </div>
        <div class="agentic-modal-body">
            <form id="agentic-signup-form">
                <div class="agentic-form-group">
                    <label for="agentic-signup-name">Full Name:</label>
                    <input type="text" id="agentic-signup-name" required>
                </div>
                <div class="agentic-form-group">
                    <label for="agentic-signup-email">Email:</label>
                    <input type="email" id="agentic-signup-email" required>
                </div>
                <div class="agentic-form-group">
                    <label for="agentic-signup-phone">Phone:</label>
                    <input type="tel" id="agentic-signup-phone" required>
                </div>
                <div class="agentic-form-group">
                    <label for="agentic-signup-password">Password:</label>
                    <input type="password" id="agentic-signup-password" required>
                </div>
                <div class="agentic-form-actions">
                    <button type="submit" class="agentic-login-btn">Sign Up</button>
                    <button type="button" class="agentic-signup-btn" onclick="showLoginModal()">Back to Login</button>
                </div>
            </form>
        </div>
    `;
    
    modalOverlay.appendChild(modal);
    document.body.appendChild(modalOverlay);
    
    // Add event listener for signup form
    document.getElementById('agentic-signup-form').onsubmit = async (e) => {
        e.preventDefault();
        const name = document.getElementById('agentic-signup-name').value;
        const email = document.getElementById('agentic-signup-email').value;
        const phone = document.getElementById('agentic-signup-phone').value;
        const password = document.getElementById('agentic-signup-password').value;
        
        try {
            const response = await fetch('http://127.0.0.1:8001/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone, password })
            });
            
            if (response.ok) {
                const result = await response.json();
                closeSignupModal();
                showToast(`✅ Account created successfully! Please login.`);
                showLoginModal();
            } else {
                const error = await response.json();
                showToast(`❌ Signup failed: ${error.detail}`);
            }
        } catch (e) {
            showToast(`❌ Signup error: ${e.message}`);
        }
    };
    
    // Close modal when clicking outside
    modalOverlay.onclick = (e) => {
        if (e.target === modalOverlay) {
            closeSignupModal();
        }
    };
}

function closeLoginModal() {
    const modal = document.getElementById('agentic-login-modal');
    if (modal) modal.remove();
}

function closeSignupModal() {
    const modal = document.getElementById('agentic-signup-modal');
    if (modal) modal.remove();
}

// Make functions global for onclick handlers
window.closeLoginModal = closeLoginModal;
window.closeSignupModal = closeSignupModal;
window.showSignupModal = showSignupModal;
window.showLoginModal = showLoginModal;

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

    // 2. Send to Background Script (MV3 Message Passing) with user info
    const data = await new Promise((resolve, reject) => {
        try {
            chrome.runtime.sendMessage({
                type: "FILL_FORM_REQUEST",
                payload: { fields, user: currentUser }
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

// Run init
init();