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
      --radius: 14px; --glow: rgb(36 87 214 / .10); --serif: ui-serif, Georgia, "Times New Roman", serif; --focus: 0 0 0 3px rgb(36 87 214 / .35);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; line-height: 1.5;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0e1422; --surface: #172033; --surface-2: #101828; --text: #e9eef8; --muted: #9aa8c2;
        --border: #2a3753; --primary: #6c97ff; --primary-hover: #8fb0ff; --on-primary: #0b1220;
        --danger: #ff8a7d; --danger-bg: #3a1b19; --ok: #5fd3a0; --ok-bg: #12332a;
        --warn-bg: #3a2f10; --warn-border: #8a6d1d; --warn-text: #f4dc9a;
        --shadow: 0 1px 2px rgb(0 0 0 / .4); --glow: rgb(108 151 255 / .14); --focus: 0 0 0 3px rgb(108 151 255 / .45);
      }
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: radial-gradient(60rem 28rem at 50% -8rem, var(--glow), transparent) no-repeat, var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
    h1, h2, h3, p { margin: 0; }
    h2 { font-size: 1.35rem; font-family: var(--serif); font-weight: 600; } h3 { font-size: 1.05rem; }
    a { color: var(--primary); }
    :focus-visible { outline: none; box-shadow: var(--focus); border-radius: 8px; }
    .skip { position: absolute; left: -999px; top: .5rem; background: var(--surface); padding: .5rem 1rem; border-radius: 8px; z-index: 100; }
    .skip:focus { left: .5rem; }
    .wrap { width: min(680px, 100% - 2rem); margin-inline: auto; }
    header.top { background: transparent; }
    header.top .wrap { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 2.25rem 0 1rem; text-align: center; }
    .brand { display: flex; flex-direction: column; align-items: center; gap: .6rem; }
    .brand svg { width: 46px; height: 46px; flex: none; filter: drop-shadow(0 6px 14px rgb(36 87 214 / .35)); }
    .brand h1 { font-family: var(--serif); font-size: 2rem; font-weight: 600; letter-spacing: -.015em; line-height: 1.15; }
    .brand small { color: var(--muted); display: block; font-size: .9rem; margin-top: .15rem; }
    .who { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: .75rem; font-size: .9rem; color: var(--muted); min-width: 0; }
    .who strong { color: var(--text); overflow: hidden; text-overflow: ellipsis; max-width: 24ch; white-space: nowrap; }
    main { flex: 1; padding: 1.25rem 0 2.5rem; }
    footer { text-align: center; padding: 1.25rem 0; color: var(--muted); font-size: .85rem; border-top: 1px solid var(--border); }
    .notice { display: flex; gap: .65rem; padding: .75rem 1rem; background: var(--warn-bg); border: 1px solid var(--warn-border); color: var(--warn-text); border-radius: 10px; margin-bottom: 1.5rem; font-size: .85rem; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; box-shadow: var(--shadow); }
    .card + .card { margin-top: 1rem; }
    .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
    .muted { color: var(--muted); font-size: .92rem; }
    .grid { display: grid; grid-template-columns: 1fr; gap: 1rem; align-items: start; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; margin-bottom: 1.25rem; text-align: center; }
    .stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: .85rem 1rem; }
    .stat b { display: block; font-family: var(--serif); font-size: 1.9rem; font-weight: 600; line-height: 1.2; }
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
    .tabs { display: flex; justify-content: safe center; gap: .25rem; overflow-x: auto; border-bottom: 1px solid var(--border); margin-bottom: 1rem; scrollbar-width: thin; }
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
      #auth .card > h2, #auth .card > p { text-align: center; }
    .divider { display: flex; align-items: center; gap: .75rem; color: var(--muted); font-size: .85rem; margin: 1.25rem 0 .9rem; }
    .divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: var(--border); }
    .demo-btn { width: 100%; }
    #demo-hint { text-align: center; margin-top: .6rem; }
    .pill.demo { background: var(--primary); color: var(--on-primary); margin-right: .4rem; }
  </style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="top"><div class="wrap">
  <div class="brand">
    <svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#2457d6"/><path d="M16 6l8 3v6c0 5-3.4 8.6-8 11-4.6-2.4-8-6-8-11V9z" fill="#fff"/></svg>
    <div><h1>Trusted Access</h1><small>Emergency information sharing prototype</small></div>
  </div>
  <div class="who hidden" id="who"><span><span class="pill demo hidden" id="demo-pill">Demo</span>Signed in as <strong id="identity"></strong></span><button class="btn secondary small" id="logout" type="button">Sign out</button></div>
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
      <div class="divider" aria-hidden="true"><span>or</span></div>
      <button class="btn secondary demo-btn" id="demo" type="button">Try the demo</button>
      <p class="field-hint" id="demo-hint">Creates a private demo account with sample data. No email needed.</p>
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
        <p class="muted">Download a copy of your vault and contacts. The whole file is encrypted in this browser with a passphrase you choose. We never see it and can't recover it.</p>
        <div class="row" style="margin-top:1rem"><button class="btn" id="export" type="button">Download encrypted backup</button></div>
      </div>
      <div class="card">
        <h3>Restore from a backup</h3>
        <p class="muted">Choose a backup file you downloaded earlier. Records are added to your vault. Nothing is overwritten or deleted.</p>
        <label for="import-file">Backup file</label>
        <input id="import-file" type="file" accept="application/json,.json">
        <p class="error-text" role="alert" id="import-error"></p>
        <div id="import-unlock" class="hidden">
          <p class="muted">This backup is encrypted. Enter the passphrase you chose when you made it.</p>
          <label for="import-pass">Backup passphrase</label>
          <input id="import-pass" type="password" autocomplete="off">
          <button class="btn block" id="import-unlock-btn" type="button">Unlock backup</button>
        </div>
        <div id="import-preview" class="hidden">
          <p id="import-summary"></p>
          <p class="muted" id="import-notes"></p>
          <ul class="list" id="import-list" style="margin-top:.75rem"></ul>
          <div class="row" style="margin-top:1rem"><button class="btn" id="import-go" type="button">Import</button><button class="btn secondary" id="import-cancel" type="button">Cancel</button></div>
        </div>
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
<dialog id="export-dialog" aria-labelledby="export-title"><form id="export-form" novalidate><h3 id="export-title">Protect your backup</h3>
  <p class="muted">Your backup is encrypted in this browser with a passphrase you choose. Without it, the file can't be opened, and nobody can recover it for you.</p>
  <label for="ex-pass">Backup passphrase</label><input id="ex-pass" type="password" autocomplete="new-password">
  <label for="ex-pass2">Confirm passphrase</label><input id="ex-pass2" type="password" autocomplete="new-password">
  <p class="field-hint">At least 12 characters. Store it separately from the backup file.</p>
  <p class="error-text" role="alert" id="export-error"></p>
  <div class="row end"><button class="btn secondary" type="button" id="export-cancel">Cancel</button><button class="btn" type="submit">Encrypt and download</button></div></form></dialog>
