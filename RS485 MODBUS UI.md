Please check the RS485 MODBUS UI TAB.
Inside the Slave Devices section, there are several problems:

The dropdowns (Function Code, Data Type, Endianness) are very small, so the full values are not visible.
These dropdowns should be widened so the user can read the selected options clearly.

After clicking “Save Configuration”, the values are not getting saved in the database.
Nothing is written to Device_Config_MODBUS.

After clicking “Save Configuration”, all fields reset back to default values in the UI.
This means the saved values are not loading back into the form.

Right now there is only one slave row, but in real use the user will add more rows using “+ Add Device”.
Every time a new row is added, one new slave device should be added.

So for example:

If the user adds 3 slave rows

And fills values in all 3 rows

Then all 3 rows must be saved in the database, and also reloaded correctly in the UI after saving or refreshing.

Summary of what must work:

All dropdown widths must be increased

All slave rows (1 or more) should save correctly

After saving, the same values should appear again in the UI

No field should reset to default unless the user deletes a row manually