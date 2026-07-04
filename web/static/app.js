let historyChart = null;

async function fetchLatest() {
  try {
    const res = await fetch("/api/latest");
    const json = await res.json();

    const statusText = document.getElementById("status-text");
    const lastUpdateSpan = document.getElementById("last-update-time");
    const tempSpan = document.getElementById("temp-value");
    const humSpan = document.getElementById("hum-value");

    if (json.status === "ok" && json.data) {
      statusText.textContent = "Sensor OK (live)";
      statusText.className = "ok";
      lastUpdateSpan.textContent = json.data.timestamp_iso;
      tempSpan.textContent = json.data.temperature_c;
      humSpan.textContent = json.data.humidity_percent;
    } else if (json.status === "error" && json.data) {
      statusText.textContent = "Sensor NOT OK (stale data)";
      statusText.className = "error";
      lastUpdateSpan.textContent = json.data.timestamp_iso;
      tempSpan.textContent = json.data.temperature_c;
      humSpan.textContent = json.data.humidity_percent;
    } else {
      statusText.textContent = "No data available";
      statusText.className = "error";
    }
  } catch (err) {
    console.error("Error fetching latest:", err);
    const statusText = document.getElementById("status-text");
    statusText.textContent = "Network error";
    statusText.className = "error";
  }
}

async function fetchHistory() {
  try {
    const res = await fetch("/api/history");
    const json = await res.json();
    const rows = json.data || [];

    // Update table
    const tbody = document.querySelector("#history-table tbody");
    tbody.innerHTML = "";

    rows.forEach((row) => {
      const tr = document.createElement("tr");
      const tdTime = document.createElement("td");
      const tdTemp = document.createElement("td");
      const tdHum = document.createElement("td");

      tdTime.textContent = row.timestamp_iso;
      tdTemp.textContent = row.temperature_c;
      tdHum.textContent = row.humidity_percent;

      tr.appendChild(tdTime);
      tr.appendChild(tdTemp);
      tr.appendChild(tdHum);
      tbody.appendChild(tr);
    });

    // Build data arrays for chart
    const labels = rows.map((r) => r.timestamp_iso.slice(11)); // time only
    const temps = rows.map((r) => parseFloat(r.temperature_c));
    const hums = rows.map((r) => parseFloat(r.humidity_percent));

    const canvas = document.getElementById("history-chart");
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext("2d");

    if (!historyChart) {
      historyChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Temperature (°C)",
              data: temps,
              borderColor: "rgba(220, 53, 69, 0.9)",
              backgroundColor: "rgba(220, 53, 69, 0.1)",
              tension: 0.2,
              yAxisID: "y1",
            },
            {
              label: "Humidity (%)",
              data: hums,
              borderColor: "rgba(23, 162, 184, 0.9)",
              backgroundColor: "rgba(23, 162, 184, 0.1)",
              tension: 0.2,
              yAxisID: "y2",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y1: { type: "linear", position: "left" },
            y2: { type: "linear", position: "right" },
          },
        },
      });
    } else {
      historyChart.data.labels = labels;
      historyChart.data.datasets[0].data = temps;
      historyChart.data.datasets[1].data = hums;
      historyChart.update();
    }
  } catch (err) {
    console.error("Error fetching history:", err);
  }
}

function tick() {
  fetchLatest();
  fetchHistory();
}

async function fetchLedStatus() {
  try {
    const res = await fetch("/api/led");
    const json = await res.json();
    const span = document.getElementById("led-status");
    const btn = document.getElementById("led-toggle-btn");
    span.textContent = json.state ? "ON" : "OFF";
    btn.textContent = json.state ? "Turn OFF" : "Turn ON";
  } catch (err) {
    console.error("Error fetching LED status:", err);
  }
}

async function toggleLed() {
  try {
    const btn = document.getElementById("led-toggle-btn");
    const span = document.getElementById("led-status");
    const currentlyOn = span.textContent === "ON";

    const res = await fetch("/api/led", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ on: !currentlyOn }),
    });
    const json = await res.json();
    span.textContent = json.state ? "ON" : "OFF";
    btn.textContent = json.state ? "Turn OFF" : "Turn ON";
  } catch (err) {
    console.error("Error toggling LED:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  tick();
  setInterval(tick, 5000);
  fetchLedStatus();
  setInterval(fetchLedStatus, 5000);

  const btn = document.getElementById("led-toggle-btn");
  btn.addEventListener("click", toggleLed);
});
