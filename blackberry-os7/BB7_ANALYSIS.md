# BlackBerry OS 7.1 Firmware Analysis — Bold 9900 Simulator

## Overview

This document analyzes the BlackBerry OS 7.1 firmware extracted from the official Bold 9900 Simulator. The analysis covers the OS architecture, file system structure, application framework, and security model.

## Device Specifications

| Property | Value |
|----------|-------|
| Device | BlackBerry Bold 9900 (Dakota) |
| OS Version | BlackBerry OS 7.1.0.318 |
| Hardware ID | 0x07001204 |
| Display | 640x480 TFT |
| RAM | 768 MB |
| CPU | Qualcomm MSM8655 (ARM Scorpion 1.2GHz) |
| Connectivity | GSM/UMTS, WiFi, Bluetooth 2.1, NFC |

## File System Structure

- `9900-fs.dmp` — Filesystem dump (255MB)
- `9900-nv.dmp` — Non-volatile storage (7MB)
- `9900.xml` — Device configuration (120+ applications)
- `Jvm.dll` — BlackBerry Java VM (17MB)
- `Java/` — 1785 COD files (compiled Java applications)
- `Debug/` — 4910 debug symbol files
- `*.alx` — 25 application descriptors

## COD File Format

COD files are ZIP archives containing compiled BlackBerry Java bytecode:

- Outer: Standard ZIP with `.cod` extension
- Inner: PSI (Portable Service Interface) v1 compiled data
- Magic: `0xDE C0 FF FF` (proprietary header)
- Bytecode: Custom register-based VM, not standard Java ME

## Application Categories

### Core OS (1783 modules)

| Category | Examples | Count |
|----------|----------|-------|
| UI Framework | net_rim_ui_*, net_rim_bb_framework_* | ~200 |
| Messaging | net_rim_bb_messaging*, net_rim_bMessage | ~50 |
| Network | net_rim_cldc_io_*, net_rim_bb_bis_* | ~100 |
| Security | net_rim_crypto*, net_rim_bb_ams_* | ~80 |
| Phone/Radio | net_rim_java_phone*, net_rim_bb_radio* | ~60 |
| Browser | net_rim_java_browser*, OlympiaWebKit* | ~40 |
| Media | net_rim_bb_medialoader*, net_rim_amms* | ~30 |
| Input | net_rim_blackberry_lang* | ~60 |
| Fonts | net_rim_font_* | ~20 |

### Third-Party Applications (2 modules)

- `com.dataviz.dxtg` — Documents To Go
- `net.rim.device.apps.games.BrickBreaker` — BrickBreaker game
- `net.rim.device.apps.games.WordMole` — WordMole game

## Application Framework

### ALX (Application Loader XML)

ALX files define application metadata for deployment:

```
Application ID: net.rim.blackberry
Name: BlackBerry Core Applications
Version: %_appsVersion:V03%
Vendor: Research In Motion Limited
Copyright: 1998-2010

Modules included:
- net_rim_bb_messaging (messaging app)
- net_rim_java_browser (web browser)
- net_rim_bb_facebook (Facebook app)
- net.rim.java.blackberrymessenger (BBM)
- net.rim.bb.appworld (App World)
- ... 100+ more modules
```

### Application Lifecycle

1. **Installation**: ALX defines modules to load
2. **JVM Startup**: Jvm.dll initializes the BlackBerry Java VM
3. **Module Loading**: COD files loaded in dependency order
4. **Application Launch**: MIDlets or UiApplications started
5. **Runtime**: Event-driven with persistent storage

## Security Model

### Application Permission System

BlackBerry OS 7 uses a capability-based security model:

- Applications request permissions via ApplicationDescriptor
- Users grant/deny at install time or runtime
- AMS (Application Management System) enforces permissions

### Key Security Components

- `net_rim_bb_ams_enforcement` — Permission enforcement
- `net_rim_bb_ams_transport_impl` — Secure transport
- `net_rim_bb_application_permissions_proxy` — Permission proxy
- `net_rim_crypto` — Cryptographic services
- `net_rim_DoDRootCerts` — Department of Defense root certificates
- `net_rim_MIDPRootCerts` — MIDP root certificates

### Cryptographic Stack

- AES, 3DES for symmetric encryption
- RSA, ECC for asymmetric
- SHA-1, SHA-256 for hashing
- X.509 certificate support
- SSL/TLS for network security

## Debug Symbols Analysis

The Debug/ directory contains 4910 `.debug` files with:

- Class names and package structure
- Method signatures
- Source file paths (internal RIM paths)
- Line number mappings

### Notable Internal Paths Found

- `C:\Lynx\runtime\` — Main development path
- `C:\Lynx\runtime\net\rim\device\apps\` — Application APIs
- `C:\tmp\rpc_rc_49429295.dir\` — Build system paths

### Class Hierarchy (from debug files)

```
java.lang.Object
├── net.rim.device.api.ui.UiApplication
├── net.rim.device.api.system.Application
├── net.rim.device.api.system.PersistentObject
├── net.rim.device.api.ui.container.MainScreen
├── net.rim.device.api.ui.component.Field
│   ├── net.rim.device.api.ui.component.ChoiceField
│   ├── net.rim.device.api.ui.component.CheckboxField
│   └── net.rim.device.api.ui.component.TextField
└── net.rim.device.api.ui.Font
```

## NV (Non-Volatile) Storage

The 7MB NV dump contains:

- Device settings and preferences
- WiFi profiles and saved networks
- Bluetooth pairings
- Email account configurations
- Application data (persistent storage)
- Security keys and certificates

## Comparison: BB7 vs BB10

| Feature | BlackBerry OS 7 | BlackBerry 10 |
|---------|----------------|---------------|
| Kernel | Proprietary | QNX Neutrino |
| App Format | COD (Java ME) | BAR (Cascades/Qt) |
| Runtime | Custom JVM | POSIX + Qt |
| UI Framework | UiApplication | Cascades |
| File System | Proprietary | QNX6 (PowerFS) |

## Conclusion

BlackBerry OS 7.1 is a mature, proprietary mobile OS built on:

1. A custom Java ME runtime with register-based bytecode
2. A capability-based security model
3. Tight integration with BlackBerry infrastructure (BES, BIS)
4. Support for NFC, WebKit browser, and multimedia

The firmware analysis reveals a well-structured but closed ecosystem with limited third-party extensibility compared to modern mobile platforms.
