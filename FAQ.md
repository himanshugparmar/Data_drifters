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

## Hardware Questions

### What voltage should I use?

**Recommended:** 7.4V (2S LiPo) or 11.1V (3S LiPo)

| Voltage | Use Case | Performance |
|---------|----------|-------------|
| 6.0V | Minimum, light load | Low torque, slow |
| 7.4V (2S) | **Recommended for most** | Good balance |
| 11.1V (3S) | High performance | Maximum torque & speed |
| 12.6V | Maximum (3S charged) | Use with caution |
| <6.0V | Not recommended | Erratic behavior |
| >12.6V | **Dangerous** | Will damage servo |

**Voltage vs Performance:**
```
Torque: Higher voltage = higher torque (up to ~50% more @ 12V vs 6V)
Speed: Higher voltage = higher speed (up to ~70% more @ 12V vs 6V)
Current: Higher voltage = higher current draw
Lifespan: Continuous 12V operation may reduce lifespan
```

---

### Can I power servos from USB?

**NO! Never power servos from USB.**

**Why:**
- USB provides max 500mA (USB 2.0) or 900mA (USB 3.0)
- Servo draws 100-2000mA, peaks higher during movement
- Insufficient current causes:
  - Erratic behavior
  - Communication errors
  - Voltage drops
  - Potential computer damage

**Correct wiring:**
```
                 External Power Supply
                      (6-12V, 2A+)
                          │
                    ┌─────┴─────┐
                    │           │
USB Adapter ────────┤  GND  VCC ├──── Servo
  (Signal/GND)      └───────────┘   (GND/VCC/DATA)
                          │
                     Common GND
```

**Key points:**
- Servo VCC from external power supply
- Servo GND connected to both power supply AND USB adapter GND
- USB adapter provides signal only
- **Common ground is essential**

---

### What type of power supply should I use?

**Options ranked:**

1. **LiPo Battery (Best)**
   - 2S (7.4V) or 3S (11.1V)
   - High current capability
   - Stable voltage
   - Portable
   - ⚠️ Requires proper charging & storage

2. **Switching Power Supply (Good)**
   - 12V 5A or higher
   - Well-regulated
   - Must handle current spikes
   - Look for "servo power supply"

3. **Bench Power Supply (Testing)**
   - Variable voltage useful
   - Set current limit to prevent damage
   - Not portable

4. **Wall Adapter (Not Recommended)**
   - Often insufficient current
   - Poor regulation
   - Voltage drop under load

**Sizing power supply:**
```
Number of servos × 2A = Minimum capacity
Example: 3 servos × 2A = 6A minimum
Actual: 3 servos × 2A = 6A × 1.5 (safety factor) = 9A recommended

Recommendation: Get 10-12A supply for 3-4 servos
```

---

### What's the maximum cable length?

**Without repeater:**
- **Reliable:** 1-3 meters
- **Maximum:** 5 meters (may need lower baudrate)

**Factors:**
- Cable quality (use shielded cable for >2m)
- Baudrate (lower baudrate = longer distance)
- Interference (keep away from power cables)

**Extending range:**

```python
# Reduce baudrate for longer cables
servo.ChangeBaudrate(1, 4)  # 115200 bps

# Lower baudrates are more reliable over distance:
# 1M bps: 1-2 meters
# 115.2K: 3-5 meters
# 57.6K: 5-10 meters
```

**Professional solution:**
- Use RS485 adapter (converts UART to differential RS485)
- RS485 supports 100+ meters
- Available from robotics suppliers

---

### Can I connect servos in daisy-chain?

**Yes, daisy-chain is supported:**

```
USB────[S1]────[S2]────[S3]────[S4]
        │       │       │       │
        └───────┴───────┴───────┘─── Common Power
```

**Wiring:**
- Connect DATA out of S1 to DATA in of S2
- All servos share power (VCC + GND)
- Each servo needs unique ID

