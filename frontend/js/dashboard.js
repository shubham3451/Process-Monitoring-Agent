const HOSTNAME = "ubuntu"; 
const API_BASE = "http://localhost:8000/api";
const WS_URL = `ws://localhost:8000/ws/hosts/${HOSTNAME}/`;

let historyPage = 1;
let totalPages = 1;


function loadHostDetails() {
    $.getJSON(`${API_BASE}/hosts/${HOSTNAME}/`, function(data) {
        const container = $("#host-details");
        container.empty();

        Object.entries(data).forEach(([key, value]) => {
            container.append(`
                <li class="host-detail-item">
                  <span class="host-key">${key}</span>
                  <span class="host-value">${value}</span>
                </li>
            `);
        });
    });
}


let ws;
let wsConnected = false;
let wsMessageReceived = false;

function connectWebSocket() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log("WebSocket connected");
        wsConnected = true;
        wsMessageReceived = false;

        setTimeout(() => {
            if (!wsMessageReceived) {
                console.log("No WS data, fetching from DB...");
                fetchLatestProcesses();
            }
        }, 3000);
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "snapshot") {
            wsMessageReceived = true;
            renderProcesses(msg.data.processes, "#live-processes");
        }
    };

    ws.onclose = () => {
        console.log("WebSocket closed, retrying...");
        wsConnected = false;
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => {
        console.log("WebSocket error");
        wsConnected = false;
    };
}

function fetchLatestProcesses() {
    $.getJSON(`${API_BASE}/hosts/${HOSTNAME}/latest/`, function (data) {
        console.log("Fetched from DB:", data);
        renderProcesses(data.processes, "#live-processes");
    }).fail(() => {
        console.error("Failed to fetch latest processes from API");
    });
}

function attachChildren(list) {
    const map = {};
    list.forEach(p => { p.children = []; map[p.pid] = p; });
    const roots = [];
    list.forEach(p => {
      if (p.ppid && map[p.ppid]) map[p.ppid].children.push(p);
      else roots.push(p);
    });
    return roots;
  }
  
  function renderProcesses(processes, selector) {
    const container = $(selector);
    container.empty();
  
    const table = $(`
      <table class="process-table">
        <thead>
          <tr>
            <th>PID</th>
            <th>Name</th>
            <th>CPU %</th>
            <th>Memory</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    `);
  
    const tbody = table.find("tbody");
  
    function cpuClass(val) {
      if (val < 30) return "cpu-low";
      if (val < 70) return "cpu-med";
      return "cpu-high";
    }
  
    const roots = attachChildren(processes);
  
    function renderRow(p, level = 0) {
      const hasChildren = p.children && p.children.length > 0;
      const row = $(`
        <tr class="process-row" data-pid="${p.pid}" data-level="${level}">
          <td>${p.pid}</td>
          <td class="name-cell" style="--lvl:${level}">
            ${hasChildren ? '<span class="toggle" aria-label="expand">▶</span>' : '<span class="toggle-spacer"></span>'}
            <span class="name">${p.name}</span>
          </td>
          <td class="${cpuClass(p.cpu_percent)}">${p.cpu_percent}</td>
          <td>${p.rss_bytes}</td>
        </tr>
      `);
  
      tbody.append(row);
  
      if (hasChildren) {
        p.children.forEach(child => {
          const childRow = renderRow(child, level + 1);
          childRow.hide();
        });
      }
      return row;
    }
  
    roots.forEach(p => renderRow(p));
    container.append(table);
  
    container.off('click', '.toggle').on('click', '.toggle', function (e) {
      e.stopPropagation();
      const row = $(this).closest('tr');
      const level = parseInt(row.attr('data-level'), 10);
  
      const isExpanded = $(this).text() === '▼';
      $(this).text(isExpanded ? '▶' : '▼');
  
      let next = row.next();
      while (next.length) {
        const nextLevel = parseInt(next.attr('data-level'), 10);
        if (isNaN(nextLevel) || nextLevel <= level) break;
  
        if (isExpanded) {
          next.hide();
          next.find('.toggle').text('▶');
        } else {
          if (nextLevel === level + 1) next.show();
        }
        next = next.next();
      }
    });
  }
  

function buildProcessTree(processes) {
    const map = {};
    const roots = [];

    processes.forEach(p => {
        p.children = [];
        map[p.pid] = p;
    });

    processes.forEach(p => {
        if (p.ppid && map[p.ppid]) {
            map[p.ppid].children.push(p);
        } else {
            roots.push(p);
        }
    });

    function renderNode(node) {
        const li = $('<li class="process-item"></li>');
        const hasChildren = node.children.length > 0;
        const toggle = hasChildren ? $('<span class="expand-toggle">▼</span>') : '';
        const text = `${node.name} (PID: ${node.pid}, CPU: ${node.cpu_percent}%, RSS: ${node.rss_bytes})`;
        li.append(toggle);
        li.append($('<span></span>').text(text));

        if (hasChildren) {
            const ul = $('<ul style="display:none;"></ul>');
            node.children.forEach(child => {
                ul.append(renderNode(child));
            });
            li.append(ul);
            toggle.click(() => ul.toggle());
        }
        return li;
    }

    const ul = $('<ul></ul>');
    roots.forEach(r => ul.append(renderNode(r)));
    return ul;
}

$(document).ready(function () {
    connectWebSocket();
    fetchLatestProcesses();  
});


function loadHistory(page = 1) {
    $.getJSON(`${API_BASE}/history/${HOSTNAME}/?page=${page}`, function(data) {
        const container = $("#historical-processes");
        container.empty();

        totalPages = Math.ceil(data.count / 1); 
        $("#page-info").text(`Page ${page} of ${totalPages}`);

        $("#history-pagination").show();
        $("#hide-history").show();
        $("#load-history").hide();

        data.results.forEach(snap => {
            const snapDiv = $('<div class="snapshot"></div>');
            snapDiv.append(`<h4 class="snapshot-title">Snapshot: ${snap.snapshot_time} &mdash; ${snap.processes.length} processes</h4>`);

            const table = $(`
                <table class="process-table">
                  <thead>
                    <tr>
                      <th>PID</th>
                      <th>Name</th>
                      <th>CPU %</th>
                      <th>Memory</th>
                    </tr>
                  </thead>
                  <tbody></tbody>
                </table>
            `);

            const tbody = table.find("tbody");
            snap.processes.forEach(proc => {
                tbody.append(`
                  <tr>
                    <td>${proc.pid}</td>
                    <td>${proc.name}</td>
                    <td>${proc.cpu_percent}</td>
                    <td>${proc.rss_bytes}</td>
                  </tr>
                `);
            });

            snapDiv.append(table);
            container.append(snapDiv);
        });

        $("#prev-page").prop("disabled", page <= 1);
        $("#next-page").prop("disabled", page >= totalPages);
    });
}

$("#load-history").click(() => {
    historyPage = 1;
    loadHistory(historyPage);
});

$("#hide-history").click(() => {
    $("#historical-processes").empty();
    $("#history-pagination").hide();
    $("#hide-history").hide();
    $("#load-history").show();
});

$("#prev-page").click(() => { if (historyPage > 1) loadHistory(--historyPage); });
$("#next-page").click(() => { if (historyPage < totalPages) loadHistory(++historyPage); });

$(document).ready(function() {
    $("#history-pagination").hide();
    $("#hide-history").hide(); 
    loadHostDetails();
    connectWebSocket();
});

