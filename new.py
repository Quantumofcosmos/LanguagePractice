from __future__ import annotations

import argparse
import yaml

from renderer import POSTS, existing_numbers


def next_number() -> int:
    nums = existing_numbers()
    return nums[-1] + 1 if nums else 1


def make_post(number: int, chapter: int, sentence: int):
    target = POSTS / f"{number:03d}.yaml"
    if target.exists():
        raise FileExistsError(f"Already exists: {target}")

    data = {
        "number": number,
        "chapter": chapter,
        "sentence": sentence,
        "english": {"tokens": [{"text": ""}]},
        "chinese": {
            "tokens": [{"text": "", "reading": "", "meaning": None, "study": False}],
            "pattern": None,
            "observation": None,
        },
        "japanese": {
            "tokens": [{
                "text": "",
                "reading": "",
                "kana": None,
                "meaning": None,
                "study": False,
            }],
            "pattern": None,
            "observation": None,
        },
        "german": {
            "tokens": [{"text": "", "reading": None, "meaning": None, "study": False}],
            "pattern": None,
            "observation": None,
        },
        "connection": None,
        "field_note": None,
    }

    target.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return target


def main():
    parser = argparse.ArgumentParser(description="Create a new learning post.")
    parser.add_argument("--number", type=int, default=None)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--sentence", type=int, required=True)
    args = parser.parse_args()

    number = args.number or next_number()
    path = make_post(number, args.chapter, args.sentence)
    print(f"Created {path}")


if __name__ == "__main__":
    main()
