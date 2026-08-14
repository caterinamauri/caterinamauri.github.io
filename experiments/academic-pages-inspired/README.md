# Academic Pages–inspired experiment

This is an isolated visual prototype for Caterina Mauri's personal website. It does not replace the current site and is not linked from its main navigation.

The layout is inspired by the open-source [Academic Pages](https://github.com/academicpages/academicpages.github.io) pattern: a persistent academic profile beside a content-led main column. The implementation is original, deliberately lightweight, and uses the current site's existing content and publication data rather than importing the full Jekyll theme.

## Preview

From the repository root:

```sh
python3 -m http.server 8000
```

Then open:

`http://localhost:8000/experiments/academic-pages-inspired/`

## Deliberate choices

- restrained editorial typography;
- no promotional claims or corporate-style cards;
- compact home page with a clear academic profile;
- real links to the current detailed pages;
- five recent publications loaded from `data/publications.json`;
- responsive mobile navigation.
