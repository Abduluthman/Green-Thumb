"""One-time migration from the legacy dictionary list to schema version 2.

This script preserves every legacy description and instruction. It normalises
classification fields mechanically and marks legacy guidance honestly; it does
not claim that the text has been independently verified.
"""

from __future__ import annotations

import json
import re
import unicodedata
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = ROOT / "dictionary.json"

STREAM_LABELS = {
    "recyclable": "Recyclable material",
    "organic": "Organic waste",
    "e-waste": "Electronic waste",
    "hazardous": "Hazardous waste",
    "general": "General waste",
    "construction": "Construction waste",
    "industrial": "Industrial waste",
    "compostable": "Compostable waste",
}

SOURCE_ALIGNED = {
    "Medicines": ["nafdac-medicine-disposal"],
    "Syringe": ["who-sharps", "nesrea-healthcare-waste"],
    "Batteries": ["nesrea-battery-regulations"],
    "Used Batteries": ["nesrea-battery-regulations"],
}

ALIAS_ADDITIONS = {
    "Glass": ["Broken Glass"],
}

PRESSURISED = {"Aerosol Can", "Fire Extinguishers", "Gas Cylinders", "Inhalers", "Lighters"}
CHEMICAL = {
    "Brake fluid",
    "Cleaning Products",
    "Engine Oil",
    "Fertilizers",
    "Glue",
    "Insecticide",
    "Oil Filters",
    "Paint",
    "Pesticides",
    "Petrol",
}
SHARP = {"Broken Glass", "Glass", "Mirrors", "Razor Blade", "Syringe"}
HEALTHCARE = {"Inhalers", "Medicines", "Syringe", "X-ray Film"}
CONTAMINATED = {"Animal Waste", "Dead Animals", "Diapers"}


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def streams(category: str) -> list[str]:
    value = category.lower()
    found = []

    # Handle labels whose words contain another stream name before applying
    # broader substring rules ("inorganic" is not organic, for example).
    if "non-recyclable" in value:
        found.append("general")
        value = value.replace("non-recyclable", "")
    if "inorganic" in value:
        found.append("general")
        value = value.replace("inorganic", "")

    checks = [
        ("hazard", "hazardous"),
        ("e-waste", "e-waste"),
        ("electronic", "e-waste"),
        ("organic", "organic"),
        ("compost", "compostable"),
        ("recycl", "recyclable"),
        ("construction", "construction"),
        ("industrial", "industrial"),
        ("municipal", "general"),
    ]
    for token, normalised in checks:
        if token in value and normalised not in found:
            found.append(normalised)
    return found or ["general"]


def flags(item: dict, normalised_streams: list[str]) -> list[str]:
    name = item["wasteType"]
    values = []
    for condition, flag in [
        (name in PRESSURISED, "pressurised"),
        (name in CHEMICAL, "chemical"),
        (name in SHARP, "sharp"),
        (name in HEALTHCARE, "healthcare"),
        (name in CONTAMINATED, "contaminated"),
        ("e-waste" in normalised_streams, "electronic"),
        ("battery" in name.lower(), "battery"),
        (name == "Petrol", "flammable"),
    ]:
        if condition and flag not in values:
            values.append(flag)
    return values


def routes(item: dict, normalised_streams: list[str]) -> list[str]:
    text = item["properDisposal"].lower()
    found = []
    checks = [
        ("hazardous" in normalised_streams or "hazardous" in text, "hazardous-collection"),
        ("e-waste" in normalised_streams or "e-waste" in text, "e-waste-collection"),
        (
            any(word in text for word in ("pharmacy", "medical facilit", "animal control", "supplier")),
            "specialist-service",
        ),
        (any(word in text for word in ("compost", "organic waste")), "compost"),
        (any(word in text for word in ("donate", "reuse", "re-use")), "reuse-or-donate"),
        (any(word in text for word in ("recycl", "scrap metal")), "recycling"),
        (any(word in text for word in ("regular trash", "general trash", "landfill", "throw")), "general-waste"),
    ]
    for condition, route in checks:
        if condition and route not in found:
            found.append(route)
    return found or ["check-locally"]


def source_ids(item: dict, normalised_streams: list[str]) -> list[str]:
    ids = list(SOURCE_ALIGNED.get(item["wasteType"], []))
    if "e-waste" in normalised_streams:
        ids.extend(["nesrea-electronics-regulations", "nesrea-epr-guidance"])
    if "hazardous" in normalised_streams and "nesrea-regulations" not in ids:
        ids.append("nesrea-regulations")
    return list(dict.fromkeys(ids))


