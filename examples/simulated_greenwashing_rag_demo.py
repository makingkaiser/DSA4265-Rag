"""Small, dependency-free simulation of a greenwashing-gap RAG workflow.

This is NOT a production pipeline. It demonstrates how retrieval + generation +
gap scoring can surface inconsistencies between promotional ESG language and
regulated disclosures / enforcement outcomes.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import List


@dataclass
class Chunk:
    company: str
    year: int
    doc_type: str  # esg_report, filing, enforcement
    text: str
    source: str


CORPUS: List[Chunk] = [
    Chunk(
        company="Volkswagen",
        year=2014,
        doc_type="esg_report",
        text=(
            "We are a leader in clean diesel technology and reducing emissions. "
            "Our vehicles are engineered for environmental performance beyond compliance."
        ),
        source="Sustainability report messaging (pre-Dieselgate, paraphrased)",
    ),
    Chunk(
        company="Volkswagen",
        year=2014,
        doc_type="filing",
        text=(
            "Regulatory standards for NOx and other pollutants are tightening and non-compliance "
            "could lead to penalties, recalls, and reputational harm."
        ),
        source="Annual filing risk-factor style language (paraphrased)",
    ),
    Chunk(
        company="Volkswagen",
        year=2015,
        doc_type="enforcement",
        text=(
            "U.S. regulators found software used to defeat emissions testing in diesel vehicles, "
            "leading to major penalties and settlements."
        ),
        source="Public Dieselgate enforcement summaries",
    ),
    Chunk(
        company="DWS Group",
        year=2020,
        doc_type="esg_report",
        text=(
            "ESG integration is a core and consistent element of our investment process across products."
        ),
        source="Marketing/annual ESG messaging (paraphrased)",
    ),
    Chunk(
        company="DWS Group",
        year=2020,
        doc_type="filing",
        text=(
            "Implementation of sustainability criteria may vary by strategy and data quality; "
            "there are limitations in consistent application."
        ),
        source="Risk disclosure style language (paraphrased)",
    ),
    Chunk(
        company="DWS Group",
        year=2022,
        doc_type="enforcement",
        text=(
            "Authorities investigated potential overstatement of ESG integration controls and practices."
        ),
        source="Public investigation summaries",
    ),
    Chunk(
        company="BNY Mellon",
        year=2021,
        doc_type="esg_report",
        text=(
            "Our responsible investment framework applies robust ESG quality review to sustainable funds."
        ),
        source="ESG communications (paraphrased)",
    ),
    Chunk(
        company="BNY Mellon",
        year=2021,
        doc_type="filing",
        text=(
            "Investment process controls and disclosures may not always operate as intended and "
            "could create regulatory risk."
        ),
        source="10-K style control/risk disclosure (paraphrased)",
    ),
    Chunk(
        company="BNY Mellon",
        year=2022,
        doc_type="enforcement",
        text=(
            "SEC announced charges regarding misstatements or omissions about ESG quality review "
            "for certain mutual funds."
        ),
        source="SEC order summary",
    ),
]

POSITIVE_WORDS = {
    "leader",
    "clean",
    "beyond",
    "robust",
    "core",
    "consistent",
    "sustainable",
    "performance",
}
RISK_WORDS = {
    "risk",
    "penalties",
    "recalls",
    "harm",
    "limitations",
    "regulatory",
    "non-compliance",
    "investigated",
    "charges",
    "misstatements",
}


TOKEN_RE = re.compile(r"[a-zA-Z\-]+")


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def score_similarity(query: str, text: str) -> float:
    q = Counter(tokenize(query))
    d = Counter(tokenize(text))
    if not q or not d:
        return 0.0
    overlap = set(q) & set(d)
    num = sum(q[w] * d[w] for w in overlap)
    qn = math.sqrt(sum(v * v for v in q.values()))
    dn = math.sqrt(sum(v * v for v in d.values()))
    return num / (qn * dn)


def tone_score(text: str) -> float:
    toks = tokenize(text)
    if not toks:
        return 0.0
    pos = sum(1 for t in toks if t in POSITIVE_WORDS)
    risk = sum(1 for t in toks if t in RISK_WORDS)
    return (pos - risk) / len(toks)


def im_gap_score(esg: str, filing: str) -> float:
    return tone_score(esg) - tone_score(filing)


def retrieve(query: str, company: str, top_k: int = 3) -> List[Chunk]:
    pool = [c for c in CORPUS if c.company.lower() == company.lower()]
    ranked = sorted(pool, key=lambda c: score_similarity(query, c.text), reverse=True)
    return ranked[:top_k]


def generate_stub_answer(query: str, docs: List[Chunk]) -> str:
    joined = " ".join(d.text for d in docs)
    has_enforcement = any(d.doc_type == "enforcement" for d in docs)
    has_risk = "risk" in joined.lower() or "penalt" in joined.lower()
    has_positive = any(w in joined.lower() for w in ("leader", "robust", "core", "clean"))

    verdict = "partially_aligned"
    if has_positive and (has_risk or has_enforcement):
        verdict = "divergent"

    return (
        f"Verdict={verdict}. Retrieved evidence shows promotional ESG claims alongside "
        f"material risk/enforcement language, suggesting a potential impression-management gap."
    )


def run_demo() -> None:
    cases = [
        ("Volkswagen", "Did Volkswagen's clean-emissions narrative align with disclosed and observed risks?"),
        ("DWS Group", "Were DWS ESG integration claims fully consistent with later findings?"),
        ("BNY Mellon", "Did ESG quality-review claims match disclosed controls and outcomes?"),
    ]

    for company, query in cases:
        docs = retrieve(query, company)
        esg_docs = [d for d in docs if d.doc_type == "esg_report"]
        filing_docs = [d for d in docs if d.doc_type == "filing"]
        gap = 0.0
        if esg_docs and filing_docs:
            gap = im_gap_score(esg_docs[0].text, filing_docs[0].text)
        answer = generate_stub_answer(query, docs)

        print("=" * 80)
        print(f"Company: {company}")
        print(f"Query: {query}")
        for idx, d in enumerate(docs, 1):
            print(f"[{idx}] ({d.doc_type}, {d.year}) {d.text} -- {d.source}")
        print(f"IM gap score (toy): {gap:.3f}")
        print(f"Generated answer: {answer}")


if __name__ == "__main__":
    run_demo()
