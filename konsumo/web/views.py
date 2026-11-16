from html import escape as esc

STYLE = r'''
:root{--ink:#172033;--muted:#718096;--line:#e5eaf2;--bg:#f5f7fb;--blue:#356ae6;--teal:#12a594;--orange:#f59e0b;--red:#e05252}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}a{text-decoration:none;color:inherit}.shell{display:flex;min-height:100vh}.side{width:235px;background:#101a2e;color:#b9c6db;padding:26px 15px;position:fixed;inset:0 auto 0 0}.brand{display:flex;gap:10px;align-items:center;color:#fff;font-size:22px;font-weight:800;padding:0 12px 34px}.mark{display:grid;place-items:center;width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#55d6be,#4178ee)}.nav-title{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#73819c;padding:0 12px 10px}.nav a{display:flex;gap:12px;padding:11px 12px;border-radius:9px;margin:3px 0;color:#aebbd1}.nav a:hover,.nav a.active{background:#1d2c49;color:#fff}.main{margin-left:235px;width:calc(100% - 235px);padding:34px 42px}.top{display:flex;justify-content:space-between;gap:18px;margin-bottom:28px}.eyebrow{font-size:12px;color:var(--blue);font-weight:800;text-transform:uppercase;letter-spacing:1px}.title{font-size:32px;line-height:1.15;margin:6px 0}.subtitle,.label{color:var(--muted)}.btn{display:inline-flex;align-items:center;border:1px solid var(--line);background:#fff;border-radius:9px;padding:10px 15px;font-weight:700}.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue)}.grid{display:grid;gap:18px}.stats{grid-template-columns:repeat(4,1fr);margin-bottom:22px}.card{background:#fff;border:1px solid var(--line);border-radius:15px;padding:21px;box-shadow:0 10px 30px #1f304f12}.stat{display:flex;justify-content:space-between}.value{font-size:28px;font-weight:800;margin-top:8px}.icon{width:39px;height:39px;border-radius:11px;display:grid;place-items:center;background:#edf3ff;color:var(--blue);font-weight:800}.two{grid-template-columns:1.4fr .8fr}.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.head h2{font-size:17px;margin:0}.metric{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--line)}.metric:last-child{border:0}.list{list-style:none;padding:0;margin:0}.list li{padding:13px 0;border-bottom:1px solid var(--line)}table{width:100%;border-collapse:collapse}th{text-align:left;color:var(--muted);font-size:12px;text-transform:uppercase;padding:12px 10px;border-bottom:1px solid var(--line)}td{padding:14px 10px;border-bottom:1px solid var(--line)}.pill{padding:4px 8px;border-radius:99px;font-size:12px;font-weight:700;background:#eef3ff;color:var(--blue)}.empty{text-align:center;color:var(--muted);padding:35px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.field{display:flex;flex-direction:column;gap:6px}.full{grid-column:1/-1}.field label{font-weight:700;font-size:13px}.field input,.field select{border:1px solid #dbe2ed;border-radius:8px;padding:11px;font:inherit}.actions{display:flex;gap:10px;margin-top:18px}.footer{color:var(--muted);font-size:12px;margin-top:30px}@media(max-width:850px){.side{width:68px}.brand{font-size:0;padding:0 10px 30px}.nav-title,.nav span{display:none}.nav a{justify-content:center}.main{margin-left:68px;width:calc(100% - 68px);padding:24px}.stats{grid-template-columns:1fr 1fr}.two{grid-template-columns:1fr}}@media(max-width:600px){.main{padding:18px 12px}.top{display:block}.top .btn{margin-top:15px}.stats{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.full{grid-column:auto}}

.analytics-stack{display:grid;gap:22px}.analytics-card{position:relative;overflow:hidden;background:linear-gradient(145deg,#fff 0%,#f7faff 100%);border:1px solid #dfe7f3;border-radius:20px;padding:24px;box-shadow:0 18px 45px #1f304f10}.analytics-card:before{content:"";position:absolute;inset:0 0 auto;height:4px;background:linear-gradient(90deg,#55d6be,#356ae6,#8aaeff)}.analytics-card-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.analytics-card-head h2{font-size:23px;letter-spacing:-.5px;margin:3px 0}.analytics-card-head p{color:var(--muted);margin:0;font-size:13px}.chart-kicker{font-size:10px;letter-spacing:1.4px;font-weight:850;color:#356ae6}.chart-unit{background:#edf3ff;color:#2858c9;border:1px solid #d8e5ff;border-radius:999px;padding:7px 12px;font-size:12px;font-weight:800}.chart-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0 16px}.chart-stats>div{background:#fff;border:1px solid #e6edf7;border-radius:12px;padding:12px 15px;min-width:0}.chart-stats span{display:block;color:var(--muted);font-size:11px;font-weight:700}.chart-stats b{display:block;font-size:20px;margin-top:4px;letter-spacing:-.3px}.chart-stats small{font-size:11px;color:var(--muted);font-weight:600}.chart-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:6px 0 0}.range-switch{display:flex;gap:5px;background:#edf2f9;padding:4px;border-radius:10px}.range-switch button{border:0;background:transparent;color:#64748b;border-radius:7px;padding:7px 12px;font:750 11px system-ui;cursor:pointer}.range-switch button.selected{background:#fff;color:#2858c9;box-shadow:0 2px 7px #20395b18}.chart-caption{font-size:11px;color:var(--muted);text-align:right}.chart-stage{position:relative;margin-top:12px;min-height:260px;border-radius:16px;background:radial-gradient(ellipse at 50% 0%,#eaf2ff 0%,#f8fbff 55%,#f2f6fc 100%);overflow:hidden}.chart-glow{position:absolute;width:55%;height:70%;left:23%;top:12%;background:#8fb4ff24;filter:blur(45px);pointer-events:none}.chart-stage svg{position:relative;display:block;width:100%;height:auto;min-height:260px;z-index:1}.usage-column{cursor:crosshair;outline:none}.usage-column:focus rect{stroke:#172f70;stroke-width:2}.chart-empty{position:absolute;inset:0;display:grid;place-items:center;color:var(--muted);font-size:13px}.chart-empty[hidden]{display:none}.chart-foot{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:11px;margin-top:12px}.chart-foot>span:first-child{display:flex;align-items:center;gap:7px}.legend-dot{width:9px;height:9px;border-radius:3px;background:linear-gradient(135deg,#78a7ff,#244eb5);display:inline-block}@media(max-width:600px){.analytics-card{padding:16px}.chart-stats{gap:6px}.chart-stats>div{padding:9px}.chart-stats b{font-size:16px}.chart-toolbar{align-items:flex-start;flex-direction:column}.chart-caption{text-align:left}.chart-stage svg{min-height:190px}}

'''

