# Web Search & Information Retrieval - Programming Assignment #2

## Student Identity
**Name:** Rakha Abid Bangsawan  
**Student ID (NPM):** 2206081585  

---

# Assignment Description

1. **[30 Points]** Add another compression algorithm besides Variable Byte Encoding (VBE), but it must be **bit-level based**, such as Elias-Gamma, OptPForDelta, or other similar algorithms.

2. **[30 Points]** Add functionality to perform scoring using **BM25**. Currently, the system only supports **TF-IDF** scoring. To implement BM25, you need to perform **pre-computation of document lengths and the average document length during indexing**, and store them in an appropriate data structure.

3. **[30 Points]** Add three additional evaluation metrics:
   - DCG (Discounted Cumulative Gain)
   - NDCG (Normalized Discounted Cumulative Gain)
   - AP (Average Precision)

4. **[10 Points]** Add the **WAND Top-K Retrieval algorithm** so that the system does not need to compute BM25 scores for all documents.

---

# Answer Q1 - Bit-Level Compression

## Algorithm
I added **Elias-Gamma** (bit-level). Elias-Gamma represents integers >= 1 as:

- Prefix: unary of (binary length - 1) as a run of `0` bits ending with `1`
- Suffix: the remaining binary bits without the leading `1`

Example: 13 (binary `1101`) has length 4, so prefix `0001` and suffix `101` -> `0001101`.

Because Elias-Gamma only supports integers >= 1, all numbers are offset by `+1` during encoding and `-1` during decoding.

## Implementation
The implementation lives in `compression.py` as `EliasGammaPostings`:
- **Postings list**: converted to a gap-based list (like VBE), then each gap is offset `+1` and encoded with Elias-Gamma.
- **TF list**: each TF is offset `+1` and encoded with Elias-Gamma.
- **Decode**: bytestream -> bits -> numbers, then offset `-1`, and for postings the gaps are accumulated back to the original docIDs.

Pipeline integration:
- `bsbi.py` and `search.py` import `EliasGammaPostings` and include a short note on how to switch to it.
- Default remains `VBEPostings` (unchanged), so to try Elias-Gamma just set `postings_encoding=EliasGammaPostings`.

# Answer Q2 - BM25 Scoring

## Algorithm
I implemented **BM25** scoring with the standard formula:

Score(D, Q) = sum over query terms t of:

- IDF(t) = log((N - df + 0.5) / (df + 0.5))
- BM25 term weight = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avgdl)))

where:
- N = number of documents
- df = document frequency for term t
- tf = term frequency of t in document D
- dl = document length of D (number of tokens)
- avgdl = average document length across the collection

## Implementation in This Codebase
Pre-computation and storage:
- During indexing, `doc_length` is already accumulated in `InvertedIndexWriter.append(...)`.
- I added `avg_doc_length` to the index metadata and store it in the same pickle file as `postings_dict`, `terms`, and `doc_length`.
- On load, the code is backward compatible: if the old metadata format is found, `avg_doc_length` is computed on the fly.

Retrieval:
- Implemented `retrieve_bm25(...)` in `bsbi.py` using Term-at-a-Time scoring.
- It reads `doc_length` and `avg_doc_length` from the index metadata, computes IDF from `postings_dict`, and scores each document.

# Answer Q3 - Additional Evaluation Metrics

## Metrics
I added three evaluation metrics:

- **DCG (Discounted Cumulative Gain)**: accumulates relevance with a log-based discount for lower ranks.
- **NDCG (Normalized DCG)**: DCG normalized by the ideal DCG (IDCG) for the same ranking length.
- **AP (Average Precision)**: mean of precision values at ranks where relevant documents appear.

## Implementation in This Codebase
All three are implemented in `evaluation.py`:

- `dcg(ranking)` computes DCG over a binary relevance list.
- `ndcg(ranking)` computes DCG and normalizes it by the ideal ranking.
- `ap(ranking, total_relevant)` computes average precision given the number of relevant docs.

The `eval(...)` function now collects and prints mean scores for RBP, DCG, NDCG, and AP across all queries.

# Answer Q4 - WAND Top-K Retrieval

## Algorithm
I implemented **WAND (Weak AND)** to retrieve Top‑K results without scoring every document.
WAND maintains a min‑heap of the current Top‑K results (threshold `theta`). It uses an **upper bound score** per term to decide a pivot document. Only when the sum of upper bounds can exceed `theta` does it compute the exact BM25 score for that pivot; otherwise it skips ahead.

## Index Changes
To support efficient upper bounds for BM25, the inverted index metadata was extended:

- `postings_dict` now stores `max_tf` per term (maximum TF in the postings list).
- The index metadata now also stores `min_doc_length` (minimum document length).

These are used to compute a conservative upper bound for BM25:

```
UB_t = IDF(t) * (max_tf * (k1 + 1)) / (max_tf + k1 * (1 - b + b * (min_dl / avgdl)))
```

## Implementation in This Codebase
- `retrieve_bm25_wand(...)` is implemented in `bsbi.py`.
- It uses `postings_dict` + `doc_length` + `avg_doc_length` + `min_doc_length` to compute term upper bounds, select the pivot doc, and score only candidates that can beat `theta`.

Note: to get the tightest upper bounds, the index should be rebuilt so that `max_tf` is stored in `postings_dict`.
