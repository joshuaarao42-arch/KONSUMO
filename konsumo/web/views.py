from html import escape as esc

STYLE = r'''
:root{--ink:#172033;--muted:#718096;--line:#e5eaf2;--bg:#f5f7fb;--blue:#356ae6;--teal:#12a594;--orange:#f59e0b;--red:#e05252}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}a{text-decoration:none;color:inherit}.shell{display:flex;min-height:100vh}.side{width:235px;background:#101a2e;color:#b9c6db;padding:26px 15px;position:fixed;inset:0 auto 0 0}.brand{display:flex;gap:10px;align-items:center;color:#fff;font-size:22px;font-weight:800;padding:0 12px 34px}.mark{display:grid;place-items:center;width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#55d6be,#4178ee)}.nav-title{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#73819c;padding:0 12px 10px}.nav a{display:flex;gap:12px;padding:11px 12px;border-radius:9px;margin:3px 0;color:#aebbd1}.nav a:hover,.nav a.active{background:#1d2c49;color:#fff}.main{margin-left:235px;width:calc(100% - 235px);padding:34px 42px}.top{display:flex;justify-content:space-between;gap:18px;margin-bottom:28px}.eyebrow{font-size:12px;color:var(--blue);font-weight:800;text-transform:uppercase;letter-spacing:1px}.title{font-size:32px;line-height:1.15;margin:6px 0}.subtitle,.label{color:var(--muted)}.btn{display:inline-flex;align-items:center;border:1px solid var(--line);background:#fff;border-radius:9px;padding:10px 15px;font-weight:700}.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue)}.grid{display:grid;gap:18px}.stats{grid-template-columns:repeat(4,1fr);margin-bottom:22px}.card{background:#fff;border:1px solid var(--line);border-radius:15px;padding:21px;box-shadow:0 10px 30px #1f304f12}.stat{display:flex;justify-content:space-between}.value{font-size:28px;font-weight:800;margin-top:8px}.icon{width:39px;height:39px;border-radius:11px;display:grid;place-items:center;background:#edf3ff;color:var(--blue);font-weight:800}.two{grid-template-columns:1.4fr .8fr}.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.head h2{font-size:17px;margin:0}.metric{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--line)}.metric:last-child{border:0}.list{list-style:none;padding:0;margin:0}.list li{padding:13px 0;border-bottom:1px solid var(--line)}table{width:100%;border-collapse:collapse}th{text-align:left;color:var(--muted);font-size:12px;text-transform:uppercase;padding:12px 10px;border-bottom:1px solid var(--line)}td{padding:14px 10px;border-bottom:1px solid var(--line)}.pill{padding:4px 8px;border-radius:99px;font-size:12px;font-weight:700;background:#eef3ff;color:var(--blue)}.empty{text-align:center;color:var(--muted);padding:35px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.field{display:flex;flex-direction:column;gap:6px}.full{grid-column:1/-1}.field label{font-weight:700;font-size:13px}.field input,.field select{border:1px solid #dbe2ed;border-radius:8px;padding:11px;font:inherit}.actions{display:flex;gap:10px;margin-top:18px}.footer{color:var(--muted);font-size:12px;margin-top:30px}@media(max-width:850px){.side{width:68px}.brand{font-size:0;padding:0 10px 30px}.nav-title,.nav span{display:none}.nav a{justify-content:center}.main{margin-left:68px;width:calc(100% - 68px);padding:24px}.stats{grid-template-columns:1fr 1fr}.two{grid-template-columns:1fr}}@media(max-width:600px){.main{padding:18px 12px}.top{display:block}.top .btn{margin-top:15px}.stats{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.full{grid-column:auto}}
'''

def _nav(active):
    items=[('/', '⌂', 'Dashboard'),('/records','▤','Records'),('/analytics','◫','Analytics'),('/forecast','◌','Forecast'),('/anomalies','△','Anomalies'),('/recommendations','✦','Recommendations')]
    return ''.join(f'<a class="{"active" if active==url else ""}" href="{url}"><b>{icon}</b><span>{label}</span></a>' for url,icon,label in items)

