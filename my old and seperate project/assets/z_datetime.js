function startClock(dateEl) {
    function updateClock() {
        const now = new Date();
        const formatted = now.toLocaleString("en-IN", {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: true
        });
        dateEl.textContent = formatted;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

function waitForDateElement(maxAttempts = 20, delay = 200) {
    let attempts = 0;

    const check = () => {
        const dateEl = document.getElementById("current-datetime");

        if (dateEl && !dateEl.dataset.clockStarted) {
            startClock(dateEl);
            dateEl.dataset.clockStarted = "true"; // prevent multiple intervals
        } else if (attempts < maxAttempts) {
            attempts++;
            setTimeout(check, delay);
        } else {
            console.error("⏰ #current-datetime still not found after waiting");
        }
    };

    check();
}

// 🔥 Observe DOM changes for Dash page navigation
function observeDashboard() {
    const observer = new MutationObserver(() => {
        const dateEl = document.getElementById("current-datetime");
        if (dateEl && !dateEl.dataset.clockStarted) {
            startClock(dateEl);
            dateEl.dataset.clockStarted = "true";
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

// Run once after page load
document.addEventListener("DOMContentLoaded", function () {
    waitForDateElement();
    observeDashboard();
});
