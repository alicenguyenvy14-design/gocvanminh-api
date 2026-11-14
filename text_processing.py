import re, unicodedata

TEENCODE = {
    "ko": "không", "k": "không", "hok": "không", "khong": "không",
    "đc": "được", "dc": "được", "đk": "được",
    "đm": "địt mẹ", "dm": "địt mẹ", "dmm": "địt mẹ", "đmm": "địt mẹ", "đkm": "địt mẹ",
    "vcl": "vãi lồn", "vl": "vãi lồn", "clm": "cái lồn má", "cl": "cái lồn",
    "cc": "cặc", "đb": "đặc biệt", "wa": "quá", "qá": "quá",
    "vs": "với", "mik": "mình", "mk": "mình", "ng": "người",
}

URL_RE   = re.compile(r"https?://\S+|www\.\S+")
MENT_RE  = re.compile(r"@\w+")
REPEAT_RE = re.compile(r"(.)\1{2,}")
REPEAT_TONE_RE = re.compile(r"([^\W\d_])([\u0300-\u036f]*)\1{2,}")   # "quáaaa" (a + dấu + aaa) -> "quá"
MASK_RE  = re.compile(r"(?<=[^\W\d_])[.\-_*+](?=[^\W\d_])")   # đ.m, d*t, c-c -> đm, dt, cc
EMOJI_RE = re.compile(r"([\U0001F300-\U0001FAFF\u2600-\u27BF\u2764])")

def normalize_text(text):
    text = unicodedata.normalize("NFC", str(text)).lower()
    text = URL_RE.sub(" url ", text)
    text = MENT_RE.sub(" user ", text)
    text = unicodedata.normalize("NFC", REPEAT_TONE_RE.sub(r"\1\2", unicodedata.normalize("NFD", text)))
    text = REPEAT_RE.sub(r"\1", text)          # "đmmmm" -> "đm", "!!!" -> "!"
    text = MASK_RE.sub("", text)
    text = EMOJI_RE.sub(r" \1 ", text)
    tokens = [TEENCODE.get(t, t) for t in text.split()]
    return " ".join(tokens)

def dedupe_key(text):
    # Khóa để phát hiện câu "gần trùng": bỏ emoji, dấu câu, khoảng trắng thừa.
    return re.sub(r"[\W_]+", " ", normalize_text(text)).strip()

def remove_accents(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("đ", "d")

