from fastapi.responses import HTMLResponse


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="description" content="Privacy-first emergency information sharing prototype">
  <title>Trusted Access</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232457d6'/%3E%3Cpath d='M16 6l8 3v6c0 5-3.4 8.6-8 11-4.6-2.4-8-6-8-11V9z' fill='white'/%3E%3C/svg%3E">
  <style>
    :root {
      --bg: #f4f6fb; --surface: #fff; --surface-2: #f4f6fb; --text: #152033; --muted: #55627a;
      --border: #d9e0ec; --primary: #2457d6; --primary-hover: #1b45b0; --on-primary: #fff;
      --danger: #b42318; --danger-bg: #fdecea; --ok: #16704a; --ok-bg: #e6f5ee;
      --warn-bg: #fff4d6; --warn-border: #e2bd55; --warn-text: #5c4300;
      --shadow: 0 1px 2px rgb(16 24 40 / .06), 0 4px 16px rgb(16 24 40 / .06);
      --radius: 12px; --focus: 0 0 0 3px rgb(36 87 214 / .35);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; line-height: 1.5;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0e1422; --surface: #172033; --surface-2: #101828; --text: #e9eef8; --muted: #9aa8c2;
        --border: #2a3753; --primary: #6c97ff; --primary-hover: #8fb0ff; --on-primary: #0b1220;
        --danger: #ff8a7d; --danger-bg: #3a1b19; --ok: #5fd3a0; --ok-bg: #12332a;
        --warn-bg: #3a2f10; --warn-border: #8a6d1d; --warn-text: #f4dc9a;
        --shadow: 0 1px 2px rgb(0 0 0 / .4); --focus: 0 0 0 3px rgb(108 151 255 / .45);
      }
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
    h1, h2, h3, p { margin: 0; }
    h2 { font-size: 1.25rem; } h3 { font-size: 1.05rem; }
    a { color: var(--primary); }
    :focus-visible { outline: none; box-shadow: var(--focus); border-radius: 8px; }
    .skip { position: absolute; left: -999px; top: .5rem; background: var(--surface); padding: .5rem 1rem; border-radius: 8px; z-index: 100; }
    .skip:focus { left: .5rem; }
    .wrap { width: min(1080px, 100% - 2rem); margin-inline: auto; }
    header.top { background: var(--surface); border-bottom: 1px solid var(--border); }
    header.top .wrap { display: flex; align-items: center; gap: 1rem; padding: .85rem 0; flex-wrap: wrap; }
    .brand { display: flex; align-items: center; gap: .65rem; margin-right: auto; }
    .brand svg { width: 34px; height: 34px; flex: none; }
    .brand h1 { font-size: 1.15rem; line-height: 1.2; }
    .brand small { color: var(--muted); display: block; font-size: .8rem; }
    .who { display: flex; align-items: center; gap: .75rem; font-size: .9rem; color: var(--muted); min-width: 0; }
    .who strong { color: var(--text); overflow: hidden; text-overflow: ellipsis; max-width: 24ch; white-space: nowrap; }
    main { flex: 1; padding: 1.25rem 0 2.5rem; }
    footer { padding: 1.25rem 0; color: var(--muted); font-size: .85rem; border-top: 1px solid var(--border); }
    .notice { display: flex; gap: .65rem; padding: .75rem 1rem; background: var(--warn-bg); border: 1px solid var(--warn-border); color: var(--warn-text); border-radius: 10px; margin-bottom: 1.25rem; font-size: .93rem; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; box-shadow: var(--shadow); }
    .card + .card { margin-top: 1rem; }
    .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
    .muted { color: var(--muted); font-size: .92rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; align-items: start; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .75rem; margin-bottom: 1rem; }
    .stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: .85rem 1rem; }
    .stat b { display: block; font-size: 1.6rem; line-height: 1.2; }
    .stat span { color: var(--muted); font-size: .85rem; }
    .stat.alert { border-color: var(--warn-border); background: var(--warn-bg); color: var(--warn-text); }
    .stat.alert span { color: inherit; }
    /* forms */
    label { display: block; font-weight: 600; font-size: .92rem; margin: .85rem 0 .3rem; }
    .field-hint { font-weight: 400; color: var(--muted); font-size: .85rem; margin-top: .25rem; }
    input, select, textarea { width: 100%; padding: .65rem .75rem; border: 1px solid var(--border); background: var(--surface-2); color: var(--text); border-radius: 8px; font: inherit; min-height: 44px; }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--primary); box-shadow: var(--focus); }
    textarea { min-height: 110px; resize: vertical; }
    input[type=checkbox] { width: 1.1rem; height: 1.1rem; min-height: 0; accent-color: var(--primary); }
    .pw { position: relative; }
    .pw input { padding-right: 4.5rem; }
    .pw button { position: absolute; right: .35rem; top: 50%; transform: translateY(-50%); }
    .meter { height: 6px; background: var(--border); border-radius: 3px; margin-top: .5rem; overflow: hidden; }
    .meter i { display: block; height: 100%; width: 0; background: var(--danger); transition: width .2s, background .2s; }
    /* buttons */
    .btn { display: inline-flex; align-items: center; justify-content: center; gap: .4rem; padding: .55rem 1rem; min-height: 44px; border: 1px solid transparent; border-radius: 8px; font: inherit; font-weight: 600; cursor: pointer; background: var(--primary); color: var(--on-primary); text-decoration: none; transition: background .15s, transform .05s; }
    .btn:hover { background: var(--primary-hover); }
    .btn:active { transform: translateY(1px); }
    .btn.block { width: 100%; margin-top: 1.1rem; }
    .btn.secondary { background: transparent; color: var(--text); border-color: var(--border); }
    .btn.secondary:hover { background: var(--surface-2); }
    .btn.danger { background: var(--danger); color: #fff; }
    .btn.danger.ghost { background: transparent; color: var(--danger); border-color: var(--danger); }
    .btn.danger.ghost:hover { background: var(--danger-bg); }
    .btn.small { min-height: 36px; padding: .3rem .7rem; font-size: .88rem; }
    .btn.link { background: none; border: 0; color: var(--primary); padding: .2rem .5rem; min-height: 32px; }
    .btn[disabled], .btn[aria-busy=true] { opacity: .6; cursor: progress; pointer-events: none; }
    .btn[aria-busy=true]::before { content: ""; width: .9em; height: .9em; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .row { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
    /* tabs */
    .tabs { display: flex; gap: .25rem; overflow-x: auto; border-bottom: 1px solid var(--border); margin-bottom: 1rem; scrollbar-width: thin; }
    .tab { background: none; border: 0; border-bottom: 3px solid transparent; padding: .7rem 1rem; font: inherit; font-weight: 600; color: var(--muted); cursor: pointer; white-space: nowrap; min-height: 44px; border-radius: 8px 8px 0 0; }
    .tab:hover { color: var(--text); }
    .tab[aria-selected=true] { color: var(--primary); border-bottom-color: var(--primary); }
    .badge { display: inline-block; min-width: 1.4rem; padding: 0 .4rem; margin-left: .35rem; border-radius: 99px; background: var(--danger); color: #fff; font-size: .75rem; text-align: center; }
    .badge.hidden { display: none; }
    /* lists */
    .list { list-style: none; padding: 0; margin: 0; display: grid; gap: .65rem; }
    .item { border: 1px solid var(--border); border-radius: 10px; padding: .85rem 1rem; background: var(--surface-2); display: flex; gap: .75rem; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }
    .item .main { min-width: 0; flex: 1 1 220px; }
    .item .title { font-weight: 600; overflow-wrap: anywhere; }
    .item .actions { display: flex; gap: .4rem; flex-wrap: wrap; }
    .pill { display: inline-block; padding: .05rem .6rem; border-radius: 99px; font-size: .78rem; font-weight: 600; background: var(--border); color: var(--text); vertical-align: middle; }
    .pill.pending { background: var(--warn-bg); color: var(--warn-text); }
    .pill.approved, .pill.owner_approved, .pill.granted { background: var(--ok-bg); color: var(--ok); }
    .pill.rejected, .pill.revoked, .pill.expired { background: var(--danger-bg); color: var(--danger); }
    .empty { text-align: center; padding: 1.75rem 1rem; color: var(--muted); border: 1px dashed var(--border); border-radius: 10px; }
    .empty b { display: block; color: var(--text); margin-bottom: .25rem; }
    .revealed { margin-top: .5rem; padding: .6rem .75rem; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; white-space: pre-wrap; overflow-wrap: anywhere; width: 100%; }
    code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .82rem; }
    code { color: var(--muted); overflow-wrap: anywhere; }
    pre { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: .75rem; white-space: pre-wrap; overflow-wrap: anywhere; max-height: 320px; overflow: auto; margin: .75rem 0 0; }
    .timeline { list-style: none; margin: 0; padding: 0 0 0 1.1rem; border-left: 2px solid var(--border); }
    .timeline li { position: relative; padding: 0 0 1rem .9rem; }
    .timeline li::before { content: ""; position: absolute; left: -1.5rem; top: .45rem; width: .65rem; height: .65rem; border-radius: 50%; background: var(--primary); border: 2px solid var(--surface); }
    .timeline time { color: var(--muted); font-size: .82rem; display: block; }
    .checks { display: grid; gap: .4rem; margin-top: .4rem; }
    .checks label { display: flex; gap: .6rem; align-items: center; font-weight: 400; margin: 0; padding: .45rem .6rem; border: 1px solid var(--border); border-radius: 8px; cursor: pointer; }
    .skeleton { height: 3.2rem; border-radius: 10px; background: linear-gradient(90deg, var(--surface-2), var(--border), var(--surface-2)); background-size: 200% 100%; animation: shimmer 1.2s infinite; }
    @keyframes shimmer { to { background-position: -200% 0; } }
    .hidden { display: none !important; }
    /* dialogs & toasts */
    dialog { border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; width: min(480px, 100% - 2rem); background: var(--surface); color: var(--text); box-shadow: 0 20px 60px rgb(0 0 0 / .35); }
    dialog::backdrop { background: rgb(8 12 24 / .55); }
    dialog h3 { margin-bottom: .5rem; }
    dialog .row.end { justify-content: flex-end; margin-top: 1.25rem; }
    #toasts { position: fixed; bottom: 1rem; left: 50%; transform: translateX(-50%); display: grid; gap: .5rem; z-index: 200; width: min(460px, 100% - 2rem); }
    .toast { padding: .75rem 1rem; border-radius: 10px; background: var(--ok-bg); color: var(--ok); border: 1px solid currentColor; box-shadow: var(--shadow); font-weight: 600; animation: pop .2s ease-out; }
    .toast.error { background: var(--danger-bg); color: var(--danger); }
    @keyframes pop { from { opacity: 0; transform: translateY(8px); } }
    .error-text { color: var(--danger); font-size: .9rem; margin-top: .6rem; min-height: 1.2em; }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    @media (max-width: 520px) { .who strong { max-width: 14ch; } .item .actions { width: 100%; } .item .actions .btn { flex: 1; } }
  </style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="top"><div class="wrap">
  <div class="brand">
    <svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#2457d6"/><path d="M16 6l8 3v6c0 5-3.4 8.6-8 11-4.6-2.4-8-6-8-11V9z" fill="#fff"/></svg>
    <div><h1>Trusted Access</h1><small>Emergency information sharing prototype</small></div>
  </div>
  <div class="who hidden" id="who"><span>Signed in as <strong id="identity"></strong></span><button class="btn secondary small" id="logout" type="button">Sign out</button></div>
</div></header>

<main id="content" class="wrap" tabindex="-1">
  <div class="notice" role="note"><span aria-hidden="true">⚠️</span><div><strong>Prototype only:</strong> this is not a legally certified emergency-release system. Keep your recovery key safe. The server cannot recover lost keys.</div></div>

  <section id="auth" aria-labelledby="auth-title">
    <div class="card" style="max-width:480px;margin-inline:auto">
      <h2 id="auth-title">Welcome</h2>
      <p class="muted">Share what matters with people you trust, only when you approve.</p>
      <div class="tabs" role="tablist" aria-label="Account" style="margin-top:1rem">
        <button class="tab" role="tab" id="tab-login" aria-selected="true" aria-controls="login-form" type="button">Sign in</button>
        <button class="tab" role="tab" id="tab-register" aria-selected="false" aria-controls="register-form" type="button" tabindex="-1">Create account</button>
      </div>
      <form id="login-form" role="tabpanel" aria-labelledby="tab-login" novalidate>
        <label for="login-email">Email</label>
        <input id="login-email" name="email" type="email" autocomplete="email" required>
        <label for="login-password">Password</label>
        <div class="pw"><input id="login-password" name="password" type="password" autocomplete="current-password" required><button class="btn link small" type="button" data-toggle-pw aria-label="Show password" aria-pressed="false">Show</button></div>
        <p class="error-text" role="alert" data-error></p>
        <button class="btn block" type="submit">Sign in</button>
      </form>
      <form id="register-form" role="tabpanel" aria-labelledby="tab-register" class="hidden" novalidate>
        <label for="reg-email">Email</label>
        <input id="reg-email" name="email" type="email" autocomplete="email" required>
        <label for="reg-password">Password</label>
        <div class="pw"><input id="reg-password" name="password" type="password" autocomplete="new-password" minlength="12" required aria-describedby="pw-hint"><button class="btn link small" type="button" data-toggle-pw aria-label="Show password" aria-pressed="false">Show</button></div>
        <div class="meter" aria-hidden="true"><i id="meter"></i></div>
        <p class="field-hint" id="pw-hint">At least 12 characters. A few random words works well.</p>
        <p class="error-text" role="alert" data-error></p>
        <button class="btn block" type="submit">Create account</button>
      </form>
    </div>
  </section>

  <section id="dashboard" class="hidden" aria-label="Owner dashboard">
    <h2 class="hidden">Owner dashboard</h2>
    <div class="stats" id="stats"></div>
    <div class="tabs" role="tablist" aria-label="Dashboard sections" id="dash-tabs">
      <button class="tab" role="tab" id="t-vault" aria-selected="true" aria-controls="p-vault" type="button">Vault</button>
      <button class="tab" role="tab" id="t-contacts" aria-selected="false" aria-controls="p-contacts" type="button" tabindex="-1">Trusted contacts</button>
      <button class="tab" role="tab" id="t-requests" aria-selected="false" aria-controls="p-requests" type="button" tabindex="-1">Access requests<span class="badge hidden" id="req-badge"></span></button>
      <button class="tab" role="tab" id="t-audit" aria-selected="false" aria-controls="p-audit" type="button" tabindex="-1">Activity</button>
      <button class="tab" role="tab" id="t-backup" aria-selected="false" aria-controls="p-backup" type="button" tabindex="-1">Backup</button>
    </div>

    <div role="tabpanel" id="p-vault" aria-labelledby="t-vault">
      <div class="grid">
        <form class="card" id="vault-form">
          <h3>Add an encrypted item</h3>
          <p class="muted">Encrypted in your browser before it is sent. This prototype keeps the key in this browser only.</p>
          <label for="v-category">Category</label>
          <select id="v-category" name="category"><option>Medical</option><option>Emergency contacts</option><option>Insurance</option><option>Documents</option><option>Property</option><option>Dependents</option><option>Pets</option><option>Instructions</option></select>
          <label for="v-title">Title</label>
          <input id="v-title" name="title" required maxlength="200" placeholder="e.g. Allergies and medication">
          <label for="v-text">Private text</label>
          <textarea id="v-text" name="text" required placeholder="Only you can read this until you share it."></textarea>
          <button class="btn block" type="submit">Encrypt and save</button>
        </form>
        <div class="card"><div class="card-head"><h3>Your vault</h3></div><ul class="list" id="items"></ul></div>
      </div>
    </div>

    <div role="tabpanel" id="p-contacts" aria-labelledby="t-contacts" class="hidden">
      <div class="grid">
        <form class="card" id="contact-form">
          <h3>Add a trusted contact</h3>
          <p class="muted">Adding someone gives them no access. You choose what they can request.</p>
          <label for="c-name">Name</label><input id="c-name" name="name" required maxlength="200" autocomplete="off">
          <label for="c-rel">Relationship</label><input id="c-rel" name="relationship" required maxlength="100" placeholder="e.g. Sister" autocomplete="off">
          <label for="c-method">Contact method</label><input id="c-method" name="contact_method" required maxlength="320" placeholder="Email or phone" autocomplete="off">
          <button class="btn block" type="submit">Add contact</button>
        </form>
        <div class="card"><div class="card-head"><h3>Your contacts</h3></div><ul class="list" id="contacts"></ul></div>
      </div>
    </div>

    <div role="tabpanel" id="p-requests" aria-labelledby="t-requests" class="hidden">
      <div class="card"><div class="card-head"><div><h3>Access requests</h3><p class="muted">Nothing is released unless you approve it. You can reject at any time.</p></div></div><ul class="list" id="requests"></ul></div>
    </div>

    <div role="tabpanel" id="p-audit" aria-labelledby="t-audit" class="hidden">
      <div class="card"><div class="card-head"><div><h3>Activity log</h3><p class="muted">Every security-relevant action, newest first.</p></div><button class="btn secondary small" id="reload" type="button">Refresh</button></div><ol class="timeline" id="audit"></ol></div>
    </div>

    <div role="tabpanel" id="p-backup" aria-labelledby="t-backup" class="hidden">
      <div class="card">
        <h3>Encrypted backup</h3>
        <p class="muted">Download a copy of your vault and contacts. Store it somewhere safe, away from this device.</p>
        <div class="row" style="margin-top:1rem"><button class="btn" id="export" type="button">Download export</button><button class="btn secondary" id="preview" type="button" aria-expanded="false" aria-controls="backup">Preview</button></div>
        <pre id="backup" class="hidden"></pre>
      </div>
    </div>
  </section>
</main>
<footer><div class="wrap">Trusted Access is a prototype and has not had a professional security review. Don't store anything you can't afford to lose.</div></footer>

<dialog id="confirm" aria-labelledby="confirm-title"><form method="dialog"><h3 id="confirm-title"></h3><p class="muted" id="confirm-body"></p><div class="row end"><button class="btn secondary" value="cancel">Cancel</button><button class="btn" id="confirm-ok" value="ok">Confirm</button></div></form></dialog>
<dialog id="token-dialog" aria-labelledby="token-title"><h3 id="token-title">Contact invite created</h3><p class="muted">Give this token to your contact through a secure channel. It is shown only once. Treat it like a password.</p><pre id="token-value"></pre><div class="row end"><button class="btn secondary" id="token-copy" type="button">Copy</button><button class="btn" id="token-close" type="button">Done</button></div></dialog>
<dialog id="policy-dialog" aria-labelledby="policy-title"><form id="policy-form"><h3 id="policy-title">Sharing rules</h3><p class="muted" id="policy-item"></p>
  <label for="p-mode">Who can request access</label>
  <select id="p-mode" name="access_mode"><option value="specific_contacts">Specific contacts</option><option value="emergency_only">Emergency only</option><option value="time_limited">Time-limited</option></select>
  <label id="p-contacts-label">Trusted contacts</label><div class="checks" id="p-contact-list" role="group" aria-labelledby="p-contacts-label"></div>
  <label for="p-approvals">Approvals required</label><input id="p-approvals" name="required_approvals" type="number" min="1" value="1"><p class="field-hint">Cannot exceed the number of selected contacts.</p>
  <p class="error-text" role="alert" id="policy-error"></p>
  <div class="row end"><button class="btn secondary" type="button" id="policy-cancel">Cancel</button><button class="btn" type="submit">Save rules</button></div></form></dialog>
<div id="toasts" aria-live="polite" aria-atomic="false"></div>

<script>
const $ = (id) => document.getElementById(id);
const state = { token: sessionStorage.getItem("trustedAccessToken"), items: [], contacts: [], requests: [] };
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const LABELS = {
  trusted_contact_created: "Trusted contact added", access_policy_changed: "Sharing rules changed", vault_item_created: "Vault item saved",
  access_approved: "Access request approved", access_rejected: "Access request rejected", access_revoked: "Access revoked",
  backup_exported: "Backup exported", access_requested: "Access requested", contact_invited: "Contact invite created",
};
const label = (t) => LABELS[t] || String(t).replace(/_/g, " ").replace(/^./, c => c.toUpperCase());
function parseDate(s) { if (!s) return null; let v = String(s).replace(" ", "T"); if (!/[zZ]|[+-]\d\d:?\d\d$/.test(v)) v += "Z"; const d = new Date(v); return isNaN(d) ? null : d; }
function ago(s) {
  const d = parseDate(s); if (!d) return "";
  const sec = Math.round((Date.now() - d) / 1000), abs = Math.abs(sec);
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  for (const [n, u] of [[60,"second"],[60,"minute"],[24,"hour"],[30,"day"],[12,"month"]]) { if (abs < n * (u === "second" ? 1 : 1) && u === "second") return rtf.format(-sec, u); }
  if (abs < 3600) return rtf.format(-Math.round(sec / 60), "minute");
  if (abs < 86400) return rtf.format(-Math.round(sec / 3600), "hour");
  if (abs < 2592000) return rtf.format(-Math.round(sec / 86400), "day");
  return d.toLocaleDateString();
}
const when = (s) => { const d = parseDate(s); return d ? `<time datetime="${esc(d.toISOString())}" title="${esc(d.toLocaleString())}">${esc(ago(s))}</time>` : ""; };

function toast(text, error = false) {
  const el = document.createElement("div"); el.className = "toast" + (error ? " error" : ""); el.textContent = text;
  if (error) el.setAttribute("role", "alert");
  $("toasts").appendChild(el); setTimeout(() => el.remove(), error ? 7000 : 3500);
}
async function api(path, options = {}) {
  options.headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) options.headers["X-Session-Token"] = state.token;
  let response;
  try { response = await fetch(path, options); } catch { throw new Error("Can't reach the server. Check your connection and try again."); }
  const body = await response.json().catch(() => ({}));
  if (response.status === 401 && state.token) { signOut("Your session expired. Please sign in again."); throw new Error("Session expired"); }
  if (!response.ok) {
    const d = body.detail;
    throw new Error(typeof d === "string" ? d : Array.isArray(d) ? d.map(x => x.msg).join("; ") : "Something went wrong. Please try again.");
  }
  return body;
}
async function busy(button, fn) {
  if (button) button.setAttribute("aria-busy", "true");
  try { return await fn(); } finally { if (button) button.removeAttribute("aria-busy"); }
}
const formData = (form) => Object.fromEntries(new FormData(form));
function confirmDialog(title, body, okText, danger = false) {
  return new Promise(resolve => {
    const d = $("confirm"); $("confirm-title").textContent = title; $("confirm-body").textContent = body;
    const ok = $("confirm-ok"); ok.textContent = okText; ok.className = "btn" + (danger ? " danger" : "");
    d.addEventListener("close", () => resolve(d.returnValue === "ok"), { once: true }); d.returnValue = "cancel"; d.showModal();
  });
}

/* Encryption: AES-GCM, key stays in this browser. */
const b64 = (bytes) => btoa(String.fromCharCode(...bytes));
const unb64 = (s) => Uint8Array.from(atob(s), c => c.charCodeAt(0));
async function encryptionKey() {
  let encoded = localStorage.getItem("trustedAccessDemoKey");
  if (!encoded) { encoded = b64(crypto.getRandomValues(new Uint8Array(32))); localStorage.setItem("trustedAccessDemoKey", encoded); }
  return crypto.subtle.importKey("raw", unb64(encoded), "AES-GCM", false, ["encrypt", "decrypt"]);
}
async function encrypt(text) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const data = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await encryptionKey(), new TextEncoder().encode(text));
  return "v1:" + b64(iv) + ":" + b64(new Uint8Array(data));
}
async function decrypt(blob) {
  const [v, iv, data] = String(blob).split(":");
  if (v !== "v1" || !iv || !data) throw new Error("Unsupported format");
  const out = await crypto.subtle.decrypt({ name: "AES-GCM", iv: unb64(iv) }, await encryptionKey(), unb64(data));
  return new TextDecoder().decode(out);
}

