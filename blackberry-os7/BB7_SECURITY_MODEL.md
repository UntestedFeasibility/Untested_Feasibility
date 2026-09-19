# BlackBerry OS 7.1 Security Model

## Overview

BlackBerry OS 7.1 implements a comprehensive, multi-layered security architecture that made it the gold standard for enterprise mobile security. This document examines the cryptographic subsystem, application permissions model, certificate infrastructure, and enterprise management capabilities.

## Security Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│              Enterprise IT Policy                    │
│  (BES enforcement, device restrictions, passwords)   │
├─────────────────────────────────────────────────────┤
│            Application Security                      │
│  (Code signing, permissions, sandboxing)            │
├─────────────────────────────────────────────────────┤
│              Transport Security                      │
│  (SSL/TLS, S/MIME, PGP, VPN)                       │
├─────────────────────────────────────────────────────┤
│             Cryptographic Core                       │
│  (AES, RSA, ECC, SHA, X.509, PKI)                  │
├─────────────────────────────────────────────────────┤
│              Hardware Security                       │
│  (Secure storage, smart cards, NFC TSM)             │
└─────────────────────────────────────────────────────┘
```

## Cryptographic Subsystem

### Core Modules

| Module | Description |
|--------|-------------|
| `net_rim_crypto` (12 segments) | Core cryptographic library |
| `net_rim_crypto_pgp` (2 segments) | PGP operations |
| `net_rim_crypto_cms` | Cryptographic Message Syntax (S/MIME) |
| `net_rim_crypto_keystore_browser` | Key store browser |
| `net_rim_crypto_keystore_browser_certificate` | Certificate key store |
| `net_rim_crypto_keystore_browser_pgp` | PGP key store |
| `net_rim_bb_crypto_api` | BlackBerry Crypto API |

### Algorithms Supported

#### Symmetric Encryption

| Algorithm | Key Sizes | Modes |
|-----------|-----------|-------|
| AES | 128, 192, 256-bit | CBC, CTR, GCM |
| 3DES | 168-bit (effective) | CBC |
| RC2 | Variable | CBC |
| DES | 56-bit | CBC (legacy) |

#### Asymmetric Encryption

| Algorithm | Key Sizes | Use Cases |
|-----------|-----------|-----------|
| RSA | 1024, 2048, 4096-bit | Key exchange, signatures |
| ECC | 256, 384, 521-bit | Key exchange, signatures |
| Diffie-Hellman | Variable | Key agreement |

#### Hashing

| Algorithm | Output Size | Use Cases |
|-----------|-------------|-----------|
| SHA-1 | 160-bit | Signatures (legacy) |
| SHA-256 | 256-bit | Signatures, integrity |
| SHA-384 | 384-bit | Signatures |
| SHA-512 | 512-bit | Signatures |
| MD5 | 128-bit | Checksums (legacy) |

#### Message Authentication

- HMAC-MD5
- HMAC-SHA-1
- HMAC-SHA-256

### Key Management

| Component | Description |
|-----------|-------------|
| `net_rim_crypto_keystore` | Central key store |
| `net_rim_crypto_keystore_browser` | Key store UI |
| `net_rim_crypto_keystore_browser_certificate` | Certificate management |
| `net_rim_crypto_keystore_browser_pgp` | PGP key management |

Key storage locations:
- Device flash memory (encrypted)
- Smart card (via PKCS#11)
- Software token (`net_rim_cldc_impl_softtoken`)

## Application Security Model

### Code Signing

All BlackBerry applications must be **code-signed** with RIM's signing keys:

```
┌─────────────────────────────────────────────────────┐
│                 Developer                            │
│  (Signs .cod files with RIM signing keys)           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Code Signing Server                    │
│  (Validates signatures, issues certificates)        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│               Device Installation                   │
│  (AMS verifies signatures before loading)           │
└─────────────────────────────────────────────────────┘
```

Signing authority levels:

| Level | API Access | Example |
|-------|------------|---------|
| Untrusted | Limited APIs only | Basic apps |
| Rim Signed | Standard APIs | Most third-party apps |
| Vendor Signed | Vendor-specific APIs | Carrier apps |
| RIM Signed | Full API access | System apps |

### Permission System

BlackBerry uses a **capability-based permission model**:

| Permission | Description |
|------------|-------------|
| `net.rim.blackberry.api.system.DeviceInfo` | Read device info |
| `net.rim.blackberry.api.system.LEDControl` | Control LED |
| `net.rim.blackberry.api.messagelist.ApplicationIndicator` | App indicator |
| `net.rim.blackberry.api.phone.Phone` | Phone access |
| `net.rim.blackberry.api.phone.SMSMessage` | SMS access |
| `net.rim.blackberry.api.email.READ` | Read email |
| `net.rim.blackberry.api.email.SEND` | Send email |
| `net.rim.blackberry.api.pim.PIM` | PIM access |
| `net.rim.blackberry.api.lbs.Location` | GPS/location |
| `net.rim.blackberry.api.browser.field.BrowserField` | Browser |
| `net.rim.blackberry.api.net.HttpEndpoint` | HTTP access |
| `net.rim.blackberry.api.bluetooth.Bluetooth` | Bluetooth |
| `net.rim.blackberry.api.nfc.NFCManager` | NFC access |

### Permission Enforcement

| Module | Description |
|--------|-------------|
| `net_rim_bb_application_permissions_proxy` | Intercepts privileged API calls |
| `net_rim_bb_trust_application_manager` | Manages trust levels |
| `net_rim_bb_ams_enforcement_impl` | Enforces sandboxing |
| `net_rim_bb_ams_transport_impl` | Secure transport layer |

### Application Sandboxing

```
┌─────────────────────────────────────────────────────┐
│                 Application Sandbox                  │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  App Code   │  │  App Data   │  │  Permissions │ │
│  │  (.cod)     │  │  (storage)  │  │  (granted)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│  Cannot access:                                     │
│  - Other app's data                                 │
│  - System files                                     │
│  - Undeclared APIs                                  │
│  - Hardware without permission                      │
└─────────────────────────────────────────────────────┘
```

## Certificate Infrastructure

### Root Certificates

| Module | Description |
|--------|-------------|
| `net_rim_DoDRootCerts` | Department of Defense root certificates |
| `net_rim_MIDPRootCerts` | MIDP root certificates (Java ME app signing) |

### Certificate Types

| Type | Usage |
|------|-------|
| X.509 v3 | SSL/TLS, S/MIME, code signing |
| PGP | Email encryption, file encryption |
| WTLS | Wireless TLS (legacy WAP) |

### Certificate Modules

| Module | Description |
|--------|-------------|
| `net_rim_bb_ldap_browser_x509` | X.509 certificate browser |
| `net_rim_bb_ldap_browser_pgp` | PGP key browser |
| `net_rim_bb_smime_lib` | S/MIME library |
| `net_rim_bb_pgp_lib` | PGP library |

## Secure Communication

### Email Encryption

| Protocol | Module | Description |
|----------|--------|-------------|
| S/MIME | `net_rim_bb_smime_lib` | Secure/Multipurpose Internet Mail Extensions |
| PGP | `net_rim_bb_pgp_lib` | Pretty Good Privacy |
| Secure Email | `net_rim_secureemail` | Secure email framework |

S/MIME capabilities:
- Message signing (CMS signatures)
- Message encryption (AES, 3DES)
- Certificate-based authentication
- Receipt requested

### Transport Layer Security

| Protocol | Module | Description |
|----------|--------|-------------|
| SSL 3.0 | `net_rim_cldc_io_ssl` | Secure Sockets Layer |
| TLS 1.0/1.1 | `net_rim_cldc_io_tls` | Transport Layer Security |
| HTTPS | `net_rim_cldc_io_https` | HTTP over TLS |
| WTLS | `net_rim_wap` | Wireless TLS (WAP) |

### VPN Support

| Module | Description |
|--------|-------------|
| `net_rim_cldc_impl_vpn` | VPN implementation |
| `net_rim_vpn_options` | VPN configuration |
| `net_rim_cldc_vpn_diagnostics` | VPN diagnostics |

Supported VPN protocols:
- IPSec (IKEv1/IKEv2)
- PPTP (legacy)
- L2TP/IPSec

## Smart Card Support

BlackBerry OS 7 includes comprehensive smart card integration:

| Module | Description |
|--------|-------------|
| `net_rim_smartcard` | Core smart card API |
| `net_rim_smartcard_datakey` | Datakey smart card |
| `net_rim_smartcard_gsacac` | GSA CAC (Common Access Card) |
| `net_rim_smartcard_piv` | PIV (Personal Identity Verification) |
| `net_rim_smartcard_piv_lib` | PIV library |
| `net_rim_satsa` / `net_rim_satsa_acf` | SATSA (Security and Trust Services API) |
| `net_rim_gemalto_acf` | Gemalto smart card |
| `net_rim_cldc_impl_softtoken` | Software token |
| `net_rim_softtokens_options` | Soft token configuration |
| `SecurIDLib` / `net_rim_rimsecuridlib` | RSA SecurID support |

### Smart Card Use Cases

1. **Two-factor authentication** — CAC/PIV for enterprise login
2. **Digital signatures** — Sign emails and documents
3. **Secure login** — VPN, web portals
4. **NFC payments** — Via TSM (Trusted Service Manager)

## Enterprise Management

### IT Policy System

| Module | Description |
|--------|-------------|
| `net_rim_bb_enterpriseconfig` | Enterprise configuration |
| `net_rim_bb_itpolicyviewer` | IT Policy viewer |
| `net_rim_config_channel_impl` | Configuration channel |
| `net_rim_sync_daemon` | Sync daemon (BES communication) |

### IT Policy Categories

| Category | Examples |
|----------|----------|
| Password | Min length, complexity, timeout, history |
| Encryption | Device encryption, media card encryption |
| Applications | Allowed/blocked apps, permissions |
| Network | WiFi, Bluetooth, NFC restrictions |
| Browser | Proxy, allowed sites, JavaScript |
| Email | S/MIME requirements, attachment restrictions |
| Security | Camera disable, USB mass storage, diagnostics |

### BES Integration

| Module | Description |
|--------|-------------|
| `net_rim_bb_activation` (2 segments) | Device activation |
| `net_rim_bb_otasl_app` | Over-the-air service loading |
| `net_rim_bb_otaupgrade` | OTA software upgrades |
| `net_rim_bis_lib` / `net_rim_bis_client` | BlackBerry Internet Service |

BES security features:
- Remote wipe
- Password policy enforcement
- Application control
- Wi-Fi/Bluetooth restrictions
- Calendar/contacts synchronization
- Secure content transfer

### Device Security Features

| Feature | Description |
|---------|-------------|
| Device encryption | AES-256 full-device encryption |
| Media card encryption | Encrypt removable storage |
| Password protection | Configurable complexity requirements |
| Auto-lock | Timeout-based screen lock |
| Remote wipe | BES-initiated data erasure |
| Security diagnostics | Security posture monitoring |

## Security Modules Reference

### Core Security

| Module | Description |
|--------|-------------|
| `net_rim_crypto` | Core cryptographic library |
| `net_rim_bb_crypto_api` | BlackBerry Crypto API |
| `net_rim_bb_ams_enforcement_impl` | AMS enforcement |
| `net_rim_bb_ams_transport_impl` | AMS transport |
| `net_rim_bb_application_permissions_proxy` | Permissions proxy |
| `net_rim_bb_trust_application_manager` | Trust management |
| `net_rim_bb_securitymonitor` | Security monitoring |

### Network Security

| Module | Description |
|--------|-------------|
| `net_rim_cldc_io_ssl` | SSL implementation |
| `net_rim_cldc_io_tls` | TLS implementation |
| `net_rim_cldc_impl_vpn` | VPN implementation |
| `net_rim_bb_smime_lib` | S/MIME library |
| `net_rim_bb_pgp_lib` | PGP library |
| `net_rim_secureemail` | Secure email framework |

### Enterprise Security

| Module | Description |
|--------|-------------|
| `net_rim_bb_enterpriseconfig` | Enterprise configuration |
| `net_rim_bb_itpolicyviewer` | IT Policy viewer |
| `net_rim_bb_password_wizard` | Password policy |
| `net_rim_bb_enterprise_wipe` | Enterprise wipe |
| `net_rim_bb_remotewipe` | Remote wipe |

## Security Comparison

| Feature | BlackBerry OS 7 | iOS 5 (2011) | Android 4.0 (2011) |
|---------|-----------------|--------------|---------------------|
| Device encryption | AES-256 (hardware) | AES-128 (hardware) | None (until 4.2) |
| App sandboxing | Capability-based | POSIX sandbox | Linux UID sandbox |
| Code signing | Required | Required | Optional |
| IT policy | Full control | Limited (MDM) | None (native) |
| Remote wipe | Full + selective | Full | Full |
| VPN | IPSec, PPTP, L2TP | IPSec, IKEv2 | IPSec, PPTP |
| Smart card | CAC/PIV, PKCS#11 | None | None |
| Secure boot | Yes | Yes | No (until 4.4) |
| Two-factor | RSA SecurID, CAC | None | None |

## Historical Significance

BlackBerry's security architecture was pioneering:

1. **Push email with NOC** — All email routed through RIM's Network Operations Center with end-to-end encryption
2. **Enterprise-grade IT policies** — Granular device control unprecedented in mobile
3. **Smart card integration** — First mainstream smartphone with CAC/PIV support
4. **Hardware encryption** — Dedicated crypto processor on later devices
5. **Code signing ecosystem** — Controlled app distribution before app stores existed

## Limitations

1. **Closed ecosystem** — Limited third-party security auditing
2. **BlackBerry Infrastructure dependency** — BES/NOC required for full functionality
3. **Legacy crypto** — Some algorithms (DES, MD5, SHA-1) considered weak
4. **Limited transparency** — Proprietary protocols difficult to verify
5. **End-of-life** — No security updates since 2013

---

*Security analysis based on BlackBerry Bold 9900 Simulator (SimPackage-7.1.0.318) module analysis.*
