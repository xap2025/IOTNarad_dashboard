// Analytics Page Socket.IO Client
// This file automatically loads when Analytics page is accessed
// Updates Dash store when RTD data arrives via Socket.IO

(function() {
    // Prevent multiple initializations
    if (window.analyticsSocketIOInitialized) {
        console.log('⚠️ Analytics Socket.IO already initialized');
        return;
    }
    
    console.log('🚀 Initializing Analytics Socket.IO client...');
    
    // Wait for Socket.IO library to load
    function initializeSocket() {
        if (typeof io === 'undefined') {
            console.warn('⚠️ Socket.IO library not loaded yet, retrying...');
            setTimeout(initializeSocket, 500);
            return;
        }
        
        createConnection();
    }
    
    function createConnection() {
        console.log('🔌 Creating Socket.IO connection for Analytics...');
        
        try {
            const socket = io({
                // Auto-detects host:port from current page
                transports: ['websocket'],
                upgrade: false,
                reconnection: true,
                reconnectionAttempts: 10,
                reconnectionDelay: 3000,
                path: '/socket.io'
            });
            
            // Debug all incoming events
            socket.onAny((event, ...args) => {
                console.log('⚡ [Analytics Socket.IO Event]', event, 'Data:', args);
            });
            
            socket.on('connect', () => {
                console.log('🟢 Analytics Socket.IO connected. ID:', socket.id);
            });
            
            socket.on('rtd_data_update', (data) => {
                console.log('📡 Analytics: Received rtd_data_update:', JSON.stringify(data, null, 2));
                safeSetProps(data);
            });
            
            socket.on('disconnect', (reason) => {
                console.warn('🔴 Analytics Socket.IO disconnected:', reason);
            });
            
            socket.on('connect_error', (error) => {
                console.error('🔴 Analytics Socket.IO connection error:', error.message);
            });
            
            // Store socket globally for debugging
            window.analyticsSocket = socket;
            window.analyticsSocketIOInitialized = true;
            
        } catch (error) {
            console.error('❌ Failed to create Analytics Socket.IO connection:', error);
        }
    }
    
    function safeSetProps(data) {
        const MAX_ATTEMPTS = 5;
        let attempt = 0;
        
        function trySetProps() {
            attempt++;
            
            if (window.dash_clientside && window.dash_clientside.set_props) {
                const storeData = {
                    timestamp: data.timestamp || new Date().toISOString(),
                    device_id: data.device_id,
                    trigger_count: Date.now() // Unique value to trigger update
                };
                
                console.log('📦 Analytics: Sending to Dash store:', storeData);
                console.log('   Store ID: analytics-rtd-trigger-store');
                
                // Use exact format from old project
                window.dash_clientside.set_props('analytics-rtd-trigger-store', {
                    data: storeData,
                    timestamp: Date.now()
                });
                
                console.log('✅ Analytics: set_props called successfully');
            } else if (attempt < MAX_ATTEMPTS) {
                console.warn(`⚠️ Analytics: Dash not ready (attempt ${attempt}), retrying...`);
                setTimeout(trySetProps, 300 * attempt);
            } else {
                console.error('❌ Analytics: Failed to send data after multiple attempts');
            }
        }
        
        trySetProps();
    }
    
    // Start initialization
    // Wait for DOM to be ready and Dash to be initialized
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeSocket, 1000); // Give Dash time to initialize
        });
    } else {
        setTimeout(initializeSocket, 1000); // Give Dash time to initialize
    }
})();

