# Self-healing

Self-healing crystallizes the capability of autonomously recovering affected parts of the system at both hardware and software levels caused by failures or abnormal states. It can also restart the system to pre-established routine schedules, if necessary.

Self-healing is one of the two self-* capabilities that can interact directly with the IE's hardware, as depicted in Figure 1.

# Relationships with Other Self-* Capabilities

![aeriOS self-* capabilities](./res/self.png)  
*Figure 1: aeriOS self-* capabilities*

## Overview

The aeriOS Self-Healing module provides automated recovery mechanisms to detect and mitigate failures in Infrastructure Elements (IEs). It continuously monitors system health and applies corrective actions when failures occur.

The module currently monitors the following scenarios:

---

### 1. Sensor Failure

- **Scenario**:  
  This can be identified by reading the values the sensor provides to the device/RPi:
  - No measurement at the device – indicates a failure in the sensing part (assuming all other functionalities are normal). In this case, the failure would be reported by self-healing to Trust-Manager component. Since the RPi is an IE with limited capabilities (in aeriOS terms), it will initially just print a message.
  - A sensor measurement that is identified as an outlier, either through an internal procedure in the device or the diagnosis component.

- **Action**:  
  Healing in this scenario could be applied by creating and sending alert messages to exclude the sensor from the set providing input to the system.

---

### 2. Device Power Alert

- **Scenario**:  
  Similar to Scenario 1, the power levels of the device can be measured and reported. The stimulus comes from the device itself, and the failure is more severe as it refers to the entire IE component (not just a sensor).

- **Action**:  
  Healing could be applied by creating and sending alert messages for recharging or battery replacement.

---

### 3. Network Protocol Violation

- **Scenario**:  
  A link-level protocol may operate in unlicensed bands (e.g., WiFi, LoRa) and have Duty Cycle (DC) limitations. Monitoring agents at the Gateway (GW) can check for violations and command reconfiguration of the DC value. Typical DC values include 0.1%, 1%, and 10%.

- **Action**:  
  Healing could be applied by enforcing reconfiguration of the IE.

---

### 4. Link Quality Issues

- **Scenario**:  
  Radio values of IE communication (e.g., to a Gateway, Base Station, Access Point) are stored. If values drop below a set threshold (based on past values), this is reported to Trust-Manager component.

- **Action**:  
  Healing can be applied by sending commands to the GW to reconfigure link parameters such as the spreading factor (SF) and rate.

---

### 5. Communication Failure Indication (No Messages Received by IE)

- **Scenario**:  
  This is a critical failure that may be caused by network or hardware issues. However, sometimes the IE has nothing to send, and it may not be an actual issue.

- **Action**:  
  A possible healing approach could involve setting up a dedicated channel (e.g., a WiFi connection) to poll and check if the IE is alive.

---

## Getting Started

This module does **not** require the deployment of other components beforehand (i.e., deploying *self-adaptation* or *self-optimization* before *self-healing* will not trigger any errors). Once deployed, it will automatically start monitoring IoT devices directly connected to Infrastructure Elements (IEs)
and detecting abnormal states associated to typical IoT scenarios.

For full functionality, the component should be deployed within the IE along with *self-api* and *Trust-manager*.

Configure the self-healing settings in:  
- [`config.ini` for self_healing_app](./src/self_healing_app/config/config.ini)  
- [`config.ini` for self_healing_api](./src/self_healing_api/config.ini)

---

## Local Deployment

To test the module locally:

1. **Download or clone the repository**:

    ```bash
    git clone https://github.com/eclipse-aerios/self-healing
    ```

2. **Create and activate a Python virtual environment**:

    ```bash
    python3 -m venv self-healing-env
    source self-healing-env/bin/activate
    ```

3. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the module**:

    ```bash
    python src/self_healing_app/main.py
    ```

**Notes**  
- If you're using `python` instead of `python3`, adjust accordingly.  
- For different operating systems, the virtual environment activation command may vary.

---

## License

This software is licensed under the **Apache License v2.0**.
