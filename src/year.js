/* The Christian year: the order of the Book of Common Prayer (1928), public
   domain.  These functions are taken unchanged from the js/liturgy.js that
   studytools.cc runs, so the day this wallpaper names is the day the site
   names, and so is the season. */
var ScriptureYear = (function () {
  "use strict";

  var DAY = 86400000;
  var DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  var ADVENT = ["FIRST SUNDAY IN ADVENT", "SECOND SUNDAY IN ADVENT",
                "THIRD SUNDAY IN ADVENT", "FOURTH SUNDAY IN ADVENT"];
  var AFTER_CHRISTMAS = ["FIRST SUNDAY AFTER CHRISTMAS", "SECOND SUNDAY AFTER CHRISTMAS"];
  var AFTER_EPIPHANY = ["FIRST SUNDAY AFTER EPIPHANY", "SECOND SUNDAY AFTER EPIPHANY",
                        "THIRD SUNDAY AFTER EPIPHANY", "FOURTH SUNDAY AFTER EPIPHANY",
                        "FIFTH SUNDAY AFTER EPIPHANY", "SIXTH SUNDAY AFTER EPIPHANY"];
  var BEFORE_LENT = ["SEPTUAGESIMA SUNDAY", "SEXAGESIMA SUNDAY", "QUINQUAGESIMA SUNDAY"];
  var IN_LENT = ["FIRST SUNDAY IN LENT", "SECOND SUNDAY IN LENT", "THIRD SUNDAY IN LENT",
                 "FOURTH SUNDAY IN LENT", "FIFTH SUNDAY IN LENT", "SIXTH SUNDAY IN LENT"];
  var AFTER_EASTER = ["FIRST SUNDAY AFTER EASTER", "SECOND SUNDAY AFTER EASTER",
                      "THIRD SUNDAY AFTER EASTER", "FOURTH SUNDAY AFTER EASTER",
                      "FIFTH SUNDAY AFTER EASTER"];
  var AFTER_TRINITY = ["FIRST SUNDAY AFTER TRINITY", "SECOND SUNDAY AFTER TRINITY",
                       "THIRD SUNDAY AFTER TRINITY", "FOURTH SUNDAY AFTER TRINITY",
                       "FIFTH SUNDAY AFTER TRINITY", "SIXTH SUNDAY AFTER TRINITY",
                       "SEVENTH SUNDAY AFTER TRINITY", "EIGHTH SUNDAY AFTER TRINITY",
                       "NINTH SUNDAY AFTER TRINITY", "TENTH SUNDAY AFTER TRINITY",
                       "ELEVENTH SUNDAY AFTER TRINITY", "TWELFTH SUNDAY AFTER TRINITY",
                       "THIRTEENTH SUNDAY AFTER TRINITY", "FOURTEENTH SUNDAY AFTER TRINITY",
                       "FIFTEENTH SUNDAY AFTER TRINITY", "SIXTEENTH SUNDAY AFTER TRINITY",
                       "SEVENTEENTH SUNDAY AFTER TRINITY", "EIGHTEENTH SUNDAY AFTER TRINITY",
                       "NINETEENTH SUNDAY AFTER TRINITY", "TWENTIETH SUNDAY AFTER TRINITY",
                       "TWENTY-FIRST SUNDAY AFTER TRINITY", "TWENTY-SECOND SUNDAY AFTER TRINITY",
                       "TWENTY-THIRD SUNDAY AFTER TRINITY", "TWENTY-FOURTH SUNDAY AFTER TRINITY"];
  var BEFORE_ADVENT = ["THIRD SUNDAY BEFORE ADVENT", "SECOND SUNDAY BEFORE ADVENT",
                       "SUNDAY NEXT BEFORE ADVENT"];

  var CHRISTMAS_DAY = "CHRISTMAS DAY";
  var EPIPHANY = "EPIPHANY";
  var EASTER_DAY = "EASTER DAY";
  var SUNDAY_AFTER_ASCENSION = "SUNDAY AFTER ASCENSION";
  var WHITSUNDAY = "WHITSUNDAY";
  var TRINITY_SUNDAY = "TRINITY SUNDAY";

  /* ---------- dates ---------- */

  function pad(n) { return String(n).padStart(2, "0"); }

  function midnight(date) { return new Date(date.getFullYear(), date.getMonth(), date.getDate()); }

  function addDays(date, n) { var d = new Date(date.getTime()); d.setDate(d.getDate() + n); return d; }

  function sundayOnOrBefore(date) { var d = midnight(date); return addDays(d, -d.getDay()); }

  function weeksBetween(a, b) { return Math.round((midnight(b) - midnight(a)) / (7 * DAY)); }

  function sameDay(a, b) { return midnight(a).getTime() === midnight(b).getTime(); }

  /* Easter by the usual computus: the first Sunday after the full moon that
     falls on or next after 21 March. */
  function easter(year) {
    var a = year % 19, b = Math.floor(year / 100), c = year % 100;
    var d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3);
    var h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4), k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7;
    var m = Math.floor((a + 11 * h + 22 * l) / 451);
    var month = Math.floor((h + l - 7 * m + 114) / 31);
    var day = ((h + l - 7 * m + 114) % 31) + 1;
    return new Date(year, month - 1, day);
  }

  /* Advent Sunday: the fourth Sunday before Christmas Day, the Sunday falling
     on or next after 27 November. */
  function advent1(year) {
    var nov27 = new Date(year, 10, 27);
    return addDays(nov27, (7 - nov27.getDay()) % 7);
  }

  function firstSundayAfterEpiphany(year) { return addDays(sundayOnOrBefore(epiphany(year)), 7); }

  function liturgicalYear(date) {
    var y = date.getFullYear();
    return midnight(date) >= advent1(y) ? y : y - 1;
  }

  function cycleLabel(sunday) {
    var s = midnight(sunday);
    var y = s.getFullYear();
    var a1 = advent1(y);

    if (s >= a1) {
      var n = weeksBetween(a1, s);
      if (n <= 3) { return ADVENT[n]; }
      /* else s is Christmas Day itself, or a Sunday within its octave */
    }

    var christmasYear = s >= christmas(y) ? y : y - 1;
    var jan1 = new Date(christmasYear + 1, 0, 1);
    var ep = epiphany(christmasYear + 1);
    var e = easter(christmasYear + 1);
    var ash = ashWednesday(christmasYear + 1);
    var qq = sundayOnOrBefore(ash);                 /* Quinquagesima */
    var first = firstSundayAfterEpiphany(christmasYear + 1);
    var lent1 = addDays(ash, 4);
    var whitsun = pentecost(christmasYear + 1);
    var trinity = trinitySunday(christmasYear + 1);
    var a1next = advent1(christmasYear + 1);

    if (sameDay(s, christmas(christmasYear))) { return CHRISTMAS_DAY; }
    if (s <= jan1) { return AFTER_CHRISTMAS[0]; }
    if (s < ep) { return AFTER_CHRISTMAS[1]; }
    if (sameDay(s, ep)) { return EPIPHANY; }

    if (s < ash) {
      var back = weeksBetween(s, qq);
      if (back < 3) { return BEFORE_LENT[2 - back]; }
      return AFTER_EPIPHANY[weeksBetween(first, s)];
    }
    if (s < e) { return IN_LENT[weeksBetween(lent1, s)]; }
    if (sameDay(s, e)) { return EASTER_DAY; }
    if (s < whitsun) {
      var after = weeksBetween(e, s);
      return after === 6 ? SUNDAY_AFTER_ASCENSION : AFTER_EASTER[after - 1];
    }
    if (sameDay(s, whitsun)) { return WHITSUNDAY; }
    if (sameDay(s, trinity)) { return TRINITY_SUNDAY; }

    var last = addDays(a1next, -7);                 /* the Sunday next before Advent */
    var back3 = weeksBetween(s, last);
    if (back3 < 3) { return BEFORE_ADVENT[2 - back3]; }
    return AFTER_TRINITY[weeksBetween(trinity, s) - 1];
  }

  function ashWednesday(year) { return addDays(easter(year), -46); }

  function ascensionDay(year) { return addDays(easter(year), 39); }

  function pentecost(year) { return addDays(easter(year), 49); }

  function trinitySunday(year) { return addDays(easter(year), 56); }

  function christmas(year) { return new Date(year, 11, 25); }

  function epiphany(year) { return new Date(year, 0, 6); }

  function season(date) {
    var d = midnight(date);
    var y = d.getFullYear();
    var eve = addDays(christmas(y), -1);
    var ep = epiphany(y);
    var e = easter(y);
    var ash = ashWednesday(y);
    var whitsun = pentecost(y);

    if (d >= advent1(y) && d < eve) { return "advent"; }
    if (d >= eve) { return "christmas"; }
    if (d < ep) { return "christmas"; }
    if (d < ash) { return "epiphany"; }
    if (d < e) { return "lent"; }
    if (d < whitsun) { return "easter"; }
    if (sameDay(d, whitsun)) { return "pentecost"; }
    return "ordinary";
  }

  /* ---------- the name of the week ---------- */

  /* A short name for the corner of the screen: "Trinity 17" rather than "The
     Seventeenth Sunday after Trinity". */
  function shortName(label) {
    var i;
    if ((i = ADVENT.indexOf(label)) > -1) return "Advent " + (i + 1);
    if ((i = AFTER_CHRISTMAS.indexOf(label)) > -1) return "Christmas " + (i + 1);
    if ((i = AFTER_EPIPHANY.indexOf(label)) > -1) return "Epiphany " + (i + 1);
    if ((i = BEFORE_LENT.indexOf(label)) > -1) return title(label.replace(" SUNDAY", ""));
    if ((i = IN_LENT.indexOf(label)) > -1) return "Lent " + (i + 1);
    if ((i = AFTER_EASTER.indexOf(label)) > -1) return "Easter " + (i + 1);
    if ((i = AFTER_TRINITY.indexOf(label)) > -1) return "Trinity " + (i + 1);
    if ((i = BEFORE_ADVENT.indexOf(label)) > -1) {
      return i === 2 ? "Advent next Sunday" : (3 - i) + " Sundays before Advent";
    }
    return title(label);
  }

  var SMALL = { a: 1, an: 1, and: 1, in: 1, of: 1, the: 1, after: 1, before: 1, next: 1, upon: 1 };
  function title(label) {
    return String(label).toLowerCase().split(" ").map(function (w, i) {
      if (i && SMALL[w]) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(" ");
  }

  /* The Sunday at the head of a date's week, and the Prayer Book's name for it. */
  function weekName(date) { return cycleLabel(sundayOnOrBefore(date)); }

  return { cycleLabel: cycleLabel, season: season, weekName: weekName, shortName: shortName,
           title: title, easter: easter, advent1: advent1,
           sundayOnOrBefore: sundayOnOrBefore, addDays: addDays };
})();