def page(title, body, version, active='/'):
    logo='<svg class="logo" viewBox="0 0 40 40" aria-label="Konsumo logo"><path d="M20 3C15 10 8 16 8 24a12 12 0 0 0 24 0C32 16 25 10 20 3Z" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="m22 11-7 12h6l-3 10 8-14h-6l2-8Z" fill="#55d6be" stroke="#55d6be" stroke-linejoin="round"/></svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Konsumo</title><style>{STYLE}.logo{{width:32px;height:32px;color:#fff}}</style></head><body><div class="shell"><aside class="side"><a class="brand" href="/">{logo}Konsumo</a><div class="nav-title">Workspace</div><nav class="nav">{_nav(active)}</nav></aside><main class="main">{body}<div class="footer">Konsumo {esc(version)} · Household utility insights</div></main></div></body></html>'

def _top(label,title,sub,button=''):
    return f'<div class="top"><div><div class="eyebrow">{esc(label)}</div><h1 class="title">{esc(title)}</h1><p class="subtitle">{esc(sub)}</p></div>{button}</div>'

def dashboard_page(cards, forecasts, anom, currency, version):
    total=sum(c['stats'].get('total',0) for c in cards); avg=sum(c['stats'].get('average',0) for c in cards)
    stats=f'<section class="grid stats"><div class="card stat"><div><div class="label">Total tracked usage</div><div class="value">{total:.1f}</div><span class="label">combined units</span></div><i class="icon">∑</i></div><div class="card stat"><div><div class="label">Daily average</div><div class="value">{avg:.1f}</div><span class="label">across resources</span></div><i class="icon">↗</i></div><div class="card stat"><div><div class="label">Resources tracked</div><div class="value">{len(cards)}</div><span class="label">electricity & water</span></div><i class="icon">◈</i></div><div class="card stat"><div><div class="label">Attention needed</div><div class="value">{anom}</div><span class="label">unusual readings</span></div><i class="icon">!</i></div></section>'
    resources=''.join(f'<div class="card"><div class="head"><h2>{esc(c["resource"].title())}</h2><span class="pill">{c["stats"].get("count",0)} days</span></div><div class="metric"><span>Total usage</span><b>{c["stats"].get("total",0):.2f}</b></div><div class="metric"><span>Daily average</span><b>{c["stats"].get("average",0):.2f}</b></div><div class="metric"><span>Peak day</span><b>{c["stats"].get("maximum",0):.2f}</b></div></div>' for c in cards)
    body=_top('Overview','Good to see you','A clear view of your household consumption.','<a class="btn primary" href="/records/new">＋ Add reading</a>')+stats+f'<section class="grid two"><div class="card"><div class="head"><h2>Resource overview</h2><span class="label">Current history</span></div><div class="grid" style="grid-template-columns:1fr 1fr">{resources}</div></div><div class="card"><div class="head"><h2>Quick actions</h2></div><ul class="list"><li><a href="/records/new">＋ Record a new meter reading</a></li><li><a href="/forecast">◌ View your 30-day forecast</a></li><li><a href="/anomalies">△ Review unusual usage</a></li><li><a href="/recommendations">✦ Get saving recommendations</a></li></ul></div></section>'
    return page('Dashboard',body,version,'/')

def records_page(rows,resource,query,page_no,limit,currency,version):
    row_html=''.join(f'<tr><td>{esc(str(r["recorded_at"])[:16])}</td><td><span class="pill">{esc(r["resource"])}</span></td><td><b>{r["amount"]:.2f}</b></td><td>{currency} {r["cost"]:.2f}</td><td><a class="btn" href="/records/{r["id"]}/edit">Edit</a></td></tr>' for r in rows) or '<tr><td colspan="5"><div class="empty">No readings yet. Add your first one above.</div></td></tr>'
    body=_top('Data','Meter readings','Review and manage your consumption history.','<a class="btn primary" href="/records/new">＋ Add reading</a>')+f'<div class="card"><table><thead><tr><th>Date</th><th>Resource</th><th>Amount</th><th>Cost</th><th></th></tr></thead><tbody>{row_html}</tbody></table></div>'
    return page('Records',body,version,'/records')

