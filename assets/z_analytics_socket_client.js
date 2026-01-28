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
                // Use polling first, then upgrade to websocket for better reliability
                // Polling works better behind proxies/firewalls, websocket is faster when available
                transports: ['polling', 'websocket'],
                upgrade: true,  // Allow upgrade from polling to websocket
                reconnection: true,
                reconnectionAttempts: Infinity,  // Keep trying to reconnect forever
                reconnectionDelay: 1000,  // Start reconnecting after 1 second
                reconnectionDelayMax: 5000,  // Max delay between reconnection attempts
                timeout: 20000,  // Connection timeout (20 seconds)
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
                // ========== DETAILED CONSOLE LOGGING FOR DEBUGGING ==========
                console.log('='.repeat(80));
                console.log('🟡 [SOCKET.IO → CLIENT] Step 4/5: ANALYTICS PAGE RECEIVED SOCKET.IO EVENT!');
                console.log('='.repeat(80));
                console.log('   📡 Event Name: rtd_data_update');
                console.log('   🏭 Device ID:', data.device_id);
                console.log('   📅 Timestamp:', data.timestamp);
                console.log('   📊 Data Type:', data.data_type);
                console.log('   📈 Parameters Count:', data.parameters_count);
                console.log('   ✅ Saved:', data.saved_count, '❌ Failed:', data.failed_count);
                console.log('   📦 Full Event Data:', JSON.stringify(data, null, 2));
                console.log('   ⏱️ Receive Time:', new Date().toISOString());
                console.log('   🔌 Socket ID:', socket.id);
                console.log('   🔄 Socket Connected:', socket.connected);
                console.log('='.repeat(80));
                console.log('   🔄 [SOCKET.IO → CLIENT] Step 5/5: Updating Dash store to trigger UI refresh...');
                console.log('='.repeat(80));
                // ========== END DETAILED LOGGING ==========
                
                safeSetProps(data);
            });
            
            socket.on('disconnect', (reason) => {
                console.warn('🔴 Analytics Socket.IO disconnected:', reason);
                if (reason === 'ping timeout') {
                    console.warn('   ⚠️ Ping timeout - connection will auto-reconnect');
                } else if (reason === 'transport close') {
                    console.warn('   ⚠️ Transport closed - connection will auto-reconnect');
                }
            });
            
            socket.on('connect_error', (error) => {
                console.error('🔴 Analytics Socket.IO connection error:', error.message);
            });
            
            socket.on('reconnect', (attemptNumber) => {
                console.log(`🟡 Analytics Socket.IO reconnected after ${attemptNumber} attempt(s)`);
            });
            
            socket.on('reconnect_attempt', () => {
                console.log('🔄 Analytics Socket.IO attempting to reconnect...');
            });
            
            socket.on('reconnect_error', (error) => {
                console.error('❌ Analytics Socket.IO reconnection error:', error.message);
            });
            
            socket.on('reconnect_failed', () => {
                console.error('❌ Analytics Socket.IO reconnection failed - will keep trying');
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
                    // ========== DETAILED CONSOLE LOGGING FOR DEBUGGING ==========
                    console.log('='.repeat(80));
                    console.log('🟢 [CLIENT → DASH STORE] Step 5/5: UPDATING DASH STORE');
                    console.log('='.repeat(80));
                    console.log('   📦 Store ID: analytics-rtd-trigger-store');
                    console.log('   📊 Store Data:', JSON.stringify(storeData, null, 2));
                    console.log('   ⏱️ Update Time:', new Date().toISOString());
                    console.log('   🔄 Calling window.dash_clientside.set_props...');
                    console.log('='.repeat(80));
                    // ========== END DETAILED LOGGING ==========
                    
                    window.dash_clientside.set_props('analytics-rtd-trigger-store', {
                        data: storeData,
                        timestamp: Date.now()
                    });
                    
                    console.log('='.repeat(80));
                    console.log('✅ [CLIENT → DASH STORE] Dash store UPDATED SUCCESSFULLY!');
                    console.log('='.repeat(80));
                    console.log('   ✅ set_props() called successfully');
                    console.log('   📦 Store ID: analytics-rtd-trigger-store');
                    console.log('   📊 Store Data:', JSON.stringify(storeData, null, 2));
                    console.log('   🔄 Analytics callback SHOULD TRIGGER NOW...');
                    console.log('   📈 Graphs and values SHOULD UPDATE IN REAL-TIME!');
                    console.log('   ⏱️ Next: Wait for Analytics callback to execute...');
                    console.log('='.repeat(80));
                } catch (error) {
                    console.error('='.repeat(80));
                    console.error('❌ [CLIENT → DASH STORE] ERROR calling set_props!');
                    console.error('='.repeat(80));
                    console.error('   ❌ Error:', error.message);
                    console.error('   📦 Store ID: analytics-rtd-trigger-store');
                    console.error('   📊 Store Data:', JSON.stringify(storeData, null, 2));
                    console.error('   🔍 Stack Trace:', error.stack);
                    console.error('='.repeat(80));
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

