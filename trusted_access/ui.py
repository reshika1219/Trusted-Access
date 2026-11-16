from fastapi.responses import HTMLResponse


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trusted Access</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #f5f7fb; color: #172033; }
    header { background: #172033; color: white; padding: 1.5rem max(1rem, calc((100% - 1100px)/2)); }
    main { max-width: 1100px; margin: 1.5rem auto; padding: 0 1rem; }
    section { background: white; border: 1px solid #dfe5ef; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
    label { display: block; font-weight: 600; margin: .6rem 0 .2rem; }
    input, select, textarea, button { box-sizing: border-box; width: 100%; padding: .65rem; border: 1px solid #bac5d6; border-radius: 7px; font: inherit; }
    textarea { min-height: 90px; }
    button { background: #2457d6; color: white; border: 0; cursor: pointer; margin-top: .75rem; }
    button.secondary { background: #536176; }
    button.danger { background: #b42318; }
    .muted { color: #536176; font-size: .92rem; }
    .notice { padding: .75rem; background: #fff4d6; border: 1px solid #e8c86a; border-radius: 7px; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f5f7fb; padding: .75rem; border-radius: 7px; }
    .hidden { display: none; }
    li { margin: .45rem 0; }
  </style>
</head>
<body>
<header><h1>Trusted Access</h1><p>Privacy-first emergency information sharing prototype</p></header>
<main>
  <div class="notice"><strong>Prototype only:</strong> This is not a legally certified emergency-release system. Keep your recovery key safe. The server cannot recover lost keys.</div>
  <section id="auth">
    <h2>Start</h2>
    <div class="grid">
      <form id="register-form"><h3>Create account</h3>
        <label>Email</label><input name="email" type="email" required>
        <label>Password (12+ characters)</label><input name="password" type="password" minlength="12" required>
        <button>Create account</button>
      </form>
      <form id="login-form"><h3>Sign in</h3>
        <label>Email</label><input name="email" type="email" required>
        <label>Password</label><input name="password" type="password" required>
        <button>Sign in</button>
      </form>
    </div>
  </section>
  <section id="dashboard" class="hidden">
    <h2>Owner dashboard</h2><p id="identity" class="muted"></p>
    <button id="logout" class="secondary">Sign out</button>
    <div class="grid">
      <form id="vault-form"><h3>Encrypted vault item</h3>
        <p class="muted">The text is encrypted in your browser before it is sent. This prototype keeps the local encryption key in this browser only.</p>
        <label>Category</label><select name="category"><option>Medical</option><option>Emergency contacts</option><option>Insurance</option><option>Documents</option><option>Property</option><option>Dependents</option><option>Pets</option><option>Instructions</option></select>
        <label>Title</label><input name="title" required>
        <label>Private text</label><textarea name="text" required></textarea>
        <button>Encrypt and save</button>
      </form>
      <form id="contact-form"><h3>Trusted contact</h3>
        <label>Name</label><input name="name" required>
        <label>Relationship</label><input name="relationship" required>
        <label>Contact method</label><input name="contact_method" required>
        <button>Add contact</button>
      </form>
    </div>
    <div class="grid">
      <section><h3>Vault items</h3><ul id="items"></ul></section>
      <section><h3>Trusted contacts</h3><ul id="contacts"></ul></section>
    </div>
    <section><h3>Access requests</h3><ul id="requests"></ul></section>
    <section><h3>Audit log</h3><pre id="audit">No events loaded.</pre></section>
    <section><h3>Encrypted backup</h3><button id="export">Download export</button><pre id="backup"></pre></section>
  </section>
  <p id="message" role="status"></p>
</main>
<script>
const state = { token: sessionStorage.getItem("trustedAccessToken") };
const $ = (id) => document.getElementById(id);
function message(text, error = false) { $("message").textContent = text; $("message").style.color = error ? "#b42318" : "#16704a"; }
async function api(path, options = {}) {
  options.headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) options.headers["X-Session-Token"] = state.token;
  const response = await fetch(path, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Request failed");
  return body;
}
function formData(form) { return Object.fromEntries(new FormData(form)); }
async function encryptionKey() {
  let encoded = localStorage.getItem("trustedAccessDemoKey");
  if (!encoded) { const bytes = crypto.getRandomValues(new Uint8Array(32)); encoded = btoa(String.fromCharCode(...bytes)); localStorage.setItem("trustedAccessDemoKey", encoded); }
  const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
  return crypto.subtle.importKey("raw", bytes, "AES-GCM", false, ["encrypt"]);
}
async function encrypt(text) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await encryptionKey();
  const data = await crypto.subtle.encrypt({name: "AES-GCM", iv}, key, new TextEncoder().encode(text));
  return "v1:" + btoa(String.fromCharCode(...iv)) + ":" + btoa(String.fromCharCode(...new Uint8Array(data)));
}
async function refresh() {
  const [items, contacts, requests, audit, me] = await Promise.all([
    api("/vault/items"), api("/trusted-contacts"), api("/access-requests"), api("/audit-events"), api("/auth/me")
  ]);
  $("identity").textContent = "Signed in as " + me.email;
  $("items").innerHTML = items.map(i => `<li><strong>${i.title}</strong> (${i.category})<br><code>${i.id}</code></li>`).join("") || "<li>None yet.</li>";
  $("contacts").innerHTML = contacts.map(c => `<li><strong>${c.name}</strong> — ${c.relationship}<br><code>${c.id}</code><br><button data-invite="${c.id}">Create contact invite</button></li>`).join("") || "<li>None yet.</li>";
  $("requests").innerHTML = requests.map(r => `<li>${r.id} — <strong>${r.status}</strong> — item ${r.vault_item_id} ${r.status === "pending" ? `<button data-approve="${r.id}">Approve</button><button class="danger" data-reject="${r.id}">Reject</button>` : ""}</li>`).join("") || "<li>None yet.</li>";
  $("audit").textContent = JSON.stringify(audit, null, 2);
}
function showDashboard() { $("auth").classList.add("hidden"); $("dashboard").classList.remove("hidden"); refresh().catch(e => message(e.message, true)); }
if (state.token) showDashboard();
$("register-form").onsubmit = async e => { e.preventDefault(); try { const r = await api("/auth/register", {method:"POST", body:JSON.stringify(formData(e.target))}); state.token = r.session_token; sessionStorage.setItem("trustedAccessToken", state.token); message("Account created."); showDashboard(); } catch (x) { message(x.message, true); } };
$("login-form").onsubmit = async e => { e.preventDefault(); try { const r = await api("/auth/login", {method:"POST", body:JSON.stringify(formData(e.target))}); state.token = r.session_token; sessionStorage.setItem("trustedAccessToken", state.token); message("Signed in."); showDashboard(); } catch (x) { message(x.message, true); } };
$("logout").onclick = () => { sessionStorage.removeItem("trustedAccessToken"); state.token = null; location.reload(); };
$("vault-form").onsubmit = async e => { e.preventDefault(); try { const data = formData(e.target); await api("/vault/items", {method:"POST", body:JSON.stringify({category:data.category, title:data.title, ciphertext:await encrypt(data.text)})}); e.target.reset(); message("Encrypted vault item saved."); refresh(); } catch (x) { message(x.message, true); } };
$("contact-form").onsubmit = async e => { e.preventDefault(); try { await api("/trusted-contacts", {method:"POST", body:JSON.stringify(formData(e.target))}); e.target.reset(); message("Trusted contact added without access."); refresh(); } catch (x) { message(x.message, true); } };
document.addEventListener("click", async e => {
  try {
    if (e.target.dataset.invite) { const r = await api("/trusted-contacts/" + e.target.dataset.invite + "/invite", {method:"POST"}); prompt("Store this development contact token securely:", r.contact_token); message("Invite created."); }
    if (e.target.dataset.approve) { await api("/access-requests/" + e.target.dataset.approve + "/approve", {method:"POST"}); message("Request approved."); refresh(); }
    if (e.target.dataset.reject) { await api("/access-requests/" + e.target.dataset.reject + "/reject", {method:"POST"}); message("Request rejected."); refresh(); }
  } catch (x) { message(x.message, true); }
});
$("export").onclick = async () => { try { const data = await api("/backup/export"); $("backup").textContent = JSON.stringify(data, null, 2); message("Export generated. Save it securely."); } catch (x) { message(x.message, true); } };
</script>
</body>
</html>"""


def register_ui(app) -> None:
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> HTMLResponse:
        return HTMLResponse(INDEX_HTML)
