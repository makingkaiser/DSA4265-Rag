# Resource & Feasibility Scan: Greenwashing / Impression-Management RAG Dataset (3-Day Build)

## 1) Goal
Build a **paired-document RAG evaluation dataset** that compares:
- **Voluntary ESG narratives** (sustainability reports), vs.
- **Regulated disclosures** (10-K annual reports),

so that queries can test whether generated answers detect a potential **impression-management gap** (tone inflation, missing risk disclosure, weak quantitative backing).

---

## 2) What I looked up (live availability checks)

I checked a set of practical sources that can be used immediately.

### Core document sources
1. **SEC company tickers JSON** (maps ticker ↔ CIK for filing retrieval)  
   - URL: https://www.sec.gov/files/company_tickers.json  
   - Status: reachable with a user agent string.
2. **SEC filing query API documentation (third-party)**  
   - URL: https://sec-api.io/docs/query-api/  
   - Status: reachable.
3. **Notre Dame SEC EDGAR dataset page** (bulk SEC text resources)  
   - URL: https://sraf.nd.edu/sec-edgar-data/  
   - Status: reachable.
4. **ResponsibilityReports.com** (large archive of corporate sustainability PDFs)  
   - URL: https://www.responsibilityreports.com/  
   - Status: reachable.
5. **CDP data portal** (climate disclosure data and frameworks)  
   - URL: https://www.cdp.net/en/data  
   - Status: reachable.
6. **FinanceBench (Hugging Face)** for financial QA-style benchmarking ideas  
   - URL: https://huggingface.co/datasets/PatronusAI/financebench  
   - Status: reachable.

### Kaggle note
- Kaggle pages were not reliably retrievable from this runtime (returned 404 from automated curl checks), and the `kaggle` CLI is not installed here.
- This is likely environment/access behavior rather than dataset non-existence.
- Practical workaround: use SEC + ResponsibilityReports + HF resources first; optionally add Kaggle manually from browser on your machine.

---

## 3) Is this feasible in **3 days**?

## Verdict: **Yes, feasible** for a strong prototype dataset and evaluation.

### Recommended target size (3-day scope)
- **Companies:** 20–30 (S&P 500 large caps for easier report availability)
- **Years:** 2 years (e.g., 2022–2023)
- **Documents:**
  - 40–60 sustainability/ESG reports
  - 40–60 corresponding 10-K filings
- **Paired units for evaluation:**
  - ~400–1,000 aligned chunks (ESG chunk ↔ nearest 10-K chunk by topic)

This size is enough to evaluate RAG retrieval quality, groundedness, and contradiction/sentiment gap signals without overextending.

---

## 4) Dataset construction design (assignment-ready)

## A. Retrieval corpus (for RAG)
Store chunks with metadata:
- `company`, `ticker`, `year`, `doc_type` (`esg_report` / `10k`), `section`, `chunk_id`, `text`, `source_url`.

Chunk strategy:
- 400–800 tokens/chunk, 10–15% overlap.
- Keep section titles (e.g., “Climate Strategy”, “Risk Factors”) as metadata.

## B. Evaluation set (gold-ish labels)
Create a query set of 80–150 prompts in 4 categories:
1. **Claim consistency**: “Does company X provide quantitative emissions targets and risks consistently across ESG and 10-K?”
2. **Risk omission**: “What climate-related operational risks are disclosed in mandatory filings but not highlighted in ESG report?”
3. **Tone vs evidence**: “Is positive ESG language backed by concrete KPIs and year-over-year values?”
4. **Numerical cross-check**: “Compare Scope 1/2 values, capex commitments, impairment/risk mentions.”

For each query, annotate:
- expected evidence chunks (top 2–5)
- whether answer should be `aligned`, `partially_aligned`, or `divergent`
- optional `gap_type` (`tone_inflation`, `metric_absence`, `risk_omission`, `time_inconsistency`)

## C. Impression-management scoring signal (simple but defendable)
For each ESG–10K pair, compute features:
- **Tone gap**: positivity score(ESG) − positivity score(10-K risk sections)
- **Specificity gap**: count of concrete numerics / total tokens (ESG vs 10-K)
- **Risk coverage gap**: % of climate-risk terms found in 10-K but absent in ESG report
- **Forward-claim grounding**: % of ESG future claims that have quantified baseline/target/date

