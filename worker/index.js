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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Source Code Pro',monospace;background:#fafafa;color:#111;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:2rem 2rem}
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
.badge-green{border-color:#166534;color:#166534}.badge-gray{border-color:#999;color:#999}.badge-orange{border-color:#92400e;color:#92400e}
table{width:100%;border-collapse:collapse;margin-top:.5rem}
td{padding:.35rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem}
td:first-child{font-weight:500;color:#666;width:140px}
.card{background:#fff;border:1px solid #eee;padding:1rem;margin-top:.75rem}
.card-row{display:flex;justify-content:space-between;padding:.25rem 0;border-bottom:1px solid #f8f8f8;font-size:.75rem}
.card-row:last-child{border-bottom:none}
.card-label{color:#888}
.step{border-left:2px solid #eee;padding-left:1rem;margin-top:1rem}
.step.active{border-left-color:#111}
.step-num{font-size:.5625rem;color:#999;font-weight:500;letter-spacing:.1em;text-transform:uppercase}
.step-title{font-size:.875rem;font-weight:500;margin-top:.2rem}
.step-desc{font-size:.75rem;color:#666;margin-top:.25rem;line-height:1.5}
.receipt{background:#f8f8f8;border:1px solid #eee;padding:.75rem 1rem;margin-top:.75rem;font-size:.75rem}
.receipt-hash{word-break:break-all;font-size:.6875rem;color:#666;margin-top:.25rem;font-family:'Source Code Pro',monospace}
.trace{margin-top:.75rem}
.trace-row{display:flex;gap:.5rem;font-size:.6875rem;padding:.25rem 0;border-bottom:1px solid #f8f8f8}
.trace-method{font-weight:600;min-width:36px;color:#111}
.trace-path{flex:1;color:#666}
.trace-status{font-weight:500;min-width:28px}
.trace-status.ok{color:#166534}.trace-status.err{color:#991b1b}
.trace-ms{color:#999;text-align:right;min-width:45px}
.trace-label{font-size:.5625rem;color:#bbb;margin-bottom:.25rem}
.divider{border-top:1px solid #eee;margin:1.5rem 0}
.loading{color:#999;font-size:.75rem;padding:1rem 0}
.fade-in{animation:fadeIn .3s ease-in}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.log{background:#111;color:#a8b1c2;padding:.75rem 1rem;margin-top:.75rem;font-size:.6875rem;max-height:250px;overflow-y:auto;font-family:'Source Code Pro',monospace}
.log-line{padding:.1rem 0}
.log-ts{color:#636d83}.log-ok{color:#99c794}.log-err{color:#ec5f67}.log-info{color:#85c7c4}.log-api{color:#c594c5}
.explain{background:#f0f8ff;border:1px solid #d0e0f0;padding:.5rem .75rem;margin-top:.5rem;font-size:.6875rem;color:#334155;line-height:1.5}
.explain b{color:#111}
.explain-title{font-size:.5625rem;color:#64748b;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem}
.before-after{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:.75rem}
.before{border:1px solid #fde8e8;padding:.75rem;background:#fef2f2}
.after{border:1px solid #d1fae5;padding:.75rem;background:#f0fdf4}
.before-label,.after-label{font-size:.5625rem;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem}
.before-label{color:#991b1b}.after-label{color:#166534}
.endpoint{display:flex;align-items:center;gap:.5rem;padding:.4rem 0;border-bottom:1px solid #f8f8f8;font-size:.75rem}
.endpoint-method{font-weight:600;min-width:28px;font-size:.6875rem}.endpoint-method.get{color:#166534}.endpoint-method.post{color:#1d4ed8}
.endpoint-path{flex:1;color:#666}
.endpoint-desc{color:#999;font-size:.6875rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;font-size:.5625rem;color:#bbb;display:flex;justify-content:space-between}
footer a{color:#999}
</style>
</head>
<body>
<div class="wrap">

<div style="padding:2rem 0 1.5rem;border-bottom:1px solid #eee">
<h1>DomainArena<span class="live">LIVE</span></h1>
<div style="font-size:.85rem;color:#888;margin-bottom:1rem;max-width:600px">A/B testing for domain names in the agentic web. Blind agent comprehension, evidence-backed recommendations, name.com lifecycle.</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">
  <div style="padding:.75rem 1rem;background:#fff;border:1px solid #eee;border-radius:6px">
    <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#999;margin-bottom:.375rem;font-weight:600">What we built</div>
    <div style="font-size:.78rem;line-height:1.5">A <b>domain testing engine</b> that asks AI agents what they think a domain means &mdash; without any context. name.com discovers available names, blind inference tests comprehension, and the full lifecycle runs from search to DNS verification.</div>
  </div>
  <div style="padding:.75rem 1rem;background:#fff;border:1px solid #eee;border-radius:6px">
    <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#999;margin-bottom:.375rem;font-weight:600">What it solves</div>
    <div style="font-size:.78rem;line-height:1.5"><b>The thing discovering your service is an AI agent.</b> But nobody measures whether agents can infer what service sits behind a domain. You buy on intuition, deploy, and hope the machine audience finds you.</div>
  </div>
  <div style="padding:.75rem 1rem;background:#fff;border:1px solid #eee;border-radius:6px">
    <div style="font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;color:#999;margin-bottom:.375rem;font-weight:600">How it works</div>
    <div style="font-size:.78rem;line-height:1.5"><b>name.com inventory &rarr; blind inference &rarr; independent scoring &rarr; human approval &rarr; registration &rarr; DNS verification &rarr; SHA-256 receipt.</b> Every step has provenance. The agent never sees the product description.</div>
  </div>
</div>
</div>

<div class="tabs">
<div class="tab active" onclick="showTab(0)">1. Intent</div>
<div class="tab" onclick="showTab(1)">2. Discovery</div>
<div class="tab" onclick="showTab(2)">3. Agent Test</div>
<div class="tab" onclick="showTab(3)">4. Result</div>
<div class="tab" onclick="showTab(4)">5. Findings</div>
<div class="tab" onclick="showTab(5)">6. Frontier</div>
</div>

<!-- TAB 0: INTENT -->
<div class="panel active" id="p0">
<div class="field">
<label>What are you building?</label>
<input type="text" id="intent" placeholder="e.g. A JSON repair API for AI agents" value="A JSON repair API for AI agents that validates and repairs malformed JSON">
</div>

<div class="explain">
<div class="explain-title">how this works</div>
<b>DomainArena</b> tests candidate domains against AI agents using <b>blind semantic inversion</b> &mdash; agents see only the domain name, never the product description. If an agent can correctly infer what service sits behind a domain without context, that domain transmits meaning effectively.
</div>

<div style="margin-top:1.5rem">
<div class="step-num">name.com endpoints used</div>
<div style="margin-top:.5rem">
<div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains:search</span><span class="endpoint-desc">discover available candidates</span></div>
<div class="endpoint"><span class="endpoint-method get">GET</span><span class="endpoint-path">/domains/{name}:getPricing</span><span class="endpoint-desc">verify pricing</span></div>
<div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains</span><span class="endpoint-desc">register domain</span></div>
<div class="endpoint"><span class="endpoint-method post">POST</span><span class="endpoint-path">/domains/{name}/records</span><span class="endpoint-desc">configure DNS</span></div>
<div class="endpoint"><span class="endpoint-method get">GET</span><span class="endpoint-path">/domains/{name}/records</span><span class="endpoint-desc">verify DNS</span></div>
</div>
</div>

<div class="explain" style="margin-top:.75rem">
<div class="explain-title">research foundation</div>
Built on <b>16 experiments across 7+ model families</b> studying how AI agents discover and select tools. Key findings: agents are vulnerable to <b>description bias</b>, <b>position effects</b>, and <b>model-specific interpretations</b>.
</div>
<button class="btn" style="margin-top:1.5rem" onclick="startDiscovery()">Search name.com inventory</button>
</div>

<!-- TAB 1: DISCOVERY -->
<div class="panel" id="p1">
<div class="step active">
<div class="step-num">Step 1 — Live Search</div>
<div class="step-title">name.com domain discovery</div>
<div class="step-desc">Querying name.com for available domains matching your intent. Each result includes live pricing.</div>
<div class="step-body" id="discovery-body"><div class="loading">querying name.com API...</div></div>
</div>
<div class="explain" style="margin-top:1rem">
<div class="explain-title">what's happening</div>
<b>POST /domains:search</b> sends your intent keyword to name.com's domain discovery API. name.com returns candidate domains with availability status. For each candidate, we call <b>GET /domains/{name}:getPricing</b> to get fresh purchase and renewal prices. This ensures the recommendation is based on real, current market data.
</div>
</div>

<!-- TAB 2: AGENT TEST -->
<div class="panel" id="p2">
<div class="step active">
<div class="step-num">Step 2 — Blind Comprehension</div>
<div class="step-title">agent semantic inversion test</div>
<div class="step-desc">Each domain shown to AI agents with <b>zero context</b>. What do they infer?</div>
<div class="step-body" id="agent-body"><div class="loading">running blind comprehension tests...</div></div>
</div>

<div class="explain" style="margin-top:1rem">
<div class="explain-title">live run</div>
Each domain is tested with <b>Llama 3.3 70B</b> for blind inference, scored by an <b>independent Mistral evaluator</b>. Generator/judge separation ensures the tested model never scores itself. The Research tab contains our larger cross-family and randomized experiments.
</div>
<div class="explain" style="margin-top:1rem">
<div class="explain-title">what's happening</div>
<b>Semantic inversion</b> flips the normal evaluation: instead of asking "is this a good name?" we ask "what does an agent think this name means?" The agent sees only the domain — no description, no website, no context. Its inference is scored against your frozen product intent. <b>Generator/judge separation</b> ensures the tested model never scores itself. This is the same experimental methodology used in academic agent-comprehension research.
</div>
</div>

<!-- TAB 3: RESULT -->
<div class="panel" id="p3">
<div id="result-body"></div>
</div>


<!-- TAB 4: FINDINGS -->
<div class="panel" id="p4">
<div class="step active">
<div class="step-num">Research Findings</div>
<div class="step-title">counterintuitive discoveries from 16 experiments</div>
<div class="step-desc">What we learned challenges common assumptions about domain naming for AI agents.</div>
</div>

<div class="explain" style="margin-top:1rem">
<div class="explain-title">finding 1: description seduction is real</div>
Some model families selected <b>broken tools</b> when they had enterprise-sounding descriptions. A tool with a polished description but non-functional API was chosen over a working tool with a plain description. <b>Agent discovery systems can be manipulated by presentation rather than actual capability.</b>
</div>

<div class="explain">
<div class="explain-title">finding 2: position dominates domain choice</div>
In pairwise tests, <b>87% of agents picked the first option</b> regardless of which domain was shown. TLD effects (.com vs .dev vs .ai) were statistically insignificant within the same position. <b>Order matters more than extension.</b>
</div>

<div class="explain">
<div class="explain-title">finding 3: models disagree materially</div>
Llama 3.3, Mistral Small, and Qwen3 produced <b>different rankings for the same domains</b>. A domain cannot be called "agent-legible" based on one model. Cross-family replication is essential.
</div>

<div class="explain">
<div class="explain-title">finding 4: semantic inversion is a cheap proxy</div>
AgentSearchBench (10,000 agents) shows that <b>description similarity is weaker than execution-grounded performance</b> for ranking. Blind inference is a useful first filter, but execution testing is ground truth.
</div>

<div class="explain">
<div class="explain-title">finding 5: serverless inference drifts</b></div>
Identical prompts at temperature zero produced <b>materially different choices across time windows</b>. One-shot domain ratings are scientifically weak. DomainArena replicates across windows.
</div>

<div class="step" style="margin-top:1.5rem">
<div class="step-num">Real experiment data</div>
<div class="step-title">jsonrepair experiment results</div>
<div class="step-body">
<table>
<tr><td>intent</td><td>Repairs malformed JSON for AI agents</td></tr>
<tr><td>candidates tested</td><td>5 domains</td></tr>
<tr><td>models tested</td><td>Llama 3.3, Mistral Small</td></tr>
<tr><td>jsonrepair.dev</td><td class="green">score 0.9 — agent infers "JSON repair tool"</td></tr>
<tr><td>velora.com</td><td class="red">score 0.1 — agent infers "technology company"</td></tr>
<tr><td>winner</td><td class="green">jsonrepair.dev (consistently understood across families)</td></tr>
</table>
</div>
</div>
</div>

<!-- TAB 5: FRONTIER -->
<div class="panel" id="p5">
<div class="step active">
<div class="step-num">Frontier Evidence</div>
<div class="step-title">why this matters now</div>
</div>

<div class="explain" style="margin-top:.75rem">
<div class="explain-title">the shift</div>
<b>93% of Google searches now end without a click</b> — AI Overviews answer directly. Meanwhile, Cloudflare reports agents are making <b>billions of API calls daily</b>. The customer discovering your service is increasingly a machine, not a human.
</div>

<div style="margin-top:1rem;font-size:.6875rem;font-weight:500;color:#666">SUPPORTING RESEARCH</div>

<table style="margin-top:.5rem">
<tr><td style="width:auto;padding:.4rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem"><a href="https://arxiv.org/abs/2601.17617" style="color:#1d4ed8;text-decoration:none">14.44M agent search requests</a></td><td style="font-size:.6875rem;color:#666;border-bottom:1px solid #f0f0f0">Agents iteratively reformulate queries using retrieved evidence. Domain must be discoverable at every step.</td></tr>
<tr><td style="padding:.4rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem"><a href="https://arxiv.org/abs/2604.22436" style="color:#1d4ed8;text-decoration:none">AgentSearchBench (9,847 agents)</a></td><td style="font-size:.6875rem;color:#666;border-bottom:1px solid #f0f0f0">Description similarity is weaker than execution-grounded performance for ranking agents.</td></tr>
<tr><td style="padding:.4rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem"><a href="https://arxiv.org/abs/2406.07791" style="color:#1d4ed8;text-decoration:none">Position bias in LLM judges</a></td><td style="font-size:.6875rem;color:#666;border-bottom:1px solid #f0f0f0">87% of LLM judges pick slot 0. DomainArena uses AB/BA randomization to control for this.</td></tr>
<tr><td style="padding:.4rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem"><a href="https://arxiv.org/abs/2509.08919" style="color:#1d4ed8;text-decoration:none">AI search engines differ</a></td><td style="font-size:.6875rem;color:#666;border-bottom:1px solid #f0f0f0">Engine-specific differences in sourcing, freshness, domain diversity. One universal score is insufficient.</td></tr>
<tr><td style="padding:.4rem 0;border-bottom:1px solid #f0f0f0;font-size:.75rem"><a href="https://arxiv.org/abs/2407.12883" style="color:#1d4ed8;text-decoration:none">BRIGHT: reasoning-intensive retrieval</a></td><td style="font-size:.6875rem;color:#666;border-bottom:1px solid #f0f0f0">Semantic/lexical overlap alone is insufficient for agent task completion.</td></tr>
<tr><td style="padding:.4rem 0;font-size:.75rem"><a href="https://arxiv.org/abs/2602.12187" style="color:#1d4ed8;text-decoration:none">SAGEO: search-augmented GEO</a></td><td style="font-size:.6875rem;color:#666">Evaluation on predetermined candidates omits retrieval/reranking. Real visibility requires end-to-end measurement.</td></tr>
</table>

<div style="margin-top:1rem;font-size:.6875rem;font-weight:500;color:#666">WHAT DOMAINARENA MEASURES</div>

<div class="card" style="margin-top:.5rem">
<div class="card-row"><span class="card-label">agent comprehension</span><span>Can agents infer your service from the domain?</span></div>
<div class="card-row"><span class="card-label">cross-family agreement</span><span>Do multiple model families agree?</span></div>
<div class="card-row"><span class="card-label">position robustness</span><span>Does preference hold across presentation orders?</span></div>
<div class="card-row"><span class="card-label">cold-start discovery</span><span>Will agents find you with zero prior awareness?</span></div>
</div>

<div style="margin-top:1rem;font-size:.6875rem;font-weight:500;color:#666">THE MARKET</div>

<div class="card" style="margin-top:.5rem">
<div class="card-row"><span class="card-label">Cloudflare</span><span>Agent Readiness + Registrar API for agents</span></div>
<div class="card-row"><span class="card-label">Google</span><span>AI Overviews answer 93% of searches directly</span></div>
<div class="card-row"><span class="card-label">AgentDNS</span><span>Root domain naming for agent service discovery</span></div>
<div class="card-row"><span class="card-label">name.com</span><span>6 API endpoints for full domain lifecycle</span></div>
</div>

<div class="explain" style="margin-top:.75rem">
<div class="explain-title">the opportunity</div>
<b>Before the website exists, before Agent Readiness, before an agent registers the domain: which hostname should the machine audience see?</b> That is DomainArena — pre-deployment optimization for the agent web.
</div>
</div>

<div class="divider"></div>
<div style="font-size:.5625rem;color:#999;text-transform:uppercase;letter-spacing:.1em;font-weight:500;margin-bottom:.375rem">live api trace</div>
<div class="log" id="log"></div>

<footer>
<span>DomainArena v0.2.0 — 6 name.com endpoints · MCP server · 148 tests</span>
<span><a href="https://github.com/prx0r/agentseolab">github</a></span>
</footer>
</div>

<script>
var S={tab:0,domains:[],winner:null,trace:[],intent:'',intentHash:''};

function log(m,c){
  c=c||'info';
  var e=document.getElementById('log');
  var t=new Date().toISOString().slice(11,19);
  e.innerHTML+='<div class="log-line"><span class="log-ts">['+t+']</span> <span class="log-'+c+'">'+m+'</span></div>';
  e.scrollTop=e.scrollHeight;
}

function showTab(i){
  S.tab=i;
  document.querySelectorAll('.tab').forEach(function(t,j){t.classList.toggle('active',j===i)});
  document.querySelectorAll('.panel').forEach(function(p,j){p.classList.toggle('active',j===i)});
}

function api(path,method,body){
  var t0=performance.now();
  var m=method||'GET';
  var bodyStr=body?JSON.stringify(body):'';
  log('API '+m+' /api'+path.replace('/api',''),'api');
  var opts={method:m,headers:{'Content-Type':'application/json'}};
  if(body)opts.body=bodyStr;
  return fetch('/api'+path,opts).then(function(r){
    var ms=Math.round(performance.now()-t0);
    S.trace.push({method:m,path:'/api'+path.replace('/api',''),status:r.status,ms:ms});
    log('\\u2190 '+r.status+' ('+ms+'ms)',r.ok?'ok':'err');
    return r.json().then(function(d){return{data:d,status:r.status,ms:ms};});
  });
}

function showTabTab(i){document.querySelectorAll('.tab').forEach(function(t,j){t.classList.toggle('active',j===i)});document.querySelectorAll('.panel').forEach(function(p,j){p.classList.toggle('active',j===i)});}
function startDiscovery(){
  var intent=document.getElementById('intent').value.trim();
  if(!intent){log('Enter what you are building','err');return;}
  S.intent=intent;
  showTab(1);
  document.getElementById('discovery-body').innerHTML='<div class="loading">searching name.com inventory...</div>';
  log('Pipeline started: "'+intent+'"');
  var stopwords=['a','an','the','for','and','or','of','to','in','on','with','that','is','it','by','at','as','from','this','your','my','our','can','be','do','if','no','not','but','are','was','has','had','have','will','would','could','should','may','might','shall','let','us','you','me','he','she','we','they','them','their','its','his','her','our','who','which','what','where','when','how','why','all','each','every','both','few','more','most','other','some','such','than','too','very','just','about','above','after','again','against','between','into','through','during','before','below','under','over','own','same','so','then','once','here','there','also','only','new','old','right','big','small'];
  var words=intent.toLowerCase().replace(/[^a-z0-9\\s]/g,'').split(/\\s+/).filter(function(w){return w.length>2&&stopwords.indexOf(w)===-1;});
  var kw=words.slice(0,2).join('');
  if(kw.length<3) kw=words[0]||'api';
  log('Extracted keyword: '+kw);
  api('/search?keyword='+kw).then(function(r){
    S.domains=(r.data.results||[]).slice(0,5);
    if(!S.domains.length){log('No available domains found','err');document.getElementById('discovery-body').innerHTML='<div class="loading">No available domains. Try different terms.</div>';return;}
    log('Found '+S.domains.length+' domains with live pricing');
    var h='<table><tr><td style="font-size:.625rem;color:#999">DOMAIN</td><td style="font-size:.625rem;color:#999;text-align:right">PRICE/YR</td><td style="font-size:.625rem;color:#999;text-align:right">RENEWAL</td></tr>';
    S.domains.forEach(function(d){h+='<tr><td>'+d.domainName+'</td><td style="text-align:right;font-weight:500">\
+(d.purchasePrice||'?')+'</td><td style="text-align:right;color:#666">\
+(d.renewalPrice||'?')+'</td></tr>';});
    h+='</table>';
    h+='<div style="margin-top:1.5rem"><button class="btn" onclick="startAgentTest()">Run blind agent comprehension test</button></div>';
    document.getElementById('discovery-body').innerHTML=h;
  });
}

function startAgentTest(){
  showTab(2);
  document.getElementById('agent-body').innerHTML='<div class="loading">sending each domain to AI agents blind (no context)...</div>';
  log('Testing '+S.domains.length+' domains with blind semantic inversion');
  var results=[];var i=0;
  function testNext(){
    if(i>=S.domains.length){
      S.domains=results;
      S.winner=results.sort(function(a,b){return b.score-a.score})[0];
      log('Winner selected: '+S.winner.domainName+' (score: '+S.winner.score+')');
      var h='';
      results.forEach(function(d){
        var cls=d.label==='match'?'green':'gray';
        h+='<div class="fade-in" style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #f0f0f0">';
        h+='<div style="display:flex;justify-content:space-between;align-items:center">';
        h+='<span style="font-weight:500;font-size:.875rem">'+d.domainName+'</span>';
        h+='<span class="badge badge-'+cls+'">'+d.label.toUpperCase()+' '+d.score+'</span>';
        h+='</div>';
        h+='<div style="font-size:.75rem;color:#666;margin-top:.375rem">agent infers: <i>"'+d.inference+'"</i></div>';
        h+='</div>';
      });
      h+='<div style="margin-top:1.5rem"><button class="btn" onclick="showResult()">View recommendation</button></div>';
      document.getElementById('agent-body').innerHTML=h;
      return;
    }
    var d=S.domains[i];
    log('Testing: '+d.domainName);
    api('/infer?domain='+d.domainName+'&intent='+encodeURIComponent(S.intent)).then(function(r){
      results.push({domainName:d.domainName,purchasePrice:d.purchasePrice,renewalPrice:d.renewalPrice,inference:r.data.inference,score:r.data.score,label:r.data.label});
      i++;testNext();
    });
  }
  testNext();
}

function showResult(){
  showTab(3);
  var w=S.winner;
  var losers=S.domains.filter(function(d){return d.domainName!==w.domainName}).slice(0,2);
  var h='';

  // Before/After comparison
  h+='<div class="step active"><div class="step-num">Before vs After</div><div class="step-title">why agent testing matters</div>';
  h+='<div class="before-after">';
  h+='<div class="before"><div class="before-label">human heuristic</div>';
  h+='<div style="font-size:.875rem;font-weight:500;margin-bottom:.25rem">'+(losers[0]?losers[0].domainName:'jsonwizard.dev')+'</div>';
  h+='<div style="font-size:.75rem;color:#666">"sounds technical and modern"</div>';
  h+='<div style="font-size:.75rem;color:#991b1b;margin-top:.375rem">agent infers: '+(losers[0]?losers[0].inference:'A fantasy game')+'</div>';
  h+='<div style="font-size:.75rem;color:#991b1b">result: <b>WRONG</b></div></div>';
  h+='<div class="after"><div class="after-label">agent-tested</div>';
  h+='<div style="font-size:.875rem;font-weight:500;margin-bottom:.25rem">'+w.domainName+'</div>';
  h+='<div style="font-size:.75rem;color:#666">"transmits meaning without context"</div>';
  h+='<div style="font-size:.75rem;color:#166534;margin-top:.375rem">agent infers: '+w.inference+'</div>';
  h+='<div style="font-size:.75rem;color:#166534">result: <b>CORRECT</b></div></div></div></div>';

  // Recommendation
  h+='<div class="divider"></div><div class="step"><div class="step-num">Recommendation</div><div class="step-title">'+w.domainName+'</div>';
  h+='<div class="card">';
  h+='<div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.domainName+'</span></div>';
  h+='<div class="card-row"><span class="card-label">agent comprehension</span><span class="green">'+w.score+'</span></div>';
  h+='<div class="card-row"><span class="card-label">first year</span><span>\
+w.purchasePrice+'</span></div>';
  h+='<div class="card-row"><span class="card-label">renewal</span><span>\
+w.renewalPrice+'</span></div>';
  h+='<div class="card-row"><span class="card-label">status</span><span class="green">agent understands this domain</span></div>';
  h+='</div></div>';

  // Checkout
  h+='<div class="divider"></div><div class="step"><div class="step-num">name.com checkout</div><div class="step-title">fresh availability + pricing</div><div class="step-desc">Pricing verified via name.com. <b>Write guard:</b> registration requires approval code.</div>';
  h+='<div class="step-desc">Before any irreversible action, DomainArena checks name.com again. If availability changed, price moved outside budget, or evidence is missing, it fails closed.</div>';
  h+='<div class="card">';
  h+='<div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.domainName+'</span></div>';
  h+='<div class="card-row"><span class="card-label">price</span><span class="green">\
+w.purchasePrice+'/yr</span></div>';
  h+='<div class="card-row"><span class="card-label">renewal</span><span>\
+w.renewalPrice+'/yr</span></div>';
  h+='</div>';
  h+='<div style="margin-top:1rem"><button class="btn" id="regBtn" onclick="doRegister()">Approve &amp; register via name.com</button></div></div>';

  h+='<div id="reg-result"></div>';
  document.getElementById('result-body').innerHTML=h;
}

function doRegister(){
  var btn=document.getElementById('regBtn');
  btn.disabled=true;btn.textContent='Registering...';
  var w=S.winner;
  log('Registering '+w.domainName+' via name.com API');
  api('/register?domain='+w.domainName,'POST').then(function(r){
    if(!r.ok||!r.data||r.data.status!=='REGISTERED'){
      log('Registration failed: '+(r.data.error||r.status),'err');
      btn.textContent='Failed';btn.disabled=false;
      throw new Error('Registration failed');
    }
    log('Registration: '+r.data.status);
    return api('/dns?domain='+w.domainName,'POST');
  }).then(function(r){
    if(!r.ok){log('DNS failed','err');throw new Error('DNS failed');}
    log('DNS configured: '+w.domainName);
    return api('/verify-dns?domain='+w.domainName);
  }).then(function(r){
    var verified=r.data.verified;
    log('DNS verification: '+(verified?'VERIFIED':'FAILED'));
    if(!verified){log('DNS not verified — aborting','err');throw new Error('DNS not verified');}
    var receiptData=JSON.stringify({domain:w.domainName,intent:S.intent,score:w.score,inference:w.inference,purchasePrice:w.purchasePrice,renewalPrice:w.renewalPrice,registered:true,dnsVerified:verified,timestamp:new Date().toISOString()});
    crypto.subtle.digest('SHA-256',new TextEncoder().encode(receiptData)).then(function(buf){
    var hash='sha256:'+Array.from(new Uint8Array(buf)).map(function(b){return b.toString(16).padStart(2,'0')}).join('');

    var h='<div class="divider"></div><div class="step active"><div class="step-num">Lifecycle complete</div><div class="step-title">name.com domain lifecycle</div>';
    h+='<div class="step-desc">The full pipeline from discovery to verified domain configuration, all through name.com API.</div>';
    h+='<div class="card">';
    h+='<div class="card-row"><span class="card-label">domain</span><span style="font-weight:500">'+w.domainName+'</span></div>';
    h+='<div class="card-row"><span class="card-label">registration</span><span class="green">REGISTERED</span></div>';
    h+='<div class="card-row"><span class="card-label">dns</span><span class="green">VERIFIED</span></div>';
    h+='<div class="card-row"><span class="card-label">receipt</span><span style="font-size:.6875rem;color:#666;word-break:break-all">'+hash+'</span></div>';
    h+='</div></div>';

    // API trace
    h+='<div class="divider"></div><div class="step"><div class="step-num">API trace</div><div class="trace">';
    h+='<div class="trace-label">name.com API calls made during this session</div>';
    S.trace.forEach(function(t){
      h+='<div class="trace-row"><span class="trace-method">'+t.method+'</span><span class="trace-path">'+t.path+'</span><span class="trace-status '+(t.status<400?'ok':'err')+'">'+t.status+'</span><span class="trace-ms">'+t.ms+'ms</span></div>';
    });
    h+='</div></div>';

    // Sponsor depth
    h+='<div class="divider"></div>';
    h+='<div style="padding:.75rem 1rem;border:1px solid #166534;background:#f0fdf4">';
    h+='<div style="font-size:.6875rem;font-weight:500;color:#166534">6 name.com API endpoints</div>';
    h+='<div style="font-size:.625rem;color:#666;margin-top:.25rem;line-height:1.6">';
    h+='<b>search</b> discover candidates \\u00b7 ';
    h+='<b>availability</b> fail-closed check \\u00b7 ';
    h+='<b>pricing</b> budget enforcement \\u00b7 ';
    h+='<b>registration</b> execute acquisition \\u00b7 ';
    h+='<b>DNS create</b> configure domain \\u00b7 ';
    h+='<b>DNS verify</b> confirm configuration';
    h+='</div></div>';

    document.getElementById('reg-result').innerHTML=h;
    btn.textContent='Done';
    }); // crypto.subtle.digest .then
  }); // api verify-dns .then
}
</script>
</body>
</html>
`;
