import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate import answer_question


QUESTIONS_PATH = Path("eval/questions.json")
RESULTS_PATH = Path("eval/results.md")


def source_hit(result: dict, must_include_source: str | None) -> bool:
    if not must_include_source:
        return True
    sources = [c["source"] for c in result.get("citations", [])]
    return must_include_source in sources


def keyword_hit(result: dict, keyword: str | None) -> bool:
    if not keyword:
        return True
    text = (result.get("answer") or "").lower()
    joined_sources = " ".join(c["source"] for c in result.get("citations", [])).lower()
    # also search citation sources is weak; prefer answer text
    return keyword.lower() in text or keyword.lower() in joined_sources


def main() -> None:
    items = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

    rows = []
    refuse_correct = 0
    refuse_total = 0
    answerable_source_hits = 0
    answerable_total = 0
    answerable_keyword_hits = 0
    failures = []

    for item in items:
        qid = item["id"]
        question = item["question"]
        should_refuse = item["should_refuse"]
        must_source = item.get("must_include_source")
        must_keyword = item.get("must_include_keyword")

        print(f"[{qid}] {question}")
        result = answer_question(question)

        refused = result["refused"]
        refuse_ok = refused == should_refuse
        if should_refuse:
            refuse_total += 1
            if refuse_ok:
                refuse_correct += 1

        src_ok = True
        kw_ok = True
        if not should_refuse:
            answerable_total += 1
            src_ok = source_hit(result, must_source)
            kw_ok = keyword_hit(result, must_keyword)
            if src_ok:
                answerable_source_hits += 1
            if kw_ok:
                answerable_keyword_hits += 1

        ok = refuse_ok and src_ok and kw_ok
        if not ok:
            failures.append(
                {
                    "id": qid,
                    "question": question,
                    "should_refuse": should_refuse,
                    "refused": refused,
                    "sources": [c["source"] for c in result["citations"]],
                    "answer": result["answer"][:240],
                }
            )

        rows.append(
            {
                "id": qid,
                "ok": ok,
                "should_refuse": should_refuse,
                "refused": refused,
                "src_ok": src_ok,
                "kw_ok": kw_ok,
            }
        )

    refuse_acc = (refuse_correct / refuse_total) if refuse_total else 0.0
    source_hit_rate = (
        answerable_source_hits / answerable_total if answerable_total else 0.0
    )
    keyword_hit_rate = (
        answerable_keyword_hits / answerable_total if answerable_total else 0.0
    )

    lines = []
    lines.append("# EvidenceQA evaluation results (Day 14)")
    lines.append("")
    lines.append(f"- Total questions: **{len(items)}**")
    lines.append(
        f"- Refuse accuracy: **{refuse_correct}/{refuse_total}** "
        f"({refuse_acc:.0%})"
    )
    lines.append(
        f"- Answerable source hit rate: **{answerable_source_hits}/{answerable_total}** "
        f"({source_hit_rate:.0%})"
    )
    lines.append(
        f"- Answerable keyword hit rate: **{answerable_keyword_hits}/{answerable_total}** "
        f"({keyword_hit_rate:.0%})"
    )
    lines.append("")
    lines.append("## Per-question")
    lines.append("")
    lines.append("| id | ok | should_refuse | refused | source_ok | keyword_ok |")
    lines.append("|---:|:--:|:-------------:|:-------:|:---------:|:----------:|")
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['ok']} | {r['should_refuse']} | {r['refused']} | "
            f"{r['src_ok']} | {r['kw_ok']} |"
        )

    lines.append("")
    lines.append("## Failures (honest)")
    lines.append("")
    if not failures:
        lines.append("No failures on this run.")
    else:
        for f in failures[:5]:
            lines.append(f"### Question {f['id']}")
            lines.append(f"- Q: {f['question']}")
            lines.append(f"- should_refuse={f['should_refuse']}, refused={f['refused']}")
            lines.append(f"- sources={f['sources']}")
            lines.append(f"- answer preview: {f['answer']}")
            lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- Gate threshold: `MIN_SCORE = 0.50`")
    lines.append("- This eval checks refuse behavior + citation source + simple keyword presence.")
    lines.append("- It is a small handmade set, not a production benchmark.")

    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {RESULTS_PATH}")
    print(f"Refuse accuracy: {refuse_correct}/{refuse_total}")
    print(f"Source hit rate: {answerable_source_hits}/{answerable_total}")


if __name__ == "__main__":
    main()