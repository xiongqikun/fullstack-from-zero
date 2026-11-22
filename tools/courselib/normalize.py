"""Normalisation of what a learner types.

A beginner who knows the right answer must not fail because an input method
produced full-width characters, an extra space, a capital letter or a pair of
quotes.  Everything here is a pure function.
"""

import re

_QUOTE_PAIRS = (
    ('"', '"'), ("'", "'"), ("`", "`"),
    ("“", "”"), ("‘", "’"), ("「", "」"), ("『", "』"),
)
_TRAILING_CJK = "。、"

_CN_DIGITS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
_CN_UNITS = {"十": 10, "百": 100, "千": 1000}
#: 万 and 亿 are part of the run so that 「三万」 is one unreadable numeral and
#: never the number 3.
_CN_RUN = re.compile("[零〇一二两三四五六七八九十百千万亿]+")
#: Measure words (量词) and nouns that can follow a Chinese numeral directly:
#: 「三个」「第二条」「第四课」「十分钟」.  A numeral followed by any other
#: Chinese character is part of a word (「一共」「一起」「一样」) and not a number.
_CN_MEASURE = frozenset("个条行次份项站张处种级位天遍步号层页列段句篇封只件块"
                        "课题章节年月岁名人台把支本首道组分秒")
#: Words that end in a numeral character but mean no number.
_CN_NOT_NUMBERS = ("统一", "唯一", "万一", "之一", "一一")
_DECIMAL = re.compile(r"\d+(?:\.\d+)+")
#: Words that, directly in front of a number, say "not this number":
#: 「不是3」「没有 3 个」「不到 3 个」「负一」.  Longest first.  An adverb
#: between 不 and 是 does not hide it: 「不太是 5」「不一定是 5」.
_NEG_BEFORE = ("不一定是", "不太是", "不大是", "不会是", "不超过", "不是", "不到", "不足", "不止",
               "没有", "并非", "没", "无", "不", "非", "负")
#: Directly after a number (and its measure word): 「一个也没有」「3 个都不是」.
_NEG_AFTER = re.compile(r"\s*[{}]?\s*[也都]?\s*(?:没|无|不是|不到)".format("".join(sorted(_CN_MEASURE))))
#: Comparison words: an answer that gives a bound gives no number, whichever
#: side of the number the word stands on: 「少于3行」「最多 3 行」「至少有 3 个」
#: 「3 个最多」「3 行以上」「5 个以内」「3 个或以上」.  左右 is not one of them:
#: 「3 个左右」 is 3, like 「差不多 3 个」.
COMPARISON_WORDS = ("少于", "小于", "低于", "不到", "不足", "不超过", "不多于", "不少于", "至多",
                    "最多", "至少", "最少", "超过", "多于", "大于", "高于",
                    "以上", "以下", "以内", "以外")
#: The four that only follow what they bound (「3 行以上」); in front of a
#: number they mean something else (「. 和 .. 以外有 5 个」 is 5).
_COMPARISON_AFTER_ONLY = ("以上", "以下", "以内", "以外")


def _alternatives(words):
    return "(?:{})".format("|".join(sorted(words, key=len, reverse=True)))


_BEFORE_WORDS = _alternatives([word for word in COMPARISON_WORDS
                               if word not in _COMPARISON_AFTER_ONLY])
_ALL_WORDS = _alternatives(COMPARISON_WORDS)
#: A comparison word before the number, maybe followed by 等于 and up to three
#: filler characters: 「大于等于 3」「至少有 3 个」「最多也就 3 行」「超过了 3 个」
#: 「至少得 3 个」「最多只有 3 个」; or alone in brackets: 「（至少）3 个」.
_COMPARE_BEFORE = re.compile(
    r"(?:" + _BEFORE_WORDS + r"(?:或?等于)?\s*[了得也就只都有是要会]{0,3}"
    + r"|[（(]\s*" + _BEFORE_WORDS + r"\s*[)）])\s*$")
#: A comparison word after the number, its measure word or a short noun:
#: 「3 行以上」「5 个文件以内」「3 个或以上」「3 个最多」; also alone in
#: brackets, which is no aside: 「3（以上）」「3 个（至少）」.
_COMPARE_AFTER = re.compile(r"\s*[一-鿿]{0,3}?\s*(?:" + _ALL_WORDS
                            + r"|[（(]\s*" + _ALL_WORDS + r"\s*[)）])")
#: 第 before a number makes it an ordinal, which a word after it does not
#: bound: 「第 3 行最多」「第三条最多」 name one line.
_ORDINAL_BEFORE = re.compile(r"第\s*$")
#: What may stand between a negation or a comparison word and the number:
#: spaces and an opening bracket (「不是（3）」「没有（3 个）」「不 是 5」).
_GAP_BEFORE = " \t(（[【「“\"'"
#: A half after the number: 「三个半」「3 个半」 is not a whole number.
_HALF_AFTER = re.compile(r"\s*[{}]?\s*半".format("".join(sorted(_CN_MEASURE))))
#: A Chinese numeral may also be followed by these: 「三到四个」 is a range.
_CN_RANGE = "到至半"
#: An aside in brackets: 「4 行（第一行是标题）」「3（不确定）」.
_ASIDE = re.compile(r"[（(][^（）()]*[)）]")
#: Kept for older callers; parse_int now looks only at the words next to a number.
_CN_NEGATION = ("没", "无", "不")


