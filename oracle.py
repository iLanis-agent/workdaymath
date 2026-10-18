#!/usr/bin/env python3
# Workday Math oracle - mirrors engine.js.
import json, re
from datetime import date, timedelta

EPOCH = date(1970, 1, 1)

def _date(s, label):
    msg = f"{label} must be a real date written like 2026-10-19, from 1970 to 2100"
    m = re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", str(s).strip())
    if not m:
        raise ValueError(msg)
    y, mo, d = int(m[1]), int(m[2]), int(m[3])
    if y < 1970 or y > 2100:
        raise ValueError(msg)
    try:
        dt = date(y, mo, d)
    except ValueError:
        raise ValueError(msg)
    return (dt - EPOCH).days

def _iso(n):
    return (EPOCH + timedelta(days=n)).isoformat()

def _holidays(text):
    t = str(text).strip()
    if t == "":
        return set()
    parts = t.split(",")
    msg = "holidays must be up to 50 dates written like 2026-10-19, separated by commas"
    if len(parts) > 50:
        raise ValueError(msg)
    out = set()
    for p in parts:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", p.strip()):
            raise ValueError(msg)
        out.add(_date(p, "holiday"))
    return out

def _weekend(n):
    return (n + 4) % 7 in (0, 6)

def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")

def _count(a, b, hol):
    return sum(1 for n in range(a, b + 1) if not _weekend(n) and n not in hol)

def _whole(x, label):
    if not isinstance(x, int) or x < 0 or x > 2000:
        raise ValueError(f"{label} must be a whole number from 0 to 2000")
    return x

def count_truth(start, end, holidays):
    a = _date(start, "start date")
    b = _date(end, "end date")
    if b < a:
        raise ValueError("end date must not be before start date")
    if b - a + 1 > 3660:
        raise ValueError("the span must be 3660 days or fewer")
    hol = _holidays(holidays)
    weekend = off = work = 0
    for n in range(a, b + 1):
        if _weekend(n):
            weekend += 1
        elif n in hol:
            off += 1
        else:
            work += 1
    return (f"From {_iso(a)} to {_iso(b)} inclusive: {_plural(b - a + 1, 'calendar day')}, "
            f"{_plural(weekend, 'weekend day')}, {_plural(off, 'holiday')}, {_plural(work, 'working day')}.")

def add_truth(start, days, holidays):
    a = _date(start, "start date")
    k = _whole(days, "working days")
    hol = _holidays(holidays)
    cur, got = a, 0
    while got < k:
        cur += 1
        if not _weekend(cur) and cur not in hol:
            got += 1
    return f"{_plural(k, 'working day')} after {_iso(a)}: {_iso(cur)}."

def buffer_truth(start, deadline, needed, holidays):
    a = _date(start, "start date")
    d = _date(deadline, "deadline")
    if d < a:
        raise ValueError("deadline must not be before start date")
    if d - a > 3660:
        raise ValueError("the span must be 3660 days or fewer")
    need = _whole(needed, "needed days")
    hol = _holidays(holidays)
    have = _count(a + 1, d, hol)
    tail = f"Spare: {have - need}." if have >= need else f"Short: {need - have}."
    return f"Working days after {_iso(a)} through {_iso(d)} inclusive: {have}. Needed: {need}. {tail}"

FNS = {"countTruth": count_truth, "addTruth": add_truth, "bufferTruth": buffer_truth}

CASES = [
    ("countTruth", ["2026-10-19", "2026-10-30", "2026-10-26"]),
    ("countTruth", ["2026-10-19", "2026-10-30", ""]),
    ("countTruth", ["2026-10-19", "2026-10-19", ""]),
    ("countTruth", ["2026-10-24", "2026-10-25", ""]),
    ("countTruth", ["2026-10-19", "2026-10-23", "2026-10-21, 2026-10-21, 2026-10-24"]),
    ("countTruth", ["2024-02-28", "2024-03-01", ""]),
    ("countTruth", ["2026-10-30", "2026-10-19", ""]),
    ("countTruth", ["2026-02-30", "2026-03-05", ""]),
    ("countTruth", ["2026-10-19", "2026-10-30", "26-10-26"]),
    ("countTruth", ["1969-12-31", "2026-10-30", ""]),
    ("countTruth", ["2026-10-19", "2101-01-01", ""]),
    ("countTruth", ["2026-10-19", "2026-10-30", "2026-13-01"]),
    ("countTruth", ["2020-01-01", "2030-01-01", ""]),
    ("addTruth", ["2026-10-19", 5, ""]),
    ("addTruth", ["2026-10-19", 5, "2026-10-21"]),
    ("addTruth", ["2026-10-23", 1, ""]),
    ("addTruth", ["2026-10-24", 0, ""]),
    ("addTruth", ["2026-10-19", 2000, ""]),
    ("addTruth", ["2026-10-19", 2001, ""]),
    ("addTruth", ["2026-10-19", -1, ""]),
    ("addTruth", ["2026-10-19", 2.5, ""]),
    ("addTruth", ["abc", 5, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-30", 8, "2026-10-26"]),
    ("bufferTruth", ["2026-10-19", "2026-10-30", 10, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-30", 9, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-19", 0, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-19", 1, ""]),
    ("bufferTruth", ["2026-10-30", "2026-10-19", 1, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-30", 2001, ""]),
    ("bufferTruth", ["2026-10-19", "2026-10-30", 3, ", "]),
    ("bufferTruth", ["2020-01-01", "2035-01-01", 3, ""]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
