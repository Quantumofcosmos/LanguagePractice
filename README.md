# Language Practice

One chronological post stream with two post types.

## Vocabulary chunks
Create a five-concept starter YAML:

```bash
python3 new.py vocabulary --title "People"
```

Vocabulary posts accept 3–6 concepts. Five is the default. They render six slides: overview, Chinese, Japanese, German, usage, reference.

## Sentence posts

```bash
python3 new.py sentence --chapter 1 --sentence 1
```

Sentence posts retain the Little Prince layout and `SENTENCES TRAVELLED` counts only sentence-type posts.

## Preview / render

```bash
python3 dev.py          # latest post
python3 dev.py 2        # specific post
python3 render.py 2
python3 render.py --all
```

Post numbers are global across both types.