/* Rendering */
const empty = (title, hint) => `<li class="empty"><b>${esc(title)}</b>${esc(hint)}</li>`;
function render() {
  const pending = state.requests.filter(r => r.status === "pending");
  $("stats").innerHTML =
    `<div class="stat"><b>${state.items.length}</b><span>Vault items</span></div>` +
    `<div class="stat"><b>${state.contacts.length}</b><span>Trusted contacts</span></div>` +
    `<div class="stat ${pending.length ? "alert" : ""}"><b>${pending.length}</b><span>Pending requests</span></div>`;
  const badge = $("req-badge"); badge.textContent = pending.length; badge.classList.toggle("hidden", !pending.length);
  $("items").innerHTML = state.items.map(i => `<li class="item"><div class="main"><div class="title">${esc(i.title)}</div><div class="muted"><span class="pill">${esc(i.category)}</span> · ${when(i.created_at)}</div></div>
    <div class="actions"><button class="btn secondary small" data-reveal="${esc(i.id)}" type="button">View</button><button class="btn secondary small" data-policy="${esc(i.id)}" type="button">Sharing</button></div><div class="revealed hidden" id="rev-${esc(i.id)}" tabindex="-1"></div></li>`).join("")
    || empty("Your vault is empty", "Add your first encrypted item using the form.");
  $("contacts").innerHTML = state.contacts.map(c => `<li class="item"><div class="main"><div class="title">${esc(c.name)}</div><div class="muted">${esc(c.relationship)} · ${esc(c.contact_method)}</div></div>
    <div class="actions"><button class="btn secondary small" data-invite="${esc(c.id)}" data-name="${esc(c.name)}" type="button">Create invite</button></div></li>`).join("")
    || empty("No trusted contacts yet", "Add someone you'd trust in an emergency.");
  const itemName = (id) => (state.items.find(i => i.id === id) || {}).title || "Unknown item";
  const contactName = (id) => (state.contacts.find(c => c.id === id) || {}).name || "A trusted contact";
  $("requests").innerHTML = state.requests.map(r => `<li class="item"><div class="main"><div class="title">${esc(contactName(r.requester_contact_id))} requested “${esc(itemName(r.vault_item_id))}”</div>
    <div class="muted"><span class="pill ${esc(r.status)}">${esc(r.status.replace("_", " "))}</span> · ${when(r.requested_at)}</div></div>
    ${["pending", "owner_approved"].includes(r.status) ? `<div class="actions">${r.status === "pending" ? `<button class="btn small" data-approve="${esc(r.id)}" type="button">Approve</button>` : ""}<button class="btn danger ghost small" data-reject="${esc(r.id)}" type="button">Reject</button></div>` : ""}</li>`).join("")
    || empty("No access requests", "When a trusted contact asks for something, it will show up here.");
}
function renderAudit(events) {
  $("audit").innerHTML = events.map(e => `<li><strong>${esc(label(e.event_type))}</strong>${when(e.created_at)}</li>`).join("") || `<li class="muted">No activity yet.</li>`;
}
function skeleton() { const s = '<li class="skeleton" aria-hidden="true"></li>'.repeat(2); for (const id of ["items", "contacts", "requests"]) $(id).innerHTML = s; }
async function refresh() {
  const [items, contacts, requests, audit, me] = await Promise.all([api("/vault/items"), api("/trusted-contacts"), api("/access-requests"), api("/audit-events"), api("/auth/me")]);
  Object.assign(state, { items, contacts, requests });
  $("identity").textContent = me.email; $("identity").title = me.email;
  render(); renderAudit(audit);
}

