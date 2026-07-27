import argparse
from renderer import existing_numbers, load_post, render_one


def main():
    parser = argparse.ArgumentParser(description="Render Little Prince Instagram carousel posts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("number", nargs="?", type=int, help="Post number, e.g. 17")
    group.add_argument("--all", action="store_true", help="Render every numbered YAML post")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML but no PNG screenshots")
    parser.add_argument("--validate-only", action="store_true", help="Validate YAML only")
    args = parser.parse_args()

    numbers = existing_numbers() if args.all else [args.number]

    for number in numbers:
        if args.validate_only:
            load_post(number)
            print(f"OK {number:03d}")
            continue

        paths = render_one(number, screenshots=not args.html_only)
        print(f"Rendered {number:03d}")
        for path in paths:
            print(f"  {path}")


if __name__ == "__main__":
    main()
