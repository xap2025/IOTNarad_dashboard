#!/usr/bin/env python3
"""
Hardware Device Initialization Test Script
Simulates hardware sending initialization message and receiving acknowledgment
Usage: python test_hardware_init_python.py --vm-ip 34.131.186.225 --serial DF5647
"""

import argparse
import json
import time
import paho.mqtt.client as mqtt
import sys

class HardwareInitTester:
    def __init__(self, vm_ip, serial_number, port=1883):
        self.vm_ip = vm_ip
        self.serial_number = serial_number
        self.port = port
        self.ack_received = False
        self.ack_message = None
        
        # MQTT client
        self.client = mqtt.Client(client_id=f"test_client_{serial_number}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"✅ Connected to MQTT broker: {self.vm_ip}:{self.port}")
            
            # Subscribe to acknowledgment topic
            ack_topic = f"Dev/Ack/{self.serial_number}"
            client.subscribe(ack_topic)
            print(f"📡 Subscribed to: {ack_topic}")
            
            # Send initialization message
            self.send_initialization()
        else:
            print(f"❌ Failed to connect. Return code: {rc}")
            sys.exit(1)
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        print(f"\n📨 Message received on topic: {topic}")
        print(f"   Payload: {payload}")
        
        # Parse acknowledgment
        try:
            data = json.loads(payload)
            self.ack_received = True
            self.ack_message = data
            print(f"✅ Acknowledgment received!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'N/A')}")
        except json.JSONDecodeError:
            print(f"⚠️  Invalid JSON in acknowledgment")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        if rc != 0:
            print(f"⚠️  Unexpected disconnection. Code: {rc}")
        else:
            print("Disconnected from MQTT broker")
    
    def send_initialization(self):
        """Send device initialization message"""
        topic = f"Dev/Init/{self.serial_number}"
        payload = {
            "SerialNumber": self.serial_number
        }
        
        message = json.dumps(payload)
        result = self.client.publish(topic, message, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"\n📤 Initialization message sent!")
            print(f"   Topic: {topic}")
            print(f"   Payload: {message}")
        else:
            print(f"❌ Failed to publish message. Return code: {result.rc}")
    
    def run(self, timeout=30):
        """Run the test"""
        print(f"\n🧪 Testing Hardware Device Initialization")
        print(f"   VM IP: {self.vm_ip}")
        print(f"   Serial Number: {self.serial_number}")
        print(f"   Port: {self.port}\n")
        
        try:
            # Connect to broker
            print(f"🔌 Connecting to {self.vm_ip}:{self.port}...")
            self.client.connect(self.vm_ip, self.port, 60)
            
            # Start network loop
            self.client.loop_start()
            
            # Wait for acknowledgment
            print(f"\n⏳ Waiting for acknowledgment (timeout: {timeout}s)...")
            start_time = time.time()
            
            while not self.ack_received and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            # Stop network loop
            self.client.loop_stop()
            self.client.disconnect()
            
            # Results
            print(f"\n{'='*50}")
            if self.ack_received:
                print("✅ TEST PASSED: Acknowledgment received successfully!")
                return True
            else:
                print("❌ TEST FAILED: No acknowledgment received within timeout")
                print("   💡 Check:")
                print("      - Server logs: docker logs iotnarad_app -f")
                print("      - MQTT broker: docker logs iotnarad_mqtt -f")
                print("      - Network connectivity")
                return False
            print(f"{'='*50}\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            self.client.loop_stop()
            self.client.disconnect()
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Test hardware device initialization on GCP VM'
    )
    parser.add_argument(
        '--vm-ip',
        required=True,
        help='GCP VM external IP address'
    )
    parser.add_argument(
        '--serial',
        default='DF5647',
        help='Device serial number (default: DF5647)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=1883,
        help='MQTT port (default: 1883)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    tester = HardwareInitTester(args.vm_ip, args.serial, args.port)
    success = tester.run(timeout=args.timeout)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

