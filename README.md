# CNF , Worker Node Introspection 

This repo contains mainly two toolchain.   

* main.py a standalone CLI client that aggregates hardware, software, proc, memory , PCI, numa topology tree etc., in a structured format.

* server.py a server-side, provides rest API, and each action serializes structured output. For example, if you have an ansible or any other pipeline 
and would like to query get OS-specific data without constantly ssh sessions to a host.

## Example

```bash
python new_main.py network
```

Will output json notice pci address / hardware ptp etc aggregate to singel view per adapter.

```json
{
    "eno1": {
        "address": "e4:43:4b:64:fe:9c",
        "bus-info": " 0000:1a:00.0",
        "driver": " ixgbe",
        "expansion-rom-version": "",
        "firmware-version": " 0x800014a5, 20.5.13",
        "hardware-raw-clock": true,
        "hardware-receive": true,
        "hardware-transmit": true,
        "name": "eno1",
        "pci": "0000:1a:00.0",
        "software-receive": true,
        "software-system-clock": true,
        "software-transmit": true,
        "supports-eeprom-access": " yes",
        "supports-priv-flags": " yes",
        "supports-register-dump": " yes",
        "supports-statistics": " yes",
        "supports-test": " yes",
        "version": " 5.14.0-226.rt14.227.mus_cgroupf"
    },
    "eno2": {
        "address": "e4:43:4b:64:fe:9d",
        "bus-info": " 0000:1a:00.1",
        "driver": " ixgbe",
        "expansion-rom-version": "",
        "firmware-version": " 0x800014a5, 20.5.13",
        "hardware-raw-clock": true,
        "hardware-receive": true,
        "hardware-transmit": true,
        "name": "eno2",
        "pci": "0000:1a:00.1",
        "software-receive": true,
        "software-system-clock": true,
        "software-transmit": true,
        "supports-eeprom-access": " yes",
        "supports-priv-flags": " yes",
        "supports-register-dump": " yes",
        "supports-statistics": " yes",
        "supports-test": " yes",
        "version": " 5.14.0-226.rt14.227.mus_cgroupf"
    },
 }
```

Similarly, we can filter by name, alias name, PCI address, and mac address.

```bash
python new_main.py network -i eth9
```

```json
{
    "eth9": {
        "address": "64:4c:36:12:f7:54",
        "bus-info": " 0000:41:00.0",
        "driver": " i40e",
        "expansion-rom-version": "",
        "firmware-version": " 8.20 0x80009bad 0.0.0",
        "hardware-raw-clock": true,
        "hardware-receive": true,
        "hardware-transmit": true,
        "name": "eth9",
        "pci": "0000:41:00.0",
        "software-receive": true,
        "software-system-clock": true,
        "software-transmit": true,
        "supports-eeprom-access": " yes",
        "supports-priv-flags": " yes",
        "supports-register-dump": " yes",
        "supports-statistics": " yes",
        "supports-test": " yes",
        "version": " 5.14.0-226.rt14.227.mus_cgroupf"
    }
}
```

```bash
 python new_main.py network -i 0000:41:00.0
 ```
