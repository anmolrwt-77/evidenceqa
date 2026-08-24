# Embedding sanity check (Day 6)

Model: sentence-transformers/all-MiniLM-L6-v2

## Sentences

1. The EU AI Act bans certain manipulative AI practices.

2. European law prohibits some harmful uses of artificial intelligence.

3. I like to bake chocolate chip cookies on weekends.

4. How do I change the oil in a bicycle?

## Scores

- similar policy meanings: 0.7439

- policy vs cookies: 0.0454

- policy vs bicycle: 0.0853

- cookies vs bicycle: 0.1046

## Conclusion

The similar pair scored much higher than the unrelated pairs, so embeddings capture meaning, not just exact words.