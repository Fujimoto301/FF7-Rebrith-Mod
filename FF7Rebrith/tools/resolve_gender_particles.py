"""Resolve all 71 original particle-bearing records using bounded evidence.

Retain gendered particles only with a matched speaker identity or an explicit
gendered actor label in the game's US data. Unmatched optional dialogue uses
polite neutral Thai; a shared NPC suffix alone is never marked video proof.
"""
import json
from pathlib import Path
import re
import shutil
from number_style import normalize_numbers

WORK = Path(__file__).resolve().parents[1]
VIDEO = "https://www.youtube.com/watch?v=i4gD0mmj5vc"


def main():
    baseline_path = WORK / "reference/gender-particle-baseline.json"
    if not baseline_path.exists():
        shutil.copyfile(WORK / "qa/chapter1/gender-particle-audit.json", baseline_path)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert baseline["entries"] == 71
    sources = json.loads((WORK / "reference/chapter1-source.json").read_text(encoding="utf-8"))
    indexes = {r["id"]: str(r["index"]) for r in sources}
    batches = {p: json.loads(p.read_text(encoding="utf-8"))
               for p in sorted((WORK / "translations/chapter1").glob("batch-*.json"))}
    owner = {index: path for path, batch in batches.items() for index in batch}
    backup = WORK / "qa/chapter1/before-gender-review"
    backup.mkdir(parents=True, exist_ok=True)
    for path in batches:
        if not (backup / path.name).exists():
            shutil.copyfile(path, backup / path.name)

    def visual(gender, seconds, observation):
        return dict(method="video_speaker_identity", gender=gender,
                    timestamp_seconds=seconds, url=VIDEO + f"&t={seconds}s",
                    observation=observation, audio_reviewed=False,
                    every_line_watched=False)

    named = {
        "tif": visual("female", 2307, "Tifa is visible addressing Sephiroth with the matched guide greeting. Same named actor identity applies to her other records."),
        "znd": visual("male", 1225, "Mayor Zander is visible speaking with his English actor label. Same named actor identity applies to the three mayor records."),
        "cld": visual("male", 2352, "Cloud is visible in the photo scene. The retained record has the unambiguous original ACTOR Cloud."),
        "skm": visual("male", 1018, "Close-up of the truck driver, with Driver label and Got some fiends at our twelve subtitle, matches this record."),
    }
    exact = {
        "$C1910_MAIN_3000_2900_00_mma": visual("male", 2352, "The photographer is visible holding his camera beside the party in the photo scene."),
        "$C1910_MAIN_2400_0100_00_mfa": visual("female", 2034, "Female innkeeper is visible at the Nibelheim inn counter. Identity is matched by the inn location and role; not the similarly labelled Kalm innkeeper."),
        "$NIBLT_NPC_10_0300_5000_00_mfa": visual("female", 2034, "Same innkeeper is visible and Make sure you're good and rested is shown, matching the game's US version of this exact record."),
        "$NIBLT_NPC_10_0300_5300_00_mma": visual("male", 1457, "Male villager is visible speaking with Villager label and I'm eager to talk to him too, but now's not the time subtitle, matching this exact record."),
        "$C1910_MAIN_7150_0500_00_mma": dict(method="explicit_game_actor_label", gender="male", actor_us="Militiaman", observation="Exact US record explicitly labels this speaker Militiaman. Initial คะ… in คะ…ครับ! is a stutter, not a feminine sentence particle.", video_verified=False),
        "$NIBLT_NPC_10_0500_1100_00_mma": dict(method="explicit_game_actor_label", gender="male", actor_us="Militiaman", observation="Exact US record explicitly labels this speaker Militiaman. This is source-data evidence, not a claim of a watched video frame.", video_verified=False),
    }
    overrides = {
        "$C1910_MAIN_0100_0080_00_mma": "ท่านผู้ชมเห็นภาพไหม\r\nอาคารพังถล่มลงมาทั้งหลัง ถนนก็ทรุดตัวลง",
        "$C1910_MAIN_1600_0100_00_mfa": "มาจากชินระใช่ไหม ขอบคุณที่ทำงานหนักเพื่อพวกเรา",
        "$NIBLT_NPC_10_0100_5100_00_mma": "รุ่นพี่ คิดว่าจะไปมิดการ์\r\nแล้วเข้ากองทัพ",
        "$C1910_MAIN_8700_0100_00_brd": "ดูสีหน้าไม่ค่อยดีเลยนะ\r\nบาดแผลเก่าจากสนามรบเจ็บขึ้นมาหรือ?",
        "$C1910_MAIN_8700_0300_00_brd": "แต่ตอนที่ทำงานให้ชินระ\r\nก็นานมาแล้วล่ะ…",
    }
    review = []
    for row in baseline["rows"]:
        key = row["id"]
        index = indexes[key]
        evidence = exact.get(key, named.get(row["speaker_code"]))
        before = row["translation"]
        if evidence:
            after = before
            decision = "retain_verified_particle"
        else:
            after = overrides.get(key, before.replace("ครับ", "").replace("ค่ะ", "").replace("คะ", ""))
            decision = "polite_neutral"
            assert not any(word in after for word in ("ครับ", "ค่ะ", "คะ")), key
        after = normalize_numbers(after)
        assert re.findall(r"</?[^>]+>", before) == re.findall(r"</?[^>]+>", after), key
        batches[owner[index]][index] = after
        review.append(dict(id=key, asset=row["asset"], before=before, after=after,
                           decision=decision, evidence=evidence,
                           reason="Matched speaker evidence" if evidence else
                           "No unambiguous matched on-screen speaker for this record; use neutral polite wording without assuming gender from a shared NPC code."))
    for path, batch in batches.items():
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = dict(video=VIDEO, reviewed_records=len(review),
                  chapter1_only=True, audio_reviewed=False,
                  all_original_particle_records_resolved=True,
                  all_lines_video_verified=False,
                  video_identity_retained=sum(r["evidence"] is not None and r["evidence"]["method"] == "video_speaker_identity" for r in review),
                  explicit_actor_label_retained=sum(r["evidence"] is not None and r["evidence"]["method"] == "explicit_game_actor_label" for r in review),
                  neutral_revisions=sum(r["decision"] == "polite_neutral" for r in review),
                  note="The clip is a speaker-identity reference. It was not watched line by line for every optional subtitle. A brief Chapter 2 probe for the Kalm innkeeper did not establish his identity and is not used as evidence.",
                  rows=review)
    (WORK / "reference/gender-particle-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
