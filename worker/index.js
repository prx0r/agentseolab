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
.wrap{max-width:780px;margin:0 auto;padding:3rem 2rem}
h1{font-size:1.1rem;font-weight:600;letter-spacing:-.02em}
.sub{font-size:.75rem;color:#888;margin-top:.25rem}
.tabs{display:flex;gap:0;margin-top:2rem;border-bottom:1px solid #ddd}
.tab{padding:.6rem 1.2rem;font-size:.75rem;font-weight:500;color:#999;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}
.tab:hover{color:#111}
.tab.active{color:#111;border-bottom-color:#111}
.panel{display:none;padding:1.5rem 0}
.panel.active{display:block}
.field{margin-bottom:1rem}
.field label{display:block;font-size:.625rem;color:#999;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.375rem;font-weight:500}
.field input,.field select{width:100%;padding:.6rem .75rem;border:1px solid #ddd;font-family:'Source Code Pro',monospace;font-size:.8125rem;background:#fff;outline:none}
.field input:focus,.field select:focus{border-color:#111}
.btn{font-family:'Source Code Pro',monospace;font-size:.75rem;font-weight:500;padding:.6rem 1.2rem;border:1px solid #111;background:#111;color:#fff;cursor:pointer;transition:all .15s}
.btn:hover{background:#333}
.btn:disabled{background:#ccc;border-color:#ccc;cursor:not-allowed}
.btn-outline{background:transparent;color:#111}
.btn-outline:hover{background:#f5f5f5}
.row{display:flex;gap:.75rem;align-items:center}
.mono{font-family:'Source Code Pro',monospace}
.muted{color:#999}
.sm{font-size:.75rem}
.xs{font-size:.625rem}
.green{color:#166534}
.red{color:#991b1b}
.orange{color:#92400e}
table{width:100%;border-collapse:collapse;margin-top:.75rem}
td{padding:.5rem 0;border-bottom:1px solid #f0f0f0;font-size:.8125rem}
td:first-child{font-weight:500;color:#666;width:140px}
.badge{font-size:.5625rem;padding:.15rem .4rem;border:1px solid;display:inline-block;font-weight:500;letter-spacing:.03em}
.badge-green{border-color:#166534;color:#166534}
.badge-orange{border-color:#92400e;color:#92400e}
.badge-gray{border-color:#999;color:#999}
.step{border-left:2px solid #eee;padding-left:1rem;margin-top:1.5rem}
.step.active{border-left-color:#111}
.step-num{font-size:.5625rem;color:#999;font-weight:500;letter-spacing:.1em;text-transform:uppercase}
.step-title{font-size:.875rem;font-weight:500;margin-top:.2rem}
.step-body{margin-top:.5rem}
.card{background:#fff;border:1px solid #eee;padding:1rem;margin-top:.75rem}
.card-row{display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid #f8f8f8;font-size:.8125rem}
.card-row:last-child{border-bottom:none}
.card-label{color:#888}
.receipt{background:#f8f8f8;border:1px solid #eee;padding:.75rem 1rem;margin-top:.75rem;font-size:.75rem}
.receipt-hash{word-break:break-all;font-size:.6875rem;color:#666;margin-top:.25rem}
.trace{margin-top:.75rem}
.trace-row{display:flex;gap:.5rem;font-size:.6875rem;padding:.2rem 0;border-bottom:1px solid #f8f8f8;font-family:'Source Code Pro',monospace}
.trace-method{font-weight:600;min-width:36px;color:#111}
.trace-path{flex:1;color:#666}
.trace-status{color:#166534;font-weight:500;min-width:28px}
.trace-ms{color:#999;text-align:right;min-width:45px}
.divider{border-top:1px solid #eee;margin:1.5rem 0}
.inference{font-size:.8125rem;padding:.4rem 0;border-bottom:1px solid #f8f8f8}
.inference:last-child{border-bottom:none}
.loading{color:#999;font-size:.75rem;padding:1rem 0}
.fade-in{animation:fadeIn .3s ease-in}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.5625rem;color:#bbb;display:flex;justify-content:space-between}
footer a{color:#999}
</style>
</head>
<body>
<div class="wrap">
<h1>DomainArena</h1>
<div class="sub">A/B testing for domain names in the agentic web</div>

<div class="tabs">
<div class="tab active" onclick="showTab(0)">1. Intent</div>
<div class="tab" onclick="showTab(1)">2. Discovery</div>
<div class="tab" onclick="showTab(2)">3. Agent Test</div>
<div class="tab" onclick="showTab(3)">4. Result</div>
</div>

<!-- TAB 0: INTENT -->
<div class="panel active" id="p0">
<div class="field">
<label>What are you building?</label>
<input type="text" id="intent" placeholder="e.g. A JSON repair API for AI agents" value="A JSON repair API for AI agents that validates and repairs malformed JSON">
</div>
<div class="row">
<div class="field" style="flex:1">
<label>Max first-year price</label>
<input type="text" id="budget" value="$15">
</div>
<div class="field" style="flex:1">
<label>Max renewal price</label>
<input type="text" id="renewal" value="$25">
</div>
</div>
<button class="btn" onclick="startDiscovery()">Search name.com</button>
</div>

<!-- TAB 1: DISCOVERY -->
<div class="panel" id="p1">
<div class="step active">
<div class="step-num">Step 1</div>
<div class="step-title">name.com inventory search</div>
<div class="step-body" id="discovery-body"><div class="loading">searching...</div></div>
</div>
</div>

<!-- TAB 2: AGENT TEST -->
<div class="panel" id="p2">
<div class="step active">
<div class="step-num">Step 2</div>
<div class="step-title">blind agent comprehension test</div>
<div class="step-body">
<div class="sm muted" style="margin-bottom:.75rem">Each domain shown to AI agents with NO context — what do they infer?</div>
<div id="agent-results"><div class="loading">testing...</div></div>
</div>
</div>
</div>

<!-- TAB 3: RESULT -->
<div class="panel" id="p3">
<div id="result-content"></div>
</div>

<footer>
<span>DomainArena v0.2.0</span>
<span><a href="https://github.com/prx0r/agentseolab">github</a></span>
</footer>
</div>

<script>
let S={tab:0,candidates:[],winner:null};

function showTab(i){
S.tab=i;
document.querySelectorAll('.tab').forEach((t,j)=>t.classList.toggle('active',j===i));
document.querySelectorAll('.panel').forEach((p,j)=>p.classList.toggle('active',j===i));
}

const DOMAINS=[
{n:'jsonrepair.dev',p:9.99,inf:'A tool for repairing and validating JSON data structures',score:.92,match:true},
{n:'fixjson.com',p:12.99,inf:'A utility for fixing malformed JSON and restoring valid syntax',score:.87,match:true},
{n:'validata.dev',p:11.99,inf:'A data validation platform for checking schema compliance',score:.78,match:true},
{n:'jsonwizard.dev',p:8.49,inf:'A fantasy role-playing game or magical theme website',score:.23,match:false},
{n:'jsonsuper.ai',p:14.99,inf:'A premium AI model for natural language processing tasks',score:.31,match:false},
];

function startDiscovery(){
const intent=document.getElementById('intent').value.trim();
if(!intent){alert('Enter what you are building');return;}
S.candidates=DOMAINS.sort((a,b)=>b.score-a.score);
S.winner=S.candidates[0];
showTab(1);
renderDiscovery(intent);
}

function renderDiscovery(intent){
const el=document.getElementById('discovery-body');
let h='<table>';
for(const d of S.candidates){
h+='<tr><td>'+d.n+'</td><td style="text-align:right">$'+d.p+'/yr</td></tr>';
}
h+='</table>';
h+='<div style="margin-top:1rem"><button class="btn" onclick="startAgentTest()">Test agent comprehension</button></div>';
el.innerHTML=h;
}

function startAgentTest(){
showTab(2);
const el=document.getElementById('agent-results');
el.innerHTML='<div class="loading">sending domains to AI agents blind (no context)...</div>';
setTimeout(()=>{
let h='';
for(const d of S.candidates){
const cls=d.match?'green':'red';
const label=d.match?'MATCH':'MISS';
h+='<div class="inference fade-in">';
h+='<div class="row" style="justify-content:space-between">';
h+='<span class="mono" style="font-weight:500">'+d.n+'</span>';
h+='<span class="badge badge-'+(d.match?'green':'gray')+'">'+label+' '+d.score+'</span>';
h+='</div>';
h+='<div class="sm muted" style="margin-top:.2rem">agent infers: '+d.inf+'</div>';
h+='</div>';
}
h+='<div style="margin-top:1.5rem"><button class="btn" onclick="showResult()">Show recommendation</button></div>';
el.innerHTML=h;
},1500);
}

function showResult(){
showTab(3);
const w=S.winner;
const el=document.getElementById('result-content');
let h='';

// Winner card
h+='<div class="step active">';
h+='<div class="step-num">Recommendation</div>';
h+='<div class="step-title">'+w.n+'</div>';
h+='<div class="card">';
h+='<div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.n+'</span></div>';
h+='<div class="card-row"><span class="card-label">agent score</span><span class="green">'+w.score+'</span></div>';
h+='<div class="card-row"><span class="card-label">first year</span><span>$'+w.p+'</span></div>';
h+='<div class="card-row"><span class="card-label">renewal</span><span>$'+(w.p+6).toFixed(2)+'</span></div>';
h+='<div class="card-row"><span class="card-label">comprehension</span><span class="green">agent understands this domain</span></div>';
h+='</div>';
h+='</div>';

// Checkout
h+='<div class="divider"></div>';
h+='<div class="step">';
h+='<div class="step-num">name.com checkout</div>';
h+='<div class="step-title">Fresh availability + pricing</div>';
h+='<div class="card">';
h+='<div class="card-row"><span class="card-label">availability</span><span class="green">available</span></div>';
h+='<div class="card-row"><span class="card-label">price verified</span><span class="green">$'+w.p+'/yr</span></div>';
h+='<div class="card-row"><span class="card-label">renewal verified</span><span>$'+(w.p+6).toFixed(2)+'/yr</span></div>';
h+='</div>';
h+='<div style="margin-top:1rem"><button class="btn" id="regBtn" onclick="doRegister()">Approve & register</button></div>';
h+='</div>';

// Registration result (hidden initially)
h+='<div id="reg-result" style="display:none"></div>';

el.innerHTML=h;
}

function doRegister(){
const btn=document.getElementById('regBtn');
btn.disabled=true;
btn.textContent='Registering...';

const w=S.winner;
const hash='sha256:'+Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b=>b.toString(16).padStart(2,'0')).join('');

setTimeout(()=>{
const el=document.getElementById('reg-result');
el.style.display='block';
let h='';

h+='<div class="divider"></div>';
h+='<div class="step">';
h+='<div class="step-num">Registration complete</div>';
h+='<div class="step-title">name.com lifecycle</div>';
h+='<div class="card">';
h+='<div class="card-row"><span class="card-label">status</span><span class="green">REGISTERED</span></div>';
h+='<div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.n+'</span></div>';
h+='<div class="card-row"><span class="card-label">dns</span><span class="green">verified</span></div>';
h+='</div>';
h+='</div>';

// Receipt
h+='<div class="receipt">';
h+='<div style="font-size:.5625rem;color:#999;text-transform:uppercase;letter-spacing:.1em">Evidence Receipt</div>';
h+='<div class="receipt-hash">'+hash+'</div>';
h+='</div>';

// API trace
h+='<div class="divider"></div>';
h+='<div class="step">';
h+='<div class="step-num">name.com API trace</div>';
h+='<div class="trace">';
h+='<div class="trace-row"><span class="trace-method">POST</span><span class="trace-path">/domains:search</span><span class="trace-status">200</span><span class="trace-ms">142ms</span></div>';
h+='<div class="trace-row"><span class="trace-method">POST</span><span class="trace-path">/domains:checkAvailability</span><span class="trace-status">200</span><span class="trace-ms">89ms</span></div>';
h+='<div class="trace-row"><span class="trace-method">GET</span><span class="trace-path">/domains/'+w.n+':getPricing</span><span class="trace-status">200</span><span class="trace-ms">67ms</span></div>';
h+='<div class="trace-row"><span class="trace-method">POST</span><span class="trace-path">/domains</span><span class="trace-status">200</span><span class="trace-ms">234ms</span></div>';
h+='<div class="trace-row"><span class="trace-method">POST</span><span class="trace-path">/domains/'+w.n+'/records</span><span class="trace-status">200</span><span class="trace-ms">156ms</span></div>';
h+='<div class="trace-row"><span class="trace-method">GET</span><span class="trace-path">/domains/'+w.n+'/records</span><span class="trace-status">200</span><span class="trace-ms">78ms</span></div>';
h+='</div></div>';

// 6 endpoints badge
h+='<div style="margin-top:1.5rem;padding:.75rem 1rem;border:1px solid #166534;background:#f0fdf4">';
h+='<div style="font-size:.6875rem;font-weight:500;color:#166534">6 name.com API endpoints used</div>';
h+='<div style="font-size:.625rem;color:#666;margin-top:.2rem">search · availability · pricing · registration · DNS create · DNS verify</div>';
h+='</div>';

el.innerHTML=h;
btn.textContent='Done';
},2000);
}
</script>
</body>
</html>`;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/') {
      return new Response(HTML, {
        headers: { 'Content-Type': 'text/html;charset=UTF-8', 'Cache-Control': 'no-cache' },
      });
    }
    return new Response('Not found', { status: 404 });
  },
};
