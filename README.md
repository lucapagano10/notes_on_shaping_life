# Notes on Shaping Life

This repo now publishes the book as an `mdBook`, using the PDF only as the original source draft.

## Current workflow

1. Convert the PDF into rough Markdown files.
2. Import the usable chapters into `src/`.
3. Build a static website with `mdBook`.
4. Publish it for free on GitHub Pages.

## Source material

The original PDF import is preserved under `build/writebook/`. That directory is intentionally treated as staging output, not the final book source.

To regenerate the staging files from a PDF:

```bash
python3 scripts/pdf_to_writebook.py /absolute/path/to/your-draft.pdf
```

To rebuild the cleaned `mdBook` source files from the staged Markdown:

```bash
python3 scripts/build_mdbook.py
```

## Local preview

Install `mdbook`:

```bash
brew install mdbook
```

Then build or serve the book:

```bash
mdbook build
mdbook serve --open
```

The generated site will be written to `book/`.

## Free publishing

This repo includes a GitHub Actions workflow at `.github/workflows/deploy-mdbook.yml` that can deploy the built book to GitHub Pages.

After pushing this repo to GitHub:

1. Enable GitHub Pages with the GitHub Actions source.
2. Push to `main`.
3. The workflow will build and deploy the site automatically.

## Notes

- `src/` is the source of truth for the final book site.
- The PDF conversion is good enough to start, but you should still do an editorial pass.
- `book.toml` currently assumes the repository path is `lucapagano10/notes_on_shaping_life`; update it if the GitHub repo name changes.
