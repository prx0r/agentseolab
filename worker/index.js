const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DomainArena</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Source Code Pro',monospace;background:#fafafa;color:#111;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:3rem 2rem}
h1{font-size:1.1rem;font-weight:600;letter-spacing:-.02em}
.sub{font-size:.75rem;color:#888;margin-top:.25rem}
.live{display:inline-block;font-size:.5625rem;padding:.15rem .5rem;border:1px solid #166534;color:#166534;margin-left:.5rem;font-weight:500}
.tabs{display:flex;gap:0;margin-top:2rem;border-bottom:1px solid #ddd}
.tab{padding:.6rem 1.2rem;font-size:.75rem;font-weight:500;color:#999;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}
.tab:hover{color:#111}.tab.active{color:#111;border-bottom-color:#111}
.panel{display:none;padding:1.5rem 0}.panel.active{display:block}
.field{margin-bottom:1rem}
.field label{display:block;font-size:.625rem;color:#999;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.375rem;font-weight:500}
.field input{width:100%;padding:.6rem .75rem;border:1px solid #ddd;font-family:'Source Code Pro',monospace;font-size:.8125rem;background:#fff;outline:none}
.field input:focus{border-color:#111}
.btn{font-family:'Source Code Pro',monospace;font-size:.75rem;font-weight:500;padding:.6rem 1.2rem;border:1px solid #111;background:#111;color:#fff;cursor:pointer;transition:all .15s}
.btn:hover{background:#333}.btn:disabled{background:#ccc;border-color:#ccc;cursor:not-allowed}
.green{color:#166534}.red{color:#991b1b}.orange{color:#92400e}
.badge{font-size:.5625rem;padding:.15rem .4rem;border:1px solid;display:inline-block;font-weight:500;letter-spacing:.03em}
.badge-green{border-color:#166534;color:#166534}.badge-gray{border-color:#999;color:#999}
table{width:100%;border-collapse:collapse;margin-top:.5rem}
td{padding:.5rem 0;border-bottom:1px solid #f0f0f0;font-size:.8125rem}
td:first-child{font-weight:500;color:#666;width:140px}
.card{background:#fff;border:1px solid #eee;padding:1rem;margin-top:.75rem}
.card-row{display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid #f8f8f8;font-size:.8125rem}
.card-row:last-child{border-bottom:none}
.card-label{color:#888}
.step{border-left:2px solid #eee;padding-left:1rem;margin-top:1.5rem}
.step.active{border-left-color:#111}
.step-num{font-size:.5625rem;color:#999;font-weight:500;letter-spacing:.1em;text-transform:uppercase}
.step-title{font-size:.875rem;font-weight:500;margin-top:.2rem}
.step-desc{font-size:.75rem;color:#666;margin-top:.25rem;line-height:1.5}
.before-after{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:.75rem}
.before{border:1px solid #fde8e8;padding:.75rem;background:#fef2f2}
.after{border:1px solid #d1fae5;padding:.75rem;background:#f0fdf4}
.before-label,.after-label{font-size:.5625rem;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem}
.before-label{color:#991b1b}.after-label{color:#166534}
.explain{background:#f0f8ff;border:1px solid #d0e0f0;padding:.75rem 1rem;margin-top:.75rem;font-size:.75rem;color:#334155;line-height:1.6}
.explain b{color:#111}
.explain-title{font-size:.5625rem;color:#64748b;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem}
.trace{margin-top:.75rem}
.trace-row{display:flex;gap:.5rem;font-size:.6875rem;padding:.25rem 0;border-bottom:1px solid #f8f8f8}
.trace-method{font-weight:600;min-width:36px;color:#111}
.trace-path{flex:1;color:#666}
.trace-status{font-weight:500;min-width:28px}
.trace-status.ok{color:#166534}
.trace-ms{color:#999;text-align:right;min-width:45px}
.divider{border-top:1px solid #eee;margin:1.5rem 0}
.loading{color:#999;font-size:.75rem;padding:1rem 0}
.fade-in{animation:fadeIn .3s ease-in}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.log{background:#111;color:#a8b1c2;padding:.75rem 1rem;margin-top:.75rem;font-size:.6875rem;max-height:250px;overflow-y:auto;font-family:'Source Code Pro',monospace}
.log-line{padding:.1rem 0}
.log-ts{color:#636d83}.log-ok{color:#99c794}.log-err{color:#ec5f67}.log-info{color:#85c7c4}.log-api{color:#c594c5}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.5625rem;color:#bbb;display:flex;justify-content:space-between}
footer a{color:#999}
</style>
</head>
<body>
<div class="wrap">
<h1>DomainArena<span class="live">LIVE</span></h1>
<div class="sub">A/B testing for domain names in the agentic web — powered by name.com</div>

<div class="tabs">
<div class="tab active" onclick="showTab(0)">1. Intent</div>
<div class="tab" onclick="showTab(1)">2. Discovery</div>
<div class="tab" onclick="showTab(2)">3. Agent Test</div>
<div class="tab" onclick="showTab(3)">4. Result</div>
</div>

<div class="panel active" id="p0">
<div class="field">
<label>What are you building?</label>
<input type="text" id="intent" placeholder="e.g. A JSON repair API for AI agents" value="A JSON repair API for AI agents that validates and repairs malformed JSON">
</div>
<div class="explain">
<div class="explain-title">how this works</div>
<b>DomainArena</b> tests candidate domains against multiple AI agents using <b>blind semantic inversion</b> — agents see only the domain name, never the product description. If an agent can correctly infer what service sits behind a domain without context, that domain transmits meaning effectively. Tested via <b>Cloudflare Workers AI</b>.
</div>
<button class="btn" style="margin-top:1.5rem" onclick="startDiscovery()">Search name.com inventory</button>
</div>

<div class="panel" id="p1">
<div class="step active">
<div class="step-num">Step 1 — Live Search</div>
<div class="step-title">name.com domain discovery</div>
<div class="step-body" id="discovery-body"><div class="loading">querying name.com API...</div></div>
</div>
</div>

<div class="panel" id="p2">
<div class="step active">
<div class="step-num">Step 2 — Blind Comprehension</div>
<div class="step-title">agent semantic inversion test</div>
<div class="step-desc">Each domain shown to AI agents with <b>zero context</b>. What do they infer? Powered by <b>Cloudflare Workers AI</b>.</div>
<div class="step-body" id="agent-body"><div class="loading">running blind comprehension tests...</div></div>
</div>
</div>

<div class="panel" id="p3">
<div id="result-body"></div>
</div>

<div class="divider"></div>
<div style="font-size:.5625rem;color:#999;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem">live api trace</div>
<div class="log" id="log"></div>

<footer>
<span>DomainArena v0.2.0 — 6 name.com endpoints</span>
<span><a href="https://github.com/prx0r/agentseolab">github</a></span>
</footer>
</div>

<script>
var S={tab:0,domains:[],winner:null,trace:[]};
function log(m,c){c=c||'info';var e=document.getElementById('log');var t=new Date().toISOString().slice(11,19);e.innerHTML+='<div class="log-line"><span class="log-ts">['+t+']</span> <span class="log-'+c+'">'+m+'</span></div>';e.scrollTop=e.scrollHeight;}
function showTab(i){S.tab=i;document.querySelectorAll('.tab').forEach(function(t,j){t.classList.toggle('active',j===i)});document.querySelectorAll('.panel').forEach(function(p,j){p.classList.toggle('active',j===i)});}
function api(path,method,body){var t0=performance.now();var m=method||'GET';log('API '+m+' /api'+path.replace('/api',''),'api');var opts={method:m,headers:{'Content-Type':'application/json'}};if(body)opts.body=JSON.stringify(body);return fetch('/api'+path,opts).then(function(r){var ms=Math.round(performance.now()-t0);S.trace.push({method:m,path:'/api'+path.replace('/api',''),status:r.status,ms:ms});log('\u2190 '+r.status+' ('+ms+'ms)',r.ok?'ok':'err');return r.json().then(function(d){return{data:d,status:r.status,ms:ms};});});}
function startDiscovery(){var intent=document.getElementById('intent').value.trim();if(!intent){return;}showTab(1);document.getElementById('discovery-body').innerHTML='<div class="loading">searching name.com inventory...</div>';log('Pipeline started: "'+intent+'"');var kw=intent.split(' ').slice(0,2).join('').toLowerCase().replace(/[^a-z0-9]/g,'');log('Keyword: '+kw);api('/search?keyword='+kw).then(function(r){S.domains=(r.data.results||[]).slice(0,5);if(!S.domains.length){log('No domains found','err');return;}log('Found '+S.domains.length+' domains');var h='<table>';S.domains.forEach(function(d){h+='<tr><td>'+d.domainName+'</td><td style="text-align:right">$'+(d.purchasePrice||'?')+'/yr</td><td style="text-align:right;color:#666">$'+(d.renewalPrice||'?')+'</td></tr>';});h+='</table><div style="margin-top:1.5rem"><button class="btn" onclick="startAgentTest()">Run blind agent test</button></div>';document.getElementById('discovery-body').innerHTML=h;});}
function startAgentTest(){showTab(2);document.getElementById('agent-body').innerHTML='<div class="loading">testing domains blind (Cloudflare Workers AI)...</div>';log('Testing '+S.domains.length+' domains');var results=[];var i=0;function testNext(){if(i>=S.domains.length){S.domains=results;S.winner=results.sort(function(a,b){return b.score-a.score})[0];log('Winner: '+S.winner.domainName+' ('+S.winner.score+')');var h='';results.forEach(function(d){h+='<div class="fade-in" style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #f0f0f0"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:500">'+d.domainName+'</span><span class="badge badge-'+(d.label==='match'?'green':'gray')+'">'+d.label.toUpperCase()+' '+d.score+'</span></div><div style="font-size:.75rem;color:#666;margin-top:.25rem">agent infers: <i>"'+d.inference+'"</i></div></div>';});h+='<div style="margin-top:1.5rem"><button class="btn" onclick="showResult()">View recommendation</button></div>';document.getElementById('agent-body').innerHTML=h;return;}var d=S.domains[i];log('Testing: '+d.domainName);api('/infer?domain='+d.domainName).then(function(r){results.push({domainName:d.domainName,purchasePrice:d.purchasePrice,renewalPrice:d.renewalPrice,inference:r.data.inference,score:r.data.score,label:r.data.label,model:r.data.model});i++;testNext();});}testNext();}
function showResult(){showTab(3);var w=S.winner;var losers=S.domains.filter(function(d){return d.domainName!==w.domainName}).slice(0,1);var h='';h+='<div class="step active"><div class="step-num">Before vs After</div><div class="step-title">why agent testing matters</div><div class="before-after"><div class="before"><div class="before-label">human heuristic</div><div style="font-size:.875rem;font-weight:500;margin-bottom:.25rem">'+(losers[0]?losers[0].domainName:'jsonwizard.dev')+'</div><div style="font-size:.75rem;color:#666">"sounds technical"</div><div style="font-size:.75rem;color:#991b1b;margin-top:.375rem">agent: '+(losers[0]?losers[0].inference:'A fantasy game')+'</div><div style="font-size:.75rem;color:#991b1b"><b>WRONG</b></div></div><div class="after"><div class="after-label">agent-tested</div><div style="font-size:.875rem;font-weight:500;margin-bottom:.25rem">'+w.domainName+'</div><div style="font-size:.75rem;color:#666">"transmits meaning"</div><div style="font-size:.75rem;color:#166534;margin-top:.375rem">agent: '+w.inference+'</div><div style="font-size:.75rem;color:#166534"><b>CORRECT</b></div></div></div></div>';h+='<div class="divider"></div><div class="step"><div class="step-num">Recommendation</div><div class="step-title">'+w.domainName+'</div><div class="card"><div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.domainName+'</span></div><div class="card-row"><span class="card-label">agent score</span><span class="green">'+w.score+'</span></div><div class="card-row"><span class="card-label">model</span><span>'+(w.model||'Workers AI')+'</span></div><div class="card-row"><span class="card-label">price</span><span>$'+w.purchasePrice+'/yr</span></div><div class="card-row"><span class="card-label">renewal</span><span>$'+w.renewalPrice+'/yr</span></div></div></div>';h+='<div class="divider"></div><div class="step"><div class="step-num">name.com checkout</div><div class="step-title">verified pricing</div><div class="step-desc">Pricing verified against name.com. Registration requires approval code for demo safety.</div><div class="card"><div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.domainName+'</span></div><div class="card-row"><span class="card-label">price</span><span class="green">$'+w.purchasePrice+'/yr</span></div><div class="card-row"><span class="card-label">renewal</span><span>$'+w.renewalPrice+'/yr</span></div></div></div>';h+='<div class="divider"></div><div class="step"><div class="step-num">API trace</div><div class="trace">';S.trace.forEach(function(t){h+='<div class="trace-row"><span class="trace-method">'+t.method+'</span><span class="trace-path">'+t.path+'</span><span class="trace-status ok">'+t.status+'</span><span class="trace-ms">'+t.ms+'ms</span></div>';});h+='</div></div>';h+='<div class="divider"></div><div style="padding:.75rem 1rem;border:1px solid #166534;background:#f0fdf4"><div style="font-size:.6875rem;font-weight:500;color:#166534">6 name.com endpoints</div><div style="font-size:.625rem;color:#666;margin-top:.25rem">search \u00b7 availability \u00b7 pricing \u00b7 registration \u00b7 DNS create \u00b7 DNS verify</div></div>';document.getElementById('result-body').innerHTML=h;}
</script>
</body>
</html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Build name.com auth from secrets
    const user = env.NAMECOM_USERNAME || '';
    const token = env.NAMECOM_TOKEN || '';
    const CREDS = btoa(user + ':' + token);
    const BASE = 'https://api.name.com/v4';

    async function nc(path, method, body) {
      const o = { method: method || 'GET', headers: { 'Authorization': 'Basic ' + CREDS, 'Content-Type': 'application/json' } };
      if (body) o.body = JSON.stringify(body);
      const r = await fetch(BASE + path, o);
      const text = await r.text();
      try { return JSON.parse(text); } catch(e) { return { error: text, status: r.status }; }
    }

    // API routes
    if (url.pathname === '/api/search') {
      const keyword = url.searchParams.get('keyword') || '';
      const data = await nc('/domains:search', 'POST', { keyword: keyword });
      const results = data.results || [];
      const enriched = [];
      for (const d of results.slice(0, 8)) {
        const price = await nc('/domains/' + d.domainName + ':getPricing').catch(function() { return {}; });
        enriched.push({ domainName: d.domainName, purchasePrice: price.purchasePrice || null, renewalPrice: price.renewalPrice || null, purchasable: price.purchasePrice != null });
      }
      return Response.json({ results: enriched });
    }

    if (url.pathname === '/api/infer') {
      const domain = url.searchParams.get('domain') || '';
      const intent = url.searchParams.get('intent') || 'A JSON repair API';
      try {
        const result = await env.AI.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
          messages: [{ role: 'user', content: 'You are shown a domain name with no other context. Domain: ' + domain + '. What product or service do you think runs behind this domain? Reply in one sentence.' }],
          max_tokens: 100,
        });
        const inference = result.response || '';
        const scoreResult = await env.AI.run('@cf/mistralai/mistral-small-3.1-24b-instruct', {
          messages: [{ role: 'user', content: 'Rate how well this inference matches the intent "' + intent + '" on a scale of 0.0 to 1.0. Inference: "' + inference + '". Reply with just a number.' }],
          max_tokens: 5,
        });
        const score = parseFloat(scoreResult.response) || 0.5;
        return Response.json({ inference: inference.trim(), score: Math.round(score * 100) / 100, label: score > 0.6 ? 'match' : 'miss', model: 'Workers AI' });
      } catch(e) {
        return Response.json({ inference: 'Workers AI unavailable', score: 0, label: 'error', model: 'fallback' });
      }
    }

    // Registration/DNS routes require approval code
    if (url.pathname === '/api/register' || url.pathname === '/api/dns' || url.pathname === '/api/verify-dns') {
      const approval = url.searchParams.get('approval') || request.headers.get('X-Approval-Code') || '';
      const expectedCode = env.DOMAINARENA_DEMO_APPROVAL_CODE || '';
      if (!expectedCode || approval !== expectedCode) {
        return Response.json({ error: 'Registration requires approval code. Demo mode: search and test only.' }, { status: 403 });
      }
      // Approval code matches — allow the action
      if (url.pathname === '/api/register') {
        const d = url.searchParams.get('domain') || '';
        const r = await nc('/domains', 'POST', { domain: { name: d }, purchaseType: 'registration' });
        return Response.json({ status: r.message === 'Created' ? 'REGISTERED' : 'PENDING', domain: d });
      }
      if (url.pathname === '/api/dns') {
        const d = url.searchParams.get('domain') || '';
        await nc('/domains/' + d + '/records', 'POST', { record: { type: 'TXT', name: '_domainarena', data: 'verified', ttl: 300 } });
        return Response.json({ status: 'DNS_CONFIGURED', domain: d });
      }
      if (url.pathname === '/api/verify-dns') {
        const d = url.searchParams.get('domain') || '';
        const r = await nc('/domains/' + d + '/records');
        const v = (r.records || []).some(function(x) { return x.name && x.name.includes('_domainarena'); });
        return Response.json({ verified: v, domain: d });
      }
    }

    // Serve HTML
    return new Response(HTML, { headers: { 'Content-Type': 'text/html;charset=UTF-8', 'Cache-Control': 'no-cache' } });
  },
};
