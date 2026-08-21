# Agent SEO Deep Research — Cool Projects & Integrations

## Key Research Findings

### 1. Agent Tool Selection is Measurable

**Paper:** "How Consistent Are LLM Agents? Measuring Behavioral Reproducibility in Multi-Step Tool-Calling Pipelines" (arXiv:2605.28840)

**Key insight:** Agents show "structural consistency, parametric variance" — they reliably choose the same tool sequences but vary in arguments.

**What this means for us:** We can measure which tools agents prefer, and the preference is stable enough to be a signal.

### 2. Tool Description Phrasing Matters

**Source:** "Tool Selection for LLM Agents: Routing Strategies" (mbrenndoerfer.com)

**Key insight:** Models are highly sensitive to description phrasing. "Search the web for current information" elicits different behavior than "Retrieve up-to-date facts from the internet."

**What this means for us:** We can A/B test MCP tool descriptions and measure which ones agents actually select.

### 3. GEO is Measurable

**Paper:** "GEO: Generative Engine Optimization" (arXiv:2311.09735, Princeton KDD 2024)

**Key findings:**
- Adding statistics with sources: up to 40% visibility lift
- Quotations from named sources: top-performing technique
- Citing external sources: ~22% lift
- Keyword stuffing: performed below baseline

**What this means for us:** We can measure exactly which content changes improve agent discovery.

### 4. Agent Behavior is Observable

**Project:** Moltbook Observatory (52 stars, academic citations)

**What it does:** Passively monitors Moltbook — the social network for AI agents. Collects posts, tracks agents, analyzes trends.

**Dataset:** 2.6M posts, 1.2M comments, 175K agents (arXiv:2605.13860)

**What this means for us:** We can integrate Moltbook data to understand agent language and preferences.

### 5. AI Visibility is Trackable

**Tool:** Rankshift (AI Visibility Tracking)

**What it does:** Tracks brand visibility across ChatGPT, Gemini, Claude, Perplexity, etc.

**What this means for us:** We can build similar tracking for our own tools.

---

## Cool Project Ideas for agentseolab

### 1. Moltbook Integration
**What:** Connect to Moltbook API to collect agent posts/comments
**Why:** Real data on what agents actually talk about
**How:** Use Moltbook SDK, store in SQLite, analyze patterns

### 2. Tool Description A/B Testing
**What:** Test different MCP tool descriptions and measure agent selection
**Why:** Description phrasing affects tool selection
**How:** Randomize descriptions, track selection rates across models

### 3. GEO Benchmarking
**What:** Measure citation rates across ChatGPT, Gemini, Claude
**Why:** Prove which content changes actually improve visibility
**How:** Run controlled experiments, track citation frequency

### 4. Agent Language Corpus
**What:** Build a corpus of agent language from Moltbook + GitHub
**Why:** Understand how agents lexically conceptualize capabilities
**How:** Collect posts, analyze word frequency, build preference model

### 5. Domain Preference Experiments
**What:** Run blind tournaments across models
**Why:** Empirically measure which domains agents prefer
**How:** Randomize order, track selection, use Bradley-Terry scoring

### 6. Search Result Choice Experiments
**What:** Test how agents choose between search results
**Why:** Understand what makes content agent-selectable
**How:** Simulated SERPs, randomized variables, measure selection

### 7. Cross-Model Consistency Study
**What:** Measure how consistent different models are in tool selection
**Why:** Understanding consistency helps predict agent behavior
**How:** Run same tasks across GPT, Claude, Gemini, measure variance

### 8. Agent Demand Heatmap
**What:** Track what capabilities agents search for most
**Why:** Prioritize which tools to build
**How:** Collect search queries, cluster by intent, measure frequency

### 9. Price Sensitivity Experiments
**What:** Test how agents respond to different pricing structures
**Why:** Understand agent economic behavior
**How:** Vary prices, measure conversion, track cost preferences

### 10. Trust Signal Experiments
**What:** Test which trust signals agents prefer
**Why:** Understand what makes agents trust a tool
**How:** Vary provenance, reputation, freshness signals, measure selection

---

## Integration Opportunities

### Moltbook Data
- Collect agent posts/comments
- Analyze language patterns
- Track agent preferences
- Build agent demand heatmap

### GEO Measurement
- Track citation rates across engines
- A/B test content changes
- Measure visibility lift
- Build evidence library

### Tool Selection Research
- A/B test MCP descriptions
- Measure cross-model consistency
- Build preference model
- Track selection patterns

---

## Key Papers to Read

1. **GEO: Generative Engine Optimization** (arXiv:2311.09735)
2. **Moltbook Observatory Archive** (arXiv:2605.13860)
3. **How Consistent Are LLM Agents?** (arXiv:2605.28840)
4. **Tool Selection for LLM Agents** (mbrenndoerfer.com)
5. **Optimizing Visibility in Generative Engines** (arXiv:2607.14035)
