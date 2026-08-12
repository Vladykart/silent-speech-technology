# Temporary static demo deployment

This guidance is for a separately authorized, bounded preview of the exact committed `demo/` artifact. This worktree does **not** deploy or alter any host, listener, firewall, DNS, repository visibility, or Pages setting.

## Artifact and preflight

1. From the repository root, run:
   ```bash
   python3 demo/generate_manifest.py
   python3 demo/validate.py
   node demo/tests/core.test.js
   ```
2. Compare every uploaded file against [`artifact-manifest.json`](artifact-manifest.json). The manifest excludes only its own hash to avoid recursion; the generator itself is hashed.
3. Publish the complete committed `demo/` directory without transformation. Do not inject analytics, consent managers, fonts, scripts, hot reload, service workers, proxies, or host branding.
4. Keep the temporary banner, truth labels, source panel, `robots.txt`, and 404 page intact.

## Required host behavior

- Static `GET` and `HEAD` only. Reject `POST`, `PUT`, `PATCH`, `DELETE`, and unexpected methods with `405`; do not route writes to another service.
- Disable directory listing and content negotiation. Do not add forms, uploads, comments, accounts, credentials, tokens, sessions, cookies, personalization, or search.
- Serve a **true HTTP 404 status** with [`404.html`](404.html); never return the demo shell as `200` for a missing path.
- No credentials or credential handling. Do not log query strings or request bodies. Minimize ordinary access logs under the preview owner’s policy. The page itself has no telemetry.
- Use HTTPS for any public preview. Do not place this artifact behind a login form or pass credentials through URLs.
- Preserve exact bytes; do not minify, bundle, optimize, rewrite links, or add a service worker.
- Keep `robots.txt` at the origin root and set `X-Robots-Tag` as below. Search exclusion is a request, not a confidentiality control.

## MIME map

| Extension | Content-Type |
|---|---|
| `.html` | `text/html; charset=utf-8` |
| `.css` | `text/css; charset=utf-8` |
| `.js` | `text/javascript; charset=utf-8` |
| `.json` | `application/json; charset=utf-8` |
| `.txt` | `text/plain; charset=utf-8` |
| `.md` | `text/markdown; charset=utf-8` |
| `.py` | `text/plain; charset=utf-8` |

Never serve `.js` or `.json` as HTML. Send `X-Content-Type-Options: nosniff`.

## Required response headers

Apply to every response, including errors; keep the page’s matching meta safeguards as defense in depth.

```text
Content-Security-Policy: default-src 'self'; base-uri 'none'; connect-src 'none'; font-src 'self'; form-action 'none'; frame-ancestors 'none'; frame-src 'none'; img-src 'self'; media-src 'none'; object-src 'none'; script-src 'self'; style-src 'self'
Cross-Origin-Opener-Policy: same-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=(), browsing-topics=()
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-Robots-Tag: noindex, nofollow, noarchive, nosnippet, noimageindex
Cache-Control: no-store
```

Do not add a permissive `connect-src`, inline script/style exception, third-party origin, reporting endpoint, or CDN. A strict transport-security header is appropriate only when the preview operator controls the HTTPS origin and understands its subdomain scope.

## Preview closeout

At the end of the authorized window, remove the preview artifact and verify the origin returns a true 404. Retain the commit SHA and manifest as release evidence, not traffic or user data. Public reachability does not upgrade any technical, performance, privacy, safety, customer, or production claim.
