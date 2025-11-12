#!/bin/bash
# Test Hardware Device Initialization on GCP VM
# Run this script ON the GCP VM to test device initialization
# Usage: ./test_hardware_init_gcp.sh [SERIAL_NUMBER]

SERIAL_NUMBER=${1:-"DF5647"}
VM_IP=${2:-"localhost"}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🧪 Testing Hardware Device Initialization${NC}"
echo -e "   Serial Number: ${YELLOW}$SERIAL_NUMBER${NC}"
echo ""

# Test 1: Check MQTT container
echo -e "${YELLOW}1️⃣ Checking MQTT container...${NC}"
if docker ps | grep -q iotnarad_mqtt; then
    echo -e "   ${GREEN}✅ MQTT container is running${NC}"
else
    echo -e "   ${RED}❌ MQTT container not running${NC}"
    echo -e "   ${CYAN}💡 Start it with: docker compose up -d mqtt${NC}"
    exit 1
fi

# Test 2: Check app container
echo ""
echo -e "${YELLOW}2️⃣ Checking app container...${NC}"
if docker ps | grep -q iotnarad_app; then
    echo -e "   ${GREEN}✅ App container is running${NC}"
    
    # Check if subscribed to Dev/Init topic
    if docker logs iotnarad_app 2>&1 | grep -q "Subscribed to: Dev/Init"; then
        echo -e "   ${GREEN}✅ App is subscribed to Dev/Init topic${NC}"
    else
        echo -e "   ${YELLOW}⚠️  App subscription status unclear${NC}"
    fi
else
    echo -e "   ${RED}❌ App container not running${NC}"
    exit 1
fi

# Test 3: Subscribe to acknowledgment topic (background)
echo ""
echo -e "${YELLOW}3️⃣ Starting acknowledgment monitor...${NC}"
ACK_TOPIC="Dev/Ack/$SERIAL_NUMBER"
echo -e "   Listening on: ${CYAN}$ACK_TOPIC${NC}"

# Start subscriber in background
docker run --rm eclipse-mosquitto:2 mosquitto_sub \
    -h $VM_IP \
    -p 1883 \
    -t "$ACK_TOPIC" \
    -v &
SUBSCRIBER_PID=$!

# Give subscriber time to connect
sleep 2

# Test 4: Publish device initialization message
echo ""
echo -e "${YELLOW}4️⃣ Publishing device initialization message...${NC}"

INIT_TOPIC="Dev/Init/$SERIAL_NUMBER"
PAYLOAD="{\"SerialNumber\": \"$SERIAL_NUMBER\"}"

echo -e "   Topic: ${CYAN}$INIT_TOPIC${NC}"
echo -e "   Payload: ${CYAN}$PAYLOAD${NC}"

if docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "$INIT_TOPIC" \
    -m "$PAYLOAD" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Initialization message sent successfully${NC}"
else
    echo -e "   ${RED}❌ Failed to send message${NC}"
    kill $SUBSCRIBER_PID 2>/dev/null
    exit 1
fi

# Test 5: Wait for acknowledgment
echo ""
echo -e "${YELLOW}5️⃣ Waiting for acknowledgment (10 seconds)...${NC}"
sleep 10

# Check if subscriber received message
if kill -0 $SUBSCRIBER_PID 2>/dev/null; then
    echo -e "   ${YELLOW}⚠️  No acknowledgment received${NC}"
    kill $SUBSCRIBER_PID 2>/dev/null
else
    echo -e "   ${GREEN}✅ Acknowledgment received${NC}"
fi

# Test 6: Check server logs
echo ""
echo -e "${YELLOW}6️⃣ Checking server logs for processing...${NC}"
if docker logs iotnarad_app --tail 50 2>&1 | grep -q "$SERIAL_NUMBER"; then
    echo -e "   ${GREEN}✅ Found serial number in logs${NC}"
    echo -e "   ${CYAN}Recent logs:${NC}"
    docker logs iotnarad_app --tail 10 2>&1 | grep -i "$SERIAL_NUMBER" | head -5
else
    echo -e "   ${YELLOW}⚠️  Serial number not found in recent logs${NC}"
    echo -e "   ${CYAN}💡 Check full logs: docker logs iotnarad_app -f${NC}"
fi

# Test 7: Test multiple serial numbers
echo ""
echo -e "${YELLOW}7️⃣ Testing with multiple serial numbers...${NC}"
TEST_SERIALS=("TEST001" "TEST002" "TEST003")

for test_serial in "${TEST_SERIALS[@]}"; do
    echo -e "   Testing: ${CYAN}$test_serial${NC}"
    test_topic="Dev/Init/$test_serial"
    test_payload="{\"SerialNumber\": \"$test_serial\"}"
    
    if docker exec -i iotnarad_mqtt mosquitto_pub \
        -h localhost \
        -p 1883 \
        -t "$test_topic" \
        -m "$test_payload" 2>/dev/null; then
        echo -e "      ${GREEN}✅ Sent${NC}"
    else
        echo -e "      ${RED}❌ Failed${NC}"
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}✅ Testing complete!${NC}"
echo ""
echo -e "${CYAN}📝 Useful commands:${NC}"
echo "   Monitor all Dev/Init messages:"
echo "      docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t 'Dev/Init/#' -v"
echo ""
echo "   Monitor all acknowledgments:"
echo "      docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t 'Dev/Init/Ack/#' -v"
echo ""
echo "   View app logs:"
echo "      docker logs iotnarad_app -f"
echo ""