def _nav(active):
    items=[('/', '⌂', 'Dashboard'),('/records','▤','Records'),('/analytics','◫','Analytics'),('/forecast','◌','Forecast'),('/anomalies','△','Anomalies'),('/recommendations','✦','Recommendations')]
    return ''.join(f'<a class="{"active" if active==url else ""}" href="{url}"><b>{icon}</b><span>{label}</span></a>' for url,icon,label in items)

def page(title, body, version, active='/'):
    logo='<svg class="logo" viewBox="0 0 40 40" aria-label="Konsumo logo"><path d="M20 3C15 10 8 16 8 24a12 12 0 0 0 24 0C32 16 25 10 20 3Z" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="m22 11-7 12h6l-3 10 8-14h-6l2-8Z" fill="#55d6be" stroke="#55d6be" stroke-linejoin="round"/></svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Konsumo</title><style>{STYLE}{CHAT_STYLE}.logo{{width:32px;height:32px;color:#fff}}.account-bar{{display:flex;justify-content:flex-end;margin-bottom:14px}}.account-bar button{{border:1px solid var(--line);background:#fff;border-radius:8px;padding:8px 13px;font:700 13px system-ui;cursor:pointer;color:var(--ink)}}</style></head><body><div class="shell"><aside class="side"><a class="brand" href="/">{logo}Konsumo</a><div class="nav-title">Workspace</div><nav class="nav">{_nav(active)}</nav></aside><main class="main"><div class="account-bar"><form method="post" action="/logout"><button type="submit">Log out</button></form></div>{body}<div class="footer">Konsumo {esc(version)} · Household utility insights</div></main></div>{CHAT_WIDGET}{CHAT_SCRIPT}</body></html>'

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
    chart = '''<section class="analytics-card">
      <div class="analytics-card-head"><div><span class="chart-kicker">RESOURCE PERFORMANCE</span><h2>{name}</h2><p>Daily consumption with depth, scale and exact reading details.</p></div><span class="chart-unit">{unit}</span></div>
      <div class="chart-stats" id="{id}-stats"><div><span>Total usage</span><b>—</b></div><div><span>Daily average</span><b>—</b></div><div><span>Peak day</span><b>—</b></div></div>
      <div class="chart-toolbar"><div class="range-switch" role="group" aria-label="Chart date range"><button type="button" data-range="7">7D</button><button type="button" data-range="30">30D</button><button type="button" data-range="60" class="selected">60D</button><button type="button" data-range="90">90D</button></div><span class="chart-caption" id="{id}-caption">Loading readings…</span></div>
      <div class="chart-stage"><div class="chart-glow"></div><svg id="{id}" viewBox="0 0 900 350" role="img" aria-label="{name} usage chart"></svg><div class="chart-empty" id="{id}-empty" hidden>No readings available for this period.</div></div>
      <div class="chart-foot"><span><i class="legend-dot"></i> Recorded usage</span><span>Hover or tap a column for details</span></div>
    </section>'''
    script = r'''<script>
(function(){
 const configs=[{id:'electricity-chart',resource:'electricity',unit:'kWh'},{id:'water-chart',resource:'water',unit:'m³'}];
 const NS='http://www.w3.org/2000/svg';
 function el(tag,attrs,text){const n=document.createElementNS(NS,tag);Object.entries(attrs||{}).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;return n;}
 function fmt(v){return Number(v).toLocaleString(undefined,{maximumFractionDigits:2});}
 function draw(config,rows,range){
   const svg=document.getElementById(config.id),empty=document.getElementById(config.id+'-empty'),caption=document.getElementById(config.id+'-caption'),stats=document.getElementById(config.id+'-stats');
   const data=rows.slice(-range),clean=data.map(x=>({date:x.date,value:Number.isFinite(Number(x.value))?Math.max(0,Number(x.value)):0}));
   svg.replaceChildren();
   if(!clean.length){empty.hidden=false;caption.textContent='No data';stats.innerHTML='<div><span>Total usage</span><b>0</b></div><div><span>Daily average</span><b>0</b></div><div><span>Peak day</span><b>0</b></div>';return;}
   empty.hidden=true;
   const total=clean.reduce((s,x)=>s+x.value,0),peak=Math.max(...clean.map(x=>x.value)),avg=total/clean.length;
   stats.innerHTML='<div><span>Total usage</span><b>'+fmt(total)+' <small>'+config.unit+'</small></b></div><div><span>Daily average</span><b>'+fmt(avg)+' <small>'+config.unit+'</small></b></div><div><span>Peak day</span><b>'+fmt(peak)+' <small>'+config.unit+'</small></b></div>';
   caption.textContent=clean[0].date+' — '+clean[clean.length-1].date+' · '+clean.length+' days';
   const W=900,H=350,left=66,right=30,top=24,bottom=62,plotW=W-left-right,plotH=H-top-bottom,max=Math.max(peak,1)*1.18,steps=4;
   const defs=el('defs');
   const front=el('linearGradient',{id:config.id+'-front',x1:'0',x2:'0',y1:'0',y2:'1'});front.append(el('stop',{offset:'0%','stop-color':'#78a7ff'}));front.append(el('stop',{offset:'100%','stop-color':'#356ae6'}));defs.append(front);
   const side=el('linearGradient',{id:config.id+'-side',x1:'0',x2:'1',y1:'0',y2:'1'});side.append(el('stop',{offset:'0%','stop-color':'#244eb5'}));side.append(el('stop',{offset:'100%','stop-color':'#172f70'}));defs.append(side);
   const topGrad=el('linearGradient',{id:config.id+'-top',x1:'0',x2:'1',y1:'0',y2:'1'});topGrad.append(el('stop',{offset:'0%','stop-color':'#b8d1ff'}));topGrad.append(el('stop',{offset:'100%','stop-color':'#6b95ed'}));defs.append(topGrad);svg.append(defs);
   for(let i=0;i<=steps;i++){const y=top+plotH*i/steps,val=max*(1-i/steps);svg.append(el('line',{x1:left,y1:y,x2:W-right,y2:y,stroke:'#dce5f3','stroke-width':'1','stroke-dasharray':i===steps?'0':'4 7'}));svg.append(el('text',{x:left-14,y:y+5,'text-anchor':'end',fill:'#718096','font-size':'12'},fmt(val)));}
   const slot=plotW/clean.length,barW=Math.max(4,Math.min(24,slot*.58)),depth=Math.min(9,barW*.35);
   clean.forEach((item,i)=>{
     const x=left+i*slot+(slot-barW)/2,barH=Math.max(item.value>0?2:0,item.value/max*plotH),y=top+plotH-barH;
     const g=el('g',{class:'usage-column',tabindex:'0',role:'img','aria-label':item.date+': '+fmt(item.value)+' '+config.unit});
     g.append(el('title',{},item.date+' · '+fmt(item.value)+' '+config.unit));
     if(barH>0){
       g.append(el('polygon',{points:x+','+y+' '+(x+depth)+','+(y-depth)+' '+(x+barW+depth)+','+(y-depth)+' '+(x+barW)+','+y,fill:'url(#'+config.id+'-top)'}));
       g.append(el('polygon',{points:(x+barW)+','+y+' '+(x+barW+depth)+','+(y-depth)+' '+(x+barW+depth)+','+(top+plotH-depth)+' '+(x+barW)+','+(top+plotH),fill:'url(#'+config.id+'-side)'}));
       g.append(el('rect',{x:x,y:y,width:barW,height:barH,rx:Math.min(4,barW/4),fill:'url(#'+config.id+'-front)'}));
     }
     g.append(el('rect',{x:x-slot*.15,y:top,width:slot*.85,height:plotH+12,fill:'transparent'}));svg.append(g);
   });
   const labelCount=Math.min(6,clean.length),seen=new Set();
   for(let i=0;i<labelCount;i++){const idx=Math.round(i*(clean.length-1)/Math.max(1,labelCount-1));if(seen.has(idx))continue;seen.add(idx);const x=left+idx*slot+slot/2;svg.append(el('text',{x:x,y:H-25,'text-anchor':'middle',fill:'#718096','font-size':'12'},clean[idx].date.slice(5)));}
   svg.append(el('text',{x:left,y:14,fill:'#718096','font-size':'11','font-weight':'700'},config.unit.toUpperCase()));
 }
 configs.forEach(config=>{
   const card=document.getElementById(config.id).closest('.analytics-card');
   fetch('/api/daily/'+config.resource).then(r=>{if(!r.ok)throw new Error('Request failed');return r.json();}).then(rows=>{
     draw(config,rows,60);
     card.querySelectorAll('[data-range]').forEach(button=>button.addEventListener('click',()=>{
       card.querySelectorAll('[data-range]').forEach(b=>b.classList.toggle('selected',b===button));draw(config,rows,Number(button.dataset.range));
     }));
   }).catch(()=>{document.getElementById(config.id+'-caption').textContent='Unable to load usage data';document.getElementById(config.id+'-empty').hidden=false;});
 });
})();
</script>'''
    body=_top('Insights','Analytics','Explore your household usage through detailed, interactive resource charts.')+'<div class="analytics-stack">'+chart.format(name='Electricity',id='electricity-chart',unit='kWh')+chart.format(name='Water',id='water-chart',unit='m³')+'</div>'+script
    return page('Analytics',body,version,'/analytics')