**Limitations:**
- **Total cable length** still applies
- **Power distribution** - voltage drop increases along chain
- **Star topology better for power** (see below)

**Star topology (recommended for 3+ servos):**
```
         Power Supply
              │
        ┌─────┼─────┬─────┐
        │     │     │     │
       S1    S2    S3    S4
         \    |    /
          \   |   /
           \  |  /
         USB Adapter
           (DATA)
```

---

## Software Questions

### What Python version is required?

**Minimum:** Python 3.10

**Recommended:** Python 3.11 or 3.12

**Check your version:**
```bash
python3 --version
```

**Not supported:**
- Python 2.x (deprecated)
- Python 3.9 and earlier

**Reason:** Library uses modern Python features (type hints, match statements, etc.)

---

### What dependencies are needed?

**Only one:** `pyserial`

```bash
pip install pyserial
```

**Full installation:**
```bash
# Clone repository
git clone https://github.com/Mickael-Roger/python-st3215
cd python-st3215

# Install dependencies
pip install -r requirements.txt

# Install library
pip install -e .
```

**Verify installation:**
```python
python3 -c "from st3215 import ST3215; print('OK')"
```

---

### Does this work on Windows/macOS/Linux?

**Yes, all three!**

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✓ Excellent | Native support, dev/ttyUSB* |
| Raspberry Pi | ✓ Excellent | GPIO UART available |
| Windows | ✓ Good | Use COM ports, need drivers |
| macOS | ✓ Good | Use /dev/cu.*, may need permissions |

**Platform-specific:**

```python
import platform

if platform.system() == 'Windows':
    device = 'COM3'
elif platform.system() == 'Darwin':  # macOS
    device = '/dev/cu.usbserial-1420'
else:  # Linux
    device = '/dev/ttyUSB0'

servo = ST3215(device)
```

---

### Can I use this in a multi-threaded application?

**Yes, with caution.**

The library uses a threading lock (`self.lock`) for thread safety, but:

**Safe:**
```python
import threading

def move_servo_1():
    servo.MoveTo(1, 2048)

def move_servo_2():
    servo.MoveTo(2, 3000)

t1 = threading.Thread(target=move_servo_1)
t2 = threading.Thread(target=move_servo_2)
t1.start()
t2.start()
t1.join()
t2.join()
```

**Unsafe:**
```python
# Don't create multiple ST3215 instances for same port
servo1 = ST3215("/dev/ttyUSB0")  # First instance
servo2 = ST3215("/dev/ttyUSB0")  # ERROR: Port already open!
```

**Best practice:**
```python
# Single servo controller instance
servo = ST3215("/dev/ttyUSB0")

# Share across threads
class ServoController:
    def __init__(self):
        self.servo = ST3215("/dev/ttyUSB0")
    
    def move_async(self, servo_id, position):
        # Thread-safe due to internal lock
        self.servo.MoveTo(servo_id, position)
```

---

## Usage Questions

### How do I convert between position and angles?

**Position to degrees:**
```python
def position_to_degrees(position):
    """Convert position (0-4095) to degrees (0-360)"""
    return (position / 4095) * 360

# Example
pos = 2048
degrees = position_to_degrees(pos)
print(f"{pos} = {degrees:.1f}°")  # 2048 = 180.0°
```

**Degrees to position:**
```python
def degrees_to_position(degrees):
    """Convert degrees (0-360) to position (0-4095)"""
    return int((degrees / 360) * 4095)

# Example
angle = 90
pos = degrees_to_position(angle)
print(f"{angle}° = {pos}")  # 90° = 1024
```

**Radians:**
```python
import math

def position_to_radians(position):
    """Convert position to radians"""
    return (position / 4095) * 2 * math.pi

def radians_to_position(radians):
    """Convert radians to position"""
    return int((radians / (2 * math.pi)) * 4095)
```

