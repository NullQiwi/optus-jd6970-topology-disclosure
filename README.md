# Optus JD6970 — Unauthenticated Topology Information Disclosure

Proof of concept for an information disclosure issue in the Optus JD6970 router.

## Summary

The router's web interface exposes `cgi/cgi_topology_info.js` without requiring an authenticated administrator session.

An unauthenticated client can:

1. Request `/login.htm`
2. Extract the token embedded in the page
3. Reproduce the token decoding used by the router's JavaScript
4. Request `cgi/cgi_topology_info.js`
5. Parse the returned `station_info` data

The response contains information about devices known to the router, including both currently connected devices and historical/offline devices.

Observed fields include:

* MAC address
* Device name / alias
* Private LAN IP address
* Connection type
* Link rate
* Signal strength
* Channel
* Online status
* Connection timestamps
* IPv6 address

In testing, the router returned **256 station records**, including **34 online** and **222 offline/history** records.

## Affected device

* **Device:** Optus JD6970
* **Firmware:** `AHGW.0.015.8c`
* **Hardware revision:** `01`

## Proof of concept

`poc.py` requests the unauthenticated login page, extracts the embedded token, and uses it to retrieve the topology information.

```bash
python3 poc.py
```

The script will ask for the router's IP address.

Only run this against equipment you own or have explicit permission to test.

## Disclosure

This repository documents research into the router's web interface and is intended for defensive security research and reproducibility.

No real device data is included in this repository.

## Researcher

**NullQiwi**

Vulnerability researcher interested in embedded equipment, routers, and network-connected devices.
