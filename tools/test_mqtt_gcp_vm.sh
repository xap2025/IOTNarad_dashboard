#!/bin/bash
# MQTT Testing Script for GCP VM (Run on the VM itself)
# Usage: ./test_mqtt_gcp_vm.sh

echo "🧪 Testing MQTT on GCP VM..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test 1: Check container
echo -e "${YELLOW}1️⃣ Checking MQTT container...${NC}"
if docker ps | grep -q iotnarad_mqtt; then
    echo -e "   ${GREEN}✅ MQTT container is running${NC}"
    docker ps | grep iotnarad_mqtt
else
    echo -e "   ${RED}❌ MQTT container not running${NC}"
    echo -e "   ${CYAN}💡 Start it with: docker compose up -d mqtt${NC}"
    exit 1
fi

# Test 2: Check port listening
echo ""
echo -e "${YELLOW}2️⃣ Checking if port 1883 is listening...${NC}"
if sudo netstat -tuln 2>/dev/null | grep -q ":1883 " || sudo ss -tuln 2>/dev/null | grep -q ":1883 "; then
    echo -e "   ${GREEN}✅ Port 1883 is listening${NC}"
else
    echo -e "   ${RED}❌ Port 1883 is not listening${NC}"
fi

# Test 3: Publish test message
echo ""
echo -e "${YELLOW}3️⃣ Publishing test message...${NC}"
TEST_TOPIC="test/gcp/vm"
TEST_PAYLOAD="{\"test\": \"from_gcp_vm\", \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}"

if docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "$TEST_TOPIC" \
    -m "$TEST_PAYLOAD" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Message published successfully${NC}"
    echo "   Topic: $TEST_TOPIC"
    echo "   Payload: $TEST_PAYLOAD"
else
    echo -e "   ${RED}❌ Failed to publish message${NC}"
fi

# Test 4: Subscribe (timeout after 3 seconds)
echo ""
echo -e "${YELLOW}4️⃣ Subscribing to test topic (3 seconds)...${NC}"
timeout 3 docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -t "$TEST_TOPIC" \
    -C 1 2>/dev/null && echo -e "   ${GREEN}✅ Message received${NC}" || echo -e "   ${YELLOW}⚠️  No message received (this is OK if no one published)${NC}"

# Test 5: Test device data topic
echo ""
echo -e "${YELLOW}5️⃣ Testing device data topic...${NC}"
DEVICE_TOPIC="iotnarad/devices/test_device_01/data"
DEVICE_PAYLOAD="{
    \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
    \"sensors\": {
        \"temperature\": 25.5,
        \"humidity\": 65.2
    },
    \"production\": {
        \"line_id\": \"Line_A\",
        \"units_produced\": 1250,
        \"oee\": 89.2,
        \"status\": \"running\"
    }
}"

if docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "$DEVICE_TOPIC" \
    -m "$DEVICE_PAYLOAD" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Device data published successfully${NC}"
    echo "   Topic: $DEVICE_TOPIC"
    echo -e "   ${CYAN}💡 Check dashboard logs: docker logs iotnarad_app -f${NC}"
else
    echo -e "   ${RED}❌ Failed to publish device data${NC}"
fi

# Test 6: Get external IP
echo ""
echo -e "${YELLOW}6️⃣ Getting VM external IP...${NC}"
EXTERNAL_IP=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null)
if [ -n "$EXTERNAL_IP" ]; then
    echo -e "   ${GREEN}✅ External IP: $EXTERNAL_IP${NC}"
    echo -e "   ${CYAN}💡 Use this IP to connect from external clients${NC}"
else
    echo -e "   ${YELLOW}⚠️  Could not retrieve external IP${NC}"
    echo -e "   ${CYAN}💡 Check GCP Console for your VM's external IP${NC}"
fi

# Test 7: Check firewall (if gcloud is available)
echo ""
echo -e "${YELLOW}7️⃣ Checking firewall rules...${NC}"
if command -v gcloud &> /dev/null; then
    if gcloud compute firewall-rules list 2>/dev/null | grep -q "mqtt"; then
        echo -e "   ${GREEN}✅ MQTT firewall rule found${NC}"
        gcloud compute firewall-rules list | grep mqtt
    else
        echo -e "   ${YELLOW}⚠️  No MQTT firewall rule found${NC}"
        echo -e "   ${CYAN}💡 Create one with:${NC}"
        echo "      gcloud compute firewall-rules create mqtt-broker-allow \\"
        echo "          --allow tcp:1883,tcp:9001 \\"
        echo "          --source-ranges 0.0.0.0/0 \\"
        echo "          --description \"Allow MQTT broker connections\""
    fi
else
    echo -e "   ${YELLOW}⚠️  gcloud CLI not available${NC}"
    echo -e "   ${CYAN}💡 Check firewall rules in GCP Console${NC}"
fi

echo ""
echo -e "${GREEN}✅ Testing complete!${NC}"
echo ""
echo -e "${CYAN}📝 Useful commands:${NC}"
echo "   View MQTT logs:    docker logs iotnarad_mqtt -f"
echo "   View app logs:     docker logs iotnarad_app -f"
echo "   Subscribe all:     docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v"
echo ""

