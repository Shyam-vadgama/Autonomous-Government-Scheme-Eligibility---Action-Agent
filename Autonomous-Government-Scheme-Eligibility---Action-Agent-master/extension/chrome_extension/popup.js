document.getElementById('reload-btn').addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.reload(tabs[0].id);
            window.close();
        }
    });
});

chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    const tab = tabs[0];
    if (tab.url.startsWith('chrome://')) {
        document.getElementById('status-text').innerText = "Restricted (Browser Page)";
        document.getElementById('status-text').style.color = "orange";
    }
});