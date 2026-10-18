// Workday Math engine - working-day counting between dates you type.
// Mirrored by oracle.py; keep the op order identical.
// Weekends are Saturday and Sunday. Holidays are only the dates the owner lists.

function _date(s, label) {
  var m = /^([0-9]{4})-([0-9]{2})-([0-9]{2})$/.exec(String(s).trim());
  var msg = label + " must be a real date written like 2026-10-19, from 1970 to 2100";
  if (!m) throw new Error(msg);
  var y = parseInt(m[1], 10), mo = parseInt(m[2], 10), d = parseInt(m[3], 10);
  if (y < 1970 || y > 2100) throw new Error(msg);
  var t = Date.UTC(y, mo - 1, d);
  var c = new Date(t);
  if (c.getUTCFullYear() !== y || c.getUTCMonth() !== mo - 1 || c.getUTCDate() !== d) throw new Error(msg);
  return t / 86400000;
}

function _iso(n) {
  return new Date(n * 86400000).toISOString().slice(0, 10);
}

function _holidays(text) {
  var t = String(text).trim();
  if (t === "") return {};
  var parts = t.split(",");
  var msg = "holidays must be up to 50 dates written like 2026-10-19, separated by commas";
  if (parts.length > 50) throw new Error(msg);
  var set = {};
  parts.forEach(function (p) {
    if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(p.trim())) throw new Error(msg);
    set[_date(p, "holiday")] = true;
  });
  return set;
}

function _weekend(n) {
  var wd = (n + 4) % 7;
  return wd === 0 || wd === 6;
}

function _plural(n, word) {
  return n + " " + word + (n === 1 ? "" : "s");
}

function _count(a, b, hol) {
  var w = 0;
  for (var n = a; n <= b; n++) {
    if (!_weekend(n) && !hol[n]) w++;
  }
  return w;
}

function _whole(x, label) {
  if (!Number.isInteger(x) || x < 0 || x > 2000) throw new Error(label + " must be a whole number from 0 to 2000");
  return x;
}

// The count truth: every kind of day between two dates, ends included.
function countTruth(start, end, holidays) {
  var a = _date(start, "start date");
  var b = _date(end, "end date");
  if (b < a) throw new Error("end date must not be before start date");
  if (b - a + 1 > 3660) throw new Error("the span must be 3660 days or fewer");
  var hol = _holidays(holidays);
  var weekend = 0, off = 0, work = 0;
  for (var n = a; n <= b; n++) {
    if (_weekend(n)) weekend++;
    else if (hol[n]) off++;
    else work++;
  }
  return "From " + _iso(a) + " to " + _iso(b) + " inclusive: " + _plural(b - a + 1, "calendar day") + ", " +
    _plural(weekend, "weekend day") + ", " + _plural(off, "holiday") + ", " + _plural(work, "working day") + ".";
}

// The add truth: the date a number of working days after a start date.
function addTruth(start, days, holidays) {
  var a = _date(start, "start date");
  var k = _whole(days, "working days");
  var hol = _holidays(holidays);
  var cur = a, got = 0;
  while (got < k) {
    cur++;
    if (!_weekend(cur) && !hol[cur]) got++;
  }
  return _plural(k, "working day") + " after " + _iso(a) + ": " + _iso(cur) + ".";
}

// The buffer truth: working days after the start through the deadline, against the days needed.
function bufferTruth(start, deadline, needed, holidays) {
  var a = _date(start, "start date");
  var d = _date(deadline, "deadline");
  if (d < a) throw new Error("deadline must not be before start date");
  if (d - a > 3660) throw new Error("the span must be 3660 days or fewer");
  var need = _whole(needed, "needed days");
  var hol = _holidays(holidays);
  var have = _count(a + 1, d, hol);
  var tail = have >= need ? "Spare: " + (have - need) + "." : "Short: " + (need - have) + ".";
  return "Working days after " + _iso(a) + " through " + _iso(d) + " inclusive: " + have + ". Needed: " + need + ". " + tail;
}
