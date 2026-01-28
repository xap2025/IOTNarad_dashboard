// Analytics Page Socket.IO Client
// This file automatically loads when Analytics page is accessed
// Updates Dash store when RTD data arrives via Socket.IO
// Socket.IO library is loaded in <head> section via app.index_string in main.py

console.log('📦 z_analytics_socket_client.js loaded!');

(function() {
    // Prevent multiple initializations
    if (window.analyticsSocketIOInitialized) {
        console.log('⚠️ Analytics Socket.IO already initialized');
        return;
    }
    
    console.log('🚀 Initializing Analytics Socket.IO client...');
    console.log('   Current URL:', window.location.href);
    console.log('   Socket.IO library available:', typeof io !== 'undefined');
    
    // Socket.IO should be loaded in <head>, but wait a moment if needed
    function initializeConnection() {
        if (typeof io === 'undefined') {
            console.warn('⚠️ Socket.IO library not available yet, retrying in 100ms...');
            setTimeout(initializeConnection, 100);
            return;
        }
        
        console.log('✅ Socket.IO library confirmed available, creating connection...');
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
                console.log('📡 Analytics: Received rtd_data_update event!');
                console.log('   Event data:', JSON.stringify(data, null, 2));
                console.log('   Device ID:', data.device_id);
                console.log('   Timestamp:', data.timestamp);
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
            console.log('✅ Analytics Socket.IO client initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to create Analytics Socket.IO connection:', error);
            console.error('   Error details:', error.message, error.stack);
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
                
                try {
                    window.dash_clientside.set_props('analytics-rtd-trigger-store', {
                        data: storeData,
                        timestamp: Date.now()
                    });
                    
                    console.log('✅ Analytics: set_props called successfully');
                    console.log('   Store should now trigger analytics callback');
                } catch (error) {
                    console.error('❌ Analytics: Error calling set_props:', error);
                    console.error('   Error details:', error.message, error.stack);
                }
            } else if (attempt < MAX_ATTEMPTS) {
                console.warn(`⚠️ Analytics: Dash not ready (attempt ${attempt}/${MAX_ATTEMPTS}), retrying in ${300 * attempt}ms...`);
                setTimeout(trySetProps, 300 * attempt);
            } else {
                console.error('❌ Analytics: Failed to send data after multiple attempts');
                console.error('   window.dash_clientside:', window.dash_clientside);
                console.error('   Make sure Dash has fully loaded');
            }
        }
        
        trySetProps();
    }
    
    // Start initialization - Socket.IO should be in <head> so this should be quick
    // Wait for DOM to be ready and Dash to initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeConnection, 500); // Give Dash time to initialize
        });
    } else {
        setTimeout(initializeConnection, 500); // Give Dash time to initialize
    }
})();