def forecast_page(fcs,currency,version,message=None):
    if message:
        content=f'<div class="card"><div class="empty"><h2>Forecast needs more history</h2><p>{esc(message)}</p><a class="btn primary" href="/records/new">＋ Add a reading</a></div></div>'
    else:
        content='<div class="grid two">'+''.join(f'<div class="card"><div class="head"><h2>{esc(r.title())}</h2><span class="label">Next 30 days</span></div><div class="metric"><span>Forecast average</span><b>{float(v.mean()):.2f}</b></div><div class="metric"><span>Forecast total</span><b>{float(v.sum()):.2f}</b></div></div>' for r,v in fcs.items())+'</div>'
    return page('Forecast',_top('Planning','30-day forecast','A forward-looking estimate based on recent usage.')+content,version,'/forecast')
def anomalies_page(data,currency,version): return page('Anomalies',_top('Attention','Unusual usage','Readings that may be worth investigating.')+'<div class="grid two">'+''.join(f'<div class="card"><div class="head"><h2>{esc(r.title())}</h2></div>'+(''.join(f'<div class="metric"><span>{esc(x["date"])}</span><b>{x["amount"]:.2f} · z {x["z_score"]}</b></div>' for x in values) if values else '<div class="empty">No unusual readings found.</div>')+'</div>' for r,values in data.items())+'</div>',version,'/anomalies')
def recommendations_page(tips,currency,version): return page('Recommendations',_top('Guidance','Ways to save','Small changes can make a measurable difference.')+'<div class="card"><ul class="list">'+''.join(f'<li>✦ &nbsp;{esc(t)}</li>' for t in tips)+'</ul></div>',version,'/recommendations')


