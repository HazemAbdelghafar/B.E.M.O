function formatDuration(seconds) {
    const hrs = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");
    return `${hrs}:${mins}:${secs}`;
}

async function fetchDeviceData() {
    try {
        const res = await fetch("/api/connected-devices/json");
        const data = await res.json();
        updatePage(data);
    } catch (err) {
        console.error("Failed to fetch device data:", err);
    }
}

function updatePage(data) {
    // === Server Section ===
    const serverDiv = document.getElementById("server-status");
    if (serverDiv) {
        const server = data.server;
        let html = `<h2>🖥️ Server</h2>`;

        if (server) {
            html += `
                <p>Status: <span class="status-connected">🟢 Connected</span></p>
                <p>IP Address: ${server.ip}</p>
                <p>Uptime: ⏱️ ${formatDuration(server.duration)}</p>
                <p>Last Seen: ${new Date(server.last_seen).toLocaleString()}</p>
            `;
        } else {
            html += `<p>Status: <span class="status-disconnected">🔴 Disconnected</span></p>`;
        }

        serverDiv.innerHTML = html;
    }

    // === Robots Section ===
    const robotsDiv = document.getElementById("robots");
    if (robotsDiv) {
        const robots = data.robots || [];
        let html = `<h2>🤖 Robots (${robots.length})</h2>`;

        if (robots.length === 0) {
            html += `<p>No robots connected.</p>`;
        } else {
            html += `
                <table class="device-table">
                    <tr><th>ID</th><th>IP</th><th>Uptime</th><th>Last Seen</th><th>Status</th></tr>
                    ${robots
                        .map(
                            (r) => `
                        <tr>
                            <td>${r.id}</td>
                            <td>${r.ip}</td>
                            <td>${formatDuration(r.duration)}</td>
                            <td>${new Date(r.last_seen).toLocaleString()}</td>
                            <td>
                                ${
                                    r.status === "connected"
                                        ? '<span class="status-connected">🟢 Connected</span>'
                                        : '<span class="status-disconnected">🔴 Disconnected</span>'
                                }
                            </td>
                        </tr>
                    `
                        )
                        .join("")}
                </table>
            `;
        }

        robotsDiv.innerHTML = html;
    }

    // === Users Section ===
    const usersDiv = document.getElementById("users");
    if (usersDiv) {
        const users = data.users || [];
        let html = `<h2>👤 Users (${users.length})</h2>`;

        if (users.length === 0) {
            html += `<p>No users connected.</p>`;
        } else {
            html += `
                <table class="device-table">
                    <tr><th>ID</th><th>IP</th><th>Uptime</th><th>Last Seen</th><th>Status</th></tr>
                    ${users
                        .map(
                            (u) => `
                        <tr>
                            <td>${u.id}</td>
                            <td>${u.ip}</td>
                            <td>${formatDuration(u.duration)}</td>
                            <td>${new Date(u.last_seen).toLocaleString()}</td>
                            <td>
                                ${
                                    u.status === "connected"
                                        ? '<span class="status-connected">🟢 Connected</span>'
                                        : '<span class="status-disconnected">🔴 Disconnected</span>'
                                }
                            </td>
                        </tr>
                    `
                        )
                        .join("")}
                </table>
            `;
        }

        usersDiv.innerHTML = html;
    }
}

// Run initially and every 5 seconds
fetchDeviceData();
setInterval(fetchDeviceData, 5000);
