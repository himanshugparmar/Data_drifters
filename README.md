# ST3215 Servo Control Library

A Python library for controlling ST3215 serial bus servo motors via UART communication.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Manual](User_manual.md) | Complete API reference and method documentation |
| [User Guide](user_guide.md) | Step-by-step tutorials and usage examples |
| [Troubleshooting](troubleshooting.md) | Common issues and their solutions |
| [FAQ](FAQ.md) | Frequently asked questions |

## ⚡ Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```python
from st3215 import ST3215

# Initialize connection
servo = ST3215("/dev/ttyUSB0")

# Ping servo ID 1
if servo.PingServo(1):
    print("Servo found!")

# Move to position 2048
servo.MoveTo(1, 2048, speed=2400, acc=50)
```

## 📋 Features

- ✅ Servo detection and ping
- ✅ Position, speed, and PWM control modes
- ✅ Read voltage, current, temperature, and load
- ✅ Configure acceleration and speed
- ✅ Servo calibration and taring
- ✅ ID and baudrate configuration
- ✅ Comprehensive error handling

## 🔧 Requirements

- Python 3.10+
- pyserial

## 📦 Project Structure

```
st3215/
├── __init__.py                 # Package initialization
├── st3215.py                   # Main servo control class
├── port_handler.py             # Serial port management
├── protocol_packet_handler.py  # Communication protocol
├── group_sync_read.py          # Bulk read operations
├── group_sync_write.py         # Bulk write operations
└── values.py                   # Constants and register definitions

test/
├── test_01_ping_servo.py
├── test_02_list_servos.py
├── test_03_read_load_voltage_current.py
├── test_04_read_temperature.py
├── test_05_read_acceleration.py
├── test_06_read_mode.py
├── test_07_read_correction.py
├── test_08_read_status.py
├── test_09_is_moving.py
├── test_10_complete_motion_control.py
├── test_11_change_baudrate.py
└── test_12_read_position.py
```

## 🚀 Testing

Set the device environment variable and run tests:

```bash
export ST3215_DEV=/dev/ttyUSB0
python3 test/test_01_ping_servo.py
```

See [User Guide](user_guide.md#testing) for detailed testing instructions.

## 📄 License

Apache License Version 2.0

## 👤 Author

Mickael Roger - [mickael@mickael-roger.com](mailto:mickael@mickael-roger.com)

## 🔗 Links

- [GitHub Repository](https://github.com/Mickael-Roger/python-st3215)
- [ST3215 Servo Documentation](https://www.waveshare.com/wiki/ST3215_Servo)

## 🆘 Need Help?

- Check the [Troubleshooting Guide](troubleshooting.md)
- Read the [FAQ](FAQ.md)
- Review the [User Manual](User_manual.md) for detailed API documentation