def record_form_page(record,currency,version):
    rid=record['id'] if record else None; action=f'/records/{rid}/edit' if rid else '/records/new'; title='Edit reading' if rid else 'Add a reading'; r=record or {}
    sel=lambda x:'selected' if r.get('resource','electricity')==x else ''
    body=_top('Data entry',title,'Keep your usage history accurate and up to date.')+f'<div class="card"><form method="post" action="{action}"><div class="form-grid"><div class="field"><label>Resource</label><select name="resource"><option value="electricity" {sel("electricity")}>Electricity · kWh</option><option value="water" {sel("water")}>Water · m³</option></select></div><div class="field"><label>Date and time</label><input name="recorded_at" type="datetime-local" required value="{esc(str(r.get("recorded_at",""))[:16].replace(" ","T"))}"></div><div class="field"><label>Amount</label><input name="amount" type="number" step=".001" min=".001" required value="{esc(str(r.get("amount","")))}"><span class="label">Enter meter usage for this period.</span></div><div class="field"><label>Cost override <span class="label">({esc(currency)}, optional)</span></label><input name="cost" type="number" step=".01" min="0" value="{esc(str(r.get("cost","")) if r.get("cost") is not None else "")}"></div><div class="field full"><label>Notes <span class="label">(optional)</span></label><input name="notes" value="{esc(str(r.get("notes","")))}" placeholder="e.g. guests, appliance repair"></div></div><div class="actions"><button class="btn primary" type="submit">Save reading</button><a class="btn" href="/records">Cancel</a></div></form></div>'
    return page(title,body,version,'/records')

def analytics_page(currency,version):
    chart = '''<div class="card"><div class="head"><h2>{name}</h2><span class="label">Daily usage · last 60 days</span></div><div style="height:280px"><canvas id="{id}" style="width:100%;height:100%"></canvas></div><p id="{id}-status" class="label">Loading usage data…</p></div>'''
    script = '''<script>
function drawUsage(id, resource) {
  fetch('/api/daily/' + resource).then(r => r.json()).then(rows => {
    const canvas = document.getElementById(id), box = canvas.parentElement;
    const data = rows.slice(-60), ctx = canvas.getContext('2d');
    const w = box.clientWidth, h = 250, dpr = window.devicePixelRatio || 1;
    canvas.width = w*dpr; canvas.height = h*dpr; ctx.scale(dpr,dpr);
    ctx.clearRect(0,0,w,h);
    if (!data.length) return;
    const max = Math.max(...data.map(x => x.value), 1), gap = 3;
    const barW = Math.max(2, (w-gap*(data.length-1))/data.length);
    data.forEach((item,i) => {
      const bh = Math.max(2, item.value/max*(h-24));
      const x = i*(barW+gap), y = h-bh-10;
      const g = ctx.createLinearGradient(0,y,0,h); g.addColorStop(0,'#6b92f0'); g.addColorStop(1,'#356ae6');
      ctx.fillStyle=g; ctx.beginPath(); ctx.roundRect(x,y,barW,bh,4); ctx.fill();
    });
    document.getElementById(id+'-status').textContent =
      data.length + ' readings · peak ' + max.toFixed(2) + ' units';
  }).catch(() => document.getElementById(id+'-status').textContent='Unable to load usage data.');
}
drawUsage('electricity-chart','electricity'); drawUsage('water-chart','water');
</script>'''
    body=_top('Insights','Analytics','Explore daily usage and compare your resources.')+'<div class="grid two">'+chart.format(name='Electricity',id='electricity-chart')+chart.format(name='Water',id='water-chart')+'</div>'+script
    return page('Analytics',body,version,'/analytics')
def forecast_page(fcs,currency,version,message=None):
    if message:
        content=f'<div class="card"><div class="empty"><h2>Forecast needs more history</h2><p>{esc(message)}</p><a class="btn primary" href="/records/new">＋ Add a reading</a></div></div>'
    else:
        content='<div class="grid two">'+''.join(f'<div class="card"><div class="head"><h2>{esc(r.title())}</h2><span class="label">Next 30 days</span></div><div class="metric"><span>Forecast average</span><b>{float(v.mean()):.2f}</b></div><div class="metric"><span>Forecast total</span><b>{float(v.sum()):.2f}</b></div></div>' for r,v in fcs.items())+'</div>'
    return page('Forecast',_top('Planning','30-day forecast','A forward-looking estimate based on recent usage.')+content,version,'/forecast')