def to_halfwidth(text):
    """Convert full-width ASCII variants and the ideographic space."""
    out = []
    for ch in str(text):
        code = ord(ch)
        if code == 0x3000:
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)


def normalize(text, case=True, quotes=True, spaces=True):
    """Return ``text`` trimmed, half-width, lower-case and without wrapping quotes.

    - full-width letters, digits and punctuation become half-width;
    - leading and trailing white space goes, inner runs collapse to one space
      (``spaces=False`` keeps inner runs);
    - one pair of surrounding quotes or backticks is removed (``quotes=False``
      keeps it), and a trailing 。 or 、 is dropped;
    - letters are lower-cased (``case=False`` keeps case).
    """
    s = to_halfwidth(text).replace("\u00a0", " ").replace("\t", " ")
    s = s.strip()
    if spaces:
        s = " ".join(s.split())
    while s and s[-1] in _TRAILING_CJK:
        s = s[:-1].rstrip()
    if quotes:
        for left, right in _QUOTE_PAIRS:
            if len(s) >= 2 and s[0] == left and s[-1] == right:
                s = s[1:-1].strip()
                break
    if case:
        s = s.lower()
    return s


def _cn_to_int(numeral):
    """Chinese numerals from 0 to 9999 (三, 十, 十二, 二十, 四十五, 一百二十, 一百零五, 两千).

    None for anything that is not one plainly written number: two digits in
    a row (三四), a colloquial short form (一百二), units out of order, a
    stray 零, and every numeral with 万 or 亿.
    """
    if numeral in ("零", "〇"):
        return 0
    total = 0
    digit = None            # a digit waiting for its unit
    last_unit = None        # the unit used last; units must get smaller
    zero_seen = False       # a 零 since the last unit
    for index, ch in enumerate(numeral):
        if ch in _CN_DIGITS:
            value = _CN_DIGITS[ch]
            if digit is not None:
                return None             # 三四, 二零
            if value == 0:
                if last_unit is None:
                    return None         # 零五
                zero_seen = True
                continue
            digit = value
        elif ch in _CN_UNITS:
            unit = _CN_UNITS[ch]
            if last_unit is not None and unit >= last_unit:
                return None             # 十百, 十十
            if digit is None:
                if unit == 10 and index == 0:
                    digit = 1           # 十, 十二
                else:
                    return None         # 百, 一百十二, 一百零十
            total += digit * unit
            digit = None
            last_unit = unit
            zero_seen = False
        else:
            return None                 # 万, 亿
    if digit is not None:
        if last_unit is None:
            if len(numeral) != 1:
                return None
        elif last_unit > 10 and not zero_seen:
            return None                 # 一百二: 120 in speech, 102 on paper
        total += digit
    elif zero_seen:
        return None                     # 一百零
    return total


def _is_cjk(ch):
    return "\u4e00" <= ch <= "\u9fff"


def _number_tokens(s):
    """Every number in ``s`` as (start, end, value); value None = unreadable."""
    tokens = [(m.start(), m.end(), int(m.group(0))) for m in re.finditer(r"-?\d+", s)]
    words = s
    for word in _CN_NOT_NUMBERS:
        words = words.replace(word, " " * len(word))
    for match in _CN_RUN.finditer(words):
        after = words[match.end():match.end() + 1]
        if after and _is_cjk(after) and after not in _CN_MEASURE and after not in _CN_RANGE:
            continue
        tokens.append((match.start(), match.end(), _cn_to_int(match.group(0))))
    return sorted(tokens)


def _negated(s, start, end):
    """Does a negation, a comparison word or a half govern the number at ``s[start:end]``?"""
    before = s[:start].rstrip(_GAP_BEFORE)
    # 「不 是 5」: a space typed inside the word does not hide it.
    squeezed = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", before)
    if any(squeezed.endswith(word) for word in _NEG_BEFORE):
        return True
    if _COMPARE_BEFORE.search(squeezed):
        return True
    after = s[end:]
    if _NEG_AFTER.match(after) or _HALF_AFTER.match(after):
        return True
    return bool(_COMPARE_AFTER.match(after) and not _ORDINAL_BEFORE.search(s[:start]))