/* Navigation */
function signedIn(on) {
  $("auth").classList.toggle("hidden", on); $("dashboard").classList.toggle("hidden", !on); $("who").classList.toggle("hidden", !on);
}
function showDashboard() { signedIn(true); skeleton(); refresh().catch(e => { if (e.message !== "Session expired") toast(e.message, true); }); }
function signOut(msg) {
  sessionStorage.removeItem("trustedAccessToken"); state.token = null; Object.assign(state, { items: [], contacts: [], requests: [] });
  signedIn(false); document.querySelectorAll("form").forEach(f => f.reset()); if (msg) toast(msg, true);
}
function setupTabs(list) {
  const tabs = [...list.querySelectorAll("[role=tab]")];
  const select = (tab, focus) => tabs.forEach(t => {
    const on = t === tab; t.setAttribute("aria-selected", on); t.tabIndex = on ? 0 : -1;
    $(t.getAttribute("aria-controls")).classList.toggle("hidden", !on); if (on && focus) t.focus();
  });
  tabs.forEach((t, i) => {
    t.onclick = () => select(t);
    t.onkeydown = (e) => {
      const k = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (k !== undefined) { e.preventDefault(); select(tabs[(k + tabs.length) % tabs.length], true); }
    };
  });
  return select;
}
setupTabs($("dash-tabs").parentElement.querySelector("#dash-tabs"));
setupTabs(document.querySelector("#auth .tabs"));
const dashSelect = (id) => $(id).click();

