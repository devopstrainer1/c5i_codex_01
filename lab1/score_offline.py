"""Offline dry-run harness for Lab 1 (no API needed).

Purpose: let the instructor confirm, before class, WHERE the planted traps bite.
It uses a TF-IDF stand-in for retrieval, so the numbers will NOT match embedding
results. Use it to validate the corpus and the scoring method, then run the real
notebook with embeddings and compare.

Usage: python score_offline.py [--k 3] [--window 400]
"""
import argparse, csv, math, re, pathlib
from collections import Counter

HERE = pathlib.Path(__file__).parent
TOKEN = re.compile(r"[a-z0-9\-\.\%]+")

def toks(t): return TOKEN.findall(t.lower())

def load_docs():
    return {p.stem.split("_")[0]: p.read_text(encoding="utf-8")
            for p in sorted((HERE / "corpus").glob("*.md"))}

def chunk_fixed(docs, window, overlap=0):
    out, step = [], window - overlap
    for sid, text in docs.items():
        for i in range(0, len(text), step):
            out.append({"source": sid, "text": text[i:i + window]})
    return out

def chunk_structure(docs):
    out = []
    for sid, text in docs.items():
        title = text.splitlines()[0].lstrip("# ").strip()
        parts = re.split(r"\n(?=## )", text)
        head, sections = parts[0], parts[1:] or []
        if not sections:
            out.append({"source": sid, "text": text}); continue
        for s in sections:
            out.append({"source": sid, "text": f"[{title}]\n{s}"})
    return out

def tfidf_rank(chunks, query, k):
    df = Counter()
    bags = [Counter(toks(c["text"])) for c in chunks]
    for b in bags: df.update(b.keys())
    n = len(chunks)
    def vec(b): return {t: (1 + math.log(f)) * math.log((n + 1) / (df.get(t, 0) + 1) + 1) for t, f in b.items()}
    qv = vec(Counter(toks(query)))
    def cos(a, b):
        num = sum(a[t] * b.get(t, 0) for t in a)
        den = math.sqrt(sum(x * x for x in a.values())) * math.sqrt(sum(x * x for x in b.values())) or 1
        return num / den
    scored = sorted(((cos(qv, vec(b)), i) for i, b in enumerate(bags)), reverse=True)
    return [chunks[i] for _, i in scored[:k]]

def evaluate(chunks, k, rows):
    res = []
    for r in rows:
        phrases = [p.strip() for p in r["gold_phrases"].split("|") if p.strip()]
        if not phrases:
            res.append((r["qid"], "n/a", "n/a", "n/a")); continue
        top = tfidf_rank(chunks, r["question"], k)
        joined = " ".join(c["text"] for c in top)
        hit_all = all(p in joined for p in phrases)
        same = any(all(p in c["text"] for p in phrases) for c in top)
        res.append((r["qid"], "Y" if hit_all else "N", "Y" if same else "N", sum(len(c["text"]) for c in top)))
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--window", type=int, default=400)
    a = ap.parse_args()
    docs = load_docs()
    rows = list(csv.DictReader(open(HERE / "queries.csv", encoding="utf-8")))
    strategies = {"A fixed": chunk_fixed(docs, a.window), "B structure": chunk_structure(docs)}
    for name, ch in strategies.items():
        res = evaluate(ch, a.k, rows)
        ok = [r for r in res if r[1] != "n/a"]
        print(f"\n{name}: {len(ch)} chunks, top-{a.k}")
        print("qid  all-gold-in-topk  one-chunk-support  chars-returned")
        for r in res: print(f"{r[0]:<4} {r[1]:^16} {r[2]:^17} {r[3]}")
        print("all-gold-in-topk:", sum(r[1] == "Y" for r in ok), "/", len(ok),
              "| one-chunk-support:", sum(r[2] == "Y" for r in ok), "/", len(ok))