Aggregate into an interpretable score:
`IM_gap_score = w1*tone_gap + w2*specificity_gap + w3*risk_coverage_gap + w4*ungrounded_claim_ratio`

Use this as a **diagnostic signal**, not legal proof of greenwashing.

---

## 5) Practical data pipeline (minimal engineering risk)

1. **Company list creation**
   - Start with 20–30 large-cap firms in emissions-sensitive sectors (energy, utilities, airlines, mining, consumer goods).
2. **Download 10-K filings**
   - Use SEC EDGAR (direct or helper API).
3. **Download sustainability reports**
   - Use responsibilityreports archive and/or company investor relations pages.
4. **Text extraction**
   - PDF/HTML to text, remove boilerplate, preserve headings.
5. **Section tagging**
   - Regex/rule-based tags: `risk`, `strategy`, `emissions`, `targets`, `governance`.
6. **Chunk + embed + index**
   - Build vector store with metadata filtering by company/year/doc_type.
7. **Create evaluation questions + labels**
   - Manual annotation on a subset (80–150 queries).
8. **Run RAG evaluation**
   - Retrieval metrics: Recall@k, MRR.
   - Generation metrics: groundedness, citation correctness, contradiction rate.

---

## 6) Feasibility risks and mitigations

1. **PDF extraction quality variance**  
   - Mitigation: focus on text-selectable PDFs first; skip OCR-heavy files in 3-day version.

2. **Different reporting boundaries (fiscal year mismatch)**  
   - Mitigation: align by filing date window ±6 months and mark uncertain pairs.

3. **No perfect “ground-truth greenwashing” labels**  
   - Mitigation: evaluate retrieval and evidence-grounded divergence detection, not legal classification.

4. **Kaggle access friction in this environment**  
   - Mitigation: treat Kaggle as optional supplement; rely on SEC + ResponsibilityReports + CDP framework references.

---

## 7) 3-day execution plan

### Day 1 (Data acquisition + preprocessing)
- Finalize company list (20–30).
- Pull 10-K + ESG docs for two years.
- Convert and clean text; implement metadata schema.

### Day 2 (RAG build + evaluation set)
- Chunk, embed, index.
- Draft 80–150 evaluation prompts.
- Label evidence for 40–60 high-priority prompts.

### Day 3 (Scoring + report outputs)
- Run retrieval and generation evaluation.
- Compute impression-gap features + examples.
- Produce tables/figures for your PDF report.

---

## 8) Recommendation for your assignment

This topic is **novel and strong** for the rubric:
- High novelty (cross-document narrative consistency in ESG vs mandatory filings).
- High data-prep effort (paired-source curation + alignment).
- Clear end-to-end RAG story with measurable evaluation.
- Rich critical analysis opportunities (false positives, ambiguity, reporting lag).

If time is tight, prioritize:
1. 10 companies × 2 years,
2. one robust retrieval index with clear metadata,
3. 50+ high-quality evaluation queries with evidence labels.

That is enough for a convincing submission.

---

## 9) Command log used for availability checks
- `curl -L -I -s -o /dev/null -w '%{http_code} %{url_effective}\n' <url>` for multiple URLs.
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://www.sec.gov/files/company_tickers.json`
- `kaggle --version` (not installed in this environment).

---

## 10) Suitable evaluation method for this use case

For your assignment, use a **three-layer evaluation** that directly matches your RAG objective.

### Layer A: Retrieval quality (can the system find the right evidence?)
Use a labeled query set with evidence chunk IDs and report:
- **Recall@k** (k=3,5,10): whether at least one gold chunk is retrieved.
- **nDCG@k**: ranking quality when multiple evidence chunks exist.
- **MRR**: how early the first relevant chunk appears.

Why this matters: if retrieval fails, generation quality is not meaningful.

### Layer B: Answer grounding & faithfulness
For each generated answer, evaluate:
- **Citation precision**: share of cited chunks that truly support statements.
- **Attribution/groundedness score**: % answer claims directly supported by retrieved text.
- **Contradiction rate**: % answers that conflict with evidence.

