"""Issue detection engine — classifies reviews for performance/stability issues."""
import re
from sqlalchemy.orm import Session

from src.models.review import Review
from src.models.issue_report import IssueReport

ISSUE_PATTERNS = {
    "crash": [
        r"\bcrash(?:es|ed|ing)?\b",
        r"\bgame\s+crash",
        r"\bcrashes?\s+(?:to\s+desktop|constantly|every)",
    ],
    "freeze": [
        r"\bfreez(?:es?|ing)\b",
        r"\bfroze\b",
        r"\bhangs?\b",
        r"\bnot\s+responding\b",
    ],
    "stutter": [
        r"\bstutter(?:s|ing)?\b",
        r"\bstammer\b",
        r"\bmicro[- ]?stutter",
        r"\bframe\s+drop",
    ],
    "fps": [
        r"\bfps\s+(?:drop|issue|problem|low|dip)",
        r"\blow\s+fps\b",
        r"\bpoor\s+performance\b",
        r"\bperformance\s+(?:issue|problem|bad|terrible)",
        r"\bcan'?t\s+(?:even\s+)?get\s+\d+\s+fps",
    ],
    "disconnect": [
        r"\bdisconnect(?:s|ed|ing)?\b",
        r"\bconnection\s+(?:lost|error|issue|problem)",
        r"\bcan'?t\s+connect",
        r"\bserver\s+(?:connection|issue|problem)",
    ],
    "save_corruption": [
        r"\bsave\s+(?:file|game|data)\s+(?:corrupt|lost|gone|broken)",
        r"\bcorrupt(?:ed)?\s+save",
        r"\blost\s+(?:my\s+)?save",
        r"\bprogress\s+lost",
    ],
    "server": [
        r"\bserver(?:s)?\s+(?:down|issue|problem|bad|full|crash)",
        r"\bmatchmak(?:ing|er)\s+(?:broken|issue|problem|long|slow)",
        r"\bqueue\s+(?:times?|long|forever)",
        r"\bhigh\s+ping\b",
        r"\blag(?:s|gy)?\b",
    ],
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def _extract_sentence(text: str, pattern: str) -> str | None:
    """Extract the sentence containing the matched pattern."""
    sentences = _SENTENCE_SPLIT.split(text)
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            cleaned = sentence.strip()
            if len(cleaned) > 200:
                cleaned = cleaned[:200] + "..."
            return cleaned
    return None


def detect_issues(review_text: str) -> list[tuple[str, str | None]]:
    """Return list of (issue_type, summary_sentence) found in review text."""
    if not review_text:
        return []
    found = []
    for issue_type, patterns in ISSUE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, review_text, re.IGNORECASE):
                summary = _extract_sentence(review_text, pattern)
                found.append((issue_type, summary))
                break
    return found


def process_reviews_for_issues(db: Session, game_id: int) -> dict[str, int]:
    """Scan all reviews for a game and create issue reports. Returns counts."""
    reviews = db.query(Review).filter(Review.game_id == game_id).all()
    issue_counts: dict[str, int] = {}
    for review in reviews:
        issues = detect_issues(review.review_text or "")
        for issue_type, summary in issues:
            existing = db.query(IssueReport).filter(
                IssueReport.game_id == game_id,
                IssueReport.review_id == review.id,
                IssueReport.issue_type == issue_type,
            ).first()
            if not existing:
                report = IssueReport(
                    game_id=game_id,
                    review_id=review.id,
                    issue_type=issue_type,
                    confidence=1.0,
                    summary=summary,
                )
                db.add(report)
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    db.commit()
    return issue_counts
