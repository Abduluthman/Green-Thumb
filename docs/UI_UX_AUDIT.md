# Frontend and UI/UX audit

Audit date: **17 September 2026**

## Summary

The previous redesign was tidy and visually polished, but it presented Green Thumb like a generic environmental landing page. Its oversized serif copy, motivational fragments, uppercase labels, ornamental recycling artwork, numbered cards and repeated arrow symbols competed with the actual product. The interface looked designed before it felt useful.

The revised direction treats Green Thumb as a small, credible research tool. It uses plain language, a compact system typeface, a restrained green palette and consistent spacing. Decoration is limited to the project mark and simple functional icons. Important limitations are visible before a user starts a scan.

## Findings and changes

| Finding | Effect on the user | Change made |
| --- | --- | --- |
| Promotional headlines such as “Know your waste. Make a difference.” | Made the product sound generic and hid the concrete task | Replaced with direct task language: “Not sure where an item belongs?” |
| Large serif display type, italics and all-caps eyebrow labels | Created a fashionable editorial style unrelated to the application | Moved to one system sans-serif family with a compact, predictable hierarchy |
| Decorative hero illustration occupied nearly half the first screen | Delayed access to the classifier without explaining how to get a good result | Replaced with a short three-step guide based on actual classifier needs |
| Three floating feature cards, each with numbers, symbols and arrows | Repeated the same hierarchy and felt generated | Consolidated the tools into one divided control group with small functional icons |
| Frequent arrow glyphs and slogan-like fragments | Added visual noise and caused character-encoding problems | Removed decorative arrows and used ordinary link labels |
| Rounded cards around nearly every block | Weakened hierarchy because everything looked equally important | Reserved bordered surfaces for actions, results and grouped content; informational sections are flatter |
| Upload and camera pages opened with vague, aspirational copy | Users had to interpret the page before acting | Titles now name the task and instructions state the next action |
| Result areas mixed status, guidance and disclaimers | Made uncertain outcomes harder to scan | Separated result status, follow-up link, limitation note and feedback action |
| Camera scanning previously used several similar button labels | Increased hesitation around starting, scanning and stopping | Buttons use explicit states: “Start camera”, “Scan item”, “Stop camera” |
| Dictionary used card-like results with external-link arrows | Suggested navigation away from the product and reduced information density | Results are now a compact grid with waste-stream and handling-risk labels |
| A broad model label led directly to generic advice | Hid important differences such as an intact bottle versus broken glass | Added an optional subtype step that opens a specific dictionary search |
| Dictionary search treated every text match equally | Common exact matches could be buried and there was no way to isolate risky items | Added exact/alias/prefix ranking plus waste-stream and handling-risk filters |
| Disposal text had no visible evidence state | Historical project copy could look like current local policy | Added jurisdiction, review status, date and related official references to detail pages |
| Prototype limitations appeared late in the flow | Could give predictions more authority than warranted | Added a persistent research-prototype notice above the main navigation |
| Footer repeated brand copy and sustainability language | Added another promotional layer after the task | Reduced it to authorship, feedback, publication and administration links |

## Interaction model

The primary journeys now follow the same pattern:

1. The page title says what the user can do.
2. Supporting text gives the minimum preparation needed.
3. The main control is presented as step 1.
4. The result is presented as step 2 with a stable empty state.
5. Limitations and correction feedback appear beside the result.

The dictionary is the exception because it is an exploration task. Search and filters remain visible as the result list scrolls, the count updates as the query changes, and item names remain the strongest text in each row. Search uses a predictable rank order: exact name, exact alias, prefixes and then broader content matches.

## Visual system

- **Type:** one system sans-serif stack, avoiding an external font request and keeping rendering familiar across platforms.
- **Colour:** neutral off-white surfaces, dark readable text and one desaturated green accent. Amber is reserved for cautionary notes.
- **Spacing:** a small consistent scale, with a maximum content width of 1120 px and narrower reading widths for forms.
- **Shape:** 7–10 px radii for controls and grouped surfaces; pills are used only for the category tag.
- **Motion:** only subtle hover feedback, disabled when reduced motion is requested.
- **Focus:** high-contrast visible focus rings across links, buttons and fields.

## Responsive and accessibility considerations

- Navigation stays visible and scrolls horizontally on narrow screens instead of hiding core routes behind an unimplemented menu.
- Two-column tasks collapse into a single sequence, preserving input before result.
- Buttons grow to practical touch targets and wrap without clipping.
- Dictionary results collapse from three columns to two and then one.
- Labels are explicit, page landmarks are retained, status messages use live regions, and decorative SVGs are hidden from assistive technology.
- The prototype notice is readable text rather than an icon-only warning.

## Remaining validation

Automated route, DOM, syntax and formatting checks pass, but a browser connection was unavailable during this audit. A final release review should cover Chrome/Edge and Firefox at 360, 768 and 1440 px widths, 200% zoom, keyboard-only navigation, Windows High Contrast Mode and a real mobile camera. The actual model should also be enabled so loading, success, uncertainty and server-error states can be judged with realistic timing.