Practical method in 3 days:
- Manual grading rubric on ~50 answers (0/1/2 scale per criterion),
- plus optional LLM-as-judge with strict prompt and human spot-check.

### Layer C: Impression-management detection utility
Treat this as **risk-flagging**, not legal adjudication. Evaluate:
- **Label agreement** for `aligned` / `partially_aligned` / `divergent` on a manually annotated subset.
- **Macro-F1** across these classes.
- **Precision@TopN risk flags** (are top flagged cases genuinely concerning upon review?).

If you have known historical enforcement/investigation outcomes, use them as weak external validation:
- Did your system rank those company-years higher on `IM_gap_score` before or around the event?

### Suggested primary metric bundle (what to present in report)
- Retrieval: Recall@5 + nDCG@5
- Generation: groundedness score + contradiction rate
- Task utility: Macro-F1 on 3-way alignment labels

This is rigorous but realistic in a 3-day timeline.

---

## 11) Simulated RAG example showing concept viability

I added a runnable toy script:
- `examples/simulated_greenwashing_rag_demo.py`

What it demonstrates:
1. A tiny corpus with **ESG-style claims**, **filing-style risk text**, and **later enforcement outcomes**.
2. Query-time retrieval over company-specific chunks.
3. A toy `IM gap score` (tone difference ESG vs filing).
4. A simple generated verdict (`aligned`/`partially_aligned`/`divergent`).

Case themes used (paraphrased summaries):
- Volkswagen (Dieselgate context)
- DWS Group (ESG integration overstatement investigations context)
- BNY Mellon (SEC ESG-related misstatement/omission context)

Important caveat:
- The script is intentionally **simulated** and uses paraphrased snippets for demonstration.
- For your final assignment, replace toy text with real extracted chunks and formal citations.

### How to run
```bash
python examples/simulated_greenwashing_rag_demo.py
```

### What success looks like
You should see outputs where:
- retrieved chunks mix positive ESG wording with risk/enforcement evidence,
- toy `IM gap score` is positive for potentially inflated narratives,
- generated verdict leans `divergent` for those historically controversial cases.


---

## 12) Direct answers to your questions (important clarifications)

### Q1) Is the data in the demo dummy?
**Yes.** The demo script uses a tiny, handcrafted, **paraphrased** corpus intended only to simulate behavior.
- It is not a benchmark dataset.
- It is not legal/compliance evidence.
- It is only a proof-of-concept template for pipeline logic.

### Q2) Is the evaluation completely deterministic (no LLM)?
For the toy script: **yes, deterministic**.
- Retrieval is lexical cosine-overlap.
- Scoring uses fixed word lists and arithmetic.
- Verdict logic is rule-based.
- No external model calls are made.

For your full assignment, you have two options:
1. **Fully deterministic track (recommended for reproducibility)**
   - BM25 or embedding retrieval with fixed seed/index settings
   - rule-based/annotated evaluation (Recall@k, nDCG, groundedness rubric)
2. **Hybrid track**
   - Add LLM-as-judge for fluency/faithfulness checks
   - Keep a human-audited subset for reliability.

### Q3) What data/example was used to test the demo?
The demo uses paraphrased, simulated text snippets for three historical controversy themes:
- Volkswagen (Dieselgate context)
- DWS Group (ESG-overstatement investigation context)
- BNY Mellon (SEC ESG-related charges context)

Again: these are toy snippets to demonstrate mechanics, not ground-truth corpora.

---

## 13) Specific datasets/resources to build this use case (availability + role)

Below is a practical catalog for your actual build.

### Tier A (highly usable in 3 days)
1. **SEC EDGAR APIs + indices (official, free)**
   - What you get: 10-K filing metadata, submissions JSON, filing index access.
   - Why useful: authoritative, regulated disclosures for the “mandatory” side.
   - Availability checked: reachable.

2. **ResponsibilityReports.com archive (public ESG PDFs)**
   - What you get: historical sustainability/CSR report links by company.
   - Why useful: direct “voluntary narrative” side.
   - Availability checked: reachable.

3. **SEC company tickers mapping**
   - What you get: ticker ↔ CIK for joining company identities.
   - Why useful: stable key for aligning 10-K to ESG reports.
   - Availability checked: reachable with user-agent.

