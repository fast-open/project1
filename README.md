# dasoftn.in static clone (Vercel + GitHub Pages)

This repository contains a static snapshot clone of `http://www.dasoftn.in` generated from the site's WordPress sitemap.

## Important repository note

Some PR platforms reject binary files in diffs. To keep PRs compatible, this repository stores a **text-only snapshot** (HTML/CSS/JS/SVG) and excludes binary assets (fonts/images).

That means:
- Pages and navigation work.
- Some typography and thumbnails may not render exactly like the source site.

## Feasibility

### Can this be hosted free on Vercel long-term?

Short answer: **yes, technically feasible** for a low-to-moderate traffic site.

Why:
- The cloned output is static HTML/CSS/JS/media, so it can be served as static hosting.
- Static assets are exactly what Vercel's free tier handles best.
- There is no database or server runtime required for this snapshot.

Caveats:
- This clone is a **snapshot**, not a live WordPress backend. New posts/changes on the original site will not automatically appear.
- If traffic grows significantly, free-tier limits may eventually be exceeded.
- You should ensure you have permission to mirror/rehost the content.

### Can this be hosted free on GitHub itself (right now)?

**Yes.** You can publish it on **GitHub Pages** for free.

This repo includes a Pages workflow at `.github/workflows/deploy-pages.yml` that deploys `cloned-site/www.dasoftn.in`.

## Files

- `cloned-site/www.dasoftn.in/`: generated static website files (text-only snapshot for PR compatibility).
- `scripts/mirror_site.sh`: reruns sitemap discovery + mirroring, then removes binary assets.
- `scripts/urls.txt`: URL list extracted from sitemap for the latest run.
- `.github/workflows/deploy-pages.yml`: GitHub Actions workflow for GitHub Pages deployment.

## Refresh the clone

```bash
./scripts/mirror_site.sh
```

## Run locally

```bash
python3 -m http.server 4173 -d cloned-site/www.dasoftn.in
```

Then open <http://localhost:4173>.

## Launch on GitHub Pages (free)

1. Push this repository to GitHub.
2. Make sure your default branch is `main` (or edit `.github/workflows/deploy-pages.yml` to your branch name).
3. In GitHub: **Settings → Pages → Source = GitHub Actions**.
4. Go to the **Actions** tab and run **Deploy static clone to GitHub Pages** (or push to `main`).
5. After deployment, your site will be available at:
   - `https://<your-username>.github.io/<repo-name>/`

> Note: Project Pages URLs include the repository name in the path.

## Deploy to Vercel

Use the Vercel dashboard and set:
- **Project Root**: repository root
- **Framework Preset**: Other
- **Output Directory**: `cloned-site/www.dasoftn.in`
- **Build Command**: leave empty

Or use CLI from repo root:

```bash
vercel --prod
```

(When prompted, set output directory to `cloned-site/www.dasoftn.in`.)