def parse_int(text):
    """Read a whole number from an answer, wherever a beginner puts it.

    Digits (also full-width) and Chinese numerals from 0 to 9999 are found
    anywhere in the answer: "3", "３ 个", "三", "三个文件", "第二条" (2),
    "第四课" (4), "一共三个" (3), "共 12 行" (12), "大概五个" (5).  A
    Chinese numeral counts only when a measure word, a non-Chinese character
    or the end of the answer follows it, so "一共" and "一起" are words, not
    numbers.  A remark in brackets after the number is left aside
    ("4 行（第一行是标题）" is 4, "3（不确定）" is 3), and words such as
    不算 / 不确定 / 不包括 elsewhere in the answer do not matter
    ("5 个，不算 . 和 .." is 5).

    Returns None when the answer holds no number, two different numbers
    ("3 或 4", "第二条，共 3 行", "三到四个"), a decimal, a version or a half
    ("3.5", "1.6a", "三个半"), when a negation governs the number itself
    ("不是3", "没有 3 个", "不到 3 个", "一个也没有", "负一"; spaces or an
    opening bracket in between do not hide it: "不是（3）", "不 是 5",
    "不太是 5"), or when a comparison word gives a bound instead of a number
    (``COMPARISON_WORDS``: "少于3行", "最多 3 行", "至少有 3 个", "3 行以上",
    "5 个以内", "超过了 3 个", "3（以上）"; "3 个左右" is still 3; after an
    ordinal the word bounds nothing: "第 3 行最多" is 3): the tool does not
    guess what was meant.
    """
    s = normalize(text)
    if _DECIMAL.search(s):
        return None
    tokens = _number_tokens(s)
    asides = [m.span() for m in _ASIDE.finditer(s)]

    def inside(token):
        return any(start <= token[0] and token[1] <= end for start, end in asides)

    outside = [token for token in tokens if not inside(token)]
    if outside:
        tokens = outside
    if not tokens:
        return None
    values = set()
    for start, end, value in tokens:
        if value is None or _negated(s, start, end):
            return None          # "三四个", "不是3": not one number
        values.add(value)
    if len(values) != 1:
        return None
    return values.pop()


#: Answers that mean "none at all"; they match an expected 0.
ZERO_WORDS = frozenset(("没有", "没", "无", "都没有", "一个都没有", "一个也没有",
                        "一个没有", "一条都没有", "一条也没有", "none", "no"))


def choice_letter(text, count):
    """Read a multiple-choice answer ("b", "Ｂ", "B.", "选 B", "(b)").

    Returns the index of the chosen option (0-based) or None.
    """
    s = normalize(text)
    for prefix in ("选择", "选", "答案是", "答案", "我选"):
        if s.startswith(prefix):
            s = s[len(prefix):].strip()
    s = s.strip("()[]{}<>.,:;!? ")
    if s.endswith("项"):
        s = s[:-1].strip()
    if len(s) == 1 and "a" <= s <= "z":
        index = ord(s) - ord("a")
        if index < count:
            return index
    return None


#: Dots a learner may type between two words of an option's text (a beginner
#: cannot type the middle dot of 「惯例·事实标准」): folded to one character, on
#: both sides, only when a typed answer is compared with option texts.
OPTION_DOTS = ".。．·・•‧∙"
_DOT_FOLD = {ord(ch): "." for ch in OPTION_DOTS}


def fold_dots(text):
    """``text`` with every character of ``OPTION_DOTS`` replaced by "."."""
    return str(text).translate(_DOT_FOLD)


def option_text_index(typed, labels):
    """The index of the one option whose text ``typed`` is, or None.

    Both sides are normalised and their dots folded (``fold_dots``); an
    answer that is the text of two options after that names none.
    """
    wanted = fold_dots(normalize(typed))
    if not wanted:
        return None
    same = [i for i, label in enumerate(labels) if fold_dots(normalize(label)) == wanted]
    return same[0] if len(same) == 1 else None


def letter_to_index(letter):
    """"A" -> 0, "b" -> 1 ...; None when ``letter`` is not a single letter."""
    if not isinstance(letter, str):
        return None
    s = normalize(letter)
    if len(s) == 1 and "a" <= s <= "z":
        return ord(s) - ord("a")
    return None


def index_to_letter(index):
    """0 -> "A", 1 -> "B" ..."""
    return chr(ord("A") + index)


def matches(answer, expected):
    """Does the learner's ``answer`` satisfy ``expected``?

    ``expected`` may be:

    - a string: equal after ``normalize`` on both sides;
    - an int (not bool): the answer must contain exactly that whole number
      (for 0, "没有" / "无" also count);
    - a compiled regular expression: must match the whole normalised answer;
    - a callable: called with the normalised answer, truthy result means yes;
    - a list, tuple, set or frozenset of the above: any one may match.
    """
    if isinstance(expected, (list, tuple, set, frozenset)):
        return any(matches(answer, one) for one in expected)
    if isinstance(expected, bool):
        raise TypeError("expected must not be a bool")
    if isinstance(expected, int):
        if expected == 0 and normalize(answer) in ZERO_WORDS:
            return True
        return parse_int(answer) == expected
    if isinstance(expected, str):
        return normalize(answer) == normalize(expected)
    if hasattr(expected, "fullmatch"):
        return expected.fullmatch(normalize(answer)) is not None
    if callable(expected):
        return bool(expected(normalize(answer)))
    raise TypeError(f"unsupported expected value: {type(expected).__name__!r}")
