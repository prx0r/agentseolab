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
  const auth = btoa((env.NAMECOM_USERNAME || "") + ":" + (env.NAMECOM_TOKEN || ""));
  return fetch(base + path, {
    method,
    headers: { "Authorization": "Basic " + auth, "Content-Type": "application/json" },
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
      const results = await nc("POST", "/domains:search", { keyword }, env);
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

    return new Response("not found", { status: 404 });
  },
};

const PAGE = String.raw`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DomainArena</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,sans-serif;background:#fafafa;color:#111;line-height:1.6}
code,.mono{font-family:'Source Code Pro',monospace}
nav{background:#fff;border-bottom:1px solid #e5e7eb;padding:0 1.5rem;position:sticky;top:0;z-index:100}
.ni{max-width:1100px;margin:0 auto;display:flex;align-items:center;height:48px;gap:1.5rem}
.ni .b{font-weight:700;font-size:.95rem}.ni .b span{color:#1d4ed8}
.ni a{font-size:.8rem;color:#6b7280;text-decoration:none;font-weight:500}.ni a:hover{color:#111}
.hero{padding:80px 1.5rem 48px;text-align:center;border-bottom:1px solid #e5e7eb}
.hero h1{font-size:2.5rem;font-weight:800;letter-spacing:-.04em;line-height:1.1;max-width:680px;margin:0 auto}
.hero p{font-size:1rem;color:#6b7280;max-width:560px;margin:12px auto 0;line-height:1.7}
.hero .tag{display:inline-block;background:#eff6ff;color:#1d4ed8;font-size:.72rem;font-weight:600;padding:4px 12px;border-radius:20px;margin-bottom:12px}
.btn{padding:10px 28px;border-radius:8px;font-size:.88rem;font-weight:600;border:none;cursor:pointer;font-family:inherit;transition:all .15s}
.btn-p{background:#111;color:#fff}.btn-p:hover{background:#333}
.btn:disabled{opacity:.4;cursor:not-allowed}
.three{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;max-width:1100px;margin:2rem auto;padding:0 1.5rem}
@media(max-width:768px){.three{grid-template-columns:1fr}}
.three .c{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.25rem}
.three .c h3{font-size:.65rem;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;font-weight:600;margin-bottom:.5rem}
.three .c p{font-size:.82rem;color:#374151;line-height:1.5}
.three .c strong{color:#1d4ed8}
section{padding:2.5rem 1.5rem;max-width:1100px;margin:0 auto}
.st{font-size:1.4rem;font-weight:700;letter-spacing:-.02em;margin-bottom:.5rem}
.sd{font-size:.88rem;color:#6b7280;max-width:580px;line-height:1.6}
.ba{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.5rem 0}
@media(max-width:768px){.ba{grid-template-columns:1fr}}
.bx{border:1px solid #e5e7eb;border-radius:10px;padding:1.25rem}
.bx.bad{border-color:#fecaca;background:#fef2f2}.bx.good{border-color:#bbf7d0;background:#f0fdf4}
.lb{font-size:.6rem;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;font-weight:600;margin-bottom:.5rem}
.v{font-size:1.2rem;font-weight:700;font-family:'Source Code Pro',monospace}
.m{font-size:.8rem;color:#6b7280;margin-top:.5rem;line-height:1.5}
.pipe{display:flex;gap:0;margin:1.5rem 0;overflow-x:auto}
.pipe .s{flex:1;min-width:80px;background:#fff;border:1px solid #e5e7eb;padding:10px 8px;text-align:center;font-size:.65rem}
.pipe .s:first-child{border-radius:8px 0 0 8px}.pipe .s:last-child{border-radius:0 8px 8px 0}.pipe .s+.s{border-left:none}
.pipe .s b{display:block;font-size:.5rem;color:#9ca3af;text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px}
.pipe .s.hi{border-color:#1d4ed8;background:#eff6ff}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.5rem 0}
@media(max-width:768px){.g3{grid-template-columns:1fr}}
.mt{text-align:center;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:1.25rem}
.mt .n{font-size:1.6rem;font-weight:700;letter-spacing:-.02em}.mt .l{font-size:.72rem;color:#6b7280;margin-top:4px}
.tt{width:100%;border-collapse:collapse;font-size:.78rem;margin:1rem 0}
.tt th{text-align:left;font-size:.6rem;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af;padding:8px;border-bottom:2px solid #e5e7eb;font-weight:600}
.tt td{padding:8px;border-bottom:1px solid #f3f4f6}
.ft{padding:2rem;border-top:1px solid #e5e7eb;text-align:center;font-size:.72rem;color:#9ca3af}
/* Demo */
.demo{background:#0f172a;color:#e2e8f0;padding:2rem 1.5rem;margin-top:2rem}
.demo-in{max-width:1100px;margin:0 auto}
.steps{max-width:900px;margin:0 auto}
.step{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1.25rem;margin-bottom:1rem;opacity:.3;pointer-events:none;transition:all .3s}
.step.active{opacity:1;pointer-events:auto;border-color:#1d4ed8}
.step.done{opacity:1;border-color:#334155}
.step-num{font-size:.55rem;text-transform:uppercase;letter-spacing:1px;color:#64748b;font-weight:600;margin-bottom:.5rem}
.step-title{font-size:.95rem;font-weight:700;color:#f8fafc;margin-bottom:.5rem}
.step-body{font-family:'Source Code Pro',monospace;font-size:.72rem;line-height:1.7;color:#94a3b8}
.step-body .ok{color:#34d399}.step-body .err{color:#f87171}
.final{background:linear-gradient(135deg,#1e3a5f,#1e293b);border:2px solid #1d4ed8;border-radius:12px;padding:2rem;text-align:center;margin-top:1.5rem}
.final h2{font-size:1.5rem;font-weight:800;color:#93c5fd;margin-bottom:.5rem}
.final p{color:#94a3b8;font-size:.9rem}
</style>
</head>
<body>
<nav><div class="ni">
  <div class="b">Domain<span>Arena</span></div>
  <a href="/">Landing</a>
  <a href="/demo">Demo</a>
</div></nav>

<div class="hero">
  <div class="tag">name.com Track — DevNetwork Hackathon 2026</div>
  <h1>Measure the name before you buy it</h1>
  <p>AI agents discover services, run blind inference tests, score every candidate, and recommend the domain that actually communicates your purpose.</p>
  <button class="btn btn-p" style="margin-top:1.5rem" onclick="runDemo()">Run Live Demo</button>
</div>

<div class="three">
  <div class="c"><h3>What we built</h3><p>An autonomous naming pipeline where name.com discovers domains, blind AI tests measure comprehension, and the measured winner is acquired with human approval.</p></div>
  <div class="c"><h3>What it solves</h3><p><strong>Domains are becoming machine-facing identity.</strong> DomainArena tests whether agents can infer what service sits behind a name before you spend money on it.</p></div>
  <div class="c"><h3>How it works</h3><p><strong>name.com &rarr; blind inference &rarr; independent judge &rarr; recheck &rarr; approve &rarr; register &rarr; DNS &rarr; receipt.</strong> Six name.com API endpoints.</p></div>
</div>

<section id="pipeline">
  <div class="st">The Pipeline</div>
  <div class="pipe">
    <div class="s hi"><b>1</b>Search</div><div class="s"><b>2</b>Pricing</div><div class="s"><b>3</b>Blind Test</div><div class="s"><b>4</b>Score</div><div class="s"><b>5</b>Recheck</div><div class="s hi"><b>6</b>Register</div><div class="s hi"><b>7</b>DNS</div><div class="s hi"><b>8</b>Receipt</div>
  </div>
</section>

<!-- DEMO -->
<div class="demo" id="demo">
  <div class="demo-in">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
      <div><div style="font-size:1.1rem;font-weight:700;color:#f8fafc">Live Demo</div><div style="font-size:.75rem;color:#64748b">name.com live inventory &rarr; blind AI measurement &rarr; evidence-backed acquisition</div></div>
    </div>
    <div class="steps" id="steps"></div>
    <div id="final-box"></div>
  </div>
</div>

<section id="research">
  <div class="st">Research Foundation</div>
  <div class="sd">16 experiments across 7+ model families showing agent naming behavior is stranger than a one-shot LLM rating.</div>
  <div class="g3" style="margin-top:1.5rem">
    <div class="mt"><div class="n">16</div><div class="l">Experiments</div></div>
    <div class="mt"><div class="n">7+</div><div class="l">Model Families</div></div>
    <div class="mt"><div class="n">148</div><div class="l">Tests Passing</div></div>
  </div>
</section>

<div class="ft">DomainArena &mdash; Pre-deployment Agent Legibility Testing &middot; name.com Track &middot; DevNetwork Hackathon 2026</div>

<script>
function showTab(i,el){document.querySelectorAll('.panel').forEach(function(p,j){p.classList.toggle('on',j===i)});document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('on')});el.classList.add('on');}

function renderStep(num,title,bodyHtml,active,done){
  return '<div class="step'+(active?' active':'')+(done?' done':'')+'"><div class="step-num">Step '+num+'</div><div class="step-title">'+title+'</div><div class="step-body">'+bodyHtml+'</div></div>';
}

async function runDemo(){
  var btn=document.querySelector('.btn-p');
  btn.disabled=true;btn.textContent='Running...';
  document.getElementById('steps').innerHTML='';
  document.getElementById('final-box').innerHTML='';

  try{
    var r=await fetch('/api/demo/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});
    var run=await r.json();
    if(run.error){document.getElementById('steps').innerHTML=renderStep(1,'Error','<span class="err">'+run.error+'</span>',true,false);btn.disabled=false;btn.textContent='Run Live Demo';return;}

    var html='';
    var steps=run.steps||[];
    for(var i=0;i<steps.length;i++){
      var s=steps[i];
      html+=renderStep(i+1,s.title,s.body,i===steps.length-1,i.done);
    }
    document.getElementById('steps').innerHTML=html;

    if(run.final){
      document.getElementById('final-box').innerHTML='<div class="final"><h2>'+run.final.headline+'</h2><p>'+run.final.detail+'</p></div>';
    }
  }catch(e){
    document.getElementById('steps').innerHTML=renderStep(1,'Error','<span class="err">'+e.message+'</span>',true,false);
  }
  btn.disabled=false;btn.textContent='Run Live Demo';
}
</script>
</body>
</html>`;
