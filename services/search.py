from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class SearchResult:
    item: Any
    score: float


class SearchService:
    """Handles search with optional tag prefixes and fuzzy matching."""

    @staticmethod
    def parse_query(query: str) -> Tuple[Optional[str], str]:
        """
        Parse search query for tag prefix.
        Returns: (tag, search_term)
        """
        if ":" not in query:
            return None, query

        tag, term = query.split(":", 1)
        tag = tag.lower().strip()
        term = term.strip()

        tag_map = {
            "s": "spell",
            "m": "monster",
            "i": "item",
            "f": "feat",
            "c": "condition",
        }

        return tag_map.get(tag, tag), term

    @staticmethod
    def fuzzy_match(query: str, text: str, threshold: float = 0.6) -> float:
        """
        Fuzzy matching so substrings score high (e.g. "anim" matches "Animate Dead").
        Returns score 0.0-1.0.
        """
        if not query:
            return 1.0

        try:
            from rapidfuzz import fuzz

            q = query.lower()
            t = text.lower()
            # partial_ratio scores high when query is a substring (best for "anim" in "Animate Dead")
            partial = fuzz.partial_ratio(q, t) / 100.0
            # ratio rewards full-string similarity
            full = fuzz.ratio(q, t) / 100.0
            return max(partial, full)
        except Exception:
            query_lower = query.lower()
            text_lower = text.lower()

            if query_lower == text_lower:
                return 1.0
            if text_lower.startswith(query_lower):
                return 0.9
            if query_lower in text_lower:
                return 0.7
            return 0.0

    @staticmethod
    def search(items: List[Any], query: str, name_attr: str = "name") -> List[Any]:
        """
        Search items by name with fuzzy matching.
        Returns sorted list by relevance.
        """
        _, term = SearchService.parse_query(query)
        if not term:
            return items

        results: List[SearchResult] = []
        for item in items:
            name = getattr(item, name_attr, "")
            score = SearchService.fuzzy_match(term, name)
            if score > 0.5:
                results.append(SearchResult(item=item, score=score))

        results.sort(key=lambda r: (-r.score, getattr(r.item, name_attr, "")))
        return [r.item for r in results]