### Tier B (useful support datasets)
4. **FinanceBench (Hugging Face)**
   - What you get: financial QA benchmark style examples.
   - Why useful: reference for evaluation/task design; not ESG-specific.
   - Availability checked: reachable.

5. **Lettria financial-articles (Hugging Face)**
   - What you get: financial news corpus.
   - Why useful: optional external context or negative controls.
   - Availability checked: reachable.

6. **CDP data portal**
   - What you get: climate disclosure ecosystem resources.
   - Why useful: vocabulary, taxonomy, and climate framing support.
   - Availability checked: reachable.

### Tier C (constraints / caution)
7. **Kaggle ESG / 10-K datasets**
   - In this runtime, Kaggle pages returned 404 and CLI is unavailable.
   - Likely an environment/access issue, not proof of non-existence.
   - Feasible workaround: download Kaggle resources manually outside this runtime and ingest locally.

8. **Some Hugging Face SEC filing datasets**
   - Some candidate repos return 401 in this environment.
   - Treat as optional; don’t block your core pipeline on these.

---

## 14) Full end-to-end plan for your assignment (data + eval + analysis)

### Step 1 — Build a reliable paired corpus
- Pick 10–20 companies across high-emissions / high-scrutiny sectors.
- For each company-year, collect:
  - 10-K (SEC)
  - sustainability/ESG report (ResponsibilityReports / IR pages)
- Normalize to plain text and preserve section headings.

### Step 2 — Create alignment-ready metadata
Use fields:
`company`, `ticker`, `cik`, `fiscal_year`, `doc_type`, `section`, `chunk_id`, `text`, `source_url`, `download_date`.

### Step 3 — Retrieval index
- Chunk 400–800 tokens, overlap 10–15%.
- Build hybrid retrieval (BM25 + dense embeddings) if possible; otherwise BM25-only baseline.
- Retrieval must support filtering by `company` and `year`.

### Step 4 — Evaluation set construction
- 80–150 prompts in 4 categories:
  - claim consistency
  - risk omission
  - tone vs evidence
  - numerical cross-check
- For each prompt, label:
  - relevant chunk IDs (2–5)
  - expected class: `aligned` / `partially_aligned` / `divergent`

### Step 5 — Evaluation protocol (deterministic-first)
1. Retrieval: Recall@5, nDCG@5, MRR.
2. Grounding: citation precision + contradiction rate via human rubric.
3. Task utility: Macro-F1 for 3-way class labels.
4. Optional: LLM judge only as secondary analysis.

### Step 6 — Critical analysis section for your report
Discuss:
- false positives (promotional tone without misconduct)
- false negatives (well-worded risk disclosures masking severity)
- reporting lag and fiscal-year mismatch
- legal caveat: this is risk signaling, not legal determination.

---

## 15) Critical feasibility assessment (realistic view)

### What is strongly feasible in 3 days
- Collecting paired ESG + 10-K docs for 10–20 companies.
- Building a retrieval corpus and reproducible evaluation set.
- Producing meaningful retrieval + groundedness metrics.
- Demonstrating “impression-management gap” signals with interpretable features.

### What is partially feasible
- Large-scale manual labeling (>150 prompts) may exceed 3 days.
- Robust cross-year entity/metric harmonization can be time-consuming.
- Advanced contradiction detection may require extra modeling.

### What is not realistically feasible in 3 days
- Building a legally robust, high-confidence “greenwashing classifier”.
- Exhaustive global coverage of companies/sectors.
- Perfect ground truth labels for misconduct intent.

### Bottom line
The project is **feasible and strong** if positioned as:
- a **RAG-based inconsistency/risk flagging system**,
- evaluated with retrieval + groundedness + divergence labeling,
- accompanied by transparent limitations and careful claims.

---

## 16) Extra command log for dataset availability checks
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://www.sec.gov/edgar/sec-api-documentation`
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://www.sec.gov/Archives/edgar/full-index/`
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://data.sec.gov/submissions/CIK0000320193.json`
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://www.responsibilityreports.com/Companies/aapl/`
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://huggingface.co/datasets/Lettria/financial-articles`
- `curl -A 'Mozilla/5.0 test@example.com' -L -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://www.kaggle.com/datasets/search?search=10-k`