**Using a class:**
```python
class PositionConverter:
    MAX_POS = 4095
    
    @staticmethod
    def to_degrees(position):
        return (position / PositionConverter.MAX_POS) * 360
    
    @staticmethod
    def to_radians(position):
        return (position / PositionConverter.MAX_POS) * 2 * math.pi
    
    @staticmethod
    def from_degrees(degrees):
        return int((degrees / 360) * PositionConverter.MAX_POS)
    
    @staticmethod
    def from_radians(radians):
        return int((radians / (2 * math.pi)) * PositionConverter.MAX_POS)
```

---

### What's the difference between MoveTo and WritePosition?

| Feature | MoveTo() | WritePosition() |
|---------|----------|-----------------|
| **Sets mode** | Yes (position mode) | No |
| **Sets speed** | Yes (if provided) | No (uses existing) |
| **Sets acceleration** | Yes (if provided) | No (uses existing) |
| **Wait option** | Yes | No |
| **High-level** | Yes | No (low-level) |
| **Recommended** | **YES** | Only for advanced use |

**Example:**

```python
# MoveTo (recommended) - complete control
servo.MoveTo(1, 2048, speed=2400, acc=50, wait=False)

# WritePosition - just sets target
servo.SetMode(1, 0)  # Must set mode
servo.SetSpeed(1, 2400)  # Must set speed
servo.SetAcceleration(1, 50)  # Must set acceleration
servo.WritePosition(1, 2048)  # Then write position
```

**Use MoveTo() unless:**
- You need maximum performance (skip redundant mode/speed/acc sets)
- You're implementing custom motion control
- You're using group sync operations

---

### How fast can I send commands?

**Limits:**

| Operation | Max Rate | Notes |
|-----------|----------|-------|
| Read single parameter | ~100 Hz | 10ms interval |
| Write single parameter | ~100 Hz | 10ms interval |
| MoveTo command | ~50 Hz | 20ms interval |
| Scan all servos | ~0.03 Hz | 30 seconds total |

**Practical example:**
```python
import time

# GOOD: Control loop at 50-100 Hz
while True:
    position = servo.ReadPosition(1)
    # Process...
    servo.MoveTo(1, new_target)
    time.sleep(0.02)  # 50 Hz

# TOO FAST: Commands may collide
while True:
    servo.MoveTo(1, target)  # No delay!
```

**Optimize with batch operations:**
```python
# Instead of reading each servo individually
for sid in [1, 2, 3, 4]:
    pos = servo.ReadPosition(sid)  # 4 × 10ms = 40ms

# Consider GroupSyncRead for better performance
# See User Manual for details
```

---

### Can I control servo speed directly in rotation mode?

**Yes! That's what rotation mode is for:**

```python
# Switch to rotation mode
servo.SetMode(1, 1)

# Set rotation speed (-3400 to +3400 step/s)
servo.Rotate(1, 1000)  # CW at 1000 step/s
servo.Rotate(1, -500)  # CCW at 500 step/s
servo.Rotate(1, 0)     # Stop

# Or use the Rotate method which sets mode automatically
servo.Rotate(1, 1000)  # Automatically switches to mode 1
```

**Rotation mode vs Position mode:**
- **Position mode:** Go to specific angle, speed is max speed
- **Rotation mode:** Continuous rotation at specified speed

---

### How do I make smooth movements?

**Several approaches:**

#### 1. **Adjust acceleration**
```python
# Smooth (gradual)
servo.SetAcceleration(1, 20)
servo.MoveTo(1, 3000)

# Aggressive (fast but jerky)
servo.SetAcceleration(1, 200)
servo.MoveTo(1, 3000)
```

#### 2. **Reduce speed**
```python
# Slow, smooth
servo.SetSpeed(1, 800)

# Fast
servo.SetSpeed(1, 3400)
```

#### 3. **Trajectory with waypoints**
```python
# Move through intermediate positions
waypoints = [2048, 2200, 2500, 2900, 3000]
for wp in waypoints:
    servo.MoveTo(1, wp, wait