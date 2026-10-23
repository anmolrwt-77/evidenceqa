# EvidenceQA evaluation results (Day 14)

- Total questions: **15**
- Refuse accuracy: **6/6** (100%)
- Answerable source hit rate: **7/9** (78%)
- Answerable keyword hit rate: **6/9** (67%)

## Per-question

| id | ok | should_refuse | refused | source_ok | keyword_ok |
|---:|:--:|:-------------:|:-------:|:---------:|:----------:|
| 1 | True | False | False | True | True |
| 2 | False | False | False | False | True |
| 3 | True | False | False | True | True |
| 4 | True | False | False | True | True |
| 5 | False | False | False | True | False |
| 6 | False | False | False | False | False |
| 7 | True | False | False | True | True |
| 8 | False | False | False | True | False |
| 9 | True | True | True | True | True |
| 10 | True | True | True | True | True |
| 11 | True | True | True | True | True |
| 12 | True | True | True | True | True |
| 13 | True | True | True | True | True |
| 14 | True | True | True | True | True |
| 15 | True | False | False | True | True |

## Failures (honest)

### Question 2
- Q: What is LLM01 in the OWASP Top 10 for LLM Applications 2026?
- should_refuse=False, refused=False
- sources=['owasp_llm_top10_2026_list.txt']
- answer preview: LLM01 in the OWASP Top 10 for LLM Applications 2026 is **Prompt Injection**.【1】

### Question 5
- Q: Name one risk that NIST associates specifically with generative AI.
- should_refuse=False, refused=False
- sources=['nist_genai_profile.txt', 'nist_genai_profile.txt', 'nist_genai_profile.txt']
- answer preview: Bias in the outputs of generative AI systems. [3]

### Question 6
- Q: What is LLM09 in the OWASP Top 10 related to?
- should_refuse=False, refused=False
- sources=['owasp_llm_top10_2026_list.txt']
- answer preview: I don't know based on the provided documents.

### Question 8
- Q: Does the EU AI Act mention prohibited AI practices in Article 5?
- should_refuse=False, refused=False
- sources=['eu_ai_act_2024_1689.txt', 'eu_ai_act_2024_1689.txt', 'nist_ai_rmf_1.0.txt']
- answer preview: I don't know based on the provided documents.

## Notes

- Gate threshold: `MIN_SCORE = 0.50`
- This eval checks refuse behavior + citation source + simple keyword presence.
- It is a small handmade set, not a production benchmark.