/* Forms */
const emailOk = (s) => /^\S+@\S+\.\S+$/.test(s);
function authForm(form, path, okText) {
  form.onsubmit = async (e) => {
    e.preventDefault(); const err = form.querySelector("[data-error]"); err.textContent = "";
    const data = formData(form);
    if (!emailOk(data.email.trim())) return void (err.textContent = "Enter a valid email address.");
    if (path.endsWith("register") && data.password.length < 12) return void (err.textContent = "Password must be at least 12 characters.");
    if (!data.password) return void (err.textContent = "Enter your password.");
    try {
      const r = await busy(form.querySelector("[type=submit]"), () => api(path, { method: "POST", body: JSON.stringify(data) }));
      state.token = r.session_token; sessionStorage.setItem("trustedAccessToken", state.token); form.reset(); toast(okText); showDashboard();
    } catch (x) { err.textContent = x.message; }
  };
}
authForm($("login-form"), "/auth/login", "Signed in.");
authForm($("register-form"), "/auth/register", "Account created. Welcome!");
$("login-form").addEventListener("input", () => $("login-form").querySelector("[data-error]").textContent = "");
$("reg-password").addEventListener("input", (e) => {
  const v = e.target.value; let s = Math.min(v.length / 16, 1) * 60;
  s += (/[a-z]/.test(v) && /[A-Z]/.test(v) ? 15 : 0) + (/\d/.test(v) ? 10 : 0) + (/[^a-zA-Z0-9\s]/.test(v) || /\s/.test(v) ? 15 : 0);
  if (v.length < 12) s = Math.min(s, 35);
  const m = $("meter"); m.style.width = s + "%"; m.style.background = s < 40 ? "var(--danger)" : s < 75 ? "#d99a00" : "var(--ok)";
});
document.querySelectorAll("[data-toggle-pw]").forEach(b => b.onclick = () => {
  const input = b.parentElement.querySelector("input"), show = input.type === "password";
  input.type = show ? "text" : "password"; b.textContent = show ? "Hide" : "Show"; b.setAttribute("aria-pressed", show); b.setAttribute("aria-label", show ? "Hide password" : "Show password");
});
$("logout").onclick = () => signOut();
$("reload").onclick = (e) => busy(e.currentTarget, () => refresh().then(() => toast("Up to date.")).catch(x => toast(x.message, true)));

