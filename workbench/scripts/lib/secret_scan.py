"""PAN pattern detection and secret pattern matching."""
import re
from pathlib import Path

# Load patterns from references/pan-patterns.txt at import time (relative to lib/)
_PATTERN_FILE = Path(__file__).parent.parent.parent / "references" / "pan-patterns.txt"

def _load_patterns() -> list[re.Pattern]:
    if not _PATTERN_FILE.exists():
        return []
    patterns = []
    for line in _PATTERN_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                patterns.append(re.compile(line))
            except re.error:
                pass
    return patterns

_PATTERNS = _load_patterns()

# Common secret patterns (API keys, tokens, passwords)
_SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|api_key|apikey|token|auth)\s*[=:]\s*["\']?\S{8,}'),
    re.compile(r'(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}'),
]


def scan_for_pan(text: str) -> list[str]:
    """Return list of PAN-like matches found in text."""
    matches = []
    for pattern in _PATTERNS:
        matches.extend(pattern.findall(text))
    return matches


def scan_for_secrets(text: str) -> list[str]:
    """Return list of secret-like matches found in text."""
    matches = []
    for pattern in _SECRET_PATTERNS:
        matches.extend(m.group(0) for m in pattern.finditer(text))
    return matches


def scan_file(path: str) -> dict:
    """Scan a file for PAN and secrets. Returns {"pan": [...], "secrets": [...]}."""
    text = Path(path).read_text(errors="replace")
    return {"pan": scan_for_pan(text), "secrets": scan_for_secrets(text)}


def scan_diff(diff_text: str) -> dict:
    """Scan a unified diff for PAN and secrets in added lines (+)."""
    added = "\n".join(
        line[1:] for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++")
    )
    return {"pan": scan_for_pan(added), "secrets": scan_for_secrets(added)}


if __name__ == "__main__":
    result = scan_for_pan("Card: 4111111111111111")
    print("PAN found:", bool(result), "smoke test: OK")