def auth_page(mode, error=None, values=None):
    values = values or {}
    signup = mode == "signup"
    heading = "Create your account" if signup else "Welcome back"
    subtitle = "Understand your household usage, one reading at a time." if signup else "Sign in to your household dashboard."
    name_field = f'<div class="field"><label for="name">Full name</label><input id="name" name="name" type="text" autocomplete="name" maxlength="80" placeholder="Your name" value="{esc(values.get("name", ""))}" required></div>' if signup else ""
    action = "/signup" if signup else "/login"
    alternate = 'Already have an account? <a href="/login">Log in</a>' if signup else 'New to Konsumo? <a href="/signup">Create an account</a>'
    error_html = f'<div class="auth-error" role="alert">{esc(error)}</div>' if error else ""
    password_hint = '<span class="hint">12+ characters; use at least three character types.</span>' if signup else ""
    username_placeholder = "Choose a username" if signup else "Your username"
    button = "Create account" if signup else "Log in"
    confirm_field = '<div class="field"><label for="confirm_password">Confirm password</label><input id="confirm_password" name="confirm_password" type="password" autocomplete="new-password" minlength="12" maxlength="128" placeholder="Enter your password again" required></div>' if signup else ""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101a2e"><title>{heading} · Konsumo</title><style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;background:radial-gradient(ellipse at 15% 10%,#1e3760 0,transparent 40%),#0b1425;color:#172033;font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;display:grid;place-items:center;padding:24px}}
