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

function updatePage(data) {
    const { server, robots } = data;

    let statusHtml = "<h2>Server</h2>";
    if (server) {
        statusHtml += `
            <p>Status: <span style="color:green;">Connected</span></p>
            <p>IP: ${server.ip}</p>
            <p>Connected at: ${server.connected_at}</p>
            <p>Duration: ${server.duration} seconds</p>
        `;
    } else {
        statusHtml += `<p>Status: <span style="color:red;">Disconnected</span></p>`;
    }

    document.getElementById("status").innerHTML = statusHtml;

    let robotsHtml = `<h2>Robots (${robots.length})</h2>`;
    if (robots.length === 0) {
        robotsHtml += "<p>No robots connected.</p>";
    } else {
        robotsHtml += `
            <table border="1">
                <tr><th>ID</th><th>IP</th><th>Connected At</th><th>Duration (s)</th></tr>
                ${robots
                    .map(
                        (r) => `
                    <tr>
                        <td>${r.id}</td>
                        <td>${r.ip}</td>
                        <td>${r.connected_at}</td>
                        <td>${r.duration}</td>
                    </tr>
                `
                    )
                    .join("")}
            </table>
        `;
    }

    document.getElementById("robots").innerHTML = robotsHtml;
}

// Call initially and then every 10 seconds
fetchDeviceData();
setInterval(fetchDeviceData, 10000);
