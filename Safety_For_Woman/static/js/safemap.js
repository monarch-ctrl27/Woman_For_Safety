/**
 * SafeHer Regional Intelligence & Moderation Map Engine
 * Uses CartoDB Voyager tiles (unrestricted, high-performance, non-blocking)
 * Overlays:
 * - Bloemfontein Crime Corridors (Westdene, Willows, Universitas, Brandwag, CBD)
 * - Crowd-Sourced Danger Hotspots & Moderation Flags
 * - Safe Sanctuaries (SAPS Police, 24h Hospitals, Women's Shelters)
 * - Safe Route Detour Inspector
 */

const SafeMap = {
  map: null,
  userMarker: null,
  centerCoords: [-29.1181, 26.2249], // Bloemfontein Central
  hotspotsLayer: null,
  facilitiesLayer: null,
  routeLayer: null,
  directRouteLayer: null,
  activeFilter: "ALL",

  init(containerId = "safemap") {
    const el = document.getElementById(containerId);
    if (!el) return;

    this.map = L.map(containerId).setView(this.centerCoords, 14);

    // Keyless, high-reliability Basemap Layers (No API key required, no watermarks, no blocking)
    const hotLayer = L.tileLayer("https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", {
      maxZoom: 19,
      subdomains: "abc",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a> | SafeHer Ops',
    });

    const esriLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
      maxZoom: 19,
      attribution: 'Tiles &copy; <a href="https://www.esri.com/">Esri</a> &mdash; World Street Map | SafeHer Ops',
    });

    const osmFrLayer = L.tileLayer("https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png", {
      maxZoom: 20,
      subdomains: "abc",
      attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | SafeHer Ops',
    });

    const cyclOsmLayer = L.tileLayer("https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png", {
      maxZoom: 18,
      subdomains: "abc",
      attribution: '&copy; <a href="https://www.cyclosm.org/">CyclOSM</a> | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | SafeHer Ops',
    });

    // Default to Humanitarian Safety Layer (HOT)
    hotLayer.addTo(this.map);

    // Layer switcher for administrative operations
    const baseMaps = {
      "🛡️ Humanitarian Safety (Default)": hotLayer,
      "🗺️ Esri World Street Map": esriLayer,
      "🌐 Standard Street Map": osmFrLayer,
      "🚶 Pedestrian & Transit Map": cyclOsmLayer,
    };
    L.control.layers(baseMaps, null, { position: "topright" }).addTo(this.map);

    this.hotspotsLayer = L.layerGroup().addTo(this.map);
    this.facilitiesLayer = L.layerGroup().addTo(this.map);
    this.routeLayer = L.layerGroup().addTo(this.map);
    this.directRouteLayer = L.layerGroup().addTo(this.map);

    this.loadHotspots();
    this.loadFacilities();

    // Map click to inspect or report
    this.map.on("click", (e) => {
      this.handleMapClick(e.latlng);
    });

    const btnPolice = document.getElementById("btn-route-nearest-police");
    if (btnPolice) btnPolice.onclick = () => this.routeToNearest("POLICE");
    const btnHosp = document.getElementById("btn-route-nearest-hospital");
    if (btnHosp) btnHosp.onclick = () => this.routeToNearest("HOSPITAL");
    const btnShelter = document.getElementById("btn-route-nearest-shelter");
    if (btnShelter) btnShelter.onclick = () => this.routeToNearest("SHELTER");
  },

  async routeToNearest(facilityType) {
    try {
      const res = await fetch(`/facilities/api/nearest/?lat=${this.centerCoords[0]}&lon=${this.centerCoords[1]}`);
      const data = await res.json();
      const target = data.all_nearby.find((f) => f.type === facilityType);
      if (target) {
        this.routeToDestination(target.lat, target.lon, target.name);
      } else if (data.nearest_facility) {
        this.routeToDestination(data.nearest_facility.lat, data.nearest_facility.lon, data.nearest_facility.name);
      }
    } catch (e) {
      console.error("Nearest routing error:", e);
    }
  },

  async loadHotspots(corridor = "ALL") {
    this.activeFilter = corridor;
    try {
      const res = await fetch("/map/api/all/");
      const data = await res.json();
      this.hotspotsLayer.clearLayers();

      data.hotspots.forEach((h) => {
        if (corridor !== "ALL" && h.corridor_code !== corridor) {
          return;
        }

        // Color coding based on severity
        let color = "#e11d48";
        let fillOpacity = 0.25;
        if (h.severity === "CRITICAL") color = "#be123c";
        if (h.severity === "MEDIUM") color = "#ea580c";
        if (h.severity === "LOW") color = "#eab308";

        // Danger zone radius circle
        const circle = L.circle([h.lat, h.lon], {
          color: color,
          fillColor: color,
          fillOpacity: fillOpacity,
          radius: h.radius_meters,
          weight: 2,
        }).addTo(this.hotspotsLayer);

        // Marker icon
        const marker = L.marker([h.lat, h.lon]).addTo(this.hotspotsLayer);

        const statusBadge = h.verification_status === "flagged"
          ? `<span class="badge badge-warning">Needs Review (Flagged)</span>`
          : `<span class="badge badge-success">Verified Hazard</span>`;

        const popupContent = `
          <div style="min-width:240px; font-family:-apple-system, sans-serif;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span class="badge badge-danger">${h.severity_label}</span>
              <small style="color:#64748b; font-weight:600;">${h.corridor_label || h.category}</small>
            </div>
            <h4 style="margin:4px 0; font-size:1rem; color:#0f172a;">${h.title}</h4>
            <p style="font-size:0.85rem; color:#334155; margin:6px 0;">${h.description}</p>
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px; line-height:1.5;">
              ⚠️ Danger Radius: <b>${h.radius_meters}m</b><br>
              🕒 Highest Risk: <b>${h.risk_time}</b><br>
              Status: ${statusBadge}
            </div>
            <div style="display:flex; gap:6px;">
              <a href="/moderation/?review_id=${h.id}" class="btn btn-outline" style="font-size:0.75rem; padding:4px 8px; flex:1; text-align:center;">
                🛡️ Moderator Review
              </a>
              <button onclick="SafeMap.routeToDestination(${h.lat}, ${h.lon}, '${h.title.replace(/'/g, "\\'")}')" class="btn btn-police" style="font-size:0.75rem; padding:4px 8px; flex:1;">
                🧭 Inspect Detour
              </button>
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);
        circle.bindPopup(popupContent);
      });
    } catch (e) {
      console.error("Error loading hotspots:", e);
    }
  },

  async loadFacilities() {
    try {
      const res = await fetch(`/facilities/api/nearest/?lat=${this.centerCoords[0]}&lon=${this.centerCoords[1]}`);
      const data = await res.json();
      this.facilitiesLayer.clearLayers();

      data.all_nearby.forEach((fac) => {
        let iconSymbol = "🛡️";
        let badgeClass = "badge-police";
        if (fac.type === "HOSPITAL") { iconSymbol = "🏥"; badgeClass = "badge-hospital"; }
        if (fac.type === "CLINIC") { iconSymbol = "⚕️"; badgeClass = "badge-hospital"; }
        if (fac.type === "SHELTER") { iconSymbol = "🏡"; badgeClass = "badge-shelter"; }

        const facIcon = L.divIcon({
          className: "facility-marker",
          html: `<div style="font-size:1.4rem; text-shadow:0 2px 4px rgba(0,0,0,0.3);">${iconSymbol}</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        });

        const marker = L.marker([fac.lat, fac.lon], { icon: facIcon }).addTo(this.facilitiesLayer);

        const popup = `
          <div style="min-width:220px; font-family:-apple-system, sans-serif;">
            <span class="badge ${badgeClass}">${fac.type_label}</span>
            <h4 style="margin:5px 0 3px; font-size:1rem; color:#0f172a;">${fac.name}</h4>
            <p style="font-size:0.8rem; color:#64748b; margin-bottom:6px;">📍 ${fac.address}</p>
            <p style="font-size:0.8rem; font-weight:600; color:#059669; margin-bottom:6px;">
              📏 Distance from Central: <b>${fac.distance_km} km</b>
            </p>
            <div style="display:flex; gap:6px; margin-top:8px;">
              <a href="tel:${fac.phone}" class="btn btn-police" style="font-size:0.75rem; padding:4px 8px; flex:1; text-align:center;">
                📞 Call
              </a>
              <button onclick="SafeMap.routeToDestination(${fac.lat}, ${fac.lon}, '${fac.name.replace(/'/g, "\\'")}')" class="btn btn-success" style="font-size:0.75rem; padding:4px 8px; flex:1.2;">
                🧭 Safe Route
              </button>
            </div>
          </div>
        `;
        marker.bindPopup(popup);
      });
    } catch (e) {
      console.error("Error loading facilities:", e);
    }
  },

  filterCorridor(corridorCode) {
    this.loadHotspots(corridorCode);
    const coords = {
      WESTDENE: [-29.1120, 26.2080],
      WILLOWS: [-29.1245, 26.2115],
      UNIVERSITAS: [-29.1118, 26.1834],
      BRANDWAG: [-29.1085, 26.1950],
      CBD: [-29.1205, 26.2210],
      ALL: [-29.1181, 26.2249],
    };
    if (coords[corridorCode]) {
      this.map.flyTo(coords[corridorCode], 15);
    }
  },

  async routeToDestination(destLat, destLon, destName = "Destination") {
    try {
      const url = `/map/api/safe-route/?start_lat=${this.centerCoords[0]}&start_lon=${this.centerCoords[1]}&dest_lat=${destLat}&dest_lon=${destLon}`;
      const res = await fetch(url);
      const data = await res.json();

      this.routeLayer.clearLayers();
      this.directRouteLayer.clearLayers();

      // Plot direct danger line in red dashed
      L.polyline(data.direct_route, {
        color: "#dc2626",
        dashArray: "6, 8",
        weight: 3,
        opacity: 0.6,
      }).addTo(this.directRouteLayer);

      // Plot safe detour route in solid green
      const safePoly = L.polyline(data.route_waypoints, {
        color: "#059669",
        weight: 6,
        opacity: 0.9,
      }).addTo(this.routeLayer);

      this.map.fitBounds(safePoly.getBounds(), { padding: [50, 50] });

      const statusBox = document.getElementById("safe-route-status");
      if (statusBox) {
        statusBox.style.display = "block";
        document.getElementById("route-dest-name").innerText = destName;
        document.getElementById("route-detour-count").innerText = `${data.detours_count} Danger Zones Bypassed`;
      }
    } catch (e) {
      console.error("Routing error:", e);
    }
  },

  handleMapClick(latlng) {
    const reportBanner = document.getElementById("report-pin-banner");
    if (reportBanner) {
      reportBanner.style.display = "flex";
      document.getElementById("pin-lat-display").innerText = latlng.lat.toFixed(5);
      document.getElementById("pin-lon-display").innerText = latlng.lng.toFixed(5);
      const link = document.getElementById("pin-report-link");
      if (link) {
        link.href = `/map/report/?lat=${latlng.lat}&lon=${latlng.lng}`;
      }
    }
  },
};