def anomalies_page(data,currency,version): return page('Anomalies',_top('Attention','Unusual usage','Readings that may be worth investigating.')+'<div class="grid two">'+''.join(f'<div class="card"><div class="head"><h2>{esc(r.title())}</h2></div>'+(''.join(f'<div class="metric"><span>{esc(x["date"])}</span><b>{x["amount"]:.2f} · z {x["z_score"]}</b></div>' for x in values) if values else '<div class="empty">No unusual readings found.</div>')+'</div>' for r,values in data.items())+'</div>',version,'/anomalies')
def recommendations_page(tips,currency,version): return page('Recommendations',_top('Guidance','Ways to save','Small changes can make a measurable difference.')+'<div class="card"><ul class="list">'+''.join(f'<li>✦ &nbsp;{esc(t)}</li>' for t in tips)+'</ul></div>',version,'/recommendations')


def auth_page(mode, error=None):
    signup = mode == "signup"
    heading = "Create your account" if signup else "Welcome back"
    subtitle = "Start making sense of your household utility use." if signup else "Sign in to continue to your household dashboard."
    name_field = '<div class="field"><label for="name">Full name</label><input id="name" name="name" type="text" autocomplete="name" maxlength="80" placeholder="Your name" required></div>' if signup else ""
    action = "/signup" if signup else "/login"
    alternate = 'Already have an account? <a href="/login">Log in</a>' if signup else 'New to Konsumo? <a href="/signup">Create an account</a>'
    error_html = f'<div class="auth-error" role="alert">{esc(error)}</div>' if error else ""
    password_hint = '<span class="hint">Use at least 8 characters.</span>' if signup else ""
    autocomplete = "new-password" if signup else "current-password"
    placeholder = "At least 8 characters" if signup else "Enter your password"
    button = "Create account" if signup else "Log in"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{heading} · Konsumo</title><style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;background:#f4f7fb;color:#172033;font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;display:grid;place-items:center;padding:24px}}
.auth-wrap{{width:min(100%,440px)}}.auth-brand{{display:flex;align-items:center;justify-content:center;gap:10px;font-size:25px;font-weight:850;margin-bottom:24px}}.mark{{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#55d6be,#4178ee);display:grid;place-items:center;color:white;font-size:21px}}
.auth-card{{background:#fff;border:1px solid #e5eaf2;border-radius:20px;padding:34px;box-shadow:0 20px 60px #1f304f12}}h1{{font-size:27px;letter-spacing:-.7px;margin:0 0 5px}}.sub{{color:#718096;margin:0 0 25px}}.field{{display:flex;flex-direction:column;gap:7px;margin:15px 0}}label{{font-weight:700;font-size:13px}}input{{width:100%;border:1px solid #dbe2ed;border-radius:10px;padding:12px 13px;font:inherit;outline:none}}input:focus{{border-color:#356ae6;box-shadow:0 0 0 3px #356ae61a}}.submit{{width:100%;border:0;border-radius:10px;background:#356ae6;color:white;padding:13px;font:700 15px system-ui;cursor:pointer;margin-top:10px}}.submit:hover{{background:#2858c9}}.switch{{text-align:center;color:#718096;margin:22px 0 0;font-size:14px}}a{{color:#356ae6;font-weight:700;text-decoration:none}}.auth-error{{background:#fff0f0;border:1px solid #ffd3d3;color:#b42318;padding:11px 13px;border-radius:9px;margin-bottom:16px;font-size:14px}}.hint{{font-size:12px;color:#718096}}@media(max-width:480px){{.auth-card{{padding:25px 20px}}}}
</style></head><body><main class="auth-wrap">
<div class="auth-brand"><span class="mark">⌁</span>Konsumo</div><section class="auth-card">
<h1>{heading}</h1><p class="sub">{subtitle}</p>{error_html}
<form method="post" action="{action}">{name_field}
<div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" placeholder="you@example.com" required></div>
<div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="{autocomplete}" minlength="8" maxlength="128" placeholder="{placeholder}" required>{password_hint}</div>
<button class="submit" type="submit">{button}</button></form><p class="switch">{alternate}</p>
</section></main></body></html>'''
