$topic = 'devices/test/uplink'
$msg   = '{"temp":25}'
docker exec -i iotnarad_mqtt sh -c "mosquitto_pub -h localhost -p 1883 -t $topic -m '$msg'"