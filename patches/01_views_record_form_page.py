"""PATCH 1 - replace the whole `record_form_page` function in konsumo/web/views.py
with this version (fixes the f-string brace bug in the embedded JavaScript)."""


def record_form_page(record, currency, version):
    rid = record["id"] if record else None
    title = f"Edit record #{rid}" if record else "New consumption record"
    res = record["resource"] if record else "electricity"
    dt = (str(record["recorded_at"])[:16].replace(" ", "T")) if record else ""
    amount = record["amount"] if record else ""
    cost = (record["cost"] if record and record["cost"] is not None else "")
    notes = record["notes"] if record else ""
    sel = lambda v: "selected" if res == v else ""  # noqa: E731
    return page(title, f"""<h1>{esc(title)}</h1>
<form method="post" class="form card">
  <label>Resource
    <select name="resource" required>
      <option value="electricity" {sel('electricity')}>Electricity (kWh)</option>
      <option value="water" {sel('water')}>Water (m³)</option>
    </select></label>
  <label>Date <input type="datetime-local" name="recorded_at" required
                     value="{esc(dt)}"></label>
  <label>Amount <input type="number" name="amount" step="0.001" min="0.001" required
                       value="{esc(amount)}" placeholder="e.g. 9.42"></label>
  <label>Cost override ({esc(currency)}, optional)
    <input type="number" name="cost" step="0.01" min="0" value="{esc(cost)}"
           placeholder="auto from tariff if blank"></label>
  <label>Notes <input type="text" name="notes" value="{esc(notes)}"
                      placeholder="e.g. meter reading, anomaly cause…"></label>
  <div class="row">
    <button class="btn primary" type="submit">Save</button>
    <a class="btn" href="/records">Cancel</a></div>
</form>
<p class="muted small" id="quote"></p>
<script>
document.querySelector('form').addEventListener('change', async () => {{
  const resource = document.querySelector('[name=resource]').value;
  const amount = parseFloat(document.querySelector('[name=amount]').value);
  if (!amount || amount <= 0) return;
  const r = await fetch('/api/quote', {{ method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{resource: resource, amount: amount}}) }});
  const j = await r.json();
  document.getElementById('quote').textContent =
    'Auto-computed cost at current tariff: {esc(currency)} ' + (j.cost ?? j.error);
}});
</script>""", version)
