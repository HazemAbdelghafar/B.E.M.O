async function fetchDeviceData() {
    try {
        const res = await fetch("/api/connected-devices/json");
        const data = await res.json();
        updatePage(data);
    } catch (err) {
        console.error("Failed to fetch device data:", err);
        document.getElementById("server-status").innerHTML = `
      <p class="status-disconnected">🔴 Server status: Disconnected</p>
    `;
    }
}

function formatDuration(seconds) {
    const hrs = Math.floor(seconds / 3600)
        .toString()
        .padStart(2, "0");
    const mins = Math.floor((seconds % 3600) / 60)
        .toString()
        .padStart(2, "0");
    const secs = (seconds % 60).toString().padStart(2, "0");
    return `${hrs}:${mins}:${secs}`;
}

function updatePage(data) {
    const { server, robots, users } = data;

    // --- Server Status ---
    let serverHtml = `<h2>🖥️ Server</h2>`;
    if (server) {
        serverHtml += `
      <p>Status: <span class="status-connected">🟢 Connected</span></p>
      <p>IP Address: ${server.ip}</p>
      <p>Uptime: ⏱️ ${formatDuration(server.duration)}</p>
      <p>Last Seen: ${new Date(server.last_seen).toLocaleString()}</p>
    `;
    } else {
        serverHtml += `<p>Status: <span class="status-disconnected">🔴 Disconnected</span></p>`;
    }
    document.getElementById("server-status").innerHTML = serverHtml;

    // --- Robots Table ---
    let robotsHtml = `<h2>🤖 Robots (${robots.length})</h2>`;
    if (robots.length === 0) {
        robotsHtml += "<p>No robots connected.</p>";
    } else {
        robotsHtml += `
      <table class="device-table">
        <thead>
          <tr><th>ID</th><th>IP</th><th>Uptime</th><th>Last Seen</th><th>Status</th></tr>
        </thead>
        <tbody>
          ${robots
              .map(
                  (r) => `
              <tr>
                <td>${r.id}</td>
                <td>${r.ip}</td>
                <td>${formatDuration(r.duration)}</td>
                <td>${new Date(r.last_seen).toLocaleString()}</td>
                <td class="${
                    r.status === "connected"
                        ? "status-connected"
                        : "status-disconnected"
                }">
                  ${r.status === "connected" ? "🟢" : "🔴"}
                </td>
              </tr>
            `
              )
              .join("")}
        </tbody>
      </table>
    `;
    }
    document.getElementById("robots").innerHTML = robotsHtml;

    // --- Users Table ---
    let usersHtml = `<h2>👤 Users (${users.length})</h2>`;
    if (users.length === 0) {
        usersHtml += "<p>No users connected.</p>";
    } else {
        usersHtml += `
      <table class="device-table">
        <thead>
          <tr><th>ID</th><th>IP</th><th>Uptime</th><th>Last Seen</th><th>Status</th></tr>
        </thead>
        <tbody>
          ${users
              .map(
                  (u) => `
              <tr>
                <td>${u.id}</td>
                <td>${u.ip}</td>
                <td>${formatDuration(u.duration)}</td>
                <td>${new Date(u.last_seen).toLocaleString()}</td>
                <td class="${
                    u.status === "connected"
                        ? "status-connected"
                        : "status-disconnected"
                }">
                  ${u.status === "connected" ? "🟢" : "🔴"}
                </td>
              </tr>
            `
              )
              .join("")}
        </tbody>
      </table>
    `;
    }
    document.getElementById("users").innerHTML = usersHtml;
}

// Initial fetch and polling every 10 seconds
fetchDeviceData();
setInterval(fetchDeviceData, 10000);
