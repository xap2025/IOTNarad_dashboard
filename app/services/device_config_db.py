    def get_can_bus_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest CAN Bus configuration from Device_Config_CANBus table
        
        CRITICAL: This must retrieve ALL CAN messages and data mappings, not just one.
        The query separates settings (limit to 1) from messages/mappings (get all).
        """
        if not self.connected or not device_id or not device_id.strip():
            return None
        
        try:
            # Escape device_id for Flux query (replace backslashes and quotes)
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            
            # Query 1: Get latest settings (only 1 record needed)
            settings_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.config_type == "settings")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            # Query 2: Get ALL CAN messages and data mappings from the latest save
            # Strategy: All messages/mappings are saved with the same timestamp in one save operation
            # So we need to find the latest timestamp and get ALL records from that timestamp
            # Step 1: Find the latest timestamp for any CAN Bus config (settings, can_message, or data_mapping)
            latest_timestamp_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            # Get latest timestamp
            latest_timestamp_result = self.query_api.query(org=self.org, query=latest_timestamp_query)
            latest_timestamp = None
            for table in latest_timestamp_result:
                for record in table.records:
                    latest_timestamp = record.get_time()
                    break
            
            # Step 2: Get ALL CAN messages and data mappings from the latest timestamp
            all_can_records = []
            if latest_timestamp:
                # Query all CAN messages and data mappings from this timestamp (within 5 second window)
                # IMPORTANT: Removed group(columns: ["config_type"]) to get ALL records from the timestamp
                from datetime import timedelta
                can_records_query = f'''
                    from(bucket: "{self.bucket}")
                    |> range(start: {latest_timestamp.isoformat()}Z, stop: {(latest_timestamp + timedelta(seconds=5)).isoformat()}Z)
                    |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
                    |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                    |> filter(fn: (r) => r.config_type == "can_message" or r.config_type == "data_mapping")
                    |> pivot(rowKey: ["_time", "_measurement"], columnKey: ["_field"], valueColumn: "_value")
                '''
                can_records_result = self.query_api.query(org=self.org, query=can_records_query)
                for table in can_records_result:
                    for record in table.records:
                        all_can_records.append({
                            "time": record.get_time(),
                            "config_type": record.values.get("config_type", ""),
                            "index": record.values.get("index", 0),
                            "can_id": record.values.get("can_id", "0x123"),
                            "direction": record.values.get("direction", "TX"),
                            "period_ms": record.values.get("period_ms", 100),
                            "variable_name": record.values.get("variable_name", ""),
                            "data_length": record.values.get("data_length", 8),
                            "byte_position": record.values.get("byte_position", "Byte 0"),
                            "data_length_str": record.values.get("data_length_str", None),
                            "data_type": record.values.get("data_type", "int8"),
                            "endianness": record.values.get("endianness", "Big Endian"),
                            "scale_factor": record.values.get("scale_factor", 1.0),
                            "offset": record.values.get("offset", 0.0)
                        })
            
            logger.debug(f"   Found {len(all_can_records)} total CAN record(s) from latest timestamp: {latest_timestamp}")
            
            # Get settings
            settings_result = self.query_api.query(org=self.org, query=settings_query)
            settings = {}
            for table in settings_result:
                for record in table.records:
                    settings = {
                        "enabled": record.values.get("enabled", False),
                        "communication_settings": {
                            "baud_rate": record.values.get("baud_rate", 125),
                            "identifier_length": record.values.get("identifier_length", "11-bit"),
                            "can_mode": record.values.get("can_mode", "Normal"),
                            "filter_mode": record.values.get("filter_mode", "None"),
                            "filter_id": record.values.get("filter_id", "0x123"),
                            "filter_mask": record.values.get("filter_mask", "0x7FF")
                        }
                    }
                    break
            
            can_messages = []
            data_mapping = []
            
            # Filter to only records from the latest timestamp (within a small window)
            if latest_timestamp:
                from datetime import timedelta
                time_window = timedelta(seconds=5)  # 5 second window for timestamp precision
                for record in all_can_records:
                    time_diff = abs(record["time"] - latest_timestamp)
                    if time_diff <= time_window:
                        config_type = record.get("config_type", "")
                        if config_type == "can_message":
                            can_messages.append({
                                "index": record.get("index", 0),
                                "can_id": record.get("can_id", "0x123"),
                                "direction": record.get("direction", "TX"),
                                "period_ms": record.get("period_ms", 100),
                                "variable_name": record.get("variable_name", ""),
                                "data_length": record.get("data_length", 8)
                            })
                        elif config_type == "data_mapping":
                            # Use data_length_str if available (new format), otherwise fallback to data_length
                            data_length_value = record.get("data_length_str")
                            if data_length_value is None:
                                # Try to get from data_length field (might be string or integer)
                                data_length_value = record.get("data_length", "1 Byte")
                                if isinstance(data_length_value, (int, float)):
                                    # Convert integer to string format
                                    data_length_value = f"{int(data_length_value)} Byte" if int(data_length_value) == 1 else f"{int(data_length_value)} Bytes"
                            
                            data_mapping.append({
                                "index": record.get("index", 0),
                                "can_id": record.get("can_id", "0x123"),
                                "byte_position": record.get("byte_position", "Byte 0"),
                                "data_length": str(data_length_value) if data_length_value else "1 Byte",
                                "data_type": record.get("data_type", "int8"),
                                "endianness": record.get("endianness", "Big Endian"),
                                "variable_name": record.get("variable_name", ""),
                                "scale_factor": record.get("scale_factor", 1.0),
                                "offset": record.get("offset", 0.0)
                            })
                logger.debug(f"   Filtered to {len(can_messages)} CAN message(s) and {len(data_mapping)} data mapping(s) from latest timestamp {latest_timestamp}")
                logger.debug(f"   CAN Message IDs: {[m.get('can_id') for m in can_messages]}")
                logger.debug(f"   Data Mapping CAN IDs: {[m.get('can_id') for m in data_mapping]}")
            else:
                # Fallback: Use all records if no timestamp found
                for record in all_can_records:
                    config_type = record.get("config_type", "")
                    if config_type == "can_message":
                        can_messages.append({
                            "index": record.get("index", 0),
                            "can_id": record.get("can_id", "0x123"),
                            "direction": record.get("direction", "TX"),
                            "period_ms": record.get("period_ms", 100),
                            "variable_name": record.get("variable_name", ""),
                            "data_length": record.get("data_length", 8)
                        })
                    elif config_type == "data_mapping":
                        data_length_value = record.get("data_length_str")
                        if data_length_value is None:
                            data_length_value = record.get("data_length", "1 Byte")
                            if isinstance(data_length_value, (int, float)):
                                data_length_value = f"{int(data_length_value)} Byte" if int(data_length_value) == 1 else f"{int(data_length_value)} Bytes"
                        
                        data_mapping.append({
                            "index": record.get("index", 0),
                            "can_id": record.get("can_id", "0x123"),
                            "byte_position": record.get("byte_position", "Byte 0"),
                            "data_length": str(data_length_value) if data_length_value else "1 Byte",
                            "data_type": record.get("data_type", "int8"),
                            "endianness": record.get("endianness", "Big Endian"),
                            "variable_name": record.get("variable_name", ""),
                            "scale_factor": record.get("scale_factor", 1.0),
                            "offset": record.get("offset", 0.0)
                        })
                logger.debug(f"   No timestamp found, using all {len(can_messages)} CAN message(s) and {len(data_mapping)} data mapping(s)")
            
            # Sort by index to ensure correct order
            can_messages.sort(key=lambda x: x.get("index", 0))
            data_mapping.sort(key=lambda x: x.get("index", 0))
            
            logger.info(f"✅ CAN Bus config loaded: {len(can_messages)} CAN message(s) and {len(data_mapping)} data mapping(s) found for device {device_id}")
            if len(can_messages) > 0:
                logger.debug(f"   CAN Message IDs: {[m.get('can_id') for m in can_messages]}")
                logger.debug(f"   CAN Message Indices: {[m.get('index') for m in can_messages]}")
            if len(data_mapping) > 0:
                logger.debug(f"   Data Mapping CAN IDs: {[m.get('can_id') for m in data_mapping]}")
                logger.debug(f"   Data Mapping Indices: {[m.get('index') for m in data_mapping]}")
            
            if not settings:
                return None
            
            settings["can_messages"] = can_messages
            settings["data_mapping"] = data_mapping
            return settings