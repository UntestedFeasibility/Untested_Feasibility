# BlackBerry OS 7.1 Architecture

## Overview

BlackBerry OS 7.1 is the final iteration of Research In Motion's legacy Java-based mobile operating system. Released in December 2011, it powered devices like the Bold 9900, Torch 9810, and Curve 9360. This document examines the system architecture based on analysis of the official Bold 9900 Simulator package.

## Device Specifications

| Property | Value |
|----------|-------|
| Device | BlackBerry Bold 9900 (Dakota) |
| OS Version | 7.1.0.318 |
| Hardware ID | 0x07001204 |
| CPU | Qualcomm MSM8655 (ARM Scorpion @1.2GHz) |
| GPU | Adreno 205 |
| RAM | 768 MB |
| Flash | 8 GB |
| Display | 640x480 TFT (2.8") |
| Connectivity | GSM/UMTS/HSPA, WiFi 802.11a/b/g/n, BT 2.1, NFC |

## System Layers

```
┌─────────────────────────────────────────────────────┐
│                  User Applications                  │
│  (Phone, Browser, BBM, Facebook, Maps, App World)  │
├─────────────────────────────────────────────────────┤
│                Application Framework                │
│  (UiApplication, Application, Invocation Framework) │
├─────────────────────────────────────────────────────┤
│                   Java ME / CLDC                     │
│  (net_rim_cldc, net_rim_os, MIDP compatibility)     │
├─────────────────────────────────────────────────────┤
│                  Platform Services                   │
│  (PIM, Messaging, Crypto, Media, Networking, NFC)   │
├─────────────────────────────────────────────────────┤
│               Native OS Kernel (proprietary)         │
│  (Real-time microkernel, drivers, file system)       │
├─────────────────────────────────────────────────────┤
│                    Hardware Layer                    │
│  (Qualcomm MSM8655 SoC, sensors, radios)            │
└─────────────────────────────────────────────────────┘
```

## Module System

BlackBerry applications are packaged as `.cod` (Compiled Object Data) files. The simulator contains **1,785 COD modules** organized by function.

### Module Categories

| Category | Module Prefix | Count | Description |
|----------|--------------|-------|-------------|
| UI Framework | `net_rim_ui_*`, `net_rim_bb_framework_*` | ~200 | Screen, Field, Manager hierarchy |
| Messaging | `net_rim_bb_messaging*`, `net_rim_bMessage` | ~50 | Email, SMS, MMS, IM |
| Networking | `net_rim_cldc_io_*`, `net_rim_bb_bis_*` | ~100 | HTTP, SSL, TCP/IP, WAP |
| Security | `net_rim_crypto*`, `net_rim_bb_ams_*` | ~80 | Encryption, permissions, certificates |
| Telephony | `net_rim_bb_phone*`, `net_rim_bb_call_control` | ~60 | Call control, SIM, radio |
| Browser | `net_rim_bb_browser*`, `OlympiaWebKit*` | ~40 | WebKit-based web browser |
| Media | `net_rim_bb_media*`, `net_rim_amms` | ~30 | Camera, video, audio, DRM |
| PIM | `net_rim_bb_addressbook*`, `net_rim_bb_calendar*` | ~40 | Contacts, calendar, tasks |
| NFC | `net_rim_nfc*` | ~10 | Near Field Communication |
| Bluetooth | `net_rim_bluetooth*` | ~15 | BT stack, file transfer, MAP |

### Application Lifecycle

```
1. Installation    ALX manifest defines modules and dependencies
        ↓
2. JVM Startup     Jvm.dll initializes the BlackBerry Java VM
        ↓
3. Module Loading  COD files loaded in dependency order
        ↓
4. App Launch      MIDlets or UiApplications started
        ↓
5. Runtime         Event-driven with persistent storage
```

## Application Framework

### Base Classes

| Class | Purpose |
|-------|---------|
| `Application` | Base class for all BB apps; lifecycle, events, storage |
| `UiApplication` | Extends Application with GUI; screen navigation, menus |
| `Screen` | Base for all visible UI containers |
| `Field` | Base for all UI components (buttons, text, lists) |
| `Manager` | Container for organizing Fields |
| `PersistentObject` | Serialized Java objects in flash memory |

### UI Component Hierarchy

```
Field
├── FieldManager (container)
├── LabelField
├── TextField
├── BasicEditField
├── RichTextField
├── ButtonField
├── ChoiceField
│   ├── CheckboxField
│   └── RadioField
├── ListField
├── GaugeField
└── CustomField (custom rendering)
```

### Screen Navigation Stack

```
MainScreen
├── Dialog (modal)
├── PopupScreen (floating)
├── FullScreen (no title/status)
└── CustomScreen (application-specific)
```

## Major Subsystems

### Telephony

| Module | Description |
|--------|-------------|
| `net_rim_bb_phone_api` | Phone API (call control, SIM management) |
| `net_rim_bb_phone_app` | Phone application UI |
| `net_rim_bb_call_control` | Low-level call control |
| `net_rim_bb_sms` / `net_rim_bb_sms_compose` | SMS |
| `net_rim_bb_mms` | MMS |
| `net_rim_bb_sim` | SIM card management |
| `net_rim_cellbroadcast` | Cell broadcast |
| `net_rim_bb_cmas` | Commercial Mobile Alert System |

Supported radio types: GPRS, UMTS, CDMA, CDMA-GPRS, WLAN, IDEN

### Networking Stack

```
┌─────────────────────────────────────┐
│   HTTP / HTTPS / WAP                │
│   (net_rim_cldc_io_http/https/wap)  │
├─────────────────────────────────────┤
│   SSL / TLS                         │
│   (net_rim_cldc_io_ssl/tls)         │
├─────────────────────────────────────┤
│   TCP/IP                            │
│   (net_rim_cldc_io_ip)              │
├─────────────────────────────────────┤
│   I/O Framework                     │
│   (net_rim_cldc_io)                 │
├─────────────────────────────────────┤
│   User-space Network Stack          │
│   (net_rim_bb_ustack)               │
└─────────────────────────────────────┘
```

Additional networking modules:
- `net_rim_bb_manage_connections` — Connection manager UI
- `net_rim_bb_externalproxy` — External proxy support
- `net_rim_wlan_*` — WiFi configuration and management
- `net_rim_cldc_impl_vpn` — VPN implementation
- `net_rim_bb_dnslookup_app` — DNS lookup utility
- `net_rim_bb_ping_app` — Ping utility

### Browser (Olympia/WebKit)

| Module | Description |
|--------|-------------|
| `net_rim_bb_browser_olympia` | WebKit-based browser core |
| `net_rim_bb_browser_field_api` | BrowserField API (embedding) |
| `net_rim_bb_browser_field2_api` | BrowserField2 (enhanced) |
| `net_rim_bb_browser_lib` | Browser library |
| `net_rim_bb_browser_daemon` | Background browser service |
| `net_rim_bb_browser_cookiejar` | Cookie management |
| `OlympiaWebKit.dll` | Native WebKit DLL |

### Media Subsystem

| Module | Description |
|--------|-------------|
| `net_rim_media` / `net_rim_media_api` | Core media APIs |
| `net_rim_bb_media_framework_api` | Media framework |
| `net_rim_bb_medialibrary` | Media library management |
| `net_rim_bb_mediarecorder` | Audio/video recording |
| `net_rim_bb_camera` | Camera control |
| `net_rim_bb_docview` | Document/image viewer |
| `net_rim_drm` / `net_rim_bb_drm_agent` | DRM |
| `net_rim_bb_mtp` | Media Transfer Protocol |
| `net_rim_speech` / `net_rim_nuance` | Speech recognition |

### Storage and Database

| Module | Description |
|--------|-------------|
| `net_rim_database` | Persistent database API |
| `net_rim_sql` | SQL database engine (SQLite-based) |
| `net_rim_bb_file_explorer` | File explorer |
| `net_rim_bb_fileindexservice` | File indexing/search |
| `net_rim_bb_passwordkeeper` | Encrypted password storage |

Storage mechanisms:
1. **PersistentObject** — Key-based serialized Java objects in flash
2. **Store API** — Binary key-value store
3. **SQLite** — Relational database via `net_rim_sql`
4. **File System** — Internal flash and SD card

### Application Management

| Module | Description |
|--------|-------------|
| `net_rim_app_manager` | Application manager |
| `net_rim_bb_ams_enforcement_impl` | AMS enforcement |
| `net_rim_bb_ams_transport_impl` | AMS transport |
| `net_rim_bb_application_permissions_proxy` | Permissions proxy |
| `net_rim_bb_trust_application_manager` | Trust management |
| `net_rim_bb_apps_framework` | Application framework |

## ALX (Application Loader XML)

ALX files define application metadata for deployment:

```xml
<Application id="net.rim.blackberry">
    <Name>BlackBerry Core Applications</Name>
    <Version>%_appsVersion:V03%</Version>
    <Vendor>Research In Motion Limited</Vendor>
    <Copyright>1998-2010</Copyright>
    
    <Files>
        <FileSet radio="GPRS">
            <And>
                <File>net_rim_bb_messaging.cod</File>
                <File>net_rim_java_browser.cod</File>
            </And>
        </FileSet>
    </Files>
</Application>
```

## Pre-loaded Applications (Bold 9900)

| Application | Package | Description |
|------------|---------|-------------|
| BlackBerry Messenger | `net.rim.java.blackberrymessenger` | BBM v6.1.0.55 |
| App World | `net.rim.bb.appworld` | App store v3.1.1.19 |
| Facebook | `net.rim.bb.facebook` | Social networking |
| Twitter | `net.rim.bb.twitter` | Microblogging |
| YouTube | `net.rim.bb.youtube` | Video streaming |
| BlackBerry Maps | `net.rim.bb.maps` | Navigation |
| BrickBreaker | `net.rim.device.apps.games.BrickBreaker` | Game |
| Word Mole | `net.rim.device.apps.games.WordMole` | Game |
| Password Keeper | `net.rim.java.passwordkeeper` | Secure storage |
| Documents To Go | `com.dataviz.dxtg` | Office suite |

## Localization

The OS supports **30+ languages** including:
- Western European: English, French, German, Spanish, Italian, Portuguese, Dutch
- Eastern European: Polish, Czech, Hungarian, Romanian, Croatian
- Asian: Chinese (Simplified/Traditional), Japanese, Korean, Thai, Vietnamese
- Middle Eastern: Arabic, Hebrew

Chinese input methods: Pinyin, CangJei, Wubi, Strokes, BoPoMoFo, Jyutping, Handwriting

## Comparison: BlackBerry OS 7 vs Modern Platforms

| Feature | BB OS 7 (2011) | iOS 5 (2011) | Android 4.0 (2011) |
|---------|----------------|--------------|---------------------|
| Kernel | Proprietary RTOS | XNU (Mach/BSD) | Linux |
| Runtime | Java ME (CLDC) | Objective-C (native) | Dalvik (Java-based) |
| App Format | .cod (pre-verified) | .ipa | .apk (DEX) |
| Security | Code signing + IT Policy | App sandbox | Linux UID sandbox |
| UI Framework | Screen/Field | UIKit | Activity/View |
| Browser | WebKit (Olympia) | Mobile Safari | WebView |
| NFC | Yes (native) | No | Yes (since 2.3) |
| Multitasking | Cooperative | Limited | Full |

## Historical Significance

BlackBerry OS 7 represents the culmination of a decade of mobile enterprise computing:

1. **Pioneered push email** — Near-real-time email delivery before smartphones were common
2. **Enterprise security standard** — Code signing, IT policies, BES integration
3. **Physical keyboard optimization** — Predictive text engine for hardware keyboards
4. **Always-on connectivity** — Persistent NOC connection for efficient data usage
5. **NFC pioneer** — Among first mainstream smartphones with native NFC

The platform's limitations (Java ME restrictions, limited UI capabilities, small app ecosystem) ultimately led to BlackBerry's transition to QNX-based BlackBerry 10 in 2013.

---

*Analysis based on BlackBerry Bold 9900 Simulator (SimPackage-7.1.0.318). All module names and architectural observations derived from simulator file system analysis.*
