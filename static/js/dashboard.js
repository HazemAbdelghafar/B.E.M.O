function formatDuration(seconds) {
    if (!Number.isFinite(seconds)) return '<span class="status-bad">N/A</span>';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hrs).padStart(2, "0")}:${String(mins).padStart(
        2,
        "0"
    )}:${String(secs).padStart(2, "0")}`;
}

async function fetchDeviceData() {
    try {
        const res = await fetch("/api/connected-devices/json");
        const data = await res.json();
        updatePage(data);
    } catch (err) {
        console.error("Failed to fetch device data:", err);
        document.getElementById(
            "status"
        ).innerHTML = `<p style="color:red;">Error fetching data</p>`;
    }
}

function formatField(value) {
    return value ? value : '<span class="status-bad">N/A</span>';
}

function updatePage(data) {
    const { server, robots } = data;

    let statusHtml = "<h2>Server</h2>";
    if (server) {
        statusHtml += `
            <p>Status: <span class="status-ok">Connected</span></p>
            <p>IP: ${formatField(server.ip)}</p>
            <p>Connected at: ${formatField(server.connected_at)}</p>
            <p>Uptime: ${formatDuration(server.duration)}</p>
            <p>Last Seen: ${formatField(server.last_seen)}</p>
            <p>Last Message: <code>${formatField(
                server.last_message
            )}</code></p>
        `;
    } else {
        statusHtml += `
            <p>Status: <span class="status-bad">Disconnected</span></p>
            <p>Last Connected: ${formatField(server.last_disconnected)}</p>
        `;
    }

    document.getElementById("status").innerHTML = statusHtml;

    let robotsHtml = `<h2>Robots (${robots.length})</h2>`;
    if (robots.length === 0) {
        robotsHtml += "<p>No robots connected.</p>";
    } else {
        robotsHtml += `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Status</th>
                        <th>IP</th>
                        <th>Connected At</th>
                        <th>Duration</th>
                        <th>Last Seen</th>
                        <th>Last Message</th>
                        <th>Last Disconnected</th>
                    </tr>
                </thead>
                <tbody>
                    ${robots
                        .map(
                            (r) => `
                        <tr>
                            <td>${r.id}</td>
                            <td>${
                                r.status === "connected"
                                    ? `<span class="status-ok">Connected</span>`
                                    : `<span class="status-bad">Disconnected</span>`
                            }</td>
                            <td>${formatField(r.ip)}</td>
                            <td>${formatField(r.connected_at)}</td>
                            <td>${formatDuration(r.duration)}</td>
                            <td>${formatField(r.last_seen)}</td>
                            <td><code>${formatField(r.last_message)}</code></td>
                            <td>${formatField(r.last_disconnected)}</td>
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    }

    document.getElementById("robots").innerHTML = robotsHtml;
}

fetchDeviceData();
setInterval(fetchDeviceData, 10000);
