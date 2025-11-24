✅ Phrase (Clean + Clear for Developer)

Please look carefully — the RS485 MODBUS configuration is not saving correctly in the database.

Here is what is happening:

1. Communication Settings are NOT being saved anymore

These values are shown correctly in the UI:

Baud Rate: 19200

Data Bits: 7

Parity: Even

Stop Bits: 2

But none of them appear in the database now.
Earlier these settings were saving correctly — now they are missing completely from the Device_Config_MODBUS measurement.

2. Protocol Settings are also NOT being saved

UI shows:

Mode: TCP

Role: Slave

But these values are also not saved in the database.

3. Polling Interval (ms) is NOT saving

UI shows the value:

4000

But this too is missing from the database.

4. Only the “Slave Devices” rows are saving

Now the slave device rows are saving correctly (which was earlier not working):

Example row:

Slave ID: 3

Function Code: 0x03 - Read Holding Registers

Register Address: 0X98

Data Type: int8

Endianness: Big Endian

Variable Name: REGISTER

These values appear properly in the database — this part is working correctly now.

❗ Problem Summary

Earlier:

Communication Settings → working

Protocol Settings → working

Polling Interval → working

Slave Devices → NOT working

Now:

Communication Settings → NOT saving

Protocol Settings → NOT saving

Polling Interval → NOT saving

Slave Devices → ONLY this is saving correctly

✔ What should happen

All of these sections must save together:

Communication Settings

Protocol Settings

Slave Devices (all rows)

Polling Interval (ms)

Nothing should be skipped.
All values should be stored in Device_Config_MODBUS with the same timestamp.