.auth-wrap{{width:min(100%,470px)}}.auth-brand{{display:flex;align-items:center;justify-content:center;gap:12px;color:#fff;font-size:27px;font-weight:850;letter-spacing:-.8px;margin-bottom:22px}}.auth-logo{{width:46px;height:50px;border-radius:13px;background:linear-gradient(145deg,#1c3557,#101a2e);border:1px solid #ffffff24;display:grid;place-items:center;padding:4px;flex:none}}.auth-logo svg{{display:block;width:100%;height:100%}}
.auth-card{{background:#fff;border:1px solid #ffffff25;border-radius:22px;padding:36px;box-shadow:0 28px 90px #0006}}h1{{font-size:29px;letter-spacing:-.9px;margin:0 0 5px}}.sub{{color:#718096;margin:0 0 25px}}.field{{display:flex;flex-direction:column;gap:7px;margin:16px 0}}label{{font-weight:750;font-size:13px}}input{{width:100%;min-width:0;border:1px solid #dbe2ed;border-radius:11px;padding:13px 14px;font:inherit;outline:none;transition:border-color .18s,box-shadow .18s}}input:focus{{border-color:#356ae6;box-shadow:0 0 0 4px #356ae61a}}.submit{{width:100%;border:0;border-radius:11px;background:linear-gradient(110deg,#356ae6,#2858c9);color:white;padding:14px;font:750 15px system-ui;cursor:pointer;margin-top:10px;box-shadow:0 8px 18px #356ae633}}.submit:hover{{filter:brightness(1.06)}}.submit:focus-visible,a:focus-visible{{outline:3px solid #55d6be;outline-offset:3px}}.switch{{text-align:center;color:#718096;margin:23px 0 0;font-size:14px}}a{{color:#356ae6;font-weight:750;text-decoration:none}}.auth-error{{background:#fff0f0;border:1px solid #ffd3d3;color:#b42318;padding:11px 13px;border-radius:10px;margin-bottom:16px;font-size:14px}}.hint{{font-size:12px;color:#718096}}.auth-foot{{text-align:center;color:#a9b7cc;font-size:12px;margin-top:18px}}
@media(max-width:520px){{body{{padding:16px}}.auth-card{{padding:26px 20px;border-radius:18px}}h1{{font-size:25px}}.auth-brand{{font-size:24px;margin-bottom:17px}}}}
</style></head><body><main class="auth-wrap">
<div class="auth-brand"><span class="auth-logo"><svg viewBox="0 0 42 57" role="img" aria-label="Konsumo logo"><path d="M21 2.5C16 9.5 3.5 23.5 3.5 34.5a17.5 17.5 0 0 0 35 0C38.5 23.5 26 9.5 21 2.5Z" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/><path d="m23.5 13-12 23h9l-2 12 12-25h-9l2-10Z" fill="#55d6be" stroke="#55d6be" stroke-linejoin="round"/></svg></span>Konsumo</div><section class="auth-card">
<h1>{heading}</h1><p class="sub">{subtitle}</p>{error_html}
<form method="post" action="{action}" id="auth-form">{name_field}
<div class="field"><label for="username">Username</label><input id="username" name="username" type="text" autocomplete="username" minlength="3" maxlength="24" pattern="[a-zA-Z0-9_]+" placeholder="{username_placeholder}" value="{esc(values.get("username", ""))}" required></div>
<div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="{'new-password' if signup else 'current-password'}" minlength="{'12' if signup else '1'}" maxlength="128" placeholder="{'At least 12 characters' if signup else 'Enter your password'}" required>{password_hint}</div>
{confirm_field}
<button class="submit" type="submit">{button}</button></form><p class="switch">{alternate}</p>
</section><div class="auth-foot">Private by design · Your household data stays yours</div></main>
<script>
(function(){const form=document.getElementById('auth-form');if(!form)return;form.addEventListener('submit',function(e){const p=form.querySelector('#password');const c=form.querySelector('#confirm_password');if(c&&p.value!==c.value){e.preventDefault();c.setCustomValidity('Passwords do not match.');c.reportValidity();}else if(c){c.setCustomValidity('');}});const c=form.querySelector('#confirm_password');if(c)c.addEventListener('input',()=>c.setCustomValidity(''));})();
</script></body></html>'''


# Floating AI assistant shared by authenticated dashboard pages.
CHAT_STYLE = r"""
.chat-launch{position:fixed;right:24px;bottom:24px;z-index:50;border:0;border-radius:999px;background:#356ae6;color:#fff;padding:14px 19px;font:700 14px system-ui;box-shadow:0 8px 28px #17203330;cursor:pointer}
.chat-panel{display:none;position:fixed;right:24px;bottom:84px;z-index:51;width:min(390px,calc(100vw - 32px));height:min(560px,calc(100vh - 120px));background:#fff;border:1px solid #e5eaf2;border-radius:18px;box-shadow:0 18px 60px #17203330;overflow:hidden;flex-direction:column}
.chat-panel.open{display:flex}.chat-head{padding:16px 18px;background:#101a2e;color:#fff;display:flex;justify-content:space-between;align-items:center}.chat-head small{display:block;color:#b9c6db;font-size:12px}.chat-head-actions{display:flex;align-items:center;gap:10px}.chat-close,.chat-new{border:0;background:transparent;color:#fff;cursor:pointer}.chat-close{font-size:22px}.chat-new{font-size:20px;padding:4px 7px;border-radius:8px}.chat-new:hover,.chat-close:hover{background:#ffffff18}.chat-suggestions{display:flex;flex-wrap:wrap;gap:7px;margin-top:3px}.chat-suggestions button{border:1px solid #dbe4f2;background:#fff;color:#29436f;border-radius:999px;padding:8px 10px;font-size:12px;cursor:pointer}.chat-suggestions button:hover{border-color:#356ae6;color:#356ae6}.chat-suggestions.hidden{display:none}
.chat-messages{padding:15px;overflow:auto;flex:1;background:#f7f9fc;display:flex;flex-direction:column;gap:10px}.chat-msg{max-width:88%;padding:10px 12px;border-radius:13px;font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere}.chat-msg.bot{background:#fff;border:1px solid #e5eaf2;align-self:flex-start}.chat-msg.user{background:#356ae6;color:#fff;align-self:flex-end}.chat-compose{display:flex;gap:8px;padding:12px;border-top:1px solid #e5eaf2}.chat-compose input{min-width:0;flex:1;border:1px solid #dbe2ed;border-radius:10px;padding:11px;font:14px system-ui}.chat-compose button{border:0;border-radius:10px;background:#356ae6;color:#fff;padding:0 15px;font-weight:700;cursor:pointer}.chat-compose button:disabled{opacity:.55;cursor:wait}
"""
CHAT_WIDGET = r"""
<button class="chat-launch" id="konsumo-chat-open" type="button">✦ Ask Konsumo AI</button>
<section class="chat-panel" id="konsumo-chat" aria-label="Konsumo AI assistant">
  <header class="chat-head"><div><strong>Konsumo AI</strong><small>Your household usage assistant</small></div><div class="chat-head-actions"><button class="chat-new" id="konsumo-chat-new" type="button" aria-label="Start a new chat" title="New chat">↻</button><button class="chat-close" id="konsumo-chat-close" type="button" aria-label="Close">×</button></div></header>
  <div class="chat-messages" id="konsumo-chat-messages"><div class="chat-msg bot">Hi! Ask me about your electricity and water usage, or how to save on household utilities.</div><div class="chat-suggestions" id="konsumo-chat-suggestions"><button type="button">How can I lower my electricity use?</button><button type="button">Summarize my latest readings</button><button type="button">Am I using more water lately?</button></div></div>
  <form class="chat-compose" id="konsumo-chat-form"><input id="konsumo-chat-input" maxlength="2000" placeholder="Ask about your usage…" autocomplete="off" required><button id="konsumo-chat-send" type="submit">Send</button></form>
</section>
"""
CHAT_SCRIPT = r"""
<script>
(function(){
 const panel=document.getElementById('konsumo-chat'),open=document.getElementById('konsumo-chat-open');
 const close=document.getElementById('konsumo-chat-close'),newChat=document.getElementById('konsumo-chat-new');
 const form=document.getElementById('konsumo-chat-form'),input=document.getElementById('konsumo-chat-input');
 const messagesEl=document.getElementById('konsumo-chat-messages'),send=document.getElementById('konsumo-chat-send');
 const suggestions=document.getElementById('konsumo-chat-suggestions'),history=[];
 if(!panel||!open||!form)return;
 const welcome='Hi! Ask me about your electricity and water usage, or how to save on household utilities.';
 function add(text,role){const node=document.createElement('div');node.className='chat-msg '+role;node.textContent=text;messagesEl.appendChild(node);messagesEl.scrollTop=messagesEl.scrollHeight;}
 function resetChat(){history.length=0;messagesEl.replaceChildren();add(welcome,'bot');if(suggestions){suggestions.classList.remove('hidden');messagesEl.appendChild(suggestions);}input.value='';}
 open.addEventListener('click',()=>{panel.classList.add('open');input.focus();});
 close.addEventListener('click',()=>panel.classList.remove('open'));
 if(newChat)newChat.addEventListener('click',resetChat);
 if(suggestions)suggestions.addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;input.value=button.textContent.trim();form.requestSubmit();});
 form.addEventListener('submit',async function(event){
   event.preventDefault();const text=input.value.trim();if(!text||send.disabled)return;
   if(suggestions)suggestions.classList.add('hidden');
   history.push({role:'user',content:text});add(text,'user');input.value='';send.disabled=true;send.textContent='…';
   const pending=document.createElement('div');pending.className='chat-msg bot';pending.textContent='Thinking…';messagesEl.appendChild(pending);messagesEl.scrollTop=messagesEl.scrollHeight;
   try{
     const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:history})});
     const data=await response.json();pending.remove();
     if(!response.ok)throw new Error(data.error||'Konsumo AI could not respond. Please try again.');
     const answer=data.answer||'I could not generate a response.';history.push({role:'assistant',content:answer});add(answer,'bot');
   }catch(error){pending.remove();history.pop();add(error.message||'Connection problem. Please try again.','bot');}
   finally{send.disabled=false;send.textContent='Send';input.focus();}
 });
})();
</script>
"""
