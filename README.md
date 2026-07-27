# Little Prince Journal

A token-based YAML → Jinja → HTML → Playwright pipeline for learning
*The Little Prince* in Chinese, Japanese and German in parallel.

## Core model

`number` is the global post number.
`chapter` is the book chapter.
`sentence` is the learning-unit number inside that chapter.

Tokens are meaningful learning units, not necessarily individual characters.

### Chinese

```yaml
- text: "六岁"
  reading: "liù suì"
  meaning: "six years old"
  study: true
```

On the language slide, each pinyin reading is physically attached to its token.
Long sentences can wrap without losing reading alignment.

### Japanese

```yaml
- text: "６つ"
  kana: "むっつ"
  reading: "muttsu"
  meaning: "six; here, six years old"
  study: true
```

`kana` becomes ruby only when it exists. Tokens without kana do not emit
`ruby` or `rt`, so they do not create an empty placeholder gap.

`reading` is romaji. The full romaji line is derived from token readings.

### WORDS

Set `study: true` on up to three tokens you want shown in WORDS.
The renderer does not choose the first three tokens automatically.

## Create

```bash
python3 new.py --chapter 1 --sentence 2
```

The global post number increments automatically.

## Preview

Preview the latest post:

```bash
python3 dev.py
```

Or a specific post:

```bash
python3 dev.py 1
```

Custom port:

```bash
python3 dev.py 1 --port 8080
```

## Render PNGs

```bash
python3 render.py 1
```
