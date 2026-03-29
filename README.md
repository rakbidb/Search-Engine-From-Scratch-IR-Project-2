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