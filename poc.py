#!/usr/bin/env python3

import base64
import json
import re
import time
import requests
from urllib.parse import urlencode

IP = input("Input the IP of the router: ")

BASE = "http://" + IP

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE + "/login.htm",
})

# Get the unauthenticated login page and extract its token.
r = session.get(BASE + "/login.htm", timeout=10)
r.raise_for_status()

m = re.search(r'<img[^>]+src=["\'](data:[^"\']+)["\']', r.text, re.I)

if not m:
    raise SystemExit("ERROR: Could not find router token.")

data_uri = m.group(1)

# Matches the router's ArcBase._t():
# strip 78 characters, then Base64-decode.
token = base64.b64decode(data_uri[78:]).decode("utf-8")

# Request only topology_info.
params = {
    "_tn": token,
    "_t": int(time.time() * 1000),
    "_": int(time.time() * 1000),
}

url = f"{BASE}/cgi/cgi_topology_info.js?{urlencode(params)}"

print("Downloading topology_info...")

r = session.get(url, timeout=10)

if not r.ok:
    raise SystemExit(f"ERROR: HTTP {r.status_code}")

data = r.text

print(f"Received {len(r.content)} bytes")

# Extract station_info.
marker = "station_info="
positions = [m.start() for m in re.finditer(re.escape(marker), data)]

if not positions:
    raise SystemExit("ERROR: station_info was not found.")

start = positions[-1] + len(marker)
end = data.find(";", start)

if end == -1:
    raise SystemExit("ERROR: Could not find end of station_info.")

obj = data[start:end].strip()

# Router escapes colons inside its generated JSON.
obj = obj.replace(r"\:", ":")

try:
    stations = json.loads(obj)["stations"]
except json.JSONDecodeError as e:
    raise SystemExit(f"ERROR: Could not parse station_info: {e}")

online = [s for s in stations if s.get("online") == "1"]
offline = [s for s in stations if s.get("online") != "1"]

print()
print("=" * 100)
print(f"Total records    : {len(stations)}")
print(f"Currently online : {len(online)}")
print(f"Offline/history  : {len(offline)}")
print("=" * 100)
print()

for i, s in enumerate(stations, 1):
    name = (
        s.get("alias_name")
        or s.get("station_name")
        or "(unnamed)"
    )

    ip = s.get("station_ip") or "-"
    mac = (s.get("station_mac") or "-").replace(r"\:", ":")
    connection = s.get("connect_type") or "-"
    status = "ONLINE" if s.get("online") == "1" else "OFFLINE"

    print(
        f"{i:3} | "
        f"{status:7} | "
        f"{name:<30} | "
        f"{ip:<15} | "
        f"{connection:<7} | "
        f"{mac}"
    )