<dialog id="edit-dialog" aria-labelledby="edit-title"><form id="edit-form" novalidate><h3 id="edit-title">Edit item</h3>
  <label for="e-category">Category</label><select id="e-category"></select>
  <label for="e-title">Title</label><input id="e-title" maxlength="200">
  <label for="e-text">Private text</label><textarea id="e-text"></textarea><p class="field-hint" id="e-hint"></p>
  <p class="error-text" role="alert" id="edit-error"></p>
  <div class="row end"><button class="btn secondary" type="button" id="edit-cancel">Cancel</button><button class="btn" type="submit">Save changes</button></div></form></dialog>
<div id="toasts" aria-live="polite" aria-atomic="false"></div>

<script>
const $ = (id) => document.getElementById(id);
const state = { token: sessionStorage.getItem("trustedAccessToken"), items: [], contacts: [], requests: [], grants: [] };
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const LABELS = {
  trusted_contact_created: "Trusted contact added", access_policy_changed: "Sharing rules changed", vault_item_created: "Vault item saved",
  access_approved: "Access request approved", access_rejected: "Access request rejected", access_revoked: "Access revoked",
  backup_exported: "Backup exported", access_requested: "Access requested", trusted_contact_invited: "Contact invite created",
  access_owner_approved: "Owner approved, awaiting contacts", access_granted: "Access granted", access_viewed: "Shared item viewed",
  backup_import_requested: "Backup import requested", vault_item_updated: "Vault item edited", vault_item_deleted: "Vault item deleted",
  trusted_contact_deleted: "Trusted contact removed",
};
const label = (t) => LABELS[t] || String(t).replace(/_/g, " ").replace(/^./, c => c.toUpperCase());
function parseDate(s) { if (!s) return null; let v = String(s).replace(" ", "T"); if (!/[zZ]|[+-]\d\d:?\d\d$/.test(v)) v += "Z"; const d = new Date(v); return isNaN(d) ? null : d; }
function ago(s) {
  const d = parseDate(s); if (!d) return "";
  const sec = Math.round((Date.now() - d) / 1000), abs = Math.abs(sec);
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  if (abs < 60) return rtf.format(-sec, "second");
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
const b64 = (bytes) => { let bin = ""; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000)); return btoa(bin); };
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
    <div class="actions"><button class="btn secondary small" data-reveal="${esc(i.id)}" type="button">View</button><button class="btn secondary small" data-policy="${esc(i.id)}" type="button">Sharing</button><button class="btn secondary small" data-edit="${esc(i.id)}" type="button">Edit</button><button class="btn danger ghost small" data-del-item="${esc(i.id)}" type="button">Delete</button></div><div class="revealed hidden" id="rev-${esc(i.id)}" tabindex="-1"></div></li>`).join("")
    || empty("Your vault is empty", "Add your first encrypted item using the form.");
  $("contacts").innerHTML = state.contacts.map(c => `<li class="item"><div class="main"><div class="title">${esc(c.name)}</div><div class="muted">${esc(c.relationship)} · ${esc(c.contact_method)}</div></div>
    <div class="actions"><button class="btn secondary small" data-invite="${esc(c.id)}" data-name="${esc(c.name)}" type="button">Create invite</button><button class="btn danger ghost small" data-del-contact="${esc(c.id)}" data-name="${esc(c.name)}" type="button">Remove</button></div></li>`).join("")
    || empty("No trusted contacts yet", "Add someone you'd trust in an emergency.");
  const itemName = (id) => (state.items.find(i => i.id === id) || {}).title || "Unknown item";
  const contactName = (id) => (state.contacts.find(c => c.id === id) || {}).name || "A trusted contact";
  const grantOf = (r) => state.grants.find(g => g.request_id === r.id && !g.revoked_at) || state.grants.find(g => g.request_id === r.id);
  const grantState = (g) => !g ? null : g.revoked_at ? "revoked" : (parseDate(g.expires_at) <= new Date() ? "expired" : "active");
  $("requests").innerHTML = state.requests.map(r => {
    const g = grantOf(r), gs = grantState(g), shown = gs === "revoked" || gs === "expired" ? gs : r.status;
    const note = gs === "active" ? ` · access ends ${when(g.expires_at)}` : gs === "revoked" ? ` · revoked ${when(g.revoked_at)}` : "";
    const actions = ["pending", "owner_approved"].includes(r.status)
      ? `${r.status === "pending" ? `<button class="btn small" data-approve="${esc(r.id)}" type="button">Approve</button>` : ""}<button class="btn danger ghost small" data-reject="${esc(r.id)}" type="button">Reject</button>`
      : gs === "active" ? `<button class="btn danger ghost small" data-revoke="${esc(g.id)}" data-item="${esc(itemName(r.vault_item_id))}" data-name="${esc(contactName(r.requester_contact_id))}" type="button">Revoke access</button>` : "";
    return `<li class="item"><div class="main"><div class="title">${esc(contactName(r.requester_contact_id))} requested “${esc(itemName(r.vault_item_id))}”</div>
    <div class="muted"><span class="pill ${esc(shown)}">${esc(shown.replace("_", " "))}</span> · ${when(r.requested_at)}${note}</div></div>
    ${actions ? `<div class="actions">${actions}</div>` : ""}</li>`; }).join("")
    || empty("No access requests", "When a trusted contact asks for something, it will show up here.");
}
function renderAudit(events) {
  $("audit").innerHTML = events.map(e => `<li><strong>${esc(label(e.event_type))}</strong>${when(e.created_at)}</li>`).join("") || `<li class="muted">No activity yet.</li>`;
}
function skeleton() { const s = '<li class="skeleton" aria-hidden="true"></li>'.repeat(2); for (const id of ["items", "contacts", "requests"]) $(id).innerHTML = s; }
async function refresh() {
  const [items, contacts, requests, grants, audit, me] = await Promise.all([api("/vault/items"), api("/trusted-contacts"), api("/access-requests"), api("/access-grants"), api("/audit-events"), api("/auth/me")]);
  Object.assign(state, { items, contacts, requests, grants });
  $("identity").textContent = me.email; $("identity").title = me.email;
  $("demo-pill").classList.toggle("hidden", !isDemoEmail(me.email));
  render(); renderAudit(audit);
}

/* Navigation */
function signedIn(on) {
  $("auth").classList.toggle("hidden", on); $("dashboard").classList.toggle("hidden", !on); $("who").classList.toggle("hidden", !on);
}
function showDashboard() { signedIn(true); skeleton(); refresh().catch(e => { if (e.message !== "Session expired") toast(e.message, true); }); }
function signOut(msg) {
  sessionStorage.removeItem("trustedAccessToken"); state.token = null; Object.assign(state, { items: [], contacts: [], requests: [], grants: [] });
  signedIn(false); document.querySelectorAll("form").forEach(f => f.reset()); updateDemoButton(); document.querySelectorAll("dialog[open]").forEach(d => d.close()); if (typeof resetImport === "function") resetImport(); if (msg) toast(msg, true);
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
/* Demo account: random credentials generated in this browser, no shared or built-in login. */
const DEMO_KEY = "trustedAccessDemoLogin";
const isDemoEmail = (e) => /^demo-[0-9a-f]{8}@demo\.example$/.test(e);
const randomHex = (n) => [...crypto.getRandomValues(new Uint8Array(n))].map(b => b.toString(16).padStart(2, "0")).join("");
function savedDemo() {
  try { const c = JSON.parse(localStorage.getItem(DEMO_KEY)); return c && isDemoEmail(c.email) && typeof c.password === "string" ? c : null; } catch { return null; }
}
function updateDemoButton() {
  const has = !!savedDemo();
  $("demo").textContent = has ? "Continue with demo account" : "Try the demo";
  $("demo-hint").textContent = has ? "Signs you back in to the demo account saved in this browser." : "Creates a private demo account with sample data. No email needed.";
}
async function seedDemo() {
  const notes = [
    ["Medical", "Allergies and medication", "Allergic to penicillin.\nDaily: 10mg lisinopril (morning).\nBlood type: O+."],
    ["Insurance", "Health insurance", "Provider: Example Health\nMember ID: DEMO-000-000\nClaims line: 555-0100"],
    ["Pets", "Biscuit's care", "Feed twice daily. Vet: Riverside Animal Clinic, 555-0123."],
  ];
  const ids = [];
  for (const [category, title, text] of notes)
    ids.push((await api("/vault/items", { method: "POST", body: JSON.stringify({ category, title, ciphertext: await encrypt(text) }) })).item_id);
  const people = [["Alex Morgan", "Sister", "alex@example.com"], ["Dr. Priya Shah", "Family doctor", "555-0147"]];
  const contactIds = [];
  for (const [name, relationship, contact_method] of people)
    contactIds.push((await api("/trusted-contacts", { method: "POST", body: JSON.stringify({ name, relationship, contact_method }) })).contact_id);
  await api("/vault/items/" + ids[0] + "/policy", { method: "PUT", body: JSON.stringify({ access_mode: "emergency_only", contact_ids: contactIds, required_approvals: 1 }) });
}
async function startSession(path, creds) {
  const r = await api(path, { method: "POST", body: JSON.stringify(creds) });
  state.token = r.session_token; sessionStorage.setItem("trustedAccessToken", state.token);
}
$("demo").onclick = (e) => busy(e.currentTarget, async () => {
  try {
    let creds = savedDemo();
    if (creds) { try { await startSession("/auth/login", creds); } catch { creds = null; } }
    if (!creds) {
      creds = { email: "demo-" + randomHex(4) + "@demo.example", password: randomHex(16) };
      await startSession("/auth/register", creds);
      try { await seedDemo(); } catch (x) { toast("Demo account created, but sample data failed: " + x.message, true); }
      localStorage.setItem(DEMO_KEY, JSON.stringify(creds));
    }
    toast("Welcome to the demo!"); showDashboard();
  } catch (x) { if (x.message !== "Session expired") toast(x.message, true); }
});
updateDemoButton();
$("logout").onclick = async (e) => {
  // End the session on the server too, so a copied token stops working. Sign out locally even if that fails.
  await busy(e.currentTarget, () => api("/auth/logout", { method: "POST" }).catch(() => {}));
  signOut();
};
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
let policyItem = null, editItem = null, editKeepsText = false;
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
    } else if (d.edit) {
      editItem = state.items.find(i => i.id === d.edit);
      $("e-category").innerHTML = $("v-category").innerHTML; $("e-category").value = editItem.category;
      $("e-title").value = editItem.title; $("edit-error").textContent = "";
      try { $("e-text").value = await decrypt(editItem.ciphertext); editKeepsText = false; $("e-hint").textContent = ""; }
      catch { $("e-text").value = ""; editKeepsText = true; $("e-hint").textContent = "This item can't be decrypted in this browser, so its text can't be shown. Leave the text blank to keep it unchanged."; }
      $("edit-dialog").showModal(); $("e-title").focus();
    } else if (d.delItem) {
      const item = state.items.find(i => i.id === d.delItem);
      if (!await confirmDialog("Delete this item?", "“" + item.title + "” will be permanently deleted, and any access contacts have to it ends immediately.", "Delete", true)) return;
      await busy(b, () => api("/vault/items/" + d.delItem, { method: "DELETE" })); toast("Item deleted."); await refresh();
    } else if (d.delContact) {
      if (!await confirmDialog("Remove " + d.name + "?", "Their invite stops working and any access they have ends immediately. Their past activity stays in your log.", "Remove contact", true)) return;
      await busy(b, () => api("/trusted-contacts/" + d.delContact, { method: "DELETE" })); toast("Contact removed."); await refresh();
    } else if (d.revoke) {
      if (!await confirmDialog("Revoke access?", d.name + " will immediately lose access to “" + d.item + "”. This can't be undone, but they can request access again.", "Revoke access", true)) return;
      await busy(b, () => api("/access-grants/" + d.revoke + "/revoke", { method: "POST" })); toast("Access revoked."); await refresh();
    } else if (d.reject) {
      if (!await confirmDialog("Reject this request?", "The contact will not get access.", "Reject", true)) return;
      await busy(b, () => api("/access-requests/" + d.reject + "/reject", { method: "POST" })); toast("Request rejected."); await refresh();
    }
  } catch (x) { if (x.message !== "Session expired") toast(x.message, true); }
});
$("edit-cancel").onclick = () => $("edit-dialog").close();
$("edit-form").onsubmit = async (e) => {
  e.preventDefault(); const title = $("e-title").value.trim(), text = $("e-text").value, err = $("edit-error");
  if (!title) return void (err.textContent = "Add a title.");
  if (!editKeepsText && !text.trim()) return void (err.textContent = "The text can't be empty.");
  try {
    await busy(e.submitter, async () => api("/vault/items/" + editItem.id, { method: "PUT", body: JSON.stringify({ category: $("e-category").value, title, ciphertext: text.trim() ? await encrypt(text) : editItem.ciphertext }) }));
    $("edit-dialog").close(); toast("Item updated."); await refresh();
  } catch (x) { if (x.message === "Session expired") $("edit-dialog").close(); else err.textContent = x.message; }
};
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
  catch {
    const range = document.createRange(); range.selectNodeContents($("token-value"));
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(range);
    toast("Couldn't copy automatically. The token is selected: press Ctrl/Cmd+C.", true);
  }
};
/* Backup encryption: the whole payload is encrypted in this browser with a passphrase the server never sees. */
const BACKUP_AAD = new TextEncoder().encode("trusted-access-backup:2");
const KDF = { iterations: 600000, min: 100000, max: 2000000 };
const randomBytes = (n) => crypto.getRandomValues(new Uint8Array(n));
async function backupKey(pass, salt, iterations, usage) {
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pass.normalize("NFKC")), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt, iterations }, base, { name: "AES-GCM", length: 256 }, false, [usage]);
}
async function encryptBackup(payload, pass) {
  const salt = randomBytes(16), iv = randomBytes(12);
  const key = await backupKey(pass, salt, KDF.iterations, "encrypt");
  const data = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: BACKUP_AAD }, key, new TextEncoder().encode(JSON.stringify(payload)));
  return { format_version: 2, app: "trusted-access", encryption: "AES-256-GCM", kdf: "PBKDF2-SHA256", iterations: KDF.iterations, salt: b64(salt), iv: b64(iv), ciphertext: b64(new Uint8Array(data)) };
}
async function decryptBackup(file, pass) {
  try {
    const key = await backupKey(pass, unb64(file.salt), file.iterations, "decrypt");
    const data = await crypto.subtle.decrypt({ name: "AES-GCM", iv: unb64(file.iv), additionalData: BACKUP_AAD }, key, unb64(file.ciphertext));
    return JSON.parse(new TextDecoder().decode(data));
  } catch { throw new Error("Couldn't unlock this backup. The passphrase is wrong, or the file was changed."); }
}
$("export").onclick = () => { $("export-error").textContent = ""; $("export-dialog").showModal(); $("ex-pass").focus(); };
$("export-cancel").onclick = () => $("export-dialog").close();
$("export-dialog").addEventListener("close", () => $("export-form").reset());
$("export-form").onsubmit = async (e) => {
  e.preventDefault(); const pass = $("ex-pass").value, err = $("export-error");
  if (pass.length < 12) return void (err.textContent = "Use at least 12 characters.");
  if (pass !== $("ex-pass2").value) return void (err.textContent = "The passphrases don't match.");
  err.textContent = "";
  try {
    const file = await busy(e.submitter, async () => {
      const data = await api("/backup/export"), inner = JSON.parse(data.encrypted_payload);
      return encryptBackup({ exported_at: new Date().toISOString(), vault_items: inner.vault_items, trusted_contacts: inner.trusted_contacts }, pass);
    });
    const url = URL.createObjectURL(new Blob([JSON.stringify(file)], { type: "application/json" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: "trusted-access-backup-" + new Date().toISOString().slice(0, 10) + ".json" });
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    $("export-dialog").close(); toast("Encrypted backup downloaded. Keep the passphrase somewhere safe."); refresh().catch(() => {});
  } catch (x) { if (x.message === "Session expired") $("export-dialog").close(); else err.textContent = x.message; }
};

/* Backup import: the file is untrusted input. Validate it here, then restore through the normal create APIs. */
const IMPORT_MAX = { bytes: 10000000, items: 500, contacts: 200 };
let pendingImport = null, lockedBackup = null;
const okStr = (v, max) => typeof v === "string" && v.trim().length > 0 && v.length <= max;
const NOT_BACKUP = "This doesn't look like a Trusted Access backup.";
function parseBackupFile(text) {
  let file; try { file = JSON.parse(text); } catch { throw new Error("That file isn't valid JSON. Choose a Trusted Access backup (.json)."); }
  if (!file || typeof file !== "object" || Array.isArray(file)) throw new Error(NOT_BACKUP);
  if (file.format_version === 2) {
    const b64ok = (v, min, max) => typeof v === "string" && v.length >= min && v.length <= max && /^[A-Za-z0-9+/]+={0,2}$/.test(v);
    if (file.app !== "trusted-access" || file.encryption !== "AES-256-GCM" || file.kdf !== "PBKDF2-SHA256" || !Number.isInteger(file.iterations)
      || file.iterations < KDF.min || file.iterations > KDF.max || !b64ok(file.salt, 16, 64) || !b64ok(file.iv, 16, 24) || !b64ok(file.ciphertext, 24, IMPORT_MAX.bytes))
      throw new Error("The backup header is invalid or damaged.");
    return { locked: true, file, notice: file.ciphertext };
  }
  if (file.format_version === 1 && typeof file.encrypted_payload === "string") {
    let payload; try { payload = JSON.parse(file.encrypted_payload); } catch { payload = null; }
    return { payload, legacy: true, notice: file.encrypted_payload };
  }
  throw new Error(NOT_BACKUP + " (unsupported format version).");
}
function planImport(payload) {
  if (!payload || typeof payload !== "object" || !Array.isArray(payload.vault_items) || !Array.isArray(payload.trusted_contacts))
    throw new Error("The backup contents can't be read. The file may be damaged or from a different version.");
  if (payload.vault_items.length > IMPORT_MAX.items || payload.trusted_contacts.length > IMPORT_MAX.contacts)
    throw new Error("This backup is larger than this prototype can import at once.");
  const key = (...parts) => JSON.stringify(parts);
  const haveItems = new Set(state.items.map(i => key(i.category, i.title, i.ciphertext)));
  const haveContacts = new Set(state.contacts.map(c => key(c.name, c.relationship, c.contact_method)));
  const out = { items: [], contacts: [], invalid: 0, duplicates: 0 };
  for (const i of payload.vault_items) {
    if (!i || !okStr(i.category, 64) || !okStr(i.title, 200) || !okStr(i.ciphertext, 2000000)) { out.invalid++; continue; }
    const k = key(i.category, i.title, i.ciphertext);
    if (haveItems.has(k)) { out.duplicates++; continue; }
    haveItems.add(k); out.items.push({ category: i.category, title: i.title, ciphertext: i.ciphertext });
  }
  for (const c of payload.trusted_contacts) {
    if (!c || !okStr(c.name, 200) || !okStr(c.relationship, 100) || !okStr(c.contact_method, 320)) { out.invalid++; continue; }
    const k = key(c.name, c.relationship, c.contact_method);
    if (haveContacts.has(k)) { out.duplicates++; continue; }
    haveContacts.add(k); out.contacts.push({ name: c.name, relationship: c.relationship, contact_method: c.contact_method });
  }
  return out;
}
const plural = (n, one, many) => n + " " + (n === 1 ? one : many);
function resetImport() {
  pendingImport = null; lockedBackup = null; $("import-file").value = ""; $("import-pass").value = "";
  $("import-error").textContent = ""; $("import-preview").classList.add("hidden"); $("import-unlock").classList.add("hidden");
}
function renderImportPreview(p) {
  const total = p.items.length + p.contacts.length;
  $("import-summary").innerHTML = total
    ? `Ready to add <strong>${esc(plural(p.items.length, "vault item", "vault items"))}</strong> and <strong>${esc(plural(p.contacts.length, "contact", "contacts"))}</strong>.`
    : "Nothing new to import. Everything in this file is already in your account.";
  const notes = [];
  if (p.legacy) notes.push("This is an older backup that isn't encrypted. Delete it once you've restored from it.");
  if (p.duplicates) notes.push(plural(p.duplicates, "record is", "records are") + " already here and will be skipped.");
  if (p.invalid) notes.push(plural(p.invalid, "record is", "records are") + " malformed and will be skipped.");
  notes.push("Sharing rules aren't included in backups, so restored items start private. Items open only in a browser that holds the original encryption key.");
  $("import-notes").textContent = notes.join(" ");
  const more = (n) => n > 5 ? `<li class="muted">…and ${n - 5} more</li>` : "";
  $("import-list").innerHTML =
    p.items.slice(0, 5).map(i => `<li class="item"><div class="main"><div class="title">${esc(i.title)}</div><div class="muted"><span class="pill">${esc(i.category)}</span></div></div></li>`).join("") + more(p.items.length) +
    p.contacts.slice(0, 5).map(c => `<li class="item"><div class="main"><div class="title">${esc(c.name)}</div><div class="muted">${esc(c.relationship)} · ${esc(c.contact_method)}</div></div></li>`).join("") + more(p.contacts.length);
  $("import-go").textContent = total ? "Import " + plural(total, "record", "records") : "Nothing to import";
  $("import-go").disabled = !total;
  $("import-preview").classList.remove("hidden");
}
$("import-file").onchange = async (e) => {
  const file = e.target.files[0]; $("import-error").textContent = ""; $("import-preview").classList.add("hidden"); $("import-unlock").classList.add("hidden"); pendingImport = null; lockedBackup = null; $("import-pass").value = "";
  if (!file) return;
  if (file.size > IMPORT_MAX.bytes) { $("import-error").textContent = "That file is too large to be a backup."; return; }
  try {
    const parsed = parseBackupFile(await file.text());
    if (parsed.locked) { lockedBackup = parsed; $("import-unlock").classList.remove("hidden"); $("import-pass").focus(); }
    else { pendingImport = { ...planImport(parsed.payload), notice: parsed.notice, legacy: true }; renderImportPreview(pendingImport); }
  } catch (x) { $("import-error").textContent = x.message; }
};
async function unlockBackup() {
  if (!lockedBackup) return; const pass = $("import-pass").value, err = $("import-error");
  if (!pass) return void (err.textContent = "Enter the passphrase.");
  err.textContent = "";
  try {
    const payload = await busy($("import-unlock-btn"), () => decryptBackup(lockedBackup.file, pass));
    pendingImport = { ...planImport(payload), notice: lockedBackup.notice };
    $("import-unlock").classList.add("hidden"); $("import-pass").value = ""; lockedBackup = null; renderImportPreview(pendingImport);
  } catch (x) { err.textContent = x.message; $("import-pass").select(); }
}
$("import-unlock-btn").onclick = unlockBackup;
$("import-pass").onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); unlockBackup(); } };
$("import-cancel").onclick = resetImport;
$("import-go").onclick = async (e) => {
  const p = pendingImport; if (!p) return;
  let done = 0; const total = p.items.length + p.contacts.length;
  try {
    await busy(e.currentTarget, async () => {
      await api("/backup/import", { method: "POST", body: JSON.stringify({ format_version: 1, encrypted_payload: p.notice }) });
      for (const i of p.items) { await api("/vault/items", { method: "POST", body: JSON.stringify(i) }); done++; }
      for (const c of p.contacts) { await api("/trusted-contacts", { method: "POST", body: JSON.stringify(c) }); done++; }
    });
    toast("Restored " + plural(done, "record", "records") + ". Restored items are private until you share them.");
  } catch (x) {
    if (x.message !== "Session expired") toast("Imported " + done + " of " + total + " records before an error: " + x.message, true);
  }
  resetImport(); if (state.token) await refresh().catch(() => {});
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
