# Anly Website

Marketing landing page for Anly — intro copy, a QR/download section, and a footer
with placeholder links for Terms of Service / Privacy Policy (to be filled in once
those documents exist; see the main Anly-master repo's CLAUDE.md for context).

Plain HTML/CSS, no build step, no dependencies.

## Local preview

```sh
cd anly-website
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy (Vercel, free subdomain)

1. Push this repo to GitHub.
2. Go to [vercel.com](https://vercel.com), sign in with GitHub, "Add New Project," import this repo.
3. Framework preset: "Other" (static site, no build command, output directory `.`).
4. Deploy — you'll get a free `https://<project-name>.vercel.app` URL.

Every push to the connected branch auto-deploys. A custom domain can be added later
under Project Settings → Domains, once you have one.

## TODO before real launch

- Swap the placeholder QR box (`.qr-placeholder` in `styles.css`) for a real QR code
  pointing at the App Store / Play Store listing, once published.
- Replace the "Notify me" `mailto:` link with a real signup if you want to capture
  emails properly instead of relying on people's mail client.
- Fill in real Terms of Service / Privacy Policy pages and link them from the footer
  (currently `#` placeholders).
