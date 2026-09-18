# Waste dictionary editorial guide

The waste dictionary is a practical companion to the classifier. It is not a substitute for instructions from a waste collector, regulator or health authority. Disposal services differ by location and can change, so every recommendation needs a visible scope and evidence status.

## What changed in schema version 2

`dictionary.json` now separates four ideas that the original `Category` field mixed together:

- **Waste streams** describe where an item may belong: recyclable, organic, general, e-waste, hazardous, construction, industrial or compostable.
- **Risk level** describes the care required: standard, take care or special handling.
- **Handling flags** identify practical concerns such as sharp, broken, pressurised, contaminated or battery-powered items.
- **Routes** describe the next step: reuse, recycle, compost, general collection, specialist collection or authorised disposal.

Each item also records its jurisdiction, editorial status, review date and related source IDs. Sources are defined once in the top-level `sources` registry.

## Evidence statuses

| Status | Meaning |
| --- | --- |
| `historical` | Advice carried over from the final-year project. It has been structured, but not independently verified during this modernization. |
| `source-linked` | One or more official references are relevant to the item or waste stream. The link does not claim that every sentence is quoted from, or specifically endorsed by, that source. |
| `locally-verified` | Reserved for advice checked against a named current service or responsible authority for the stated jurisdiction. No item should receive this status without a dated editorial record. |

The interface states these limits. It does not silently present historical text as settled local policy.

## Editorial workflow

When adding or reviewing an item:

1. Use a stable lowercase hyphenated `id` and a clear everyday `name`.
2. Add only useful search aliases. Do not duplicate the name or add speculative spellings.
3. Select every applicable waste stream, then set the risk level and handling flags independently.
4. Write a short description that helps the user identify the item.
5. Make disposal and preparation instructions concrete. Mention what must be removed, contained or kept separate.
6. Scope the advice to a jurisdiction. Use `NG-FC` for the Federal Capital Territory and `NG` only for national guidance.
7. Attach official or primary references where possible and set `reviewedAt` to the actual review date.
8. Keep the status `historical` when the evidence only supports general context.
9. Run the Python and frontend tests before publishing.

The top-level `lastDataAudit` is the latest structural/content review date for the catalogue. It should not be advanced for formatting-only changes.

## Design decisions and counterarguments

**Use multiple streams rather than one category.** A phone is both e-waste and potentially hazardous, while food-soiled paper may be organic or general waste depending on the service. The tradeoff is added editorial work and the possibility of over-tagging. The tests therefore enforce a small controlled vocabulary.

**Show risk separately from material.** Material alone does not explain whether an object is sharp, contaminated or pressurised. The tradeoff is that users may read a caution label as a formal hazard classification. The labels use plain operational language and the detail page explains the required action.

**Rank search results instead of using fuzzy automatic matches.** Exact names and aliases appear first, followed by prefixes and broader text matches. This improves common searches without silently guessing a different item. Misspellings remain less forgiving; typo suggestions can be added later only if they are visibly presented as suggestions.

**Ask for a subtype after broad model predictions.** The seven-class model cannot tell a bottle from broken glass or an aerosol can from ordinary metal. Optional refinement connects the prediction to safer guidance. It adds one step, so the classifier still shows a usable broad result and never requires the refinement.

**Prefer official references and a small contact directory.** This avoids sending users to an unverified private operator. It also means the directory is initially sparse. Add service providers only after confirming their accepted materials, area, contact details and verification date.

**Preserve historical advice while labelling it.** Removing all unreviewed entries would make the product much less useful and erase part of the project history. Keeping it can still expose stale advice, so the evidence status and local-rule warning remain visible until each entry is reviewed.

**Accept corrections in context.** Each detail page opens the existing feedback form with the item name and dictionary-correction topic filled in. This gives the administrator a review queue without allowing public edits to safety-related guidance. The tradeoff is that the administrator must still verify and apply accepted changes manually.

## Current scope

The catalogue contains 136 entries. It includes official contextual references from AEPB/FCTA, NESREA, NAFDAC and WHO. Source links have been attached to relevant special-handling and e-waste records, but the full disposal wording has not been certified by those organisations. Exact service availability, collection points and operating hours still require direct local verification.

The one-time migration utility is `scripts/migrate_dictionary_v2.py`. The original version 1 file is retained only in the ignored local backup and is not required to run the application.
