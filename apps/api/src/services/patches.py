"""Patch tracker — extracts and stores patch note data."""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.models.patch import Patch


def extract_patch_categories(notes: str) -> dict[str, str]:
    """Extract bug fixes, performance fixes, server fixes from patch notes text."""
    categories = {
        "bug_fixes": "",
        "performance_fixes": "",
        "server_fixes": "",
    }
    if not notes:
        return categories
    lines = notes.lower().split("\n")
    current_section = "bug_fixes"
    for line in lines:
        stripped = line.strip()
        if "bug" in stripped or "fix" in stripped:
            current_section = "bug_fixes"
        elif "performance" in stripped or "optimization" in stripped or "fps" in stripped:
            current_section = "performance_fixes"
        elif "server" in stripped or "network" in stripped or "connection" in stripped:
            current_section = "server_fixes"
        elif stripped.startswith("-") or stripped.startswith("*"):
            if current_section:
                categories[current_section] += line + "\n"
    for key in categories:
        categories[key] = categories[key].strip()
    return categories


def upsert_patch(
    db: Session,
    game_id: int,
    version: Optional[str],
    title: Optional[str],
    notes: Optional[str],
    released_at: Optional[date],
) -> Patch:
    """Create a patch record for a game."""
    categories = extract_patch_categories(notes)
    patch = Patch(
        game_id=game_id,
        version=version,
        title=title,
        notes=notes,
        bug_fixes=categories["bug_fixes"] or None,
        performance_fixes=categories["performance_fixes"] or None,
        server_fixes=categories["server_fixes"] or None,
        released_at=released_at,
    )
    db.add(patch)
    db.commit()
    return patch
