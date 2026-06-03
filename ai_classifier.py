import re

# navi + typos: navii, navy, nawii, nawi, navvy
_NAVI  = r"(?:nav[iy]{1,2}i?|naw[iy]{1,2}i?|navvy)"
# cand + typos: kand, qand, cnd, knd, cand (fara diacritic deja inclus)
_CAND  = r"(?:[ck][âa]nd|[ck]nd|qand)"
# joaca + typos: joc, juca, joac, joca, joka, juca
_JOACA = r"(?:jo(?:ac[aă]?|c[aă]?|uc[aă]?|ka?)|juc[aă]?)"
_ORA   = r"or[aă]?"
_INCEPE = r"(?:incepe|începe|start(?:s)?)"
_ACUM  = r"(?:acum|now)"
_AZI   = r"(?:azi|azi\s+(?:noapte|seara|seară)|in\s+seara\s+asta|în\s+seara\s+asta|seara\s+asta|diseara|diseară)"
_MAINE = r"m[aâ]ine"
_TIMP  = r"(?:time|ora|timp)"

_PATTERNS = [
    # ── română: când joacă navi ──────────────────────────────────────────
    rf"{_CAND}\s+{_JOACA}\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+{_CAND}\s+{_JOACA}\s*\??",
    rf"{_JOACA}\s+{_NAVI}\s*\??",                         # "joaca navi?"
    rf"{_NAVI}\s+{_JOACA}\s*\??",                         # "navi joaca?"

    # ── română: când e / când este navi ──────────────────────────────────
    rf"{_CAND}\s+(?:e|este)\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+{_CAND}\s+(?:e|este)\s*\??",

    # ── română: când începe navi ─────────────────────────────────────────
    rf"{_CAND}\s+{_INCEPE}\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+{_CAND}\s+{_INCEPE}\s*\??",
    rf"{_NAVI}\s+{_INCEPE}\s*\??",

    # ── română: la ce oră / ce oră ───────────────────────────────────────
    rf"la\s+ce\s+{_ORA}\s+(?:{_JOACA}\s+|{_INCEPE}\s+|e\s+|este\s+)?{_NAVI}\s*\??",
    rf"ce\s+{_ORA}\s+(?:{_JOACA}\s+|{_INCEPE}\s+|e\s+|este\s+)?{_NAVI}\s*\??",
    rf"{_NAVI}\s+la\s+ce\s+{_ORA}\s*\??",
    rf"(?:ora|orele?)\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+(?:ora|orele?)\s*\??",
    rf"ora\s+meciului\s+(?:cu\s+)?{_NAVI}\s*\??",

    # ── română: la cât ───────────────────────────────────────────────────
    rf"la\s+c[aâ]t\s+(?:{_JOACA}\s+|{_INCEPE}\s+|e\s+)?{_NAVI}\s*\??",
    rf"{_NAVI}\s+la\s+c[aâ]t\s*\??",

    # ── română: meci ─────────────────────────────────────────────────────
    rf"{_CAND}\s+e\s+meciul\s+(?:cu\s+)?{_NAVI}\s*\??",
    rf"meciul\s+(?:cu\s+)?{_NAVI}\s+{_CAND}\s*\??",
    rf"meciul\s+(?:cu\s+)?{_NAVI}\s*\??",                # "meciul navi?"
    rf"urm[aă]torul\s+meci\s+(?:cu\s+|al\s+)?{_NAVI}\s*\??",
    rf"{_NAVI}\s+urm[aă]torul\s+meci\s*\??",

    # ── română: azi / mâine / diseară ────────────────────────────────────
    rf"{_NAVI}\s+(?:{_AZI}|{_MAINE})\s*\??",
    rf"(?:{_AZI}|{_MAINE})\s+{_NAVI}\s*\??",
    rf"(?:{_AZI}|{_MAINE})\s+{_JOACA}\s+{_NAVI}\s*\??",
    rf"{_CAND}\s+{_JOACA}\s+{_NAVI}\s+(?:{_AZI}|{_MAINE})\s*\??",
    rf"{_CAND}\s+{_JOACA}\s+(?:{_AZI}|{_MAINE})\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+{_JOACA}\s+(?:{_AZI}|{_MAINE})\s*\??",

    # ── română: acum ─────────────────────────────────────────────────────
    rf"{_NAVI}\s+{_JOACA}\s+{_ACUM}\s*\??",
    rf"{_JOACA}\s+{_NAVI}\s+{_ACUM}\s*\??",

    # ── română: program ──────────────────────────────────────────────────
    rf"program(?:ul)?\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+program(?:ul)?\s*\??",

    # ── engleză ───────────────────────────────────────────────────────────
    rf"when\s+(?:does?\s+|do\s+|is\s+)?{_NAVI}\s+(?:play(?:ing)?|game|match|start)\s*\??",
    rf"when\s+(?:does?\s+|is\s+)?{_NAVI}\s+(?:on|live)\s*\??",
    rf"when\s+{_NAVI}\s*\??",
    rf"what\s+time\s+(?:does?\s+|do\s+|is\s+)?{_NAVI}\s*\??",
    rf"{_NAVI}\s+(?:schedule|when|game\s+time|match\s+time|start\s+time|time)\s*\??",
    rf"{_NAVI}\s+(?:next\s+)?(?:game|match|play)\s*\??",
    rf"next\s+(?:game|match)\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+(?:today|tonight|tomorrow)\s*\??",
    rf"(?:today|tonight|tomorrow)\s+{_NAVI}\s*\??",
    rf"is\s+{_NAVI}\s+playing\s*\??",
    rf"(?:when|what\s+time)\s+navi\s+vs\s*\??",

    # ── vs cu ? ──────────────────────────────────────────────────────────
    rf"{_NAVI}\s+vs\.?\s*\?",

    # ── română: "cand navi?" (fara verb) ─────────────────────────────────
    rf"{_CAND}\s+{_NAVI}\s*\??",
    rf"{_NAVI}\s+{_CAND}\s*\??",

    # ── română: typos cand ───────────────────────────────────────────────
    rf"c[ao]nd\s+{_NAVI}\s*\??",                # cond/cand cu o
    rf"cand\s+{_JOACA}\s+{_NAVI}\s*\??",        # cand fara diacritic (deja prins mai sus, redundant dar sigur)

    # ── engleză: typos when ──────────────────────────────────────────────
    rf"w(?:he?|ee)n\s+{_NAVI}\s*\??",           # when, wen, ween navi
    rf"wen\s+{_NAVI}\s*\??",                     # wen navi (fara play)
    rf"wen\s+(?:does?\s+|is\s+)?{_NAVI}\s+(?:play(?:ing)?|game|match)\s*\??",
    rf"wut\s+time\s+{_NAVI}\s*\??",             # wut time navi
    rf"wat\s+time\s+{_NAVI}\s*\??",             # wat time navi

    # ── engleză: typos schedule ──────────────────────────────────────────
    rf"{_NAVI}\s+s(?:ch?|h)[ea]d[uoa]*l[eu]?\s*\??",  # scedule, shedule, schedual
]

_RE = re.compile("|".join(_PATTERNS), re.IGNORECASE)


class AIClassifier:
    def classify_batch(self, messages: list[dict]) -> list[bool]:
        return [bool(_RE.search(m["message"])) for m in messages]