$("vault-form").onsubmit = async (e) => {
  e.preventDefault(); const f = e.target, data = formData(f);
  if (!data.title.trim() || !data.text.trim()) return toast("Add a title and some text first.", true);
  try {
    await busy(f.querySelector("[type=submit]"), async () => api("/vault/items", { method: "POST", body: JSON.stringify({ category: data.category, title: data.title.trim(), ciphertext: await encrypt(data.text) }) }));
    f.reset(); toast("Encrypted item saved."); await refresh();
  } catch (x) { toast(x.message, true); }
};
$("contact-form").onsubmit = async (e) => {
  e.preventDefault(); const f = e.target;
  try {
    await busy(f.querySelector("[type=submit]"), () => api("/trusted-contacts", { method: "POST", body: JSON.stringify(formData(f)) }));
    f.reset(); toast("Contact added. They have no access yet."); await refresh();
  } catch (x) { toast(x.message, true); }
};

/* Actions */
let policyItem = null;
document.addEventListener("click", async (e) => {
  const b = e.target.closest("button"); if (!b) return; const d = b.dataset;
  try {
    if (d.reveal) {
      const box = $("rev-" + d.reveal);
      if (!box.classList.contains("hidden")) { box.classList.add("hidden"); b.textContent = "View"; return; }
      const item = state.items.find(i => i.id === d.reveal);
      try { box.textContent = await decrypt(item.ciphertext); } catch { box.textContent = "Can't decrypt this item in this browser. It was encrypted with a different key."; }
      box.classList.remove("hidden"); b.textContent = "Hide";
    } else if (d.policy) {
      if (!state.contacts.length) { toast("Add a trusted contact first, then choose what they can request.", true); return dashSelect("t-contacts"); }
      policyItem = state.items.find(i => i.id === d.policy);
      $("policy-item").textContent = "For “" + policyItem.title + "”"; $("policy-error").textContent = "";
      $("p-contact-list").innerHTML = state.contacts.map(c => `<label><input type="checkbox" name="contact" value="${esc(c.id)}"> ${esc(c.name)} <span class="muted">(${esc(c.relationship)})</span></label>`).join("");
      $("p-approvals").max = state.contacts.length; $("p-approvals").value = 1; $("policy-dialog").showModal();
    } else if (d.invite) {
      const r = await busy(b, () => api("/trusted-contacts/" + d.invite + "/invite", { method: "POST" }));
      $("token-title").textContent = "Invite for " + d.name; $("token-value").textContent = r.contact_token; $("token-dialog").showModal();
    } else if (d.approve) {
      if (!await confirmDialog("Approve this request?", "The contact will be able to see the item you shared. You can revoke access later.", "Approve")) return;
      await busy(b, () => api("/access-requests/" + d.approve + "/approve", { method: "POST" })); toast("Request approved."); await refresh();
    } else if (d.reject) {
      if (!await confirmDialog("Reject this request?", "The contact will not get access.", "Reject", true)) return;
      await busy(b, () => api("/access-requests/" + d.reject + "/reject", { method: "POST" })); toast("Request rejected."); await refresh();
    }
  } catch (x) { if (x.message !== "Session expired") toast(x.message, true); }
});
$("policy-cancel").onclick = () => $("policy-dialog").close();
$("policy-form").onsubmit = async (e) => {
  e.preventDefault(); const ids = [...e.target.querySelectorAll("[name=contact]:checked")].map(c => c.value);
  const approvals = Number($("p-approvals").value), err = $("policy-error");
  if (!ids.length) return void (err.textContent = "Select at least one contact.");
  if (!(approvals >= 1) || approvals > ids.length) return void (err.textContent = "Approvals must be between 1 and " + ids.length + ".");
  try {
    await busy(e.submitter, () => api("/vault/items/" + policyItem.id + "/policy", { method: "PUT", body: JSON.stringify({ access_mode: $("p-mode").value, contact_ids: ids, required_approvals: approvals }) }));
    $("policy-dialog").close(); toast("Sharing rules saved."); await refresh();
  } catch (x) { err.textContent = x.message; }
};
$("token-close").onclick = () => { $("token-dialog").close(); $("token-value").textContent = ""; };
$("token-copy").onclick = async (e) => {
  try { await navigator.clipboard.writeText($("token-value").textContent); e.target.textContent = "Copied ✓"; setTimeout(() => e.target.textContent = "Copy", 2000); }
  catch { toast("Copy failed. Select the text and copy it manually.", true); }
};
let backupData = null;
async function loadBackup(button) { backupData = await busy(button, () => api("/backup/export")); $("backup").textContent = JSON.stringify(backupData, null, 2); }
$("export").onclick = async (e) => {
  try {
    await loadBackup(e.currentTarget);
    const url = URL.createObjectURL(new Blob([JSON.stringify(backupData, null, 2)], { type: "application/json" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: "trusted-access-backup-" + new Date().toISOString().slice(0, 10) + ".json" });
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); toast("Backup downloaded. Store it somewhere safe."); refresh().catch(() => {});
  } catch (x) { if (x.message !== "Session expired") toast(x.message, true); }
};
$("preview").onclick = async (e) => {
  const pre = $("backup"), open = pre.classList.contains("hidden");
  try { if (open) await loadBackup(e.currentTarget); pre.classList.toggle("hidden", !open); e.currentTarget.setAttribute("aria-expanded", open); e.currentTarget.textContent = open ? "Hide preview" : "Preview"; }
  catch (x) { if (x.message !== "Session expired") toast(x.message, true); }
};
if (state.token) showDashboard();
</script>
</body>
</html>"""


def register_ui(app) -> None:
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> HTMLResponse:
        return HTMLResponse(
            INDEX_HTML,
            headers={
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "X-Frame-Options": "DENY",
            },
        )
