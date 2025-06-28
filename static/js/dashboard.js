async function fetchDeviceData() {
    try {
        const res = await fetch("/api/connected-devices/json");
        const data = await res.json();
        updatePage(data);
    } catch (err) {
        console.error("Failed to fetch device data:", err);
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

function updatePage(data) {
    const { server, robots, users } = data;

    let serverHtml = "<h2>Server</h2>";
    if (server) {
        serverHtml += `
            <p>Status: <span class="status-ok">Connected</span></p>
            <p>IP: ${server.ip}</p>
            <p>Connected at: ${server.connected_at}</p>
            <p>Uptime: ${formatDuration(server.duration)}</p>
            <p>Last seen: ${server.last_seen || "N/A"}</p>
        `;
    } else {
        serverHtml += `<p>Status: <span class="status-bad">Disconnected</span></p>`;
    }

    const serverDiv = document.getElementById("server-status");
    if (serverDiv) serverDiv.innerHTML = serverHtml;

    let robotsHtml = `<h2>Robots (${robots.length})</h2>`;
    if (robots.length === 0) {
        robotsHtml += "<p>No robots connected.</p>";
    } else {
        robotsHtml += `
            <table>
                <tr><th>ID</th><th>IP</th><th>Connected At</th><th>Uptime</th><th>Last Seen</th></tr>
                ${robots
                    .map(
                        (r) => `
                    <tr>
                        <td>${r.id}</td>
                        <td>${r.ip}</td>
                        <td>${r.connected_at}</td>
                        <td>${formatDuration(r.duration)}</td>
                        <td>${r.last_seen || "N/A"}</td>
                    </tr>
                `
                    )
                    .join("")}
            </table>
        `;
    }

    const robotsDiv = document.getElementById("robots");
    if (robotsDiv) robotsDiv.innerHTML = robotsHtml;

    let usersHtml = `<h2>Users (${users.length})</h2>`;
    if (users.length === 0) {
        usersHtml += "<p>No users connected.</p>";
    } else {
        usersHtml += `
            <table>
                <tr><th>ID</th><th>IP</th><th>Connected At</th><th>Uptime</th><th>Last Seen</th></tr>
                ${users
                    .map(
                        (u) => `
                    <tr>
                        <td>${u.id}</td>
                        <td>${u.ip}</td>
                        <td>${u.connected_at}</td>
                        <td>${formatDuration(u.duration)}</td>
                        <td>${u.last_seen || "N/A"}</td>
                    </tr>
                `
                    )
                    .join("")}
            </table>
        `;
    }

    const usersDiv = document.getElementById("users");
    if (usersDiv) usersDiv.innerHTML = usersHtml;
}

document.addEventListener("DOMContentLoaded", () => {
    fetchDeviceData();
    setInterval(fetchDeviceData, 10000);
});
