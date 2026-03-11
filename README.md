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