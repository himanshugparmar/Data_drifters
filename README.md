# ST3215 Servo Motor Python Module

This Python module provides a high-level API to communicate and control ST3215 servo motors via serial communication. It wraps around a low-level protocol to easily manage motion, configuration, and diagnostics of ST3215 devices using `pyserial` and custom STS protocol definitions. The recent update introduces new classes and methods enhancing the module's functionality and usability.

## Features

- Auto-detection of connected servos
- Read servo telemetry: position, speed, temperature, voltage, current, load
- Write target position, speed, and acceleration
- Rotate continuously in either direction
- Define and correct middle position
- EEPROM locking, ID and baudrate reconfiguration
- **New**: Group synchronization for read (`GroupSyncRead`) and write (`GroupSyncWrite`) operations
- **New**: Enhanced port handling through `PortHandler`
- **New**: Advanced packet handling with `protocol_packet_handler`
- **New**: Support for additional servo model `ST3215`

## Installation
You can install the module using pip:

```bash
pip install -e .
```

## Example Usage

```python
from st3215 import ST3215, GroupSyncRead, GroupSyncWrite

servo = ST3215('/dev/ttyUSB0')
ids = servo.ListServos()
if ids:
    servo.MoveTo(ids[0], 2048)

# New usage examples for GroupSyncRead and GroupSyncWrite
group_read = GroupSyncRead()
group_write = GroupSyncWrite()

# Example of using PortHandler
port_handler = PortHandler('/dev/ttyUSB0')
```

## Full API Documentation

### New Classes and Methods

#### `GroupSyncRead`
Synchronize reading data from multiple servos.

- **Example**:
```python
group_read.add_param(1, 'Position')
data = group_read.get_data()
```

#### `GroupSyncWrite`
Synchronize writing data to multiple servos.

- **Example**:
```python
group_write.add_param(1, 'Position', 2048)
group_write.send_data()
```

#### `PortHandler(device)`
Handle serial port operations for the servos.

- **Parameters**: `device` (str) – Device port
- **Example**:
```python
port_handler.open_port()
port_handler.set_baudrate(57600)
```

#### `protocol_packet_handler`
Handle the protocol packets for communication.

- **Example**:
```python
packet = protocol_packet_handler.create_packet()
protocol_packet_handler.send_packet(packet)
```

#### `ST3215`
Additional methods and updates to existing methods.

- **New Method**: `ReadMultiple(ids)`
  - **Parameters**: `ids` (list[int]) – List of servo IDs
  - **Returns**: `dict` with positions
  - **Example**:
  ```python
  positions = servo.ReadMultiple([1, 2, 3])
  ```

### Existing Methods
(No changes to existing methods; see previous documentation for details)

## Troubleshooting

### New Issues and Solutions

- **Problem**: GroupSyncRead returns incomplete data.
  - **Solution**: Ensure all servos are properly connected and IDs are correctly specified in the read group.
- **Problem**: Errors when using `PortHandler` on incorrect device port.
  - **Solution**: Verify the device port and ensure it is correctly specified when initializing `PortHandler`.

For further issues, refer to the existing troubleshooting section or contact support.

---

This update ensures that the documentation is aligned with the latest functionalities introduced in the software, providing users with the necessary guidance to utilize new features effectively.