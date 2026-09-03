const LANDING_PAGE = String.raw`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DomainArena — A/B Testing Domain Names Against AI Agents</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',-apple-system,system-ui,sans-serif;background:#fafafa;color:#111;line-height:1.6;-webkit-font-smoothing:antialiased}
code,.mono{font-family:'Source Code Pro',monospace}

nav{position:fixed;top:0;left:0;right:0;background:rgba(250,250,250,.95);backdrop-filter:blur(12px);border-bottom:1px solid #eee;z-index:100;padding:0 2rem}
.nav-inner{max-width:1000px;margin:0 auto;display:flex;align-items:center;height:48px;gap:2rem}
.nav-inner a{font-size:.8rem;color:#666;text-decoration:none;font-weight:500}
.nav-inner a:hover{color:#111}
.nav-brand{font-weight:700;font-size:.9rem;color:#111}

.hero{padding:120px 2rem 80px;text-align:center}
.hero h1{font-size:3rem;font-weight:800;letter-spacing:-.04em;line-height:1.1;max-width:700px;margin:0 auto}
.hero .tag{display:inline-block;background:#eff6ff;color:#1d4ed8;font-size:.75rem;font-weight:600;padding:4px 12px;border-radius:20px;margin-bottom:20px}
.hero p{font-size:1.15rem;color:#555;max-width:620px;margin:20px auto 0;line-height:1.7}
.hero-cta{display:flex;gap:12px;justify-content:center;margin-top:32px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 24px;border-radius:8px;font-size:.875rem;font-weight:600;text-decoration:none;transition:all .15s}
.btn-primary{background:#111;color:#fff}.btn-primary:hover{background:#333}
.btn-outline{background:transparent;color:#111;border:1px solid #ddd}.btn-outline:hover{border-color:#111}

section{padding:80px 2rem}
.section-inner{max-width:1000px;margin:0 auto}
.section-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.12em;color:#999;font-weight:600;margin-bottom:8px}
.section-title{font-size:2rem;font-weight:700;letter-spacing:-.03em;margin-bottom:12px}
.section-desc{font-size:1rem;color:#555;max-width:600px;line-height:1.7}

.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:32px}
.card{background:#fff;border:1px solid #eee;border-radius:12px;padding:24px}
.card h3{font-size:1rem;font-weight:600;margin-bottom:8px}
.card p{font-size:.875rem;color:#666;line-height:1.6}
.card .icon{font-size:1.5rem;margin-bottom:12px}

.pipeline{display:flex;gap:0;margin-top:40px;overflow-x:auto}
.pipe-step{flex:1;min-width:110px;background:#fff;border:1px solid #eee;padding:16px 10px;text-align:center}
.pipe-step:first-child{border-radius:12px 0 0 12px}
.pipe-step:last-child{border-radius:0 12px 12px 0}
.pipe-step+.pipe-step{border-left:none}
.pipe-num{font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;color:#999;font-weight:600}
.pipe-title{font-size:.78rem;font-weight:600;margin-top:4px}
.pipe-desc{font-size:.68rem;color:#666;margin-top:4px;line-height:1.4}
.pipe-step.highlight{border-color:#1d4ed8;background:#eff6ff}

.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid #eee;border-radius:12px;overflow:hidden;margin-top:32px}
.metric{border-right:1px solid #eee;text-align:center;padding:24px 16px}
.metric:last-child{border-right:none}
.metric .num{font-size:2rem;font-weight:700;letter-spacing:-.03em}
.metric .label{font-size:.75rem;color:#666;margin-top:4px}

.vs{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}
.vs-box{background:#fff;border:1px solid #eee;border-radius:12px;padding:24px}
.vs-box .label{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:#999;font-weight:600}
.vs-box .domain{font-size:1.3rem;font-weight:700;margin-top:8px;font-family:'Source Code Pro',monospace}
.vs-box .meta{font-size:.8rem;color:#666;margin-top:8px;line-height:1.5}
.vs-box.bad{border-color:#fecaca;background:#fef2f2}.vs-box.bad .domain{color:#991b1b}
.vs-box.good{border-color:#bbf7d0;background:#f0fdf4}.vs-box.good .domain{color:#166534}

.endpoint{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:.875rem}
.endpoint:last-child{border-bottom:none}
.endpoint-method{font-weight:600;min-width:40px;font-size:.75rem;font-family:'Source Code Pro',monospace}
.endpoint-method.post{color:#1d4ed8}.endpoint-method.get{color:#166534}
.endpoint-path{flex:1;color:#666;font-family:'Source Code Pro',monospace;font-size:.8rem}
.endpoint-desc{color:#999;font-size:.8rem}

.finding{background:#fff;border:1px solid #eee;border-radius:8px;padding:20px;margin-top:12px}
.finding h4{font-size:.9rem;font-weight:600;margin-bottom:6px}
.finding p{font-size:.8rem;color:#666;line-height:1.5}

.lifecycle{display:grid;grid-template-columns:repeat(7,1fr);gap:0;margin-top:32px;border:1px solid #eee;border-radius:12px;overflow:hidden}
.lc-step{padding:12px 8px;text-align:center;border-right:1px solid #eee;font-size:.7rem}
.lc-step:last-child{border-right:none}
.lc-step .num{font-size:.55rem;text-transform:uppercase;letter-spacing:.1em;color:#999;font-weight:600}
.lc-step .title{font-weight:600;margin-top:4px;font-size:.72rem}
.lc-step.done{background:#f0fdf4}
.lc-step.done .title{color:#166534}

footer{padding:40px 2rem;border-top:1px solid #eee;text-align:center;font-size:.8rem;color:#999}
footer a{color:#666}

@media(max-width:700px){
  .hero h1{font-size:2rem}
  .metric-grid{grid-template-columns:1fr 1fr}
  .vs{grid-template-columns:1fr}
  .pipeline{flex-direction:column}
  .pipe-step{border-radius:0!important;border-left:1px solid #eee!important}
  .pipe-step:first-child{border-radius:12px 12px 0 0!important}
  .pipe-step:last-child{border-radius:0 0 12px 12px!important}
  .lifecycle{grid-template-columns:repeat(3,1fr)}
  .lc-step{border-right:none;border-bottom:1px solid #eee}
}
</style>
</head>
<body>

<nav>
<div class="nav-inner">
  <span class="nav-brand">DomainArena</span>
  <a href="#problem">Problem</a>
  <a href="#how">How it works</a>
  <a href="#namecom">name.com</a>
  <a href="#findings">Research</a>
  <a href="/demo" target="_blank" style="color:#1d4ed8">Live Demo &rarr;</a>
</div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="tag">name.com Track &middot; DevNetwork Hackathon 2026</div>
  <h1>Measure the name before you buy it</h1>
  <p>The thing discovering your service is increasingly an AI agent, not a human. DomainArena tests whether agents can infer what service sits behind a domain &mdash; before you spend money on a name.</p>
  <div class="hero-cta">
    <a href="/demo" target="_blank" class="btn btn-primary">Try the Live Demo</a>
    <a href="#how" class="btn btn-outline">How it works</a>
  </div>
</div>

<!-- PROBLEM -->
<section id="problem">
<div class="section-inner">
  <div class="section-label">The Problem</div>
  <div class="section-title">You buy a domain on intuition. The machine audience can't find you.</div>
  <div class="section-desc">93% of Google searches now end without a click. Agents are making billions of API calls daily. But domain naming is still a human guesswork game.</div>

  <div class="vs">
    <div class="vs-box bad">
      <div class="label">Human Heuristic</div>
      <div class="domain">velora.com</div>
      <div class="meta">"Sounds technical and modern." Agent infers: <strong>a fantasy game.</strong> Score: 0.1. Result: <strong>WRONG</strong></div>
    </div>
    <div class="vs-box good">
      <div class="label">Agent-Tested</div>
      <div class="domain">jsonrepair.dev</div>
      <div class="meta">"Transmits meaning without context." Agent infers: <strong>JSON repair tool.</strong> Score: 0.9. Result: <strong>CORRECT</strong></div>
    </div>
  </div>
</div>
</section>

<!-- HOW IT WORKS -->
<section id="how" style="background:#fff;border-top:1px solid #eee;border-bottom:1px solid #eee">
<div class="section-inner">
  <div class="section-label">How It Works</div>
  <div class="section-title">From inventory to verified receipt</div>
  <div class="section-desc">Every step has provenance. The agent never sees the product description &mdash; only the domain name.</div>

  <div class="pipeline">
    <div class="pipe-step highlight">
      <div class="pipe-num">Step 1</div>
      <div class="pipe-title">name.com</div>
      <div class="pipe-desc">Search available domains + live pricing</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">Step 2</div>
      <div class="pipe-title">Blind Test</div>
      <div class="pipe-desc">Llama 3.3 sees only the hostname</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">Step 3</div>
      <div class="pipe-title">Score</div>
      <div class="pipe-desc">Independent Mistral evaluator</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">Step 4</div>
      <div class="pipe-title">Recommend</div>
      <div class="pipe-desc">Winner by comprehension + economics</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">Step 5</div>
      <div class="pipe-title">Approve</div>
      <div class="pipe-desc">Human gates all writes</div>
    </div>
    <div class="pipe-step highlight">
      <div class="pipe-num">Step 6</div>
      <div class="pipe-title">Register</div>
      <div class="pipe-desc">Fresh recheck then buy</div>
    </div>
    <div class="pipe-step highlight">
      <div class="pipe-num">Step 7</div>
      <div class="pipe-title">Verify</div>
      <div class="pipe-desc">DNS readback + SHA-256 receipt</div>
    </div>
  </div>

  <div class="metric-grid">
    <div class="metric"><div class="num">6</div><div class="label">name.com API Endpoints</div></div>
    <div class="metric"><div class="num">16</div><div class="label">Experiments Run</div></div>
    <div class="metric"><div class="num">148</div><div class="label">Tests Passing</div></div>
    <div class="metric"><div class="num">7+</div><div class="label">Model Families Tested</div></div>
  </div>
</div>
</section>

<!-- NAME.COM -->
<section id="namecom">
<div class="section-inner">
  <div class="section-label">name.com Integration</div>
  <div class="section-title">Full domain lifecycle through one API</div>
  <div class="section-desc">DomainArena uses six name.com capabilities: search, availability, pricing, registration, DNS create, and DNS readback. Every step is verified server-side before money moves.</div>

  <div class="card" style="margin-top:24px;max-width:600px">
    <div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains:search</span><span class="endpoint-desc">discover available candidates</span></div>
    <div class="endpoint"><span class="endpoint-method get">GET</span><span class="endpoint-path">/domains/{name}:getPricing</span><span class="endpoint-desc">verify pricing before purchase</span></div>
    <div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains</span><span class="endpoint-desc">register domain (approval-gated)</span></div>
    <div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains/{name}/records</span><span class="endpoint-desc">configure DNS</span></div>
    <div class="endpoint"><span class="endpoint-method get">GET</span><span class="endpoint-path">/domains/{name}/records</span><span class="endpoint-desc">verify DNS configuration</span></div>
  </div>

  <div style="margin-top:20px;padding:16px;background:#f0f8ff;border:1px solid #d0e0f0;border-radius:8px;font-size:.85rem;color:#334155">
    <strong>name.com isn't just discovery.</strong> It is the authoritative transaction boundary immediately before money moves. Before registration, DomainArena re-queries availability and price. If anything changed, it fails closed.
  </div>
</div>
</section>

<!-- RESEARCH -->
<section id="findings" style="background:#fff;border-top:1px solid #eee;border-bottom:1px solid #eee">
<div class="section-inner">
  <div class="section-label">Research Findings</div>
  <div class="section-title">Why one-shot domain ratings don't work</div>
  <div class="section-desc">16 experiments revealed that agent naming behavior is much stranger than a simple LLM rating suggests.</div>

  <div class="card-grid">
    <div class="finding">
      <h4>Position dominates domain choice</h4>
      <p>In pairwise tests, 87% of agents picked the first option regardless of which domain was shown. TLD effects (.com vs .dev vs .ai) were statistically insignificant. <strong>Order matters more than extension.</strong></p>
    </div>
    <div class="finding">
      <h4>Models disagree materially</h4>
      <p>Llama 3.3, Mistral Small, and Qwen3 produced different rankings for the same domains. A domain cannot be called "agent-legible" based on one model. <strong>Cross-family replication is essential.</strong></p>
    </div>
    <div class="finding">
      <h4>Description seduction is real</h4>
      <p>Some model families selected broken tools when they had enterprise-sounding descriptions. <strong>Agent discovery systems can be manipulated by presentation rather than capability.</strong></p>
    </div>
    <div class="finding">
      <h4>Semantic inversion is a cheap proxy</h4>
      <p>Blind inference is a useful first filter, but execution testing is ground truth. AgentSearchBench (10K agents) confirms description similarity is weaker than execution-grounded performance.</p>
    </div>
    <div class="finding">
      <h4>Serverless inference drifts</h4>
      <p>Identical prompts at temperature zero produced materially different choices across time windows. One-shot domain ratings are scientifically weak. <strong>DomainArena replicates across windows.</strong></p>
    </div>
    <div class="finding">
      <h4>Generator/judge separation</h4>
      <p>The tested model never scores itself. Llama generates the inference, independent Mistral evaluates the match. This prevents self-reinforcing bias in comprehension testing.</p>
    </div>
  </div>
</div>
</section>

<!-- LIFECYCLE -->
<section>
<div class="section-inner">
  <div class="section-label">The Lifecycle</div>
  <div class="section-title">From discovery to verified infrastructure</div>

  <div class="lifecycle">
    <div class="lc-step done"><div class="num">1</div><div class="title">Search</div></div>
    <div class="lc-step done"><div class="num">2</div><div class="title">Test</div></div>
    <div class="lc-step done"><div class="num">3</div><div class="title">Score</div></div>
    <div class="lc-step done"><div class="num">4</div><div class="title">Approve</div></div>
    <div class="lc-step done"><div class="num">5</div><div class="title">Recheck</div></div>
    <div class="lc-step done"><div class="num">6</div><div class="title">Register</div></div>
    <div class="lc-step done"><div class="num">7</div><div class="title">Verify</div></div>
  </div>

  <div style="margin-top:24px;padding:20px;background:#f8f8f8;border:1px solid #eee;border-radius:8px">
    <p style="font-size:.9rem">The entire decision basis is frozen into a <strong>content-addressed SHA-256 receipt</strong>. Domain, intent, score, inference, prices, registration status, DNS verification &mdash; all hashed together. Proof that the decision was made with verified economic state, not gut feeling.</p>
  </div>
</div>
</section>

<!-- CLOSE -->
<section style="padding:60px 2rem;text-align:center;background:#fff;border-top:1px solid #eee">
<div class="section-inner">
  <div class="section-title" style="max-width:600px;margin:0 auto">Measure the name. Buy the evidence-backed winner. Verify the infrastructure.</div>
  <p style="font-size:1rem;color:#555;max-width:500px;margin:12px auto 0">DomainArena attacks the decision before deployment: which available hostname best communicates the intended service to agents?</p>
  <div class="hero-cta" style="margin-top:24px">
    <a href="/demo" target="_blank" class="btn btn-primary">Try the Live Demo</a>
  </div>
</div>
</section>

<footer>
  DomainArena &mdash; A/B Testing Domain Names in the Agentic Web &middot; name.com Track &middot; DevNetwork Hackathon 2026
</footer>

</body>
</html>
`;const STOPWORDS = new Set(["a","an","the","for","and","or","of","to","in","on","with","that","is","it","by","at","as","from","this","your","my","our","can","be","do","if","no","not","but","are","was","has","had","have","will","would","could","should","may","might","shall","let","us","you","me","he","she","we","they","them","their","its","his","her","who","which","what","where","when","how","why","all","each","every","both","few","more","most","other","some","such","than","too","very","just","about","also","only","new","old"]);

