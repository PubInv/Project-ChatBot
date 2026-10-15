# Embedding the Project Finder on pubinv.org (issue #5)

The finder is `chatbot/widget.js`: a guided chat that asks for skills, learning goals and an area, then recommends projects from `data/projects.json` using Public Invention's rules (`pipeline/ranking.py`). It renders inside a shadow DOM, so the site theme can't break it and it can't break the theme.

## 1. Add it to the Volunteer page

An Editor can do this (it needs the `unfiltered_html` capability, which Editors have on this site).

1. Pages → **Volunteer** → **Beaver Builder**.
2. Drag an **HTML** module under "Find Your Project with the Chatbot".
3. Paste:

```html
<div id="pubinv-project-finder"></div>
<script type="module" src="https://cdn.jsdelivr.net/gh/PubInv/Project-ChatBot@main/chatbot/widget.js"></script>
```

4. Preview, then publish.

The script loads from jsDelivr, and the project list loads from `raw.githubusercontent.com`. The page sends no Content-Security-Policy, and FlyingPress isn't delaying scripts there, so nothing else needs changing. jsDelivr caches `@main` for up to 12 hours. After changing `widget.js`, purge it at `https://purge.jsdelivr.net/gh/PubInv/Project-ChatBot@main/chatbot/widget.js` (and the same for `recommend.js`). The data itself refreshes within 5 minutes of the weekly Action.

## 2. Pre-fill the form with the chosen projects

The finder's "Volunteer for these projects" button opens `/volunteer/?projects=<names>`. For Gravity Forms to fill the field from that, an Administrator:

1. Forms → form #4 → the "Which projects at Public Invention are you interested in?" field → **Advanced**.
2. Tick **Allow field to be populated dynamically** and set the parameter name to `projects`.
3. Save the form.

Until then the link still opens the form; the field just starts empty.

## 3. Optional: replace the ChatGPT button

The button currently opens the custom GPT. After the finder is on the page, point the button at `#pubinv-project-finder` instead, or keep both. To update the GPT itself so it reads the same live data, follow the Setup section of `ChatBot_Instructions.md`.

## Try it locally

```bash
python3 -m http.server 8000   # from the repo root
# open http://localhost:8000/chatbot/
```
