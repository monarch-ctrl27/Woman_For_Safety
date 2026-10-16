# Woman For Safety 🛡️ Operations, Moderation & Simulation Platform
> **Bloom Innovators — BizTech Nexus Innovation Hackathon 2026**
> *Crowd-Sourced Safety Map & Hands-Free Panic Response Platform (SRS v1.2 Compliant)*

Woman For Safety is a comprehensive women's safety ecosystem comprising an **Android-first Flutter mobile application** (under active development for end-users) paired with this **Django Operations, Moderation & Simulation Web Console**.

This platform provides community safety moderators, campus security directors, institutional partners, and system administrators with:
1. **Live Corridor Hazard Intelligence:** Real-time visibility into crowd-sourced danger zones across all major Bloemfontein safety corridors.
2. **Community Moderation Queue & Audit Trail:** Formal review workflows (Approve, Disagree/Remove, Adjust Radius, Flag) with immutable audit logs.
3. **Emergency Pipeline Simulation Center:** Testing and demonstration of zero-unlock mobile triggers (Triple-press, Voice 'Help', Fall detection, Geofence breach) and the 60-second stand-down window.
4. **Next-of-Kin Dual-Channel Escalation:** Real-time dispatch audit logs ensuring alerts reach verified Next-of-Kin contacts (Voice/SMS + WhatsApp Backup) with GPS coordinates and nearest safe havens, strictly adhering to SRS v1.2 safety constraints (no automated police dispatch).
5. **Institutional Partner Oversight:** Enterprise licensing management for university campuses (UFS, CUT), accredited student residences, and Business Improvement Districts (BIDs).

---

## 🏛️ Bloemfontein Focus Corridors
The platform comes pre-seeded with rich, realistic telemetry across Bloemfontein's primary student and transit corridors:
* **Westdene Corridor:** Student housing belt, taxi alleys, and commercial walkways.
* **Willows / CUT Student Belt:** Central University of Technology perimeter, Park Road underpass, and transit intersections.
* **Universitas / UFS Campus Fringe:** University of the Free State residence gates, Kellner Street, and hospital corridors.
* **Brandwag Retail Corridor:** Retail centres, ATM clusters, and pedestrian pass-throughs.
* **Bloemfontein CBD / Station Fringe:** Railway footbridges, Harvey Road, and central taxi ranks.

---

## 🗺️ High-Performance Keyless Basemaps (No API Keys Required)
* **Zero API Key Requirement & No Watermarks:** The platform uses the global **Humanitarian OpenStreetMap (HOT)** layer (`https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png`) as the primary basemap. It requires zero API keys, never displays "API Key Required" watermarks, and offers high-visibility street hierarchy specifically designed for crisis response and safety navigation.
* **In-Map Basemap Switcher:** Administrators and evaluators can switch basemap layers on the fly via the top-right layer control:
  * 🛡️ **Humanitarian Safety Map (Default):** High contrast, optimized for pedestrian danger buffers.
  * 🗺️ **Esri World Street Map:** Clean cartographic styling powered by Esri.
  * 🌐 **Standard Street Map:** High-speed OpenStreetMap France mirror.
  * 🚶 **CyclOSM Walk & Transit Map:** Highlights pedestrian walkways, lit avenues, and transit stops.
* **1-Tap Corridor Filters:** Instant smooth panning and filtering across all 5 Bloemfontein safety corridors.
* **Automated Detour Routing:** Evaluates walking paths against active danger radii and plots green safe bypass detours.
* **Safe Sanctuary Shortcuts:** 1-tap automated routing to the nearest SAPS police station, 24h trauma center (Pelonomi / Universitas Academic Hospital), or safe shelter.

---

## ⚡ Emergency Pipeline Simulation Center (`/emergency/simulation/`)
Evaluators and administrators can simulate zero-unlock mobile triggers directly from the web console:
1. **🔘 Triple Power Key Press (SRS §3.5 FR-PANIC-1):** Simulates 3 rapid hardware key presses firing an immediate Next-of-Kin dispatch without screen unlock.
2. **🎙️ Hands-Free Voice Distress ("Help!") (SRS §2.8):** Simulates spoken distress keywords in South African English (`en-ZA`), initiating the 60-second stand-down countdown.
3. **📱 Automatic Accelerometer Fall Detection (SRS §2.8):** Simulates dual-phase IMU detection (free-fall followed by severe impact) triggering an audible alert tone and stand-down window.
4. **📍 Geofence Danger Zone Breach (SRS §3.4 FR-GEO):** Simulates GPS coordinates entering within 600m of any selected corridor hotspot, triggering haptic vibration alerts and stand-down countdown.
5. **⏳ Stand-Down & False Alarm PIN Disarm (SRS §12.1):** Simulates entering the 4-digit Safe PIN (`2468`) to stand down false alarms before automatic escalation.

