# The volunteer form on pubinv.org (issue #3)

Checked on 2026-10-15 from the public page and an Editor login. Nothing on the site was changed.

## What the form is

- `https://www.pubinv.org/volunteer/` (page 76, built with Beaver Builder) holds **Gravity Forms form #4**.
- Fields: Name (first, last), Email, LinkedIn/GitHub/portfolio, How did you find Public Invention, Which projects are you interested in (free text, with a hint to "use our Project Chat bot"), What drives you to volunteer, How much time can you commit, Phone.
- It asks nothing about skills, so the form alone can't match a volunteer to a project.
- The same page and `/projects/` link to the ChatGPT custom GPT with a "Find Your Project with the Chatbot" button.

## Where the data goes

- Gravity Forms saves every submission as an **entry in the WordPress database** (Forms → Entries → form #4). It also sends any **notification emails** set on the form, and shows a **confirmation** (a message, a page, or a redirect).
- An Editor account has no Gravity Forms permissions, so the entries, notification recipients and confirmation can only be checked by an Administrator. Issue #3 mentions a Calendly step; it isn't on the page, so it's most likely the form's confirmation redirect.
- The site also runs Jetpack Forms (0 responses), which isn't used for volunteering.

## Questions for an Administrator

1. Forms → form #4 → Settings → **Notifications**: who receives each submission?
2. Settings → **Confirmations**: is it a redirect to Calendly? Which questions does Calendly ask that the form already asked (name, email, interests)? Those are the redundant ones to remove.
3. Does anyone review **Entries** today, or only the emails?

## Recommendation

- Keep Gravity Forms as the store: it already holds the entries and sends the emails, and nothing new needs hosting.
- Let the Project Finder fill in the "Which projects" field (see `docs/wordpress-embed.md`), so every submission names real projects instead of free text.
- Optionally add a "Skills" field to form #4 with the same skill list as `data/skills.json`, so Robert can see a volunteer's skills next to their picks.

## The site's own project list

WordPress also has a **Projects** post type: 35 project pages (33 published) with "Activity Statuses", "Means", "Project Categories" and "Skills Needed" taxonomies. It overlaps the workbook but isn't the same list. `data/site_pages.json` links the 12 workbook projects that have a page, so the finder and the GPT send people to the page on pubinv.org instead of raw GitHub.
