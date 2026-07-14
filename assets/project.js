(function () {
  "use strict";

  const state = {
    data: null,
    tasks: [
      { title: "Prepare API contract", priority: "High", status: "In progress" },
      { title: "Review deployment runbook", priority: "Medium", status: "Queued" }
    ],
    todos: [
      { title: "Validate input handling", done: false },
      { title: "Add reviewer notes", done: true }
    ],
    stream: []
  };

  const $ = (selector) => document.querySelector(selector);
  const html = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[char]));

  const setText = (selector, value) => {
    const node = $(selector);
    if (node) node.textContent = value;
  };

  const setHref = (selector, value) => {
    const node = $(selector);
    if (node) node.href = value;
  };

  const hashNumber = (value) => {
    let hash = 0;
    const text = String(value || "demo-wallet").toLowerCase();
    for (let index = 0; index < text.length; index += 1) {
      hash = ((hash << 5) - hash) + text.charCodeAt(index);
      hash |= 0;
    }
    return Math.abs(hash);
  };

  const scoreFromWallet = (wallet, maxScore) => {
    const hash = hashNumber(wallet);
    const utilization = 18 + (hash % 64);
    const repayment = 42 + (hash % 55);
    const liquidations = hash % 4;
    const age = 20 + (hash % 980);
    const health = Math.max(0, Math.min(maxScore, Math.round((repayment * 5.8) + (age * 0.22) - (utilization * 2.6) - (liquidations * 78))));
    return { health, utilization, repayment, liquidations, age };
  };

  const metricCards = (metrics) => metrics.map((metric) => `
    <article class="metric-card">
      <span>${html(metric.label)}</span>
      <strong>${html(metric.value)}</strong>
      <small>${html(metric.detail || "")}</small>
    </article>
  `).join("");

  const stackPills = (items) => items.map((item) => `<span>${html(item)}</span>`).join("");

  const renderShell = (data) => {
    document.documentElement.style.setProperty("--accent", data.accent);
    document.documentElement.style.setProperty("--accent-two", data.accentTwo);
    document.title = `${data.title} | Live Project`;
    setText("#brand-title", data.title);
    setText("#category", data.category);
    setText("#project-title", data.title);
    setText("#mission", data.mission);
    setText("#runtime-note", data.runtime);
    setText("#footer-repo", data.repo);
    setText("#footer-date", new Date().getFullYear());
    setHref("#repo-link", data.links.repo);
    setHref("#repo-link-2", data.links.repo);
    setHref("#architecture-link", data.docs.find((item) => item.label === "Architecture")?.url || data.links.repo);
    setHref("#portfolio-link", data.links.portfolio);
    $("#metric-grid").innerHTML = metricCards(data.metrics);
    $("#stack-list").innerHTML = stackPills(data.stack);
    $("#component-list").innerHTML = data.components.map((item) => `<span>${html(item)}</span>`).join("");
    $("#doc-grid").innerHTML = data.docs.map((doc) => `
      <a class="doc-card" href="${html(doc.url)}">
        <strong>${html(doc.label)}</strong>
        <span>${html(doc.note)}</span>
      </a>
    `).join("");
  };

  const renderEndpointTable = (endpoints) => {
    if (!endpoints || endpoints.length === 0) return "";
    return `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Method</th><th>Path</th><th>Purpose</th></tr></thead>
          <tbody>
            ${endpoints.map((row) => `
              <tr><td>${html(row.method)}</td><td><code>${html(row.path)}</code></td><td>${html(row.purpose)}</td></tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  };

  const setDemo = (content) => {
    $("#demo-root").innerHTML = content;
  };

  const setSide = (content) => {
    $("#side-root").innerHTML = content;
  };

  function renderTaskApi(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Task API Live Console</h3>
        <p>Create tasks, inspect the browser-side API response, and review the same resource model used by the FastAPI project.</p>
        <div class="form-grid">
          <label>Task title<input id="task-title" value="Ship GitHub Pages project surface"></label>
          <label>Priority<select id="task-priority"><option>High</option><option>Medium</option><option>Low</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="add-task">Create Task</button><button class="ghost-button" id="complete-task">Complete First Task</button></div>
        <div id="task-board" class="task-board result-box"></div>
        <pre id="task-response" class="code-box"></pre>
      </div>
    `);
    setSide(`
      <div class="demo-panel">
        <h3>API Contract</h3>
        ${renderEndpointTable(data.endpoints)}
      </div>
    `);
    const render = () => {
      $("#task-board").innerHTML = state.tasks.map((task, index) => `
        <div class="mini-card">
          <strong>${html(task.title)}</strong>
          <span>${html(task.priority)} priority - ${html(task.status)}</span>
        </div>
      `).join("");
      $("#task-response").textContent = JSON.stringify({ status: 201, authenticated: true, records: state.tasks }, null, 2);
    };
    $("#add-task").addEventListener("click", () => {
      state.tasks.unshift({ title: $("#task-title").value || "Untitled task", priority: $("#task-priority").value, status: "Queued" });
      render();
    });
    $("#complete-task").addEventListener("click", () => {
      if (state.tasks[0]) state.tasks[0].status = "Done";
      render();
    });
    render();
  }

  function renderTodo(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Todo Application</h3>
        <p>This mirrors the repo's core add, view, mark-done, remove, and clear flow in a browser-ready interface.</p>
        <div class="form-grid">
          <label>New task<input id="todo-title" value="Prepare interview demo"></label>
          <label>Status<select id="todo-status"><option>Open</option><option>Done</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="todo-add">Add Task</button><button class="ghost-button" id="todo-clear">Clear Done</button></div>
        <div id="todo-list" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Functions</h3><div class="status-list">${data.sample.functions.map((item) => `<span>${html(item)}<b>Ready</b></span>`).join("")}</div></div>`);
    const render = () => {
      $("#todo-list").innerHTML = state.todos.map((todo, index) => `
        <div class="mini-card">
          <strong>${todo.done ? "[Done] " : ""}${html(todo.title)}</strong>
          <span><button class="ghost-button" data-toggle="${index}">${todo.done ? "Reopen" : "Mark Done"}</button></span>
        </div>
      `).join("");
      document.querySelectorAll("[data-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
          const item = state.todos[Number(button.dataset.toggle)];
          item.done = !item.done;
          render();
        });
      });
    };
    $("#todo-add").addEventListener("click", () => {
      state.todos.unshift({ title: $("#todo-title").value || "New task", done: $("#todo-status").value === "Done" });
      render();
    });
    $("#todo-clear").addEventListener("click", () => {
      state.todos = state.todos.filter((todo) => !todo.done);
      render();
    });
    render();
  }

  function renderWeather(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Weather Lookup</h3>
        <p>Search a city and retrieve a live browser-side weather result using Open-Meteo. If the network is unavailable, the app uses a realistic fallback.</p>
        <div class="form-grid">
          <label>City<input id="weather-city" value="Chennai"></label>
          <label>Mode<select id="weather-mode"><option>Current weather</option><option>Operations check</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="weather-run">Get Weather</button></div>
        <div id="weather-result" class="result-box"></div>
      </div>
    `);
    setSide(`
      <div class="demo-panel">
        <h3>App Features</h3>
        <div class="status-list">${data.highlights.map((item) => `<span>${html(item)}<b>Live</b></span>`).join("")}</div>
      </div>
    `);
    const fallback = (city) => {
      const hash = hashNumber(city);
      return { city, temperature: 24 + (hash % 12), humidity: 45 + (hash % 42), wind: 6 + (hash % 18), source: "Fallback sample" };
    };
    const renderWeatherResult = (result) => {
      $("#weather-result").innerHTML = `
        <div class="cards-grid">
          <div class="mini-card"><strong>${html(result.temperature)} C</strong><span>Temperature</span></div>
          <div class="mini-card"><strong>${html(result.humidity)}%</strong><span>Humidity</span></div>
          <div class="mini-card"><strong>${html(result.wind)} km/h</strong><span>Wind speed</span></div>
        </div>
        <p>${html(result.city)} - ${html(result.source)}</p>
      `;
    };
    $("#weather-run").addEventListener("click", async () => {
      const city = $("#weather-city").value || "Chennai";
      $("#weather-result").innerHTML = "<p>Loading weather data...</p>";
      try {
        const geo = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1`).then((res) => res.json());
        if (!geo.results || !geo.results[0]) throw new Error("City not found");
        const place = geo.results[0];
        const weather = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${place.latitude}&longitude=${place.longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m`).then((res) => res.json());
        renderWeatherResult({
          city: `${place.name}, ${place.country}`,
          temperature: Math.round(weather.current.temperature_2m),
          humidity: Math.round(weather.current.relative_humidity_2m),
          wind: Math.round(weather.current.wind_speed_10m),
          source: "Open-Meteo live API"
        });
      } catch (error) {
        renderWeatherResult(fallback(city));
      }
    });
    $("#weather-run").click();
  }

  function renderPii(data) {
    const sample = data.sample.text;
    setDemo(`
      <div class="demo-panel">
        <h3>PII Detection and Redaction</h3>
        <p>Paste logs, API payloads, or support text. The browser demo detects common sensitive patterns and produces a redacted review copy.</p>
        <label>Input text<textarea id="pii-input">${html(sample)}</textarea></label>
        <div class="demo-actions"><button class="button" id="pii-run">Detect PII</button><button class="ghost-button" id="pii-clear">Clear</button></div>
        <div id="pii-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Detection Classes</h3><div class="stack-list">${stackPills(data.sample.classes)}</div></div>`);
    const patterns = [
      { label: "Email", regex: /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, replace: "[EMAIL]" },
      { label: "Phone", regex: /\b(?:\+91[-\s]?)?[6-9]\d{9}\b/g, replace: "[PHONE]" },
      { label: "Aadhaar-like ID", regex: /\b\d{4}\s?\d{4}\s?\d{4}\b/g, replace: "[AADHAAR]" },
      { label: "PAN-like ID", regex: /\b[A-Z]{5}\d{4}[A-Z]\b/g, replace: "[PAN]" },
      { label: "IPv4", regex: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g, replace: "[IP]" }
    ];
    const run = () => {
      let text = $("#pii-input").value;
      const findings = [];
      patterns.forEach((item) => {
        const matches = text.match(item.regex) || [];
        if (matches.length) findings.push({ type: item.label, count: matches.length });
        text = text.replace(item.regex, item.replace);
      });
      $("#pii-output").innerHTML = `
        <div class="cards-grid">
          ${findings.length ? findings.map((item) => `<div class="mini-card"><strong>${html(item.count)}</strong><span>${html(item.type)} findings</span></div>`).join("") : '<div class="mini-card"><strong>0</strong><span>No high-confidence PII found</span></div>'}
        </div>
        <pre class="code-box">${html(text)}</pre>
      `;
    };
    $("#pii-run").addEventListener("click", run);
    $("#pii-clear").addEventListener("click", () => { $("#pii-input").value = ""; run(); });
    run();
  }

  function renderExtraction(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Contract Address Extraction</h3>
        <p>Extract Ethereum contract addresses from notes, logs, or scraped text, then prepare clean output for downstream wallet or protocol analysis.</p>
        <label>Source text<textarea id="extract-input">${html(data.sample.text)}</textarea></label>
        <div class="demo-actions"><button class="button" id="extract-run">Extract Addresses</button></div>
        <div id="extract-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Pipeline</h3><div class="status-list">${data.sample.pipeline.map((item) => `<span>${html(item)}<b>Step</b></span>`).join("")}</div></div>`);
    const run = () => {
      const matches = Array.from(new Set(($("#extract-input").value.match(/0x[a-fA-F0-9]{40}/g) || [])));
      $("#extract-output").innerHTML = matches.length ? `
        <p>${matches.length} unique contract addresses found.</p>
        <pre class="code-box">${html(matches.join("\n"))}</pre>
      ` : "<p>No valid Ethereum contract addresses found.</p>";
    };
    $("#extract-run").addEventListener("click", run);
    run();
  }

  function renderScoring(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>${html(data.sample.scoreLabel)} Console</h3>
        <p>Enter a wallet address to calculate deterministic demo features and an explainable score similar to the repository's scoring workflow.</p>
        <div class="form-grid">
          <label>Wallet address<input id="wallet-input" value="${html(data.sample.wallet)}"></label>
          <label>Risk model<select id="risk-model"><option>${html(data.sample.model)}</option><option>Conservative</option><option>Growth weighted</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="score-run">Calculate Score</button></div>
        <div id="score-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Feature Inputs</h3><div class="stack-list">${stackPills(data.sample.features)}</div></div>`);
    const run = () => {
      const max = data.sample.maxScore || 1000;
      const result = scoreFromWallet($("#wallet-input").value, max);
      const score = Math.min(max, Math.max(0, result.health));
      const percent = Math.round((score / max) * 100);
      const rating = percent > 72 ? "Low risk" : percent > 45 ? "Moderate risk" : "High risk";
      $("#score-output").innerHTML = `
        <div class="mini-card"><strong>${score} / ${max}</strong><span>${rating}</span><div class="meter" style="--value:${percent}%"><span></span></div></div>
        <div class="cards-grid">
          <div class="mini-card"><strong>${result.utilization}%</strong><span>Utilization</span></div>
          <div class="mini-card"><strong>${result.repayment}%</strong><span>Repayment behavior</span></div>
          <div class="mini-card"><strong>${result.liquidations}</strong><span>Liquidation events</span></div>
        </div>
        <pre class="code-box">${html(JSON.stringify({ wallet: $("#wallet-input").value, score, rating, model: $("#risk-model").value, features: result }, null, 2))}</pre>
      `;
    };
    $("#score-run").addEventListener("click", run);
    run();
  }

  function renderDefiServer(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>DeFi Scoring Stream</h3>
        <p>Simulate a Kafka-style wallet event entering the FastAPI service and producing a reputation score.</p>
        <div class="form-grid">
          <label>Wallet<input id="stream-wallet" value="${html(data.sample.wallet)}"></label>
          <label>Event type<select id="stream-event"><option>borrow</option><option>repay</option><option>liquidation</option><option>deposit</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="stream-run">Process Event</button></div>
        <div id="stream-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Service Endpoints</h3>${renderEndpointTable(data.endpoints)}</div>`);
    const render = () => {
      $("#stream-output").innerHTML = state.stream.length ? state.stream.map((item) => `
        <div class="mini-card"><strong>${html(item.event)} - score ${html(item.score)}</strong><span>${html(item.wallet)} processed at ${html(item.time)}</span></div>
      `).join("") : "<p>No stream events processed yet.</p>";
    };
    $("#stream-run").addEventListener("click", () => {
      const wallet = $("#stream-wallet").value;
      const event = $("#stream-event").value;
      const score = scoreFromWallet(wallet + event + Date.now(), 1000).health;
      state.stream.unshift({ wallet, event, score, time: new Date().toLocaleTimeString() });
      render();
    });
    render();
  }

  function renderAvi(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>AVI Tenant Automation</h3>
        <p>Build a safe tenant payload and command preview for the VMware AVI controller workflow.</p>
        <div class="form-grid">
          <label>Controller URL<input id="avi-controller" value="${html(data.sample.controller)}"></label>
          <label>Tenant name<input id="avi-tenant" value="${html(data.sample.tenant)}"></label>
          <label>Cloud<select id="avi-cloud"><option>Default-Cloud</option><option>Production-Cloud</option><option>Lab-Cloud</option></select></label>
          <label>Action<select id="avi-action"><option>Create tenant</option><option>Update tenant</option><option>Delete tenant</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="avi-run">Generate Request</button></div>
        <pre id="avi-output" class="code-box"></pre>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Automation Flow</h3><div class="status-list">${data.sample.flow.map((item) => `<span>${html(item)}<b>Ready</b></span>`).join("")}</div>${renderEndpointTable(data.endpoints)}</div>`);
    const run = () => {
      const payload = {
        name: $("#avi-tenant").value,
        cloud_ref: `/api/cloud?name=${$("#avi-cloud").value}`,
        action: $("#avi-action").value,
        secure_mode: true
      };
      $("#avi-output").textContent = `POST ${$("#avi-controller").value}/api/tenant\nAuthorization: Bearer <token>\nContent-Type: application/json\n\n${JSON.stringify(payload, null, 2)}`;
    };
    $("#avi-run").addEventListener("click", run);
    run();
  }

  function renderCompliance(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Contract Compliance Review</h3>
        <p>Paste a clause set and run a browser-side compliance triage. The repo contains the backend or RAG implementation for full deployment.</p>
        <label>Contract text<textarea id="contract-input">${html(data.sample.text)}</textarea></label>
        <div class="demo-actions"><button class="button" id="contract-run">Run Review</button><button class="ghost-button" id="contract-sample">Load Risky Sample</button></div>
        <div id="contract-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Review Controls</h3><div class="stack-list">${stackPills(data.sample.controls)}</div></div>`);
    const rules = [
      { label: "Confidentiality", pattern: /confidential|non-disclosure|nda/i, severity: "Required" },
      { label: "Termination", pattern: /termination|terminate|notice period/i, severity: "Required" },
      { label: "Liability limit", pattern: /liability|indemnity|damages/i, severity: "High impact" },
      { label: "Data protection", pattern: /data protection|privacy|gdpr|personal data/i, severity: "High impact" },
      { label: "Governing law", pattern: /governing law|jurisdiction|venue/i, severity: "Required" },
      { label: "Payment terms", pattern: /payment|invoice|fees|net 30/i, severity: "Commercial" }
    ];
    const run = () => {
      const text = $("#contract-input").value;
      const findings = rules.map((rule) => ({ ...rule, present: rule.pattern.test(text) }));
      const missing = findings.filter((item) => !item.present);
      const risk = Math.min(100, 18 + missing.length * 13 + (text.length < 220 ? 14 : 0));
      $("#contract-output").innerHTML = `
        <div class="mini-card"><strong>${risk}% review risk</strong><span>${missing.length} missing or weak control areas</span><div class="meter" style="--value:${risk}%"><span></span></div></div>
        <div class="table-wrap"><table><thead><tr><th>Control</th><th>Status</th><th>Severity</th></tr></thead><tbody>
          ${findings.map((item) => `<tr><td>${html(item.label)}</td><td>${item.present ? "Present" : "Needs review"}</td><td>${html(item.severity)}</td></tr>`).join("")}
        </tbody></table></div>
      `;
    };
    $("#contract-run").addEventListener("click", run);
    $("#contract-sample").addEventListener("click", () => { $("#contract-input").value = data.sample.riskyText; run(); });
    run();
  }

  function renderAdmission(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Admission Counselor Workspace</h3>
        <p>Enter a student profile and generate course recommendations, SWOT notes, and next actions.</p>
        <div class="form-grid">
          <label>Interest area<input id="student-interest" value="AI and cloud computing"></label>
          <label>Strength<input id="student-strength" value="Python, problem solving"></label>
          <label>Preferred location<select id="student-location"><option>India</option><option>USA</option><option>UK</option><option>Online</option></select></label>
          <label>Budget<select id="student-budget"><option>Medium</option><option>Low</option><option>High</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="admission-run">Generate Guidance</button></div>
        <div id="admission-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Guidance Model</h3><div class="stack-list">${stackPills(data.sample.signals)}</div></div>`);
    $("#admission-run").addEventListener("click", () => {
      const interest = $("#student-interest").value;
      const strength = $("#student-strength").value;
      const programs = data.sample.programs.map((program, index) => `
        <div class="mini-card"><strong>${html(program)}</strong><span>Fit score ${92 - index * 7}% for ${html(interest)}</span></div>
      `).join("");
      $("#admission-output").innerHTML = `
        <div class="cards-grid">${programs}</div>
        <pre class="code-box">${html(`SWOT summary\nStrengths: ${strength}\nOpportunity: Build projects around ${interest}\nRisk: Validate eligibility, deadlines, and funding early\nNext actions: shortlist programs, prepare SOP, collect transcripts`)}</pre>
      `;
    });
    $("#admission-run").click();
  }

  function renderWarehouse(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Secure Warehouse Operations</h3>
        <p>Operate a production-style warehouse dashboard with inventory, orders, shipments, and role-aware controls.</p>
        <div class="form-grid">
          <label>Role<select id="warehouse-role"><option>Admin</option><option>Manager</option><option>Auditor</option></select></label>
          <label>Inventory action<select id="warehouse-action"><option>Reorder low stock</option><option>Approve shipment</option><option>Audit access logs</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="warehouse-run">Run Action</button></div>
        <div id="warehouse-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>System Layers</h3><div class="status-list">${data.components.map((item) => `<span>${html(item)}<b>OK</b></span>`).join("")}</div>${renderEndpointTable(data.endpoints)}</div>`);
    const render = () => {
      $("#warehouse-output").innerHTML = `
        <div class="cards-grid">
          <div class="mini-card"><strong>1240</strong><span>Units tracked</span></div>
          <div class="mini-card"><strong>18</strong><span>Open orders</span></div>
          <div class="mini-card"><strong>6</strong><span>Shipments in transit</span></div>
        </div>
        <div class="table-wrap"><table><thead><tr><th>SKU</th><th>Stock</th><th>Status</th><th>Access</th></tr></thead><tbody>
          ${data.sample.inventory.map((row) => `<tr><td>${html(row.sku)}</td><td>${html(row.stock)}</td><td>${html(row.status)}</td><td>${html($("#warehouse-role").value)}</td></tr>`).join("")}
        </tbody></table></div>
        <pre class="code-box">${html(JSON.stringify({ role: $("#warehouse-role").value, action: $("#warehouse-action").value, jwtRequired: true, auditLogged: true }, null, 2))}</pre>
      `;
    };
    $("#warehouse-run").addEventListener("click", render);
    render();
  }

  function renderBlueCarbon(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>BlueCarbon MRV Calculator</h3>
        <p>Estimate blue-carbon project credits from protected area, biomass density, and survival assumptions.</p>
        <div class="form-grid">
          <label>Project area hectares<input id="bc-area" type="number" value="120"></label>
          <label>Biomass tCO2e per hectare<input id="bc-biomass" type="number" value="18"></label>
          <label>Survival rate percent<input id="bc-survival" type="number" value="86"></label>
          <label>Verification buffer percent<input id="bc-buffer" type="number" value="15"></label>
        </div>
        <div class="demo-actions"><button class="button" id="bc-run">Calculate Credits</button></div>
        <div id="bc-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>MRV Stages</h3><div class="status-list">${data.sample.stages.map((item) => `<span>${html(item)}<b>Tracked</b></span>`).join("")}</div></div>`);
    const run = () => {
      const area = Number($("#bc-area").value || 0);
      const biomass = Number($("#bc-biomass").value || 0);
      const survival = Number($("#bc-survival").value || 0) / 100;
      const buffer = Number($("#bc-buffer").value || 0) / 100;
      const gross = area * biomass * survival;
      const net = Math.round(gross * (1 - buffer));
      $("#bc-output").innerHTML = `
        <div class="cards-grid">
          <div class="mini-card"><strong>${Math.round(gross)}</strong><span>Gross tCO2e</span></div>
          <div class="mini-card"><strong>${net}</strong><span>Creditable tCO2e</span></div>
          <div class="mini-card"><strong>${Math.round(buffer * 100)}%</strong><span>Verification buffer</span></div>
        </div>
        <pre class="code-box">${html(JSON.stringify({ areaHectares: area, biomassPerHectare: biomass, survivalRate: survival, verificationBuffer: buffer, netCredits: net }, null, 2))}</pre>
      `;
    };
    $("#bc-run").addEventListener("click", run);
    run();
  }

  function renderProfile(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Cloud Career Command Center</h3>
        <p>Filter the project map by domain and open the strongest repositories for a cloud, AWS, Google Cloud, IBM, AI, or backend interview.</p>
        <div class="form-grid">
          <label>Interview focus<select id="profile-filter"><option>All</option><option>Cloud</option><option>AI</option><option>Backend</option><option>Security</option><option>DeFi</option></select></label>
          <label>Review style<select id="profile-style"><option>Architecture first</option><option>Live demo first</option><option>Security first</option></select></label>
        </div>
        <div class="demo-actions"><button class="button" id="profile-run">Build Review Path</button></div>
        <div id="profile-output" class="result-box"></div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Profile Strengths</h3><div class="stack-list">${stackPills(data.sample.strengths)}</div></div>`);
    const render = () => {
      const focus = $("#profile-filter").value;
      const items = data.sample.projects.filter((item) => focus === "All" || item.domain === focus);
      $("#profile-output").innerHTML = `
        <div class="cards-grid">
          ${items.map((item) => `<a class="mini-card" href="${html(item.url)}"><strong>${html(item.name)}</strong><span>${html(item.domain)} - ${html(item.reason)}</span></a>`).join("")}
        </div>
        <pre class="code-box">${html(`Recommended review style: ${$("#profile-style").value}\nFocus: ${focus}\nProjects selected: ${items.length}`)}</pre>
      `;
    };
    $("#profile-run").addEventListener("click", render);
    render();
  }

  function renderOperations(data) {
    setDemo(`
      <div class="demo-panel">
        <h3>Production Operations View</h3>
        <p>This project is presented with its runtime layers, documentation, and reviewer workflow.</p>
        <div class="cards-grid">${data.highlights.map((item) => `<div class="mini-card"><strong>Ready</strong><span>${html(item)}</span></div>`).join("")}</div>
      </div>
    `);
    setSide(`<div class="demo-panel"><h3>Project Components</h3><div class="status-list">${data.components.map((item) => `<span>${html(item)}<b>Mapped</b></span>`).join("")}</div></div>`);
  }

  function renderDemo(data) {
    const map = {
      "task-api": renderTaskApi,
      "todo": renderTodo,
      "weather": renderWeather,
      "pii": renderPii,
      "extraction": renderExtraction,
      "scoring": renderScoring,
      "defi-server": renderDefiServer,
      "avi": renderAvi,
      "compliance": renderCompliance,
      "admission": renderAdmission,
      "warehouse": renderWarehouse,
      "bluecarbon": renderBlueCarbon,
      "profile": renderProfile
    };
    (map[data.demoType] || renderOperations)(data);
  }

  async function boot() {
    try {
      const data = await fetch("assets/project-data.json", { cache: "no-store" }).then((response) => {
        if (!response.ok) throw new Error("Unable to load project data");
        return response.json();
      });
      state.data = data;
      renderShell(data);
      renderDemo(data);
    } catch (error) {
      setDemo(`<div class="demo-panel"><h3>Project data unavailable</h3><p>${html(error.message)}</p></div>`);
      setSide("");
    }
  }

  boot();
}());
