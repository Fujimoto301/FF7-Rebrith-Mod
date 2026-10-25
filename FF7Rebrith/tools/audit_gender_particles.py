"""Check the final particle review against assembled translations and evidence."""
import json
from collections import Counter
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
WORDS = ("ครับ", "ค่ะ", "คะ")


def main():
    edits = json.loads((WORK / "translations/chapter1-th.json").read_text(encoding="utf-8"))
    baseline = json.loads((WORK / "reference/gender-particle-baseline.json").read_text(encoding="utf-8"))
    review = json.loads((WORK / "reference/gender-particle-review.json").read_text(encoding="utf-8"))
    originals = {r["id"]: r for r in baseline["rows"]}
    rows = review["rows"]
    assert len(rows) == len(originals) == 71
    assert {r["id"] for r in rows} == set(originals)
    retained = set()
    for row in rows:
        key = row["id"]
        assert row["before"] == originals[key]["translation"], key
        actual = edits["assets"][row["asset"]]["entries"][key]
        assert actual == row["after"], key
        evidence = row["evidence"]
        if row["decision"] == "polite_neutral":
            assert evidence is None and not any(w in actual for w in WORDS), key
        else:
            assert row["decision"] == "retain_verified_particle" and evidence, key
            assert evidence["method"] in ("video_speaker_identity", "explicit_game_actor_label"), key
            if evidence["gender"] == "female":
                assert "ครับ" not in actual, key
            elif evidence["gender"] == "male":
                assert "ค่ะ" not in actual and "คะ" not in actual.replace("คะ…ครับ", "ครับ"), key
            else:
                raise AssertionError(key)
            retained.add(key)
    particle_rows = []
    for asset, patch in edits["assets"].items():
        for key, value in patch["entries"].items():
            counts = {w: value.count(w) for w in WORDS if w in value}
            if counts:
                assert key in retained, (key, "Unreviewed particle")
                particle_rows.append(dict(asset=asset, id=key, translation=value, particles=counts,
                                          stutter_not_female_particle="คะ…ครับ" in value))
    assert len(particle_rows) == len(retained)
    report = dict(original_records_reviewed=len(rows),
                  decisions=dict(Counter(r["decision"] for r in rows)),
                  retained_evidence=dict(Counter(r["evidence"]["method"] for r in rows if r["evidence"])),
                  current_particle_records=len(particle_rows),
                  particle_occurrences={w: sum(r["particles"].get(w, 0) for r in particle_rows) for w in WORDS},
                  all_original_particle_records_resolved=True, all_lines_video_verified=False,
                  audio_reviewed=False, runtime_tested=False,
                  evidence_file="reference/gender-particle-review.json",
                  japanese_reference_file="reference/japanese-video-reference.json",
                  rows=particle_rows)
    output = WORK / "qa/chapter1/gender-particle-audit.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
