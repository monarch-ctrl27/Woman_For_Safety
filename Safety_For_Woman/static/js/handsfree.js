/**
 * SafeHer Hands-Free Safety Suite
 * Implements:
 * 1. Triple-Press Key / Power Button Panic Trigger
 * 2. Continuous Voice Recognition ("Help!" / "Emergency")
 * 3. Automatic Accelerometer Fall-Detection
 * 4. Geofence Proximity Monitor with Device Vibration & Stand-Down
 */

const SafeHer = {
  activeCoords: { lat: -29.1181, lon: 26.2249 }, // Default Bloemfontein Central
  batteryLevel: null,
  voiceActive: false,
  recognition: null,
  keyPressTimes: [],
  fallDetectionArmed: false,
  lastAcceleration: 0,
  freeFallDetected: false,
  geofenceInterval: null,

  init() {
    this.initGeolocation();
    this.initBattery();
    this.initTriplePress();
    this.initVoiceRecognition();
    this.initFallDetection();
    this.startGeofenceMonitor();
  },

  getCsrfToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name + "=")) {
        return decodeURIComponent(c.substring(name.length + 1));
      }
    }
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute("content") : "";
  },

  initGeolocation() {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.activeCoords.lat = pos.coords.latitude;
          this.activeCoords.lon = pos.coords.longitude;
          const display = document.getElementById("user-coords-display");
          if (display) {
            display.innerText = `${this.activeCoords.lat.toFixed(4)}, ${this.activeCoords.lon.toFixed(4)}`;
          }
        },
        (err) => console.log("Geolocation notice:", err.message),
        { enableHighAccuracy: true, timeout: 10000 }
      );

      navigator.geolocation.watchPosition((pos) => {
        this.activeCoords.lat = pos.coords.latitude;
        this.activeCoords.lon = pos.coords.longitude;
      });
    }
  },

  initBattery() {
    if ("getBattery" in navigator) {
      navigator.getBattery().then((battery) => {
        this.batteryLevel = Math.round(battery.level * 100);
        battery.addEventListener("levelchange", () => {
          this.batteryLevel = Math.round(battery.level * 100);
        });
      });
    }
  },

  /* -------------------------------------------------------------
     TRIGGER 1: TRIPLE-PRESS POWER / KEY EVENT
  ------------------------------------------------------------- */
  initTriplePress() {
    window.addEventListener("keydown", (e) => {
      // Ignore typing inside input or textarea
      if (["INPUT", "TEXTAREA"].includes(e.target.tagName)) return;

      const now = Date.now();
      // Keep only presses within the last 1.2 seconds
      this.keyPressTimes = this.keyPressTimes.filter((t) => now - t < 1200);
      this.keyPressTimes.push(now);

      if (this.keyPressTimes.length >= 3) {
        console.warn("SafeHer: Triple-press emergency trigger fired!");
        this.keyPressTimes = [];
        this.firePanic("TRIPLE_PRESS", true);
      }
    });
  },

  simulateTriplePress() {
    this.firePanic("TRIPLE_PRESS", true);
  },

  /* -------------------------------------------------------------
     TRIGGER 2: HANDS-FREE VOICE RECOGNITION ("HELP!")
  ------------------------------------------------------------- */
  initVoiceRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const badge = document.getElementById("voice-status-badge");

    if (!SpeechRec) {
      if (badge) {
        badge.innerText = "Browser Unsupported";
        badge.className = "badge badge-warning";
      }
      return;
    }

    try {
      this.recognition = new SpeechRec();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-ZA";

      this.recognition.onstart = () => {
        this.voiceActive = true;
        if (badge) {
          badge.innerText = "Listening for 'Help'...";
          badge.className = "badge badge-success";
        }
      };

      this.recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const phrase = event.results[i][0].transcript.toLowerCase();
          console.log("SafeHer Voice heard:", phrase);
          if (
            phrase.includes("help") ||
            phrase.includes("safeher") ||
            phrase.includes("emergency") ||
            phrase.includes("police")
          ) {
            console.warn("SafeHer: Voice distress keyword detected!");
            this.playAlertSound();
            this.firePanic("VOICE", false);
            break;
          }
        }
      };

      this.recognition.onerror = (e) => {
        console.log("Voice recognition notice:", e.error);
      };

      this.recognition.onend = () => {
        // Automatically restart if voice protection remains armed
        if (this.voiceActive) {
          setTimeout(() => {
            try { this.recognition.start(); } catch (err) {}
          }, 1000);
        }
      };

      // Start recognition on initial user interaction
      document.addEventListener("click", () => {
        if (!this.voiceActive && this.recognition) {
          try { this.recognition.start(); } catch (err) {}
        }
      }, { once: true });

    } catch (e) {
      console.log("Speech initialization exception:", e);
    }
  },

  simulateVoiceTrigger() {
    this.playAlertSound();
    this.firePanic("VOICE", false);
  },

  /* -------------------------------------------------------------
     TRIGGER 3: AUTOMATIC ACCELEROMETER FALL DETECTION
  ------------------------------------------------------------- */
  initFallDetection() {
    const badge = document.getElementById("fall-status-badge");

    if (window.DeviceMotionEvent) {
      this.fallDetectionArmed = true;
      if (badge) {
        badge.innerText = "Sensors Armed";
        badge.className = "badge badge-success";
      }

      window.addEventListener("devicemotion", (event) => {
        const acc = event.accelerationIncludingGravity;
        if (!acc) return;

        const magnitude = Math.sqrt((acc.x || 0)**2 + (acc.y || 0)**2 + (acc.z || 0)**2);

        // Phase 1: Free fall condition (< 3.5 m/s^2)
        if (magnitude < 3.5) {
          this.freeFallDetected = true;
          setTimeout(() => { this.freeFallDetected = false; }, 800);
        }

        // Phase 2: High impact spike (> 24.0 m/s^2) following free fall
        if (this.freeFallDetected && magnitude > 24.0) {
          this.freeFallDetected = false;
          console.warn("SafeHer: Sudden fall impact detected by accelerometer!");
          this.firePanic("FALL_DETECTION", false);
        }
      });
    } else {
      if (badge) {
        badge.innerText = "Simulation Ready";
        badge.className = "badge badge-info";
      }
    }
  },

  simulateFall() {
    this.firePanic("FALL_DETECTION", false);
  },

  /* -------------------------------------------------------------
     TRIGGER 4: GEOFENCE PROXIMITY & VIBRATION (60s STAND-DOWN)
  ------------------------------------------------------------- */
  startGeofenceMonitor() {
    // Check geofence proximity every 15 seconds
    this.checkGeofence();
    this.geofenceInterval = setInterval(() => {
      this.checkGeofence();
    }, 15000);
  },

  async checkGeofence() {
    try {
      const url = `/map/api/check-geofence/?lat=${this.activeCoords.lat}&lon=${this.activeCoords.lon}`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.status === "warning" && data.approaching_danger) {
        console.warn(`Approaching danger hotspot: ${data.hotspot.title} (${data.distance_meters}m away)`);
        
        // Vibrate phone: 500ms on, 200ms off, 500ms on, 200ms off, 500ms on
        if ("vibrate" in navigator) {
          navigator.vibrate([500, 200, 500, 200, 500]);
        }
        this.playAlertSound();

        // Show proximity banner
        const banner = document.getElementById("proximity-alert-banner");
        if (banner) {
          banner.style.display = "block";
          document.getElementById("proximity-hotspot-name").innerText = data.hotspot.title;
          document.getElementById("proximity-distance-val").innerText = `${data.distance_meters} meters`;
        }

        // Trigger stand-down if approaching critical danger
        if (data.hotspot.severity === "CRITICAL" && !window.standDownInitiated) {
          window.standDownInitiated = true;
          this.firePanic("GEOFENCE_APPROACH", false, data.hotspot.id);
        }
      }
    } catch (e) {
      // Network or geofence error silently ignored
    }
  },

  /* -------------------------------------------------------------
     CORE PANIC DISPATCHER
  ------------------------------------------------------------- */
  async firePanic(triggerSource, immediate = false, hotspotId = null) {
    if ("vibrate" in navigator) {
      navigator.vibrate([400, 150, 400, 150, 800]);
    }

    try {
      const payload = {
        trigger_source: triggerSource,
        immediate: immediate,
        latitude: this.activeCoords.lat,
        longitude: this.activeCoords.lon,
        battery_level: this.batteryLevel,
        hotspot_id: hotspotId,
      };

      const res = await fetch("/emergency/trigger/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (result.redirect_url) {
        window.location.href = result.redirect_url;
      } else if (result.alert_id) {
        window.location.href = `/emergency/stand-down/${result.alert_id}/`;
      }
    } catch (err) {
      // Form POST fallback
      const form = document.createElement("form");
      form.method = "POST";
      form.action = "/emergency/trigger/";

      const csrfInput = document.createElement("input");
      csrfInput.type = "hidden";
      csrfInput.name = "csrfmiddlewaretoken";
      csrfInput.value = this.getCsrfToken();
      form.appendChild(csrfInput);

      const srcInput = document.createElement("input");
      srcInput.type = "hidden";
      srcInput.name = "trigger_source";
      srcInput.value = triggerSource;
      form.appendChild(srcInput);

      document.body.appendChild(form);
      form.submit();
    }
  },

  playAlertSound() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "triangle";
      osc.frequency.setValueAtTime(880, ctx.currentTime); // High A
      osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.4);

      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } catch (e) {}
  },
};

document.addEventListener("DOMContentLoaded", () => {
  SafeHer.init();
});
