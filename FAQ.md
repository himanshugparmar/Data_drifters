```markdown
# ST3215 Servo Control Library - FAQ

Frequently Asked Questions about the ST3215 Python library.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Hardware Questions](#hardware-questions)
3. [Software Questions](#software-questions)
4. [Usage Questions](#usage-questions)
5. [Performance Questions](#performance-questions)
6. [Troubleshooting Questions](#troubleshooting-questions)
7. [Advanced Questions](#advanced-questions)

---

## General Questions

### What is ST3215?

ST3215 is a serial bus servo motor with built-in controller. It communicates via UART/RS485 protocol and provides position, speed, and PWM control modes. Common in robotics applications.

**Key Specifications:**
- Position resolution: 4096 steps (12-bit)
- Operating voltage: 6-12.6V
- Operating current: 100-2000mA typical
- Torque: ~15 kg·cm @ 12V
- Speed: Up to 3400 steps/second
- Communication: UART (half-duplex)
- Default baudrate: 1M bps

---

### What's the difference between ST3215 and other servos (like Dynamixel)?

| Feature | ST3215 | Dynamixel AX-12 | Standard RC Servo |
|---------|--------|-----------------|-------------------|
| Protocol | ST3215/SCS | Dynamixel | PWM |
| Communication | UART/RS485 | UART/RS485 | PWM (1-2ms) |
| Addressability | Yes (ID 0-253) | Yes (ID 0-253) | No |
| Position feedback | Yes (digital) | Yes (digital) | Some models |
| Speed control | Yes | Yes | No |
| Multi-turn | No | Some models | No |
| Cost | Low | Medium-High | Low |
| Library support | Limited | Excellent | Universal |

**ST3215 Advantages:**
- Lower cost than Dynamixel
- Digital control (better than PWM)
- Multiple operation modes
- Good torque for price

**Disadvantages:**
- Less documentation than Dynamixel
- Fewer library options
- Smaller community

---

### Is this library compatible with other servo models?

**Compatible:** Other Feetech/SCS series servos using the same protocol:
- STS3215
- STS3032
- SCS115
- SCS15 (with limitations)

**Not Compatible:**
- Dynamixel servos (different protocol)
- Herkulex servos (different protocol)
- Standard RC PWM servos (different control method)

**Testing compatibility:**
```python
# Try basic ping
servo = ST3215("/dev/ttyUSB0")
if servo.LinkServo(1):
    print("Compatible servo detected!")
else:
    print("Servo not responding - might be different protocol")
```

---

### Can I use this with Arduino or Raspberry Pi?

**Yes, both!**

#### Raspberry Pi (Recommended)
```python
# GPIO UART (pins 8/10)
servo = ST3215("/dev/ttyAMA0")

# USB adapter
servo = ST3215("/dev/ttyUSB0")
```

**Pros:** Native Python support, this library works directly

#### Arduino
**Note:** This is a Python library. For Arduino, you need:
- SCServo library (Arduino C++)
- Available at: https://github.com/ftservo/SCServo

**Bridge solution:** Use Arduino for servo control, Raspberry Pi for main logic

---

### What's the maximum number of servos I can control?

**Theoretical:** 253 servos (ID 0-253, ID 254 is broadcast)

**Practical limits:**

| Factor | Typical Limit | Notes |
|--------|---------------|-------|
| Power supply | 4-8 servos | 2A per servo needed |
| Bus speed | 20-30 servos | Communication bandwidth |
| Update rate | 10-20 servos | If polling all servos frequently |
| Cable length | 5 meters | Signal degradation |

**Recommendations:**
- **1-4 servos:** Simple daisy-chain, single power supply
- **5-10 servos:** Star topology power, may need RS485 repeater
- **10+ servos:** Multiple buses (multiple USB adapters), robust power distribution

---

## Software Questions

### What new methods have been introduced?

The `Ping6Servo` method has been introduced to provide enhanced functionality. This method allows users to perform a specific operation related to the servo's capabilities. Details on its usage and parameters can be found in the updated user manual.

### What changes have been made to method signatures?

The `ST3215` method's signature has been modified. This change affects how the method is called or interacts with other components. Users should refer to the updated method signature in the user manual to ensure compatibility with existing implementations.

---

## Usage Questions

### How do I use the new `Ping6Servo` method?

The `Ping6Servo` method is designed to enhance the library's functionality. While specific details on its parameters and usage are not provided here, users are encouraged to consult the updated user manual for comprehensive guidance on implementing this method effectively.

---

## Advanced Questions

### How do I adapt to the modified `ST3215` method signature?

With the modification of the `ST3215` method's signature, users should review the updated documentation to understand the new parameters and usage patterns. This ensures that existing codebases remain compatible and leverage the latest improvements.

---

**Last Updated:** February 2026  
**Library Version:** 0.0.1  
**Author:** Mickael Roger
```