def migrate(items: list[dict]) -> dict:
    migrated = []
    for legacy in items:
        normalised_streams = streams(legacy["wasteCategory"])
        handling_flags = flags(legacy, normalised_streams)
        risk = (
            "special-handling" if "hazardous" in normalised_streams else ("take-care" if handling_flags else "standard")
        )
        linked_sources = source_ids(legacy, normalised_streams)
        migrated.append(
            {
                "id": slug(legacy["wasteType"]),
                "name": legacy["wasteType"],
                "aliases": list(
                    dict.fromkeys((legacy.get("otherNames") or []) + ALIAS_ADDITIONS.get(legacy["wasteType"], []))
                ),
                "streams": normalised_streams,
                "riskLevel": risk,
                "handlingFlags": handling_flags,
                "description": legacy["description"],
                "guidance": {
                    "disposal": legacy["properDisposal"],
                    "preparation": legacy.get("precautions") or "Check local requirements before disposal.",
                    "routes": routes(legacy, normalised_streams),
                    "jurisdiction": "General guidance; confirm for the FCT",
                    "status": "source-linked" if linked_sources else "historical",
                    "reviewedAt": "2026-09-18" if linked_sources else None,
                    "sourceIds": linked_sources,
                },
                "legacyCategory": legacy["wasteCategory"],
            }
        )

    return {
        "schemaVersion": 2,
        "lastDataAudit": "2026-09-18",
        "defaultJurisdiction": {
            "code": "NG-FC",
            "name": "Federal Capital Territory, Nigeria",
            "authority": "Abuja Environmental Protection Board (AEPB)",
            "contactNote": "Confirm collection options for your district before travelling or disposing of an item.",
            "phoneNumbers": ["07026550000", "08091038888"],
            "sourceId": "fcta-waste-contact",
        },
        "streams": STREAM_LABELS,
        "riskLevels": {
            "standard": "Standard handling",
            "take-care": "Take care",
            "special-handling": "Special handling",
        },
        "routeLabels": {
            "recycling": "Material recycling",
            "compost": "Composting or organic collection",
            "reuse-or-donate": "Reuse or donation",
            "e-waste-collection": "Electronic-waste collection",
            "hazardous-collection": "Hazardous-waste collection",
            "specialist-service": "Specialist or take-back service",
            "general-waste": "General waste",
            "check-locally": "Check local options",
        },
        "sources": {
            "aepb-profile": {
                "title": "Abuja Environmental Protection Board",
                "organisation": "Federal Capital Territory Administration",
                "url": "https://www.fcta.gov.ng/ova_dep/abuja-environmental-protection-board-aepb/",
            },
            "fcta-waste-contact": {
                "title": "FCT municipal frequently asked questions",
                "organisation": "Federal Capital Territory Administration",
                "url": "https://www.fcta.gov.ng/faq/",
            },
            "nesrea-regulations": {
                "title": "National environmental laws and regulations",
                "organisation": "NESREA",
                "url": "https://nesrea.gov.ng/laws-regulations/",
            },
            "nesrea-electronics-regulations": {
                "title": "National Environmental (Electrical/Electronic Sector) Regulations, 2022",
                "organisation": "NESREA",
                "url": "https://nesrea.gov.ng/laws-regulations/",
            },
            "nesrea-battery-regulations": {
                "title": "National Environmental (Battery Control) Regulations, 2024",
                "organisation": "NESREA",
                "url": "https://nesrea.gov.ng/laws-regulations/",
            },
            "nesrea-healthcare-waste": {
                "title": "National Environmental (Healthcare Waste Control) Regulations, 2021",
                "organisation": "NESREA",
                "url": "https://nesrea.gov.ng/laws-regulations/",
            },
            "nesrea-epr-guidance": {
                "title": "Extended Producer Responsibility guidance",
                "organisation": "NESREA",
                "url": "https://www.nesrea.gov.ng/wp-content/uploads/2021/02/Finalized_EPR_Guidance_Document.pdf",
            },
            "nafdac-medicine-disposal": {
                "title": "Safe disposal of old medicines at home",
                "organisation": "NAFDAC",
                "url": "https://nafdac.gov.ng/wp-content/uploads/Files/Resources/Poison_Control/Safe-disposal-of-Old-Medicines-at-Home-Tips-for-Parents-and-Caregivers.pdf",
            },
            "who-sharps": {
                "title": "Safe handling and disposal recommendations for sharps",
                "organisation": "World Health Organization",
                "url": "https://cdn.who.int/media/docs/default-source/substance-use/9789241596275-eng.pdf",
            },
        },
        "items": migrated,
    }


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DICTIONARY, help="legacy version 1 JSON file")
    parser.add_argument("--output", type=Path, default=DICTIONARY, help="version 2 output file")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("the input is already migrated or has an unexpected shape")
    args.output.write_text(json.dumps(migrate(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Migrated {len(data)} entries to schema version 2 at {args.output}")


if __name__ == "__main__":
    main()
