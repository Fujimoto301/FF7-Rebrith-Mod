"""Apply reviewed numeric wording to Chapter 1 and retain an edit history."""
import json
from pathlib import Path
import re
import shutil

from number_style import normalize_numbers

WORK = Path(__file__).resolve().parents[1]


def main():
    backup = WORK / "qa/chapter1/before-number-style"
    backup.mkdir(parents=True, exist_ok=True)
    sources = json.loads((WORK / "reference/chapter1-source.json").read_text(encoding="utf-8"))
    by_index = {str(r["index"]): r for r in sources}
    changes = []
    for path in sorted((WORK / "translations/chapter1").glob("batch-*.json")):
        if not (backup / path.name).exists():
            shutil.copyfile(path, backup / path.name)
        batch = json.loads(path.read_text(encoding="utf-8"))
        for index, before in batch.items():
            after = normalize_numbers(before)
            if before == after:
                continue
            assert re.findall(r"</?[^>]+>", before) == re.findall(r"</?[^>]+>", after)
            row = by_index[index]
            changes.append(dict(index=int(index), id=row["id"], asset=row["asset"], before=before, after=after))
            batch[index] = after
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path = WORK / "reference/gender-particle-review.json"
    if not (backup / review_path.name).exists():
        shutil.copyfile(review_path, backup / review_path.name)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    for row in review["rows"]:
        before = row["after"]
        row["after"] = normalize_numbers(before)
        if before != row["after"]:
            row["number_style_adjusted"] = True
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = WORK / "qa/chapter1/number-style-changes.json"
    if changes:
        report.write_text(json.dumps(dict(changed_records=len(changes), rows=changes), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(changes)} numeric dialogue records; IDs and tags preserved")


if __name__ == "__main__":
    main()
