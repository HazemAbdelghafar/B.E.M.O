async function fetchDeviceData() {
    try {
        const res = await fetch("/api/connected-devices/json");
        const data = await res.json();
        updatePage(data);
    } catch (err) {
        console.error("Fetch failed:", err);
        // Do not overwrite server status block if fetch fails
    }
}

function formatDuration(seconds) {
    const h = Math.floor(seconds / 3600)
        .toString()
        .padStart(2, "0");
    const m = Math.floor((seconds % 3600) / 60)
        .toString()
        .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${h}:${m}:${s}`;
}

function renderSection(title, dataList, type) {
    let html = `<h2>${title} (${dataList.length})</h2>`;
    if (dataList.length === 0) {
        html += "<p>None connected.</p>";
    } else {
        html += `
            <table>
                <tr>
                    <th>ID</th>
                    <th>IP</th>
                    <th>Status</th>
                    <th>Connected At</th>
                    <th>Uptime</th>
                    <th>Last Seen</th>
                </tr>
                ${dataList
                    .map(
                        (d) => `
                        <tr>
                            <td>${d.id}</td>
                            <td>${d.ip}</td>
                            <td class="${
                                d.status === "connected"
                                    ? "status-ok"
                                    : "status-bad"
                            }">${d.status}</td>
                            <td>${d.connected_at}</td>
                            <td>${formatDuration(d.duration)}</td>
                            <td>${d.last_seen || "N/A"}</td>
                        </tr>
                    `
                    )
                    .join("")}
            </table>
        `;
    }
    document.getElementById(type).innerHTML = html;
}

function updatePage(data) {
    const { server, robots, users } = data;

    let serverHtml = "<h2>Server</h2>";
    if (server && server.status === "connected") {
        serverHtml += `
            <p>Status: <span class="status-ok">Connected</span></p>
            <p>IP: ${server.ip}</p>
            <p>Connected at: ${server.connected_at}</p>
            <p>Uptime: ${formatDuration(server.duration)}</p>
            <p>Last Seen: ${server.last_seen || "N/A"}</p>
        `;
    } else {
        serverHtml += `<p>Status: <span class="status-bad">Disconnected</span></p>`;
    }

    document.getElementById("server-status").innerHTML = serverHtml;

    renderSection("Robots", robots, "robots");
    renderSection("Users", users, "users");
}

// Initial load + refresh every 10 seconds
fetchDeviceData();
setInterval(fetchDeviceData, 10000);