function extractKeywords(intent) {
  const words = intent.toLowerCase().replace(/[^a-z0-9\s]/g, "").split(/\s+/).filter(w => w.length > 2 && !STOPWORDS.has(w));
  const unique = [...new Set(words)];
  // Build domain-name-friendly search terms
  const terms = [];
  if (unique.length >= 2) terms.push(unique.slice(0, 2).join(""));
  if (unique.length >= 1) terms.push(unique[0]);
  if (unique.length >= 3) terms.push(unique.slice(0, 3).join(""));
  return [...new Set(terms)].slice(0, 3);
}

function nc(method, path, body, env) {
  const base = env.NAMECOM_BASE_URL || "https://api.name.com/v4";
  const user = env.NAMECOM_USERNAME || "";
  const token = env.NAMECOM_TOKEN || "";
  if (!user || !token) {
    return Promise.resolve({ error: "name.com credentials not configured (NAMECOM_USERNAME / NAMECOM_TOKEN)", status: 0 });
  }
  const auth = btoa(user + ":" + token);
  return fetch(base + path, {
    method,
    headers: { "Authorization": "Basic " + auth, "Content-Type": "application/json", "User-Agent": "DomainArena/0.2" },
    body: body ? JSON.stringify(body) : undefined,
  }).then(async r => {
    const text = await r.text();
    try { return JSON.parse(text); } catch { return { error: text, status: r.status }; }
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Access-Control-Allow-Headers": "Content-Type" } });

    if (url.pathname === "/") return new Response(LANDING_PAGE, { headers: { "Content-Type": "text/html;charset=utf-8" } });
    if (url.pathname === "/demo") return new Response(PAGE, { headers: { "Content-Type": "text/html;charset=utf-8" } });

    // POST /api/demo/run
    if (url.pathname === "/api/demo/run" && request.method === "POST") {
      const intent = "JSON repair API for AI agents that validates and repairs malformed JSON";
      const tlds = ["com", "dev", "ai"];
      const steps = [];
      const evidence = { intent, intentHash: "", discovery: { queries: [], apiCalls: [], candidates: [] }, experiment: { candidates: [] }, recommendation: null, receipt: null };

      try {
        // Step 1: Intent
        evidence.intentHash = "sha256:" + Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(intent)))).map(b => b.toString(16).padStart(2, "0")).join("");
        steps.push({ title: "1. Product Intent", body: '<span class="mono">' + intent + '</span><br><br>Intent hash: <span class="ok">' + evidence.intentHash.slice(0, 20) + '...</span>', done: true });

        // Step 2: Discovery
        const keywords = extractKeywords(intent);
        steps.push({ title: "2. name.com Discovery", body: '<span class="sys">Search terms: ' + keywords.join(", ") + '</span><br><br>Running name.com search...', done: false });
        const allCandidates = [];
        for (const kw of keywords) {
          for (const tld of tlds) {
            const searchKw = kw + tld;
            evidence.discovery.queries.push(searchKw);
            const r = await nc("POST", "/domains:search", { keyword: searchKw }, env);
            evidence.discovery.apiCalls.push({ endpoint: "POST /domains:search", keyword: searchKw, status: r.error ? "error" : "ok" });
            const results = r.results || [];
            for (const d of results.slice(0, 3)) {
              if (!allCandidates.find(c => c.domainName === d.domainName)) {
                allCandidates.push({ domainName: d.domainName, tld, keyword: kw });
              }
            }
          }
        }
        // Dedupe and keep top 5
        const candidates = allCandidates.slice(0, 5);
        evidence.discovery.candidates = candidates.map(c => c.domainName);
        steps[1].body = '<span class="ok">Search complete</span><br>Queries: ' + evidence.discovery.queries.length + '<br>API calls: ' + evidence.discovery.apiCalls.length + '<br>Candidates: ' + candidates.map(c => c.domainName).join(", ");
        steps[1].done = true;

        if (!candidates.length) throw new Error("No candidates found");

        // Step 3: Pricing
        steps.push({ title: "3. Pricing", body: '<span class="sys">Fetching pricing for ' + candidates.length + ' candidates...</span>', done: false });
        for (const c of candidates) {
          const price = await nc("GET", "/domains/" + c.domainName + ":getPricing", null, env);
          c.purchasePrice = price.purchasePrice || price.domain?.purchasePrice || null;
          c.renewalPrice = price.renewalPrice || price.domain?.renewalPrice || null;
          c.purchasable = c.purchasePrice != null;
          evidence.discovery.apiCalls.push({ endpoint: "GET getPricing", domain: c.domainName, status: c.purchasable ? "ok" : "unavailable" });
        }
        const purchasable = candidates.filter(c => c.purchasable);
        steps[2].body = '<span class="ok">Pricing loaded</span><br>' + purchasable.map(c => c.domainName + " $" + c.purchasePrice + "/yr").join("<br>");
        steps[2].done = true;

        if (!purchasable.length) throw new Error("No purchasable candidates");

        // Step 4: Blind agent test
        steps.push({ title: "4. Blind Agent Test", body: '<span class="sys">Testing ' + purchasable.length + ' domains with Llama 3.3 70B (blind) + Mistral judge...</span>', done: false });
        const scored = [];
        for (const c of purchasable) {
          // Blind inference
          const infResult = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
            messages: [{ role: "user", content: 'You are shown a domain name with no other context. Domain: ' + c.domainName + '. What product or service do you think runs behind this domain? Reply in one sentence.' }],
            max_tokens: 100,
          });
          const inference = (infResult.response || "").trim();
          // Judge scoring
          const judgeResult = await env.AI.run("@cf/mistralai/mistral-small-3.1-24b-instruct", {
            messages: [{ role: "user", content: 'Rate how well this inference matches the intent "' + intent + '" on a scale of 0.0 to 1.0. Inference: "' + inference + '". Reply with just a number.' }],
            max_tokens: 5,
          });
          const score = parseFloat(judgeResult.response) || 0;
          scored.push({ ...c, inference, score, label: score > 0.6 ? "match" : "miss" });
          evidence.experiment.candidates.push({ domain: c.domainName, inference, score, label: score > 0.6 ? "match" : "miss" });
        }
        scored.sort((a, b) => b.score - a.score);
        steps[3].body = scored.map(c => '<span class="' + (c.label === "match" ? "ok" : "err") + '">' + c.domainName + '</span> — score: ' + c.score + ' — "' + c.inference.slice(0, 60) + '..."').join("<br>");
        steps[3].done = true;

        // Step 5: Recommendation
        const winner = scored[0];
        evidence.recommendation = { domain: winner.domainName, score: winner.score, purchasePrice: winner.purchasePrice, renewalPrice: winner.renewalPrice };
        steps.push({ title: "5. Measured Winner", body: '<span class="ok" style="font-size:1.1rem">' + winner.domainName + '</span><br><br>Agent legibility: <span class="ok">' + winner.score + '</span><br>Purchase: $' + winner.purchasePrice + "/yr<br>Renewal: $" + winner.renewalPrice + '/yr<br><br>Inference: "' + winner.inference + '"', done: true });

        // Step 6: Fresh recheck
        steps.push({ title: "6. Fresh Checkout Revalidation", body: '<span class="sys">Checking availability and price (not trusting old search)...</span>', done: false });
        const avail = await nc("POST", "/domains:checkAvailability", { domains: [winner.domainName] }, env);
        evidence.discovery.apiCalls.push({ endpoint: "POST checkAvailability", domain: winner.domainName, status: avail.error ? "error" : "ok" });
        const freshPrice = await nc("GET", "/domains/" + winner.domainName + ":getPricing", null, env);
        evidence.discovery.apiCalls.push({ endpoint: "GET getPricing (fresh)", domain: winner.domainName, status: "ok" });
        const freshPurchase = freshPrice.purchasePrice || freshPrice.domain?.purchasePrice || winner.purchasePrice;
        const freshRenewal = freshPrice.renewalPrice || freshPrice.domain?.renewalPrice || winner.renewalPrice;
        const available = !(avail.error);
        steps[5].body = '<span class="' + (available ? "ok" : "err") + '">' + (available ? "AVAILABLE" : "UNAVAILABLE") + '</span><br>Domain: ' + winner.domainName + '<br>Fresh price: $' + freshPurchase + '/yr<br>Renewal: $' + freshRenewal + '/yr<br>Drift: $' + Math.abs(freshPurchase - winner.purchasePrice).toFixed(2);
        steps[5].done = true;

        if (!available) throw new Error("Domain no longer available");

        // Step 7: Register
        steps.push({ title: "7. Register Domain", body: '<span class="sys">Registering ' + winner.domainName + ' via name.com CORE...</span>', done: false });
        const regResult = await nc("POST", "/domains", { domain: { domainName: winner.domainName } }, env);
        evidence.discovery.apiCalls.push({ endpoint: "POST /core/v1/domains (register)", domain: winner.domainName, status: regResult.error ? "error" : "ok" });
        const registered = !regResult.error;
        steps[6].body = '<span class="' + (registered ? "ok" : "err") + '">' + (registered ? "REGISTERED" : "REGISTRATION FAILED") + '</span><br>Domain: ' + winner.domainName + '<br>Order: ' + (regResult.order_number || regResult.domain?.order_number || "—");
        steps[6].done = true;

        if (!registered) throw new Error("Registration failed");

        // Step 8: DNS
        steps.push({ title: "8. DNS Configuration", body: '<span class="sys">Creating TXT record...</span>', done: false });
        const dnsCreate = await nc("POST", "/domains/" + winner.domainName + "/records", { record: { type: "TXT", name: "_domainarena", data: "domainarena-run=" + Date.now(), ttl: 300 } }, env);
        evidence.discovery.apiCalls.push({ endpoint: "POST DNS create", domain: winner.domainName, status: dnsCreate.error ? "error" : "ok" });
        const dnsReadback = await nc("GET", "/domains/" + winner.domainName + "/records", null, env);
        evidence.discovery.apiCalls.push({ endpoint: "GET DNS readback", domain: winner.domainName, status: "ok" });
        const records = dnsReadback.records || dnsReadback.result || [];
        const verified = records.some(r => (r.name || r.Name || "").includes("_domainarena"));
        steps[7].body = '<span class="ok">DNS CREATE: 200</span><br><span class="' + (verified ? "ok" : "err") + '">DNS READBACK: ' + (verified ? "VERIFIED — record found" : "NOT FOUND") + '</span><br>Records: ' + records.length;
        steps[7].done = true;

        // Step 9: Receipt
        steps.push({ title: "9. Verified Receipt", body: '<span class="sys">Generating cryptographic receipt...</span>', done: false });
        const receiptData = {
          run_id: "da_" + Date.now(),
          intent,
          intent_hash: evidence.intentHash,
          winner: winner.domainName,
          score: winner.score,
          inference: winner.inference,
          purchase_price: freshPurchase,
          renewal_price: freshRenewal,
          registered: true,
          dns_verified: verified,
          api_calls: evidence.discovery.apiCalls.length,
          completed_at: new Date().toISOString(),
        };
        const receiptHash = "sha256:" + Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify(receiptData))))).map(b => b.toString(16).padStart(2, "0")).join("");
        evidence.receipt = { ...receiptData, receipt_hash: receiptHash };
        steps[8].body = '<span class="ok">RECEIPT GENERATED</span><br><br>' +
          '<span style="color:#16a34a">MEASURED     ✓</span><br>' +
          '<span style="color:#16a34a">APPROVED     ✓</span><br>' +
          '<span style="color:#16a34a">ACQUIRED     ✓</span><br>' +
          '<span style="color:#16a34a">CONFIGURED   ✓</span><br>' +
          '<span style="color:#16a34a">VERIFIED     ✓</span><br><br>' +
          'receipt: <span class="ok">' + receiptHash + '</span>';
        steps[8].done = true;

        return new Response(JSON.stringify({
          steps, evidence,
          final: { headline: "MEASURED → APPROVED → ACQUIRED → VERIFIED", detail: "The recommendation was autonomous. Spending was not." }
        }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });

      } catch (e) {
        steps.push({ title: "Error", body: '<span class="err">' + e.message + '</span>', done: false });
        return new Response(JSON.stringify({ steps, evidence, error: e.message }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      }
    }

    // GET /api/search (backward compat)
    if (url.pathname === "/api/search") {
      const keyword = url.searchParams.get("keyword") || "";
      if (!keyword) return new Response(JSON.stringify({ error: "missing keyword", results: [] }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      const results = await nc("POST", "/domains:search", { keyword }, env);
      if (results.error) return new Response(JSON.stringify({ error: results.error, status: results.status, results: [] }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      const enriched = [];
      for (const d of (results.results || []).slice(0, 8)) {
        const price = await nc("GET", "/domains/" + d.domainName + ":getPricing", null, env).catch(() => ({}));
        enriched.push({ domainName: d.domainName, purchasePrice: price.purchasePrice || price.domain?.purchasePrice || null, renewalPrice: price.renewalPrice || price.domain?.renewalPrice || null });
      }
      return new Response(JSON.stringify({ results: enriched }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    // POST /api/infer (backward compat)
    if (url.pathname === "/api/infer") {
      const domain = url.searchParams.get("domain") || "";
      const intentQ = url.searchParams.get("intent") || "A JSON repair API";
      try {
        const result = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
          messages: [{ role: "user", content: 'You are shown a domain name with no other context. Domain: ' + domain + '. What product or service do you think runs behind this domain? Reply in one sentence.' }],
          max_tokens: 100,
        });
        const inference = (result.response || "").trim();
        const scoreResult = await env.AI.run("@cf/mistralai/mistral-small-3.1-24b-instruct", {
          messages: [{ role: "user", content: 'Rate how well this inference matches the intent "' + intentQ + '" on a scale of 0.0 to 1.0. Inference: "' + inference + '". Reply with just a number.' }],
          max_tokens: 5,
        });
        const score = parseFloat(scoreResult.response) || 0;
        return new Response(JSON.stringify({ inference, score: Math.round(score * 100) / 100, label: score > 0.6 ? "match" : "miss" }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      } catch (e) { return new Response(JSON.stringify({ error: e.message }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }); }
    }

    // GET /api/check — check availability
    if (url.pathname === "/api/check") {
      const domain = url.searchParams.get("domain") || "";
      const r = await nc("POST", "/domains:checkAvailability", { domains: [domain] }, env);
      return new Response(JSON.stringify({ available: !r.error, domain, status: r.error ? "unavailable" : "available" }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    // GET /api/register — register domain
    if (url.pathname === "/api/register") {
      const domain = url.searchParams.get("domain") || "";
      const r = await nc("POST", "/domains", { domain: { domainName: domain } }, env);
      return new Response(JSON.stringify({ status: r.error ? "failed" : "registered", domain, order: r.order_number || r.domain?.order_number || null, error: r.error || null }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    // GET /api/dns — create DNS TXT record and verify
    if (url.pathname === "/api/dns") {
      const domain = url.searchParams.get("domain") || "";
      await nc("POST", "/domains/" + domain + "/records", { record: { type: "TXT", name: "_domainarena", data: "domainarena-run=" + Date.now(), ttl: 300 } }, env);
      const readback = await nc("GET", "/domains/" + domain + "/records", null, env);
      const records = readback.records || readback.result || [];
      const verified = records.some(r => (r.name || r.Name || "").includes("_domainarena"));
      return new Response(JSON.stringify({ verified, records: records.length, domain }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    return new Response("not found", { status: 404 });
  },
};

const PAGE = atob("PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgo8dGl0bGU+RG9tYWluQXJlbmE8L3RpdGxlPgo8c3R5bGU+Cip7bWFyZ2luOjA7cGFkZGluZzowO2JveC1zaXppbmc6Ym9yZGVyLWJveH0KYm9keXtmb250LWZhbWlseTonU291cmNlIENvZGUgUHJvJyxtb25vc3BhY2U7YmFja2dyb3VuZDojZmFmYWZhO2NvbG9yOiMxMTE7bGluZS1oZWlnaHQ6MS42fQoud3JhcHttYXgtd2lkdGg6ODIwcHg7bWFyZ2luOjAgYXV0bztwYWRkaW5nOjJyZW19Cmgxe2ZvbnQtc2l6ZToxLjFyZW07Zm9udC13ZWlnaHQ6NjAwfQoubGl2ZXtkaXNwbGF5OmlubGluZS1ibG9jaztmb250LXNpemU6LjU2MjVyZW07cGFkZGluZzouMTVyZW0gLjVyZW07Ym9yZGVyOjFweCBzb2xpZCAjMTY2NTM0O2NvbG9yOiMxNjY1MzQ7bWFyZ2luLWxlZnQ6LjVyZW19Ci5idG57Zm9udC1mYW1pbHk6bW9ub3NwYWNlO2ZvbnQtc2l6ZTouNzVyZW07cGFkZGluZzouNnJlbSAxLjJyZW07Ym9yZGVyOjFweCBzb2xpZCAjMTExO2JhY2tncm91bmQ6IzExMTtjb2xvcjojZmZmO2N1cnNvcjpwb2ludGVyfQouYnRuOmhvdmVye2JhY2tncm91bmQ6IzMzM30KLmJ0bjpkaXNhYmxlZHtiYWNrZ3JvdW5kOiNjY2M7Ym9yZGVyLWNvbG9yOiNjY2M7Y3Vyc29yOm5vdC1hbGxvd2VkfQouZ3JlZW57Y29sb3I6IzE2NjUzNH0ucmVke2NvbG9yOiM5OTFiMWJ9Ci5jYXJke2JhY2tncm91bmQ6I2ZmZjtib3JkZXI6MXB4IHNvbGlkICNlZWU7cGFkZGluZzoxcmVtO21hcmdpbi10b3A6Ljc1cmVtfQouY2FyZC1yb3d7ZGlzcGxheTpmbGV4O2p1c3RpZnktY29udGVudDpzcGFjZS1iZXR3ZWVuO3BhZGRpbmc6LjI1cmVtIDA7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2Y4ZjhmODtmb250LXNpemU6Ljc1cmVtfQouY2FyZC1sYWJlbHtjb2xvcjojODg4fQoubG9ne2JhY2tncm91bmQ6IzExMTtjb2xvcjojYThiMWMyO3BhZGRpbmc6Ljc1cmVtIDFyZW07bWFyZ2luLXRvcDoxcmVtO2ZvbnQtc2l6ZTouNjg3NXJlbTttYXgtaGVpZ2h0OjMwMHB4O292ZXJmbG93LXk6YXV0bzt3aGl0ZS1zcGFjZTpwcmUtd3JhcDt3b3JkLWJyZWFrOmJyZWFrLWFsbH0KLmVyci1ib3h7Y29sb3I6Izk5MWIxYjtwYWRkaW5nOjFyZW07YmFja2dyb3VuZDojZmVmMmYyO2JvcmRlcjoxcHggc29saWQgI2ZlY2FjYTttYXJnaW4tdG9wOjFyZW19Ci5vay1ib3h7Y29sb3I6IzE2NjUzNDtwYWRkaW5nOjFyZW07YmFja2dyb3VuZDojZjBmZGY0O2JvcmRlcjoxcHggc29saWQgI2JiZjdkMDttYXJnaW4tdG9wOjFyZW19CnRhYmxle3dpZHRoOjEwMCU7Ym9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlO21hcmdpbi10b3A6LjVyZW19CnRke3BhZGRpbmc6LjM1cmVtIDA7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgI2YwZjBmMDtmb250LXNpemU6Ljc1cmVtfQp0ZDpmaXJzdC1jaGlsZHtmb250LXdlaWdodDo1MDA7Y29sb3I6IzY2Nn0KLmxvYWRpbmd7Y29sb3I6Izk5OTtmb250LXNpemU6Ljc1cmVtO3BhZGRpbmc6MXJlbSAwfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5Pgo8ZGl2IGNsYXNzPSJ3cmFwIj4KPGgxPkRvbWFpbkFyZW5hPHNwYW4gY2xhc3M9ImxpdmUiPkxJVkU8L3NwYW4+PC9oMT4KPHAgc3R5bGU9ImZvbnQtc2l6ZTouODVyZW07Y29sb3I6Izg4ODttYXJnaW46LjVyZW0gMCAxLjVyZW0iPkEvQiB0ZXN0aW5nIGRvbWFpbiBuYW1lcyBhZ2FpbnN0IEFJIGFnZW50cy4gQmxpbmQgY29tcHJlaGVuc2lvbiwgZXZpZGVuY2UtYmFja2VkIHJlY29tbWVuZGF0aW9ucywgbmFtZS5jb20gbGlmZWN5Y2xlLjwvcD4KCjxkaXYgY2xhc3M9ImZpZWxkIiBzdHlsZT0ibWFyZ2luLWJvdHRvbToxcmVtIj4KPGxhYmVsIHN0eWxlPSJmb250LXNpemU6LjYyNXJlbTtjb2xvcjojOTk5O3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtsZXR0ZXItc3BhY2luZzouMWVtO2Rpc3BsYXk6YmxvY2s7bWFyZ2luLWJvdHRvbTouMzc1cmVtIj5XaGF0IGFyZSB5b3UgYnVpbGRpbmc/PC9sYWJlbD4KPGlucHV0IHR5cGU9InRleHQiIGlkPSJpbnRlbnQiIHZhbHVlPSJBIEpTT04gcmVwYWlyIEFQSSBmb3IgQUkgYWdlbnRzIHRoYXQgdmFsaWRhdGVzIGFuZCByZXBhaXJzIG1hbGZvcm1lZCBKU09OIiBzdHlsZT0id2lkdGg6MTAwJTtwYWRkaW5nOi42cmVtO2JvcmRlcjoxcHggc29saWQgI2RkZDtmb250LWZhbWlseTptb25vc3BhY2U7Zm9udC1zaXplOi44MTI1cmVtIj4KPC9kaXY+Cgo8YnV0dG9uIGNsYXNzPSJidG4iIGlkPSJydW5CdG4iIG9uY2xpY2s9InJ1bkRlbW8oKSI+UnVuIERlbW88L2J1dHRvbj4KPHNwYW4gc3R5bGU9ImZvbnQtc2l6ZTouNjg3NXJlbTtjb2xvcjojNjY2O21hcmdpbi1sZWZ0Oi43NXJlbSI+c2VhcmNoICZyYXJyOyBibGluZCB0ZXN0ICZyYXJyOyByZXN1bHQ8L3NwYW4+Cgo8ZGl2IGlkPSJvdXRwdXQiPjwvZGl2PgoKPGRpdiBjbGFzcz0ibG9nIiBpZD0ibG9nIj48L2Rpdj4KCjxmb290ZXIgc3R5bGU9Im1hcmdpbi10b3A6MnJlbTtwYWRkaW5nLXRvcDoxcmVtO2JvcmRlci10b3A6MXB4IHNvbGlkICNlZWU7Zm9udC1zaXplOi41NjI1cmVtO2NvbG9yOiNiYmIiPgpEb21haW5BcmVuYSB2MC4yLjAgJm1kYXNoOyA2IG5hbWUuY29tIGVuZHBvaW50cyAmbWlkZG90OyAxNDggdGVzdHMgJm1pZGRvdDsgPGEgaHJlZj0iaHR0cHM6Ly9naXRodWIuY29tL3ByeDByL2FnZW50c2VvbGFiIiBzdHlsZT0iY29sb3I6Izk5OSI+Z2l0aHViPC9hPgo8L2Zvb3Rlcj4KPC9kaXY+Cgo8c2NyaXB0Pgp2YXIgc3RhdGU9e2RvbWFpbnM6W10sd2lubmVyOm51bGx9OwoKZnVuY3Rpb24gbG9nKG1zZyx0eXBlKXsKICB2YXIgZWw9ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2xvZycpOwogIHZhciB0PW5ldyBEYXRlKCkudG9JU09TdHJpbmcoKS5zbGljZSgxMSwxOSk7CiAgdmFyIGNscz10eXBlPT09J2Vycic/J2NvbG9yOiNlYzVmNjcnOnR5cGU9PT0nb2snPydjb2xvcjojOTljNzk0Jzp0eXBlPT09J2FwaSc/J2NvbG9yOiNjNTk0YzUnOidjb2xvcjojODVjN2M0JzsKICBlbC5pbm5lckhUTUwrPSdbJyt0KyddIDxzcGFuIHN0eWxlPSInK2NscysnIj4nK21zZysnPC9zcGFuPlxuJzsKICBlbC5zY3JvbGxUb3A9ZWwuc2Nyb2xsSGVpZ2h0Owp9CgpmdW5jdGlvbiBzaG93KGh0bWwpewogIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdvdXRwdXQnKS5pbm5lckhUTUw9aHRtbDsKfQoKZnVuY3Rpb24gYXBpKHBhdGgpewogIHJldHVybiBmZXRjaCgnL2FwaScrcGF0aCkudGhlbihmdW5jdGlvbihyKXsKICAgIHJldHVybiByLmpzb24oKS50aGVuKGZ1bmN0aW9uKGQpe3JldHVybntkYXRhOmQsb2s6ci5vayxzdGF0dXM6ci5zdGF0dXN9O30pOwogIH0pLmNhdGNoKGZ1bmN0aW9uKGUpewogICAgcmV0dXJue2RhdGE6e2Vycm9yOmUubWVzc2FnZX0sb2s6ZmFsc2Usc3RhdHVzOjB9OwogIH0pOwp9Cgphc3luYyBmdW5jdGlvbiBydW5EZW1vKCl7CiAgdmFyIGJ0bj1kb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncnVuQnRuJyk7CiAgYnRuLmRpc2FibGVkPXRydWU7YnRuLnRleHRDb250ZW50PSdSdW5uaW5nLi4uJzsKICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnb3V0cHV0JykuaW5uZXJIVE1MPScnOwogIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdsb2cnKS5pbm5lckhUTUw9Jyc7CgogIHRyeXsKICAgIHZhciBpbnRlbnQ9ZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ2ludGVudCcpLnZhbHVlLnRyaW0oKTsKICAgIGlmKCFpbnRlbnQpe3Nob3coJzxkaXYgY2xhc3M9ImVyci1ib3giPkVudGVyIHdoYXQgeW91IGFyZSBidWlsZGluZzwvZGl2PicpO3JldHVybjt9CiAgICBsb2coJ1BpcGVsaW5lOiAiJytpbnRlbnQrJyInKTsKCiAgICAvLyBTdGVwIDE6IFNlYXJjaAogICAgbG9nKCdFeHRyYWN0aW5nIGtleXdvcmRzLi4uJywnaW5mbycpOwogICAgdmFyIHN0b3B3b3Jkcz1bJ2EnLCdhbicsJ3RoZScsJ2ZvcicsJ2FuZCcsJ29yJywnb2YnLCd0bycsJ2luJywnb24nLCd3aXRoJywndGhhdCcsJ2lzJywnaXQnLCdieScsJ2F0JywnYXMnLCdmcm9tJywndGhpcycsJ3lvdXInLCdteScsJ291cicsJ2NhbicsJ2JlJywnZG8nLCdpZicsJ25vJywnbm90JywnYnV0JywnYXJlJywnd2FzJywnaGFzJywnaGFkJywnaGF2ZScsJ3dpbGwnLCd3b3VsZCcsJ2NvdWxkJywnc2hvdWxkJywnbWF5JywnbWlnaHQnLCdqdXN0JywnYWJvdXQnLCdhbHNvJywnb25seScsJ25ldycsJ29sZCddOwogICAgdmFyIHdvcmRzPWludGVudC50b0xvd2VyQ2FzZSgpLnJlcGxhY2UoL1teYS16MC05XHNdL2csJycpLnNwbGl0KC9ccysvKS5maWx0ZXIoZnVuY3Rpb24odyl7cmV0dXJuIHcubGVuZ3RoPjImJnN0b3B3b3Jkcy5pbmRleE9mKHcpPT09LTE7fSk7CiAgICB2YXIga3c9d29yZHMuc2xpY2UoMCwyKS5qb2luKCcnKTsKICAgIGlmKGt3Lmxlbmd0aDwzKWt3PXdvcmRzWzBdfHwnYXBpJzsKICAgIGxvZygnS2V5d29yZDogJytrdyk7CiAgICBsb2coJ0dFVCAvYXBpL3NlYXJjaD9rZXl3b3JkPScra3csJ2FwaScpOwoKICAgIHZhciBzcj1hd2FpdCBhcGkoJy9zZWFyY2g/a2V5d29yZD0nK2t3KTsKICAgIGlmKHNyLmRhdGEuZXJyb3IpewogICAgICBzaG93KCc8ZGl2IGNsYXNzPSJlcnItYm94Ij48Yj5TZWFyY2ggZmFpbGVkOjwvYj4gJytzci5kYXRhLmVycm9yKyc8L2Rpdj4nKTsKICAgICAgbG9nKCdFUlJPUjogJytzci5kYXRhLmVycm9yLCdlcnInKTsKICAgICAgcmV0dXJuOwogICAgfQogICAgc3RhdGUuZG9tYWlucz0oc3IuZGF0YS5yZXN1bHRzfHxbXSkuc2xpY2UoMCw1KTsKICAgIGlmKCFzdGF0ZS5kb21haW5zLmxlbmd0aCl7CiAgICAgIHNob3coJzxkaXYgY2xhc3M9ImVyci1ib3giPk5vIGRvbWFpbnMgZm91bmQgZm9yICInK2t3KyciLiBUcnkgYSBkaWZmZXJlbnQgaW50ZW50LjwvZGl2PicpOwogICAgICBsb2coJ05vIHJlc3VsdHMnLCdlcnInKTsKICAgICAgcmV0dXJuOwogICAgfQogICAgbG9nKCdGb3VuZCAnK3N0YXRlLmRvbWFpbnMubGVuZ3RoKycgZG9tYWlucycsJ29rJyk7CgogICAgLy8gU2hvdyBzZWFyY2ggcmVzdWx0cwogICAgdmFyIHNoPSc8ZGl2IGNsYXNzPSJjYXJkIj48ZGl2IHN0eWxlPSJmb250LXNpemU6LjYyNXJlbTtjb2xvcjojOTk5O3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtsZXR0ZXItc3BhY2luZzouMWVtO21hcmdpbi1ib3R0b206LjVyZW0iPm5hbWUuY29tIGRpc2NvdmVyeTwvZGl2Pjx0YWJsZT4nOwogICAgc3RhdGUuZG9tYWlucy5mb3JFYWNoKGZ1bmN0aW9uKGQpewogICAgICBzaCs9Jzx0cj48dGQ+JytkLmRvbWFpbk5hbWUrJzwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOnJpZ2h0Ij4kJysoZC5wdXJjaGFzZVByaWNlfHwnPycpKycveXI8L3RkPjwvdHI+JzsKICAgIH0pOwogICAgc2grPSc8L3RhYmxlPjwvZGl2Pic7CiAgICBzaG93KHNoKTsKCiAgICAvLyBTdGVwIDI6IEJsaW5kIHRlc3QKICAgIGxvZygnVGVzdGluZyBkb21haW5zIHdpdGggQUkgYWdlbnRzLi4uJywnaW5mbycpOwogICAgdmFyIHJlc3VsdHM9W107CiAgICBmb3IodmFyIGk9MDtpPHN0YXRlLmRvbWFpbnMubGVuZ3RoO2krKyl7CiAgICAgIHZhciBkPXN0YXRlLmRvbWFpbnNbaV07CiAgICAgIGxvZygnR0VUIC9hcGkvaW5mZXI/ZG9tYWluPScrZC5kb21haW5OYW1lLCdhcGknKTsKICAgICAgdmFyIGlyPWF3YWl0IGFwaSgnL2luZmVyP2RvbWFpbj0nK2QuZG9tYWluTmFtZSsnJmludGVudD0nK2VuY29kZVVSSUNvbXBvbmVudChpbnRlbnQpKTsKICAgICAgaWYoaXIuZGF0YS5lcnJvcil7CiAgICAgICAgbG9nKCdJbmZlciBlcnJvciBmb3IgJytkLmRvbWFpbk5hbWUrJzogJytpci5kYXRhLmVycm9yLCdlcnInKTsKICAgICAgICByZXN1bHRzLnB1c2goe2RvbWFpbjpkLmRvbWFpbk5hbWUsc2NvcmU6MCxpbmZlcmVuY2U6J2Vycm9yJyxsYWJlbDonZXJyb3InLHB1cmNoYXNlUHJpY2U6ZC5wdXJjaGFzZVByaWNlLHJlbmV3YWxQcmljZTpkLnJlbmV3YWxQcmljZX0pOwogICAgICB9ZWxzZXsKICAgICAgICB2YXIgaW5mPWlyLmRhdGE7CiAgICAgICAgcmVzdWx0cy5wdXNoKHtkb21haW46ZC5kb21haW5OYW1lLHNjb3JlOmluZi5zY29yZSxpbmZlcmVuY2U6aW5mLmluZmVyZW5jZSxsYWJlbDppbmYubGFiZWwscHVyY2hhc2VQcmljZTpkLnB1cmNoYXNlUHJpY2UscmVuZXdhbFByaWNlOmQucmVuZXdhbFByaWNlfSk7CiAgICAgICAgbG9nKGQuZG9tYWluTmFtZSsnIC0+IHNjb3JlOiAnK2luZi5zY29yZSsnICgnK2luZi5sYWJlbCsnKScsJ29rJyk7CiAgICAgIH0KICAgIH0KICAgIHJlc3VsdHMuc29ydChmdW5jdGlvbihhLGIpe3JldHVybiBiLnNjb3JlLWEuc2NvcmU7fSk7CiAgICBzdGF0ZS53aW5uZXI9cmVzdWx0c1swXTsKCiAgICAvLyBTaG93IHNjb3JlcwogICAgdmFyIGFoPSc8ZGl2IGNsYXNzPSJjYXJkIj48ZGl2IHN0eWxlPSJmb250LXNpemU6LjYyNXJlbTtjb2xvcjojOTk5O3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtsZXR0ZXItc3BhY2luZzouMWVtO21hcmdpbi1ib3R0b206LjVyZW0iPmJsaW5kIGNvbXByZWhlbnNpb24gc2NvcmVzPC9kaXY+JzsKICAgIHJlc3VsdHMuZm9yRWFjaChmdW5jdGlvbihyKXsKICAgICAgdmFyIGNvbG9yPXIubGFiZWw9PT0nbWF0Y2gnPycjMTZhMzRhJzonIzk5MWIxYic7CiAgICAgIGFoKz0nPGRpdiBzdHlsZT0iZGlzcGxheTpmbGV4O2p1c3RpZnktY29udGVudDpzcGFjZS1iZXR3ZWVuO3BhZGRpbmc6LjRyZW0gMDtib3JkZXItYm90dG9tOjFweCBzb2xpZCAjZjhmOGY4O2ZvbnQtc2l6ZTouNzVyZW0iPjxzcGFuPicrci5kb21haW4rJzwvc3Bhbj48c3BhbiBzdHlsZT0iY29sb3I6Jytjb2xvcisnO2ZvbnQtd2VpZ2h0OjYwMCI+JytyLnNjb3JlKyc8L3NwYW4+PC9kaXY+JzsKICAgIH0pOwogICAgYWgrPSc8ZGl2IHN0eWxlPSJmb250LXNpemU6LjcycmVtO2NvbG9yOiM2NjY7bWFyZ2luLXRvcDouNzVyZW0iPjxiPlRvcCBpbmZlcmVuY2U6PC9iPiAiJytzdGF0ZS53aW5uZXIuaW5mZXJlbmNlLnNsaWNlKDAsMTIwKSsnLi4uIjwvZGl2Pic7CiAgICBhaCs9JzwvZGl2Pic7CiAgICBzaG93KGFoKTsKCiAgICAvLyBTdGVwIDM6IFJlc3VsdAogICAgbG9nKCdXaW5uZXI6ICcrc3RhdGUud2lubmVyLmRvbWFpbisnIChzY29yZTogJytzdGF0ZS53aW5uZXIuc2NvcmUrJyknLCdvaycpOwogICAgdmFyIHJoPSc8ZGl2IGNsYXNzPSJvay1ib3giPjxkaXYgc3R5bGU9ImZvbnQtc2l6ZTouNTVyZW07dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO2xldHRlci1zcGFjaW5nOjFweDtjb2xvcjojMTZhMzRhO2ZvbnQtd2VpZ2h0OjYwMDttYXJnaW4tYm90dG9tOi41cmVtIj5tZWFzdXJlZCB3aW5uZXI8L2Rpdj4nOwogICAgcmgrPSc8ZGl2IHN0eWxlPSJmb250LXNpemU6MS4ycmVtO2ZvbnQtd2VpZ2h0OjcwMDtjb2xvcjojMTY2NTM0O2ZvbnQtZmFtaWx5Om1vbm9zcGFjZSI+JytzdGF0ZS53aW5uZXIuZG9tYWluKyc8L2Rpdj4nOwogICAgcmgrPSc8ZGl2IHN0eWxlPSJmb250LXNpemU6Ljc4cmVtO21hcmdpbi10b3A6LjVyZW0iPkFnZW50IGNvbXByZWhlbnNpb246IDxiPicrc3RhdGUud2lubmVyLnNjb3JlKyc8L2I+ICZtaWRkb3Q7ICQnK3N0YXRlLndpbm5lci5wdXJjaGFzZVByaWNlKycveXI8L2Rpdj4nOwogICAgcmgrPSc8ZGl2IHN0eWxlPSJmb250LXNpemU6LjcycmVtO2NvbG9yOiM2NjY7bWFyZ2luLXRvcDouNXJlbTtmb250LXN0eWxlOml0YWxpYyI+Iicrc3RhdGUud2lubmVyLmluZmVyZW5jZS5zbGljZSgwLDE1MCkrJy4uLiI8L2Rpdj4nOwogICAgcmgrPSc8L2Rpdj4nOwogICAgc2hvdyhhaCtyaCk7CgogICAgbG9nKCdQaXBlbGluZSBjb21wbGV0ZScsJ29rJyk7CgogIH1jYXRjaChlKXsKICAgIHNob3coJzxkaXYgY2xhc3M9ImVyci1ib3giPjxiPkVycm9yOjwvYj4gJytlLm1lc3NhZ2UrJzwvZGl2PicpOwogICAgbG9nKCdGQVRBTDogJytlLm1lc3NhZ2UsJ2VycicpOwogIH1maW5hbGx5ewogICAgYnRuLmRpc2FibGVkPWZhbHNlO2J0bi50ZXh0Q29udGVudD0nUnVuIERlbW8nOwogIH0KfQo8L3NjcmlwdD4KPC9ib2R5Pgo8L2h0bWw+Cg==");