---

## 🛡️ SRS v1.2 Mandatory Safety Compliance Notice
> **CRITICAL ARCHITECTURAL GUARANTEE (SRS v1.2 §2.8):**
> Woman For Safety emergency escalations route **exclusively to the user's verified Next-of-Kin contacts**. 
> - **No build claims or executes automated police dispatch.**
> - Alerts provide the recipient with the user's live GPS coordinates, battery level, trigger source, and the contact number of the nearest safe sanctuary (e.g. SAPS Bloemfontein Central or Pelonomi GBV Care Centre), empowering next-of-kin to coordinate assistance safely.
> - **Dual-Channel Delivery:** Priority Voice Call / SMS paired with immediate WhatsApp message backup (FR-PANIC-6).
> - **Honest Failure Reporting:** Immediate warning surfaced if zero Next-of-Kin contacts are configured (FR-PANIC-9).

---

## 🚀 Quick Start Guide

### 1. Launch Server
Run `main.py` directly using PyCharm's Play button, or run from terminal:

```powershell
.\.venv\Scripts\python.exe main.py
```
*(Or via `manage.py`: `.\.venv\Scripts\python.exe Safety_For_Woman\manage.py runserver 127.0.0.1:8000`)*

Open your browser to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

### 2. Pre-Seeded Demonstration Accounts (All Passwords Included)

| Role | Username | Password | Purpose & Capabilities |
|---|---|---|---|
| **System Administrator** | `admin` | `Woman For SafetyAdmin2026!` | Full Django admin access, platform configuration, and telemetry oversight |
| **Community Safety Moderator** | `mod_thandi` | `Woman For SafetyMod2026!` | Review flagged danger pins, approve/remove hotspots, view audit logs |
| **Community Safety Moderator** | `mod_lerato` | `Woman For SafetyMod2026!` | Secondary corridor review, dispute resolution, radius modification |
| **Primary End-User** | `sarah` | `Woman For SafetyPassword2026!` | Pre-configured with Next-of-Kin contacts, PIN `2468`, simulation profile |
| **Student User** | `zanele` | `Woman For SafetyUser2026!` | Student commuter profile with Willows / CUT route history |
| **Campus Safety Officer** | `ufs_safety` | `Woman For SafetyUFS2026!` | UFS Institutional Partner account with campus corridor perimeter telemetry |

---

### 3. Re-Seeding Fresh Demonstration Data
To reset the database with fresh mock hotspots, facilities, simulations, and moderation audit logs at any time:

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe Safety_For_Woman\manage.py flush --no-input
.\.venv\Scripts\python.exe Safety_For_Woman\manage.py seed_safety_data
```

---

## 🧪 Automated Test Suite (7/7 Passing)
Run the full automated test suite verifying geofence proximity calculations, safe rerouting detour generation, emergency dispatch to Next-of-Kin, and Safe PIN cancellation:

```powershell
.\.venv\Scripts\python.exe Safety_For_Woman\manage.py test core
```
```
----------------------------------------------------------------------
Ran 7 tests in ~12s

OK
```

---

## 📁 Repository Structure

```
Woman_For_Safety/
├── main.py                                      # One-click PyCharm application launcher
├── README.md                                    # Hackathon submission documentation
├── Safety_For_Woman/
│   ├── manage.py                                # Django CLI management utility
│   ├── safeher/                                 # Project configuration, settings, root URLs
│   ├── core/                                    # Ops dashboard, site middleware, seeding commands, tests
│   ├── accounts/                                # Roles (Admin/Mod/Inst/User), Safe PIN, NOK contacts
│   ├── hotspots/                                # Corridors, live map, geofence check, safe detour API
│   ├── facilities/                              # SAPS stations, 24h trauma hospitals, safe shelters locator
│   ├── emergency/                               # Simulation center, stand-down timer, NOK dispatch service
│   ├── moderation/                              # Flagged pin queue, review workflow, audit log
│   ├── templates/                               # Responsive operations console templates
│   │   ├── base.html                            # Master layout with Preview Mode watermark banner
│   │   ├── core/dashboard.html                  # Operations Cockpit with real-time telemetry
│   │   ├── emergency/simulation.html            # Interactive 4-trigger Simulation Center
│   │   ├── hotspots/map.html                    # CartoDB Voyager map with corridor filter buttons
│   │   └── moderation/                          # Dashboard, review, and immutable audit log screens
│   └── static/                                  # Stylesheet, CartoDB safemap.js, sensor triggers
```
#   W o m a n _ F o r _ S a f e t y 
 
 