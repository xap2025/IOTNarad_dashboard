// Check for appInitializer
if (window.appInitializer) {
    console.log("🔌 Using appInitializer system for Socket.IO");
    window.appInitializer.onReady(initializeSocket);
} else {
    console.error("⚠️ appInitializer not available. Falling back to timeout");
    setTimeout(initializeSocket, 2000);
}

function initializeSocket() {
    console.log("🚀 Initializing Socket.IO connection");
    
    if (typeof io === "undefined") {
        console.error("❌ Socket.IO library not loaded - cannot initialize");
        return;
    }
    
    createConnection();
}

function createConnection() {
    console.log("🔌 Creating Socket.IO connection");
    
    try {
        const socket = io({
            // Auto-detects host:port from current page
            transports: ["websocket"],
            upgrade: false,
            reconnection: true,
            reconnectionAttempts: 10,
            reconnectionDelay: 3000,
            path: "/socket.io"
        });

        // Debug all incoming events
        socket.onAny((event, ...args) => {
            console.log("⚡ [Socket.IO Event]", event, "Data:", args);
        });

        socket.on("connect", () => {
            console.log("🟢 Socket.IO connected. ID:", socket.id);
        });

        socket.on("device_data", (data) => {
            console.log("📡 Received device_data:", JSON.stringify(data, null, 2));
            safeSetProps(data);
        });

        socket.on("disconnect", (reason) => {
            console.warn("🔴 Socket.IO disconnected:", reason);
        });

        socket.on("connect_error", (error) => {
            console.error("🔴 Connection Error:", error.message);
        });

    } catch (error) {
        console.error("❌ Failed to create Socket.IO connection:", error);
    }
}

function safeSetProps(data) {
    const MAX_ATTEMPTS = 5;
    let attempt = 0;
    
    function trySetProps() {
        attempt++;
        
        if (window.dash_clientside && window.dash_clientside.set_props) {
            console.log("📦 Sending to Dash store:", data);
            window.dash_clientside.set_props('socket-data-store', {
                data: data,
                timestamp: Date.now()
            });
        } else if (attempt < MAX_ATTEMPTS) {
            console.warn(`⚠️ Dash not ready (attempt ${attempt})`);
            setTimeout(trySetProps, 300 * attempt);
        } else {
            console.error("❌ Failed to send data after multiple attempts");
        }
    }
    
    trySetProps();
}