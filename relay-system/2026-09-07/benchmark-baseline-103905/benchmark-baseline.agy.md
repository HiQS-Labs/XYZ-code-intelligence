### ANSWER
1. **Size**: **50**. This is exactly the right default. It derives directly from the TREC (Text REtrieval Conference) ad-hoc track convention, which established 50 topics as the standard minimum for statistically stable, discriminative IR evaluation without overwhelming human assessors.
2. **Slice allocation**: Stratify strictly by **query TYPE**, not language. The known failure mode is saturation via filename leakage; balancing languages does nothing to prevent this. Split the 50 as:
   * **10 Name-carried**: Baseline sanity checks (solvable by filename/BM25).
   * **15 Behaviour-described**: e.g., "Where is the cart total calculated?" (Defeats filename leakage; tests dense embeddings).
   * **15 Cross-file**: e.g., "Where is the API client used to fetch user data?" (Tests deeper contextual relevance).
   * **10 No-answer**: Out-of-scope or hallucinated concepts (Tests discrimination and thresholding).
   This avoids re-saturation by hard-capping filename-answerable queries at 20% (10/50), forcing the system to rely on semantic and relational understanding to achieve high scores.
3. **Dev split**: **15** queries. They **must** be strictly disjoint from the frozen 50. Tuning the no-answer threshold on the test set guarantees overfitting and invalidates the benchmark's integrity.
4. **Growth rule**: Add another 50 queries when the MRR difference between the top two configurations (e.g., hybrid vs hybrid+rerank) is less than **0.05** while both score above **0.85**, indicating the set is saturating and losing its discriminative power.

### FINDINGS
* **[Blocker]** Stratifying by language. This ignores the root cause of your saturation (filename leakage). You must stratify by query difficulty/type to force the models to work.
* **[Blocker]** Reusing the frozen set for tuning. The dev split for tuning thresholds must be entirely disjoint.
* **[Should]** Adopt the TREC standard of 50 queries as your defensible, non-arbitrary baseline rather than bespoke numbers.

### RECOMMENDATION
Build a 50-query TREC-style test collection stratified strictly by query complexity (10 name, 15 behavior, 15 cross-file, 10 no-answer), with a disjoint 15-query dev set for thresholding.
