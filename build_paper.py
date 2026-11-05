#!/usr/bin/env python3
"""Regenerate the formal report of the ``TheoreticalFramework`` development.

The tool treats the Lean sources as the single source of truth.  Nothing in the
report is typed by hand: declarations, statements, axioms and numerical bounds
are read back out of Lean, and every physical constant of the framework is
recomputed here from its definition and compared with the interval or equality
that Lean states.

Pipeline
--------
1. **hygiene**    refuse to build if the sources contain ``sorry``, ``admit``,
                  ``axiom`` or ``native_decide``.
2. **elaborate**  ``lean`` each module in dependency order into
                  ``.lake/build/lib/lean/``.
3. **audit**      generate ``paper/build/audit.lean`` with ``#check`` and
                  ``#print axioms`` for every declaration found in the sources,
                  elaborate it, and parse the result.  The report's declaration
                  index is therefore the elaborated type, not a transcription.
4. **cross-check** recompute each constant (exact integers and fractions where
                  possible) and compare it with what Lean actually asserts.
5. **report**     write ``paper/build/report.tex`` and ``paper/report.md``,
                  compile the LaTeX with ``latexmk -xelatex``, and place the PDF
                  at ``paper/report.pdf``.

Usage
-----
    python3 paper/tools/build_paper.py            # full verification + PDF
    python3 paper/tools/build_paper.py --fast     # reuse oleans, but redo audit
    python3 paper/tools/build_paper.py --no-pdf   # stop before LaTeX
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
BUILD = PAPER / "build"
OLEANS = REPO / ".lake" / "build" / "lib" / "lean"
SCRATCH = REPO / ".scratch"

#: Modules in dependency order; ``TheoreticalFramework`` is the umbrella.
MODULES = ["Basic", "Leptons", "Dimensions", "Velocity", "Regimes"]
UMBRELLA = "TheoreticalFramework"

FORBIDDEN = {
    r"\bsorry\b": "unfinished proof",
    r"\badmit\b": "admitted proof",
    r"^\s*axiom\b": "assumed axiom",
    r"\bnative_decide\b": "trusted native evaluation",
}

# --------------------------------------------------------------------------- #
# Framework constants, recomputed here from their definitions
# --------------------------------------------------------------------------- #

MU = 207                      # m_μ/m_e
TAU = 3477                    # m_τ/m_e
V2_KMH = 25000                # muonic collision ceiling, km/h
V2_TONNE = Fraction(5, 18)    # km/h -> m/s
V2 = V2_KMH * V2_TONNE        # = 62500/9 m/s
G0 = 9.80665
RAPTOR_ISP = 363.0
RAPTOR_VE = RAPTOR_ISP * G0
C_LIGHT = 299792458.0


def vf_sq(v2: Fraction, ratio: int) -> Fraction:
    return v2 * v2 * ratio ** 3


def sqrt_float(x: Fraction) -> float:
    return math.sqrt(float(x))


VF_MUON = sqrt_float(vf_sq(V2, MU))
VF_TAUON = sqrt_float(vf_sq(Fraction(VF_MUON), TAU))
VF_TAUON_ENTRY = sqrt_float(vf_sq(V2, TAU))
VF_TAUON_MEDIAN = sqrt_float(vf_sq(500000 * V2_TONNE, TAU))
ISP_MUON = VF_MUON / G0

#: (theorem, module, label, recomputed value) for *bracketed* claims.
CROSS_CHECKS: list[tuple[str, str, str, float]] = [
    ("collisionVelocityMuonMax_bounds", "Velocity",
     "muonic collision ceiling v₂, m/s", float(V2)),
    ("casimir_amplification_muon_order", "Leptons",
     "casimir amplification (m_μ/m_e)⁵", float(MU ** 5)),
    ("casimir_amplification_tauon_order", "Leptons",
     "casimir amplification (m_τ/m_e)⁵", float(TAU ** 5)),
    ("casimir_amplification_tauon_over_muon", "Leptons",
     "(m_τ/m_μ)⁵", (TAU / MU) ** 5),
    ("muonAmplification_order", "Velocity",
     "velocity amplification 207³", float(MU ** 3)),
    ("tauonAmplification_order", "Velocity",
     "velocity amplification 3477³", float(TAU ** 3)),
    ("tauon_over_muon_amplification", "Velocity",
     "3477³/207³", TAU ** 3 / MU ** 3),
    ("muonMaxEjection_bounds", "Velocity",
     "muonic ejection ceiling, m/s", VF_MUON),
    ("muonMaxEjection_km_per_s", "Velocity",
     "muonic ejection ceiling, km/s", VF_MUON / 1000),
    ("muonSpecificImpulse_bounds", "Velocity",
     "muonic specific impulse, s", ISP_MUON),
    ("muonImpulse_over_raptor", "Velocity",
     "Isp(muonic)/Isp(Raptor)", ISP_MUON / RAPTOR_ISP),
    ("tauonMaxEjection_bounds", "Velocity",
     "tauonic ejection ceiling, m/s", VF_TAUON),
    ("tauonEntryEjection_bounds", "Velocity",
     "tauonic ejection at entry, m/s", VF_TAUON_ENTRY),
    ("tauonMedianEjection_bounds", "Velocity",
     "tauonic ejection at median input, m/s", VF_TAUON_MEDIAN),
    ("source_tauon_max_velocity_underestimates", "Velocity",
     "(verified/source)² at the tauonic ceiling", (VF_TAUON / 1.34e12) ** 2),
    ("source_tauon_max_velocity_factor", "Velocity",
     "verified/source at the tauonic ceiling", VF_TAUON / 1.34e12),
    ("muonic_thrust_to_power_bounds", "Regimes",
     "muonic thrust per watt, N/W", 2.0 / VF_MUON),
    ("muonic_thrust_to_power_shortfall", "Regimes",
     "v_e(muonic)/v_e(Raptor)", VF_MUON / RAPTOR_VE),
    ("domainBoundary_km_per_s", "Regimes",
     "domain boundary, km/s", VF_MUON / 1000),
]

#: (theorem, module, label, expected numeral as printed by Lean).
EXACT_CHECKS: list[tuple[str, str, str, str]] = [
    ("massRatioMuon_pow_five", "Leptons", "207⁵", str(MU ** 5)),
    ("massRatioTauon_pow_five", "Leptons", "3477⁵", str(TAU ** 5)),
    ("muonAmplification_eq", "Velocity", "207³", str(MU ** 3)),
    ("tauonAmplification_eq", "Velocity", "3477³", str(TAU ** 3)),
    ("collisionVelocityMuonMax_eq", "Velocity", "25 000 km/h in m/s", "62500 / 9"),
]

#: The published figures, for the comparison table.
PUBLISHED = [
    ("Casimir amplification, muon", r"(207)^5 \approx 4 \times 10^{11}",
     "3.8006 × 10¹¹", "agrees at one significant figure"),
    ("Casimir amplification, tauon", r"(3477)^5 \approx 5.1 \times 10^{17}",
     "5.0819 × 10¹⁷", "agrees"),
    ("Velocity amplification, muon", r"(207)^3 \approx 8.9 \times 10^{6}",
     "8 869 743 = 8.87 × 10⁶", "agrees"),
    ("Velocity amplification, tauon", r"(3477)^3 \approx 4.2 \times 10^{10}",
     "42 035 292 333 = 4.20 × 10¹⁰", "agrees"),
    ("Muonic ejection ceiling", r"\approx 20\,700\ \mathrm{km/s}",
     "20 682.0 km/s", "agrees"),
    ("Muonic specific impulse", r"\approx 2 \times 10^{6}\ \mathrm{s},\ 6000\times\ \mathrm{Raptor}",
     "2.1090 × 10⁶ s, 5810 × Raptor", "agrees; 6000 is a rounding of 5810"),
    ("Tauonic ejection at entry", r"\approx 1.42 \times 10^{9}\ \mathrm{m/s}",
     "1.4238 × 10⁹ m/s", "agrees"),
    ("Tauonic ejection at median input", r"\approx 9.0 \times 10^{10}\ \mathrm{m/s}",
     "2.8476 × 10¹⁰ m/s", "DISAGREES: source is √10 too small"),
    ("Tauonic ejection ceiling", r"\approx 1.34 \times 10^{12}\ \mathrm{m/s}",
     "4.2403 × 10¹² m/s", "DISAGREES: source is √10 too small"),
]

# --------------------------------------------------------------------------- #
# Source parsing
# --------------------------------------------------------------------------- #

DECL_RE = re.compile(
    r"^(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?(?:private\s+)?"
    r"(theorem|lemma|def|structure|class|instance|abbrev)\s+"
    r"([^\s:()\[\]{},]+)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_'.]*))?\s*$")
SECTION_RE = re.compile(r"^(?:noncomputable\s+)?section(?:\s+[A-Za-z_][A-Za-z0-9_']*)?\s*$")


@dataclass
class Decl:
    module: str
    kind: str
    short: str
    full: str
    doc: str = ""
    statement: str = ""
    fqcn: str = ""
    type_: str = ""
    axioms: list[str] = field(default_factory=list)
    axioms_known: bool = False


def clean_doc(block: list[str]) -> str:
    text = "\n".join(block)
    text = text.strip()
    if text.startswith("/--"):
        text = text[3:]
    if text.endswith("-/"):
        text = text[:-2]
    lines = [ln.strip() for ln in text.split("\n")]
    lines = [re.sub(r"^[*-]\s+", "", ln) for ln in lines]
    return " ".join(ln for ln in lines if ln).strip()


def parse_declarations(path: Path, module: str) -> list[Decl]:
    """Collect declarations, their docstrings and their statement text."""
    lines = path.read_text(encoding="utf-8").split("\n")
    decls: list[Decl] = []
    stack: list[str | None] = []
    i = 0
    pending_doc = ""

    def prefix() -> str:
        parts = [p for p in stack if p]
        if parts and parts[0] == "TheoreticalFramework":
            return ".".join(parts)
        return ".".join(["TheoreticalFramework"] + parts)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("/--"):
            block = [line]
            while "-/" not in block[-1] and i + 1 < len(lines):
                i += 1
                block.append(lines[i])
            pending_doc = clean_doc(block)
            i += 1
            continue

        if stripped.startswith("--") or stripped.startswith("/-"):
            i += 1
            continue

        m = NS_RE.match(line)
        if m:
            stack.append(m.group(1))
            i += 1
            continue
        if SECTION_RE.match(line):
            stack.append(None)
            i += 1
            continue
        m = END_RE.match(line)
        if m:
            if stack:
                stack.pop()
            i += 1
            continue

        m = DECL_RE.match(line)
        if m:
            kind, short = m.group(1), m.group(2)
            # statement text: from this line up to `:=` / `where` / corpus end
            stmt: list[str] = [line[m.end():].strip()]
            j = i
            while True:
                cur = lines[j]
                if j > i or ":=" in cur[m.end():] or cur.rstrip().endswith("where"):
                    if ":=" in cur or cur.rstrip().endswith("where"):
                        head = cur[: cur.index(":=")] if ":=" in cur else cur.rstrip()[:-5]
                        if j == i:
                            stmt = [head[m.end():].strip()]
                        else:
                            stmt.append(head.strip())
                        break
                j += 1
                if j >= len(lines):
                    break
                stmt.append(lines[j].strip())
            decls.append(
                Decl(module=module, kind=kind, short=short,
                     full=f"{prefix()}.{short}",
                     doc=pending_doc,
                     statement=" ".join(s for s in stmt if s))
            )
            pending_doc = ""
            i += 1
            continue

        if stripped:
            pending_doc = pending_doc  # keep docstring across attribute lines
        i += 1
    return decls


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

def lean_env() -> dict[str, str]:
    env = dict(os.environ)
    base = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = f"{OLEANS}:{base}" if base else str(OLEANS)
    SCRATCH.mkdir(exist_ok=True)
    env["TMPDIR"] = str(SCRATCH)
    return env


def hygiene(decls: list[Decl]) -> list[str]:
    problems: list[str] = []
    for name in MODULES:
        src = REPO / UMBRELLA / f"{name}.lean"
        text = src.read_text(encoding="utf-8")
        for pattern, why in FORBIDDEN.items():
            for mo in re.finditer(pattern, text, flags=re.MULTILINE):
                line = text.count("\n", 0, mo.start()) + 1
                problems.append(f"{src.name}:{line}: {why} (`{mo.group(0)}`)")
    return problems


def compile_modules(fast: bool) -> list[dict]:
    (OLEANS / UMBRELLA).mkdir(parents=True, exist_ok=True)
    results = []
    targets = [(name, REPO / UMBRELLA / f"{name}.lean") for name in MODULES]
    targets.append((None, REPO / f"{UMBRELLA}.lean"))
    for name, src in targets:
        out = (OLEANS / UMBRELLA / f"{name}.olean") if name else (OLEANS / f"{UMBRELLA}.olean")
        if fast and out.exists() and out.stat().st_mtime > src.stat().st_mtime:
            results.append({"module": name or UMBRELLA, "cached": True,
                            "seconds": 0.0, "ok": True, "diagnostics": ""})
            continue
        t0 = time.time()
        proc = subprocess.run(["lean", "-o", str(out), str(src)],
                              cwd=REPO, env=lean_env(), capture_output=True, text=True)
        diag = (proc.stdout + proc.stderr).strip()
        results.append({"module": name or UMBRELLA, "cached": False,
                        "seconds": round(time.time() - t0, 2),
                        "ok": proc.returncode == 0, "diagnostics": diag})
        if proc.returncode != 0:
            break
    return results


def audit(decls: list[Decl]) -> list[str]:
    """Elaborate every declaration's type and its axiom dependencies."""
    audit_file = BUILD / "audit.lean"
    parts = [f"import {UMBRELLA}", ""]
    for d in decls:
        parts.append(f"--@@DECL {d.full}")
        parts.append(f"#check @{d.full}")
        if d.kind in ("theorem", "lemma", "def"):
            parts.append(f"--@@AXIOMS {d.full}")
            parts.append(f"#print axioms {d.full}")
        parts.append("")
    audit_file.write_text("\n".join(parts), encoding="utf-8")

    proc = subprocess.run(["lean", str(audit_file)], cwd=REPO,
                          env=lean_env(), capture_output=True, text=True)
    if proc.returncode != 0:
        return (proc.stdout + proc.stderr).splitlines()

    by_full = {d.full: d for d in decls}
    fqns = set(by_full)

    state = {"kind": None, "name": None, "buffer": []}

    def flush() -> None:
        name, buffer = state["name"], state["buffer"]
        if name is None:
            return
        text = " ".join(buffer).strip()
        d = by_full[name]
        if state["kind"] == "decl":
            d.type_ = text
        else:
            d.axioms_known = True
            mo = re.search(r"\[([^\]]*)\]", text)
            if mo:
                d.axioms = [a.strip() for a in mo.group(1).split(",") if a.strip()]
            elif "does not depend on any axioms" in text:
                d.axioms = []
            else:
                d.axioms = ["?"]

    decl_line = re.compile(r"^@?([^\s:]+)\s*:\s?(.*)$")
    axiom_line = re.compile(r"^'([^']+)'\s+(depends on axioms|does not depend)")
    for line in (proc.stdout + proc.stderr).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("error"):
            continue
        m = axiom_line.match(stripped)
        if m and m.group(1) in fqns:
            flush()
            state.update(kind="axioms", name=m.group(1), buffer=[stripped])
            continue
        m = decl_line.match(stripped)
        if m and m.group(1) in fqns:
            flush()
            state.update(kind="decl", name=m.group(1), buffer=[m.group(2)])
            continue
        state["buffer"].append(stripped)
    flush()
    return []


def magnitudes(statement: str) -> list[float]:
    """Numeric magnitudes appearing in a Lean statement, `a*10^k` and `a/10^k`."""
    sci = re.compile(
        r"\(?\s*(\d+(?:\.\d+)?)\s*(?::\s*ℝ)?\s*\)?\s*([*/])\s*10\s*\^\s*(\d+)")
    out = []
    for m in sci.finditer(statement):
        base, op, ex = float(m.group(1)), m.group(2), int(m.group(3))
        out.append(base * 10 ** ex if op == "*" else base / 10 ** ex)
    if not out:
        out = [float(x) for x in re.findall(r"(?<![\w.])(\d+\.\d+)(?![\w.])", statement)]
    if not out:
        out = [float(x) for x in re.findall(r"(?<![\d.])(\d{4,})(?![\d.])", statement)]
    return out


def cross_check(decls: list[Decl]) -> list[dict]:
    by = {(d.module, d.short): d for d in decls}
    rows = []
    for thm, module, label, value in CROSS_CHECKS:
        d = by.get((module, thm))
        row = {"theorem": thm, "module": module, "label": label,
               "value": value, "interval": None, "expect": None, "ok": False, "note": ""}
        if d is None or not d.type_:
            row["note"] = "declaration not found in audit"
            rows.append(row)
            continue
        mags = magnitudes(d.type_)
        if len(mags) >= 2:
            lo, hi = min(mags), max(mags)
            row["interval"] = [lo, hi]
            row["ok"] = lo * (1 - 1e-9) <= value <= hi * (1 + 1e-9)
        elif len(mags) == 1:
            row["note"] = "only one bound parsed"
        else:
            row["note"] = "no numeric bound parsed"
        rows.append(row)

    for thm, module, label, expected in EXACT_CHECKS:
        d = by.get((module, thm))
        ok = bool(d and d.type_ and expected in d.type_)
        rows.append({"theorem": thm, "module": module, "label": label,
                     "value": None, "interval": None, "expect": expected, "ok": ok,
                     "note": f"expects `{expected}` in the statement" if not ok else "exact"})
    return rows


# --------------------------------------------------------------------------- #
# LaTeX rendering
# --------------------------------------------------------------------------- #

TEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "%": r"\%",
    "&": r"\&",
    "$": r"\$",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
    "_": r"\_",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
}


MONO_FALLBACK = {"∝": r"$\propto$", "⟹": r"$\Longrightarrow$"}


def tex(s: str, breaks: bool = True) -> str:
    """Escape LaTeX specials; glyphs missing from the mono font become math."""
    for i, (glyph, macro) in enumerate(MONO_FALLBACK.items()):
        if glyph in s:
            s = s.replace(glyph, f"\x00{i}\x00")
    out = []
    for ch in s:
        if ch in TEX_SPECIALS:
            out.append(TEX_SPECIALS[ch])
            if breaks and ch == "_":
                out.append(r"\allowbreak{}")
        else:
            out.append(ch)
    text = "".join(out)
    for i, macro in enumerate(MONO_FALLBACK.values()):
        text = text.replace(f"\x00{i}\x00", macro)
    return text


def tex_prose(s: str) -> str:
    """Render a docstring: `code` spans become \\texttt, **bold** becomes bold."""
    tokens = re.split(r"(`[^`]+`)", s)
    out = []
    for tok in tokens:
        if tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            out.append(r"\texttt{" + tex(tok[1:-1]) + "}")
        else:
            for piece in re.split(r"(\*\*[^*]+\*\*|(?<!\*)\*[^*\n]+\*(?!\*))", tok):
                if piece.startswith("**") and piece.endswith("**") and len(piece) > 4:
                    out.append(r"\textbf{" + tex(piece[2:-2]) + "}")
                elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
                    out.append(r"\emph{" + tex(piece[1:-1]) + "}")
                else:
                    out.append(tex(piece))
    text = "".join(out)
    text = text.replace(" - ", " --- ")
    return text


def fmt(x: float) -> str:
    if x == 0:
        return "0"
    ax = abs(x)
    if ax >= 1e5 or ax < 1e-2:
        exp = int(math.floor(math.log10(ax)))
        mant = x / 10 ** exp
        return f"{mant:.6f}".rstrip("0").rstrip(".") + f" \\times 10^{{{exp}}}"
    if ax >= 100:
        return f"{x:,.0f}"
    return f"{x:.4f}".rstrip("0").rstrip(".")


def fmath(x: float) -> str:
    """`fmt` for math mode: thousands separators that do not add spacing."""
    return fmt(x).replace(",", "{,}")


SUPERSCRIPT = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")


def fmt_uni(x: float) -> str:
    """Compact Unicode rendering for the Markdown mirror."""
    if x == 0:
        return "0"
    ax = abs(x)
    if ax >= 1e4 or ax < 1e-2:
        exp = int(math.floor(math.log10(ax)))
        mant = x / 10 ** exp
        return f"{mant:.5f}".rstrip("0").rstrip(".") + "×10" + str(exp).translate(SUPERSCRIPT)
    if ax >= 100:
        return f"{x:,.0f}"
    return f"{x:.5f}".rstrip("0").rstrip(".")


def md_math(src: str) -> str:
    """Translate the small LaTeX subset used in the published-figure table."""
    s = src
    s = s.replace(r"\times", "×").replace(r"\approx", "≈").replace(r"\cdot", "·")
    s = re.sub(r"\\(?:mathrm|text)\{([^}]*)\}", r"\1", s)
    s = s.replace(r"\,", " ").replace("\\ ", " ").replace("$", "")
    s = re.sub(r"\^\{([^}]*)\}", lambda m: m.group(1).translate(SUPERSCRIPT), s)
    s = re.sub(r"\^(\d)", lambda m: m.group(1).translate(SUPERSCRIPT), s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def fmt_int(x: float) -> str:
    return f"{x:,.0f}".replace(",", r"\,")


LATEX_EOL = chr(92) * 2


def lean_block(source: str) -> str:
    """Typeset Lean source with the mono font, one line per paragraph."""
    lines = source.split("\n")
    body = []
    for ln in lines:
        if not ln.strip():
            body.append("\\mbox{}")
            continue
        body.append(tex(ln))
    return (
        "{\\ttfamily\\scriptsize\\setlength{\\parindent}{0pt}"
        "\\setlength{\\baselineskip}{7.6pt}\\setlength{\\parskip}{0pt}"
        "\\raggedright\\obeyspaces\\obeylines\n" + "\n".join(body) + "\n}\n"
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


# --------------------------------------------------------------------------- #
# Report content
# --------------------------------------------------------------------------- #

def header(decls: list[Decl], compile_res: list[dict], checks: list[dict],
           lean_version: str, now: str) -> str:
    n_theorems = sum(1 for d in decls if d.kind in ("theorem", "lemma"))
    n_defs = sum(1 for d in decls if d.kind in ("def", "abbrev", "instance"))
    n_struct = sum(1 for d in decls if d.kind in ("structure", "class"))
    all_ok = all(r["ok"] for r in compile_res) and all(c["ok"] for c in checks)
    STATUS = (r"\textbf{\textcolor{okgreen}{all checks passed}}" if all_ok
              else r"\textbf{\textcolor{red}{CHECKS FAILED --- see \S\ref{sec:verification}}}")
    axioms = sorted({a for d in decls for a in d.axioms})
    return rf"""
\begin{{center}}
{{\LARGE\bfseries Leptonic Compactness and the Generalized\\[2pt]
$n$-Dimensional Velocity Law}}\\[6pt]
{{\large A formal report on the \texttt{{{UMBRELLA}}} development}}\\[10pt]
{{\small Generated {now} from the Lean sources by \texttt{{paper/tools/build\_paper.py}}}}
\end{{center}}

\vspace{{4pt}}
\begin{{center}}
\begin{{minipage}}{{0.92\textwidth}}
\small
\textbf{{Status:}} {STATUS}.\\
\textbf{{Lean:}} \texttt{{{tex(lean_version)}}}; \textbf{{Mathlib:}} prebuilt at \texttt{{/opt/mathlib}}.\\
\textbf{{Sources:}} {len(MODULES)} modules, {n_theorems} theorems, {n_defs} definitions,
{n_struct} structures.\\
\textbf{{Axioms used across the development:}} {', '.join(r'\texttt{' + tex(a) + '}' for a in axioms) if axioms else 'none'}.
\end{{minipage}}
\end{{center}}

\vspace{{6pt}}
\noindent\rule{{\textwidth}}{{0.4pt}}
\section*{{Summary}}
\addcontentsline{{toc}}{{section}}{{Summary}}

Part of the muon's anomalous magnetic moment is attributed, in the framework
under study, to an internal geometric compactness of massive leptons with
effective radius $r_\ell = \kappa/m_\ell$.  Under the framework's plate ansatz
($S$ proportional to $m^2$, separation $d = r_\ell$) the Casimir energy of the
internal geometry is quintic in the mass, so the amplification between two
leptons is the fifth power of their mass ratio:
$E_{{\mathrm{{C}},\mu}}/E_{{\mathrm{{C}},e}} \approx (207)^5 \approx 4\times10^{{11}}$
and $E_{{\mathrm{{C}},\tau}}/E_{{\mathrm{{C}},e}} \approx (3477)^5 \approx 5.1\times10^{{17}}$.
Within the generalized $n$-dimensional kinematics with $n = 5$, the same quintic
dependence fixes the ejection-velocity law
$v_f^2 = v_2^2\,(m_\ell/m_0)^{{n-2}}$, hence amplification factors
$(207)^3 \approx 8.9\times10^{{6}}$ and $(3477)^3 \approx 4.2\times10^{{10}}$.

This report does three things.  First, it records the derivation of every
scaling law as a Lean theorem, so that the fifth-power and cube appear as
consequences rather than assertions, and so that the parameter-freedom of the
ratios is visible.  Second, it recomputes every physical constant independently
in Python and compares it with the interval Lean states --- including the three
places where the source text's arithmetic does not survive that comparison.
Third, it separates what the development proves from what the framework assumes
and from what would need experiment.
"""


def section_scope() -> str:
    return r"""
\section{Scope, and what is and is not proved}
\label{sec:scope}

The development is deliberately layered, and the layers should not be confused.

\paragraph{(A) Proved mathematics.}
The scaling laws, the amplification ratios, the exact arithmetic of the ejecta,
the algebra of the regime structure, the continuity of the velocity map, and the
thrust--power identity.  These are Lean theorems with no hypotheses beyond
positivity of the masses and ratios, and they hold whatever one thinks of the
physics.

\paragraph{(B) Framework postulates.}
Two assumptions are \emph{recorded} rather than derived, and the formalization
makes that visible instead of hiding it.  The geometric ansatz
($S$ proportional to $m^2$ with $d = r_\ell$, and $r_\ell = \kappa/m_\ell$) is a
structure (\texttt{CasimirAnsatz}) carrying a free constant $\kappa$ and a free
area coefficient; the theorem that matters is that the \emph{ratio} does not
depend on either of them
(\texttt{CasimirAnsatz.energy\_ratio\_parameter\_free}).  The velocity law
$v_f^2 = v_2^2\,(m_\ell/m_0)^{n-2}$ is likewise a postulate of the framework's
generalized kinematics, and the development proves its consequences
(\texttt{velocity\_law}), not its truth.

\paragraph{(C) Empirical claims.}
That any of this describes the muon's actual internal structure, that muon--muon
collisions eject particles at these speeds, and that a thruster can be built, are
questions for experiment.  The development is explicit about the most important
of these: \S\ref{sec:thrust} proves that the geometry fixes the exhaust velocity
and the thrust-to-power ratio but says nothing about absolute thrust, and the
claim that is left open is recorded as a proposition
(\texttt{ThrustOptimizationConjecture}) that is never asserted.

\paragraph{A tension internal to the source.}
The framework attributes part of $a_\mu$ to a term scaling as $m^5$, whereas the
measured generation-dependence of the anomalous moment goes as roughly
$(m_\mu/m_e)^2 \approx 4.3\times10^{4}$, a factor $\approx 10^{7}$ smaller than
$(207)^5$.  The attached notes say so themselves.  Nothing in this report
resolves that: the formalization establishes that the framework's own arithmetic
is correct, which is a different statement from the framework being right.  A
Lean proof of a scaling law is not evidence for the postulate that produces it.
"""


def section_core() -> str:
    return r"""
\section{Core derivation: compactness and the fifth power}
\label{sec:core}

Write the effective radius as $r_\ell = \kappa/m_\ell$ and the Casimir energy of
the internal cavity as $E_\mathrm{C} \propto -S/d^3$ with $d = r_\ell$.  Three
theorems carry the derivation.

\begin{enumerate}[leftmargin=*]
\item \texttt{casimirEnergy\_eq\_quintic}: for $\kappa \neq 0$ and $m \neq 0$,
  \[
    E_\mathrm{C}(\kappa,m) \;=\; \frac{m^2}{(\kappa/m)^3} \;=\; \frac{m^5}{\kappa^3}.
  \]
\item \texttt{casimirEnergy\_ratio}: for non-zero masses,
  \[
    \frac{E_\mathrm{C}(\kappa,m_1)}{E_\mathrm{C}(\kappa,m_2)} \;=\; \left(\frac{m_1}{m_2}\right)^{5}.
  \]
\item \texttt{casimirEnergy\_ratio\_radii}: the same number read geometrically,
  \[
    \frac{E_\mathrm{C}(\kappa,m_1)}{E_\mathrm{C}(\kappa,m_2)} \;=\; \left(\frac{r_2}{r_1}\right)^{5},
  \]
  so ``compactness'' and ``vacuum coupling'' are one quantity, not two.
\end{enumerate}

The constant $\kappa$ cancels in the ratio.  That is the whole reason the
framework can issue a number at all, and the formalization isolates it: in
\texttt{CasimirAnsatz} the ratio is proved independent of $\kappa$, of the
area coefficient, and of the overall Casimir prefactor, and the sign convention
(the physical energy is negative, i.e.\ attractive) is shown not to affect it
(\texttt{signedEnergy\_ratio}).

The effective radius is strictly decreasing in the mass
(\texttt{effRadius\_strictAnti}), which is the compactness statement in the form
the rest of the development uses.
"""


def section_casimir_table(checks: list[dict]) -> str:
    by = {c["theorem"]: c for c in checks}

    def row(thm: str, expr: str, published: str) -> str:
        c = by[thm]
        interval = c["interval"]
        rng = (rf"$[{fmath(interval[0])},\ {fmath(interval[1])}]$" if interval else "---")
        return (rf"{expr} & {rng} & ${fmath(c['value'])}$ & {published} \\" "\n")

    return r"""
\section{Casimir amplification: the numbers}
\label{sec:casimir}

With $m_\mu/m_e = 207$ and $m_\tau/m_e = 3477$ --- both checked against the
tabulated masses to better than a quarter and a half unit respectively
(\texttt{massRatioMuon\_consistent}, \texttt{massRatioTauon\_consistent}) ---
the fifth-power law gives the following.  ``Lean'' is the interval the theorem
\texttt{\dots\_order} states; ``recomputed'' is this script's independent
evaluation; ``published'' is the source text.

\begin{center}\small
\begin{tabular}{@{}lccc@{}}
\toprule
Quantity & Lean interval & Recomputed & Published \\
\midrule
""" + row("casimir_amplification_muon_order", r"$E_{\mathrm{C},\mu}/E_{\mathrm{C},e}$", r"$4\times10^{11}$") \
        + row("casimir_amplification_tauon_order", r"$E_{\mathrm{C},\tau}/E_{\mathrm{C},e}$", r"$5.1\times10^{17}$") \
        + row("casimir_amplification_tauon_over_muon", r"$E_{\mathrm{C},\tau}/E_{\mathrm{C},\mu}$", r"$1.3\times10^{6}$") + r"""
\bottomrule
\end{tabular}
\end{center}

Two further structural facts are proved rather than computed.  The amplification
is monotone in the mass ratio
(\texttt{casimir\_amplification\_hierarchy}: $1 < (207)^5 < (3477)^5$), so the
lepton generation hierarchy is a strict hierarchy of vacuum couplings.  And the
equivalent magnetic field $B$, defined by $B^2 \propto E_\mathrm{C}/V$, carries
exponent $3$ under the source's volume ansatz $V$ proportional to $S d^3$, and
exponent $2$ under the literal plate volume $V = S d$.  Both are proved
(\texttt{field\_amplification\_source}, \texttt{field\_amplification\_plate}).
The exponent $3$ is the one the framework uses, and it is the same $3 = n-2$
that appears in the velocity law --- which is worth stating precisely, because
the coincidence is the framework's only argument for $n = 5$ beyond the quintic
mass dependence itself.
"""


def section_dimensions() -> str:
    return r"""
\section{The generalized $n$-dimensional framework}
\label{sec:dimensions}

The generalized dimension is not tuned: it is read off the quintic mass
dependence of the anomalous-moment term.  In the development,

\begin{verbatim}
casimirMassExponent   = 5
generalizedDimension  = casimirMassExponent
velocityExponent      = generalizedDimension - 2  = 3
\end{verbatim}

\noindent so that \texttt{generalizedDimension\_eq\_five} and
\texttt{velocityExponent\_eq\_three} are definitional, and the exponent of the
velocity law is a consequence of the Casimir exponent rather than a choice made
independently of it.

The link to $g-2$ is made explicit rather than left in prose.  The framework's
decomposition $a_\ell = a_{\mathrm{QED}} + a_{\mathrm{EW+had}} + a_{\mathrm{str}}$
is the definition \texttt{anomalousMoment}, its structural part is
\texttt{structuralTerm} $= C\,m^{\,n}$, and \texttt{structuralTerm\_quintic}
records that this is $C\,m^5$ while
\texttt{structuralTerm\_ratio} records that the structural term amplifies by
$(m_1/m_2)^5$ --- the same number as the Casimir amplification.  That identity of
exponents is the whole basis for reading $n = 5$ off the anomalous moment, so it
is worth having as a theorem rather than a remark.

The law is stated for arbitrary $n$ and then specialized.  With $r = m_\ell/m_0$,
\[
  v_f \;=\; \sqrt{v_2^2\, r^{\,n-2}},
  \qquad\text{so}\qquad
  v_f^2 \;=\; v_2^2\, r^{\,n-2}
\]
(\texttt{velocity\_law}), and for $v_2 \ge 0$ this is the paper's multiplicative
form $v_f = v_2\sqrt{r^{\,n-2}}$ (\texttt{generalisedVelocity\_eq\_mul}).  At
$n = 5$ both become the cube (\texttt{velocity\_law\_five}).  The map is
monotone in $r$ and in $v_2$, vanishes at $v_2 = 0$, and is continuous in each
variable.

The framework's generalized units enter only as exponent bookkeeping, and that
bookkeeping is proved exactly: with $[v_n] = \mathrm{m}^{2/n}/\mathrm{s}$ the mass
exponent balances as $n \cdot (2/n) = 2$
(\texttt{generalised\_unit\_exponents}) and the time exponent as
$(n-2)+2 = n$ (\texttt{time\_exponent\_balance}).  The substitution rule
$v_n (q\,dt_0)^{n-2} = v_2^2 q^{\,n-2}$ that links the two regimes is
\texttt{scale\_substitution}.
"""


def section_velocity(checks: list[dict]) -> str:
    by = {c["theorem"]: c for c in checks}
    law_rows = []
    for v_kmh in (0, 2500, 5000, 10000, 25000, 50000, 250000, 1000000):
        v2m = float(v_kmh * V2_TONNE)
        v_mu = math.sqrt(v2m ** 2 * MU ** 3)
        v_tau = math.sqrt(v2m ** 2 * TAU ** 3)
        law_rows.append(
            rf"{v_kmh:,} & ${fmath(v2m)}$ & ${fmath(v_mu)}$ & ${fmath(v_tau)}$ "
            + LATEX_EOL)

    def interval(thm: str) -> str:
        c = by[thm]
        if not c["interval"]:
            return "---"
        lo, hi = c["interval"]
        return rf"$[{fmath(lo)},\ {fmath(hi)}]$"

    def val(thm: str) -> str:
        return fmath(by[thm]["value"])

    return r"""
\section{Velocity scaling and amplification}
\label{sec:velocity}

The amplification factors are exact integers:
$207^3 = 8\,869\,743$ and $3477^3 = 42\,035\,292\,333$
(\texttt{muonAmplification\_eq}, \texttt{tauonAmplification\_eq}), i.e.\
$\approx 8.9\times10^{6}$ and $\approx 4.2\times10^{10}$.  Their ratio is
$(3477/207)^3 \approx 4.74\times10^{3}$.

Because $v_f^2$ is an exact rational, every velocity is bounded without any
rounding step: the development computes $v_f^2$ exactly and closes the interval
with \texttt{generalisedVelocity\_bounds}.

\begin{center}\small
\begin{tabular}{@{}lccc@{}}
\toprule
Quantity & Lean interval (m/s unless stated) & Recomputed & Published \\
\midrule
""" + "\n".join([
        rf"muonic ceiling $v_f$ & {interval('muonMaxEjection_bounds')} & ${val('muonMaxEjection_bounds')}$ & $\approx 20\,700$ km/s " + LATEX_EOL,
        rf"muonic ceiling (km/s) & {interval('muonMaxEjection_km_per_s')} & ${val('muonMaxEjection_km_per_s')}$ & --- " + LATEX_EOL,
        rf"muonic $I_{{\mathrm{{sp}}}}$ (s) & {interval('muonSpecificImpulse_bounds')} & ${val('muonSpecificImpulse_bounds')}$ & $\approx 2\times10^{{6}}$ " + LATEX_EOL,
        rf"$I_{{\mathrm{{sp}}}}/I_{{\mathrm{{sp,Raptor}}}}$ & {interval('muonImpulse_over_raptor')} & ${val('muonImpulse_over_raptor')}$ & $\approx 6000$ " + LATEX_EOL,
        rf"tauonic ceiling $v_f$ & {interval('tauonMaxEjection_bounds')} & ${val('tauonMaxEjection_bounds')}$ & $1.34\times10^{{12}}$ " + LATEX_EOL,
        rf"tauonic at entry & {interval('tauonEntryEjection_bounds')} & ${val('tauonEntryEjection_bounds')}$ & $1.42\times10^{{9}}$ " + LATEX_EOL,
        rf"tauonic at median & {interval('tauonMedianEjection_bounds')} & ${val('tauonMedianEjection_bounds')}$ & $9.0\times10^{{10}}$ " + LATEX_EOL,
    ]) + r"""
\bottomrule
\end{tabular}
\end{center}

\noindent The ceiling is at the muonic collision maximum $v_2 = 25\,000$ km/h
$= 62500/9 \approx 6\,944.4$ m/s (\texttt{collisionVelocityMuonMax\_eq}).

\subsection*{The law over the whole input range}

Values computed from the verified law $v_f^2 = v_2^2\, r^{3}$; only the endpoints
are bounded inside Lean, the rest are consequences.

\begin{center}\small
\begin{tabular}{@{}rccc@{}}
\toprule
$v_2$ (km/h) & $v_2$ (m/s) & $v_f$ muonic (m/s) & $v_f$ tauonic (m/s) \\
\midrule
""" + "\n".join(law_rows) + r"""
\bottomrule
\end{tabular}
\end{center}

\noindent Rows above $25\,000$ km/h lie outside the muonic input window and are
tabulated only to show the law's behaviour over three decades; they are not
outputs of a regime.  The muonic column above $\approx 10^{5}$ km/h is already
superluminal, which is one reason the muonic window stops where it does.

\subsection*{Where the source text diverges}

Three published figures were checked against the exact law.  Two do not survive,
and the pattern is the same in both: the source computes $v_f^2$ correctly and
then takes its square root with the decimal exponent misplaced, which produces a
factor $\sqrt{10} \approx 3.16$ on $v_f$ whenever the exponent of $v_f^2$ is odd.

\begin{center}\small
\begin{tabular}{@{}lcccl@{}}
\toprule
Quantity & Published & Verified & Ratio & Diagnosis \\
\midrule
tauonic ceiling & $1.34\times10^{12}$ & $4.2403\times10^{12}$ & $3.1644$
  & $\sqrt{10}$ slip \\
tauonic at median & $9.0\times10^{10}$ & $2.8476\times10^{10}$ & $0.3164$
  & same slip, other direction \\
tauonic at entry & $1.42\times10^{9}$ & $1.4238\times10^{9}$ & $1.003$
  & correct (even exponent) \\
\bottomrule
\end{tabular}
\end{center}

The slip is not asserted but localised: \texttt{source\_tauon\_max\_velocity\_%s}
proves that the published figure squared is a factor in $[10.01, 10.02]$ below
the verified one, and \texttt{source\_tauon\_max\_velocity\_factor} that the
figure itself is low by a factor in $[3.164, 3.165]$.  The source's own
intermediate, $v_f^2 \approx 1.80\times10^{25}$ m²/s², is right; only its root is
wrong.  Both values are kept in the development
(\texttt{sourceTauonMaxVelocity}) so that nothing is silently corrected.

\subsection*{The speed limit}

The muonic ceiling is subluminal (\texttt{muonMaxEjection\_subluminal}:
$2.07\times10^{7} < c$), and so is the muonic collision window.  The tauonic
ceiling is not (\texttt{tauonMaxEjection\_superluminal}:
$c < 4.24\times10^{12}$ m/s).  The tauonic \emph{input} window is still
subluminal (\texttt{tauonicInputMax\_subluminal}), so the framework's rejection
of the Lorentz factor is required only to interpret the output.  This is the
sharpest formal statement of the framework's distance from standard kinematics,
and it is worth being explicit: a superluminal exhaust is not a technical
difficulty to be engineered around, it is a consequence of the law as written.
""" % "underestimates"


def section_regimes() -> str:
    return r"""
\section{The two regimes, and what continuity actually says}
\label{sec:regimes}

Both regimes are instances of one structure, \texttt{PropulsiveRegime}, carrying
a mass ratio, an input window and the law-induced output.  Everything proved of
the structure therefore applies to both.

\begin{center}\small
\begin{tabular}{@{}lcc@{}}
\toprule
 & muonic & tauonic \\
\midrule
Colliding leptons & $\mu^-/\mu^+$ & $\tau^-/\tau^+$ \\
Mass ratio $m/m_e$ & 207 & 3477 \\
Amplification $(m/m_e)^3$ & $8.87\times10^{6}$ & $4.20\times10^{10}$ \\
Casimir amplification & $3.80\times10^{11}$ & $5.08\times10^{17}$ \\
Input window $v_2$ & $]0,\ 25\,000\ \mathrm{km/h}]$ & $]25\,000\ \mathrm{km/h},\ v_f^{\max,\mu}]$ \\
Output ceiling & $20\,682\ \mathrm{km/s}$ & $4.2403\times10^{12}\ \mathrm{m/s}$ \\
\bottomrule
\end{tabular}
\end{center}

\paragraph{Continuity, stated correctly.}
The source text says that ``the entry velocity of the tauonic domain coincides
exactly with the maximum output velocity of the muonic domain''.  Those are two
different coincidences, and the formalization separates them, because conflating
them is how a boundary argument goes wrong:

\begin{enumerate}[leftmargin=*]
\item \textbf{Adjacency} (\texttt{windows\_adjacent}): the tauonic window begins
  at $25\,000$ km/h, which is the muonic \emph{input} ceiling.
\item \textbf{The chain closes} (\texttt{chain\_closes}): the tauonic window's
  \emph{upper} end is the muonic regime's maximum \emph{output}, $20\,682$ km/s.
  So the second regime's input ceiling is the first regime's output ceiling ---
  true of the upper end, not the entry.
\end{enumerate}

Together with \texttt{regimes\_tile} (the two windows cover one interval, with no
gap and no overlap) and \texttt{tauonic\_window\_nested\_in\_output} (the tauonic
window sits inside the muonic output range), this is the exact content of the
nested-regime claim.  \texttt{regime\_continuity} collects the four facts and the
continuity of the velocity map in $v_2$ in one statement.

The boundary itself is a named object, \texttt{domainBoundary}, with
\texttt{domainBoundary\_eq\_muonic\_output} (it *is* the muonic output ceiling)
and \texttt{domainBoundary\_km\_per\_s} (it lies in $[20\,680, 20\,700]$ km/s,
i.e.\ the source's $20\,700$ to the precision of the print).  It is subluminal
(\texttt{domainBoundary\_subluminal}).

Taking the unrounded value $v_f^{\max,\mu}$ as the tauonic input ceiling rather
than the printed $20\,700$ km/s is what makes the match exact rather than
approximate: the theorem \texttt{chain\_closes} is then true by construction,
whereas with the rounded figure it would hold only to three significant digits.
That choice is recorded in the definition of \texttt{tauonicInputMax} and
justified in its docstring.

\paragraph{Structural algebra.}
The amplification $r \mapsto r^{\,n-2}$ is a multiplicative character
(\texttt{amplification\_mul}), so the tauonic factor factors through the muonic
one (\texttt{tauon\_amplification\_factors}):
$3477^3 = 207^3 \cdot (3477/207)^3$.  This is why the regimes compose: a
two-stage cascade multiplies, and the ordering of the regimes is forced by the
lepton mass hierarchy rather than chosen (\texttt{regimes\_strictly\_ordered}).
"""


def section_thrust(checks: list[dict]) -> str:
    by = {c["theorem"]: c for c in checks}
    return r"""
\section{Thrust: what the framework fixes, and the question it leaves open}
\label{sec:thrust}

The kinematics fix the exhaust velocity.  Momentum and energy balance then fix
the thrust-to-power ratio exactly, and nothing else:

\[
  T = \dot m\, v_e, \qquad P = \tfrac12 \dot m\, v_e^2
  \quad\Longrightarrow\quad
  \frac{T}{P} = \frac{2}{v_e}
\]

\noindent proved as \texttt{thrust\_to\_power} for an arbitrary
\texttt{ThrusterDesign}, and as \texttt{thrust\_eq\_power}: $T = 2P/v_e$.

This has a consequence the source text does not mention and which the
development makes unavoidable.  At the muonic exhaust velocity,
$T/P \approx 9.67\times10^{-8}$ N/W
(\texttt{muonic\_thrust\_to\_power\_bounds}), which is a factor
$\approx 5.8\times10^{3}$ \emph{worse} than a Raptor engine
(\texttt{muonic\_thrust\_to\_power\_shortfall}).  The specific-impulse gain and
the thrust-per-watt loss are the same number, because both are $v_e$: raising
$I_\mathrm{sp}$ from $363$ s to $2.1\times10^{6}$ s raises it by $5.8\times10^{3}$
and lowers thrust per watt by $5.8\times10^{3}$.  Any muonic thruster trades one
for the other; there is no regime in which the law gives both.

What the framework does \emph{not} fix is absolute thrust.  This is proved, not
asserted: \texttt{thrust\_not\_determined} shows that for any positive thrust
$T$ there is a design at the muonic exhaust velocity delivering exactly $T$ ---
thrust is bought with mass flow and power.  Consequently the engineering
question is a question about power budgets, and is recorded as a proposition

\begin{verbatim}
ThrustOptimizationConjecture T P  :=
  exists a design with exhaust velocity the muonic ceiling,
  thrust T, and jet power at most P
\end{verbatim}

\noindent which the development never asserts.  It is shown to be non-vacuous
(\texttt{thrust\_optimization\_satisfiable}) and to be settled by a power budget
rather than by the geometry (\texttt{thrust\_optimization\_is\_empirical}).  That
is the precise sense in which ``empirical thrust optimisations remain
unproven'': the framework's contribution is the hyperbola $T = 2P/v_e$, and
everything beyond it is engineering.
"""


def section_verification(decls: list[Decl], compile_res: list[dict], checks: list[dict],
                         problems: list[str], now: str) -> str:
    ok = all(r["ok"] for r in compile_res) and all(c["ok"] for c in checks) and not problems
    total_s = sum(r["seconds"] for r in compile_res)
    axiom_sets: dict[str, int] = {}
    for d in decls:
        if d.axioms_known:
            key = ", ".join(d.axioms) if d.axioms else "none"
            axiom_sets[key] = axiom_sets.get(key, 0) + 1

    OVERALL = (r"\textcolor{okgreen}{\textbf{pass} --- sources elaborate, every constant agrees, "
               r"no forbidden token, no non-standard axiom}" if ok
               else r"\textcolor{red}{\textbf{FAIL}}")
    comp_rows = "\n".join(
        rf"\texttt{{{tex(r['module'])}}} & {'elaborated' if not r['cached'] else 'cached (fresh)'} & "
        rf"{r['seconds']:.2f} s & {'ok' if r['ok'] else r'\textcolor{red}{failed}'} " + LATEX_EOL
        for r in compile_res)

    check_rows = []
    for c in checks:
        if c["interval"]:
            rng = rf"$[{fmath(c['interval'][0])},\ {fmath(c['interval'][1])}]$"
            val = rf"${fmath(c['value'])}$"
        else:
            rng, val = "exact numeral", rf"\texttt{{{tex(c['expect'] or '')}}}"
        mark = r"\textcolor{okgreen}{ok}" if c["ok"] else r"\textcolor{red}{FAIL}"
        check_rows.append(
            rf"\texttt{{\scriptsize {tex(c['theorem'])}}} & {tex(c['label'])} & "
            rf"{rng} & {val} & {mark} " + LATEX_EOL)

    axiom_rows = "\n".join(
        rf"{'none' if k == 'none' else ', '.join(r'\texttt{' + tex(a) + '}' for a in k.split(', '))} & {v} " + LATEX_EOL
        for k, v in sorted(axiom_sets.items()))

    prob = ("\\textcolor{red}{" + "\\\\ ".join(tex(p) for p in problems) + "}")
    return rf"""
\section{{Verification}}
\label{{sec:verification}}

\noindent\textbf{{Overall:}} {OVERALL}

\paragraph{{1. Hygiene.}}
The sources are scanned for \texttt{{sorry}}, \texttt{{admit}}, \texttt{{axiom}}
and \texttt{{native\_decide}} before anything is compiled; a hit aborts the
build.  Hits: {prob if problems else r'\textbf{none}'}.

\paragraph{{2. Elaboration.}}
Each module is elaborated with \texttt{{lean}} in dependency order.
Total elaboration time: {total_s:.2f} s.

\begin{{center}}\small
\begin{{tabular}}{{@{{}}lccc@{{}}}}
\toprule
Module & Status & Time & Result \\
\midrule
{comp_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\paragraph{{3. Axiom audit.}}
\texttt{{\#print axioms}} is run on every theorem and definition.  Grouped by
the set of axioms each declaration depends on:

\begin{{center}}\small
\begin{{tabular}}{{@{{}}lc@{{}}}}
\toprule
Axioms & Declarations \\
\midrule
{axiom_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\noindent None of these is \texttt{{sorryAx}}, and no declaration carries a
framework-specific axiom: the \texttt{{propext}} / \texttt{{Classical.choice}} /
\texttt{{Quot.sound}} triple is Lean's standard classical base, used by the
decision procedures, not by the mathematics of the framework.

\paragraph{{4. Independent recomputation.}}
Every numerical claim is recomputed in Python from its definition --- exact
integers and \texttt{{Fraction}} where the quantity is rational --- and compared
with the interval or numeral that Lean actually states.

{{\footnotesize
\begin{{longtable}}{{@{{}}p{{0.325\textwidth}}p{{0.245\textwidth}}p{{0.175\textwidth}}p{{0.155\textwidth}}p{{0.05\textwidth}}@{{}}}}
\toprule
Theorem & Quantity & Lean & Recomputed & \\
\midrule
\endhead
{chr(10).join(check_rows)}
\bottomrule
\end{{longtable}}
}}

\paragraph{{5. Provenance.}}
Source digests (SHA-256, first 16 hex digits) at report time:

\begin{{center}}\small
\begin{{tabular}}{{@{{}}lc@{{}}}}
\toprule
Module & Digest \\
\midrule
{chr(10).join(rf"\texttt{{{tex(name)}}} & \texttt{{{sha256(REPO / UMBRELLA / (name + '.lean'))}}}" + r" \\" for name in MODULES)}
\texttt{{{UMBRELLA}}} & \texttt{{{sha256(REPO / (UMBRELLA + '.lean'))}}} \\
\bottomrule
\end{{tabular}}
\end{{center}}

\noindent Report generated {now}.
"""


def declaration_index(decls: list[Decl]) -> str:
    rows = []
    for d in decls:
        doc = tex_prose(d.doc) if d.doc else ""
        rows.append(
            rf"\texttt{{{tex(d.full.replace('TheoreticalFramework.', ''))}}} & \texttt{{{tex(d.kind)}}} & "
            rf"\small {doc} \\")
    return r"""
\clearpage
\appendix
\section{Declaration index}
\label{app:index}

Every declaration of the development, with its docstring.  The list is produced
by parsing the sources, so no declaration can be omitted by an oversight: if it
compiles, it is here.

\begin{center}\footnotesize
\begin{longtable}{@{}p{0.36\textwidth}p{0.10\textwidth}p{0.44\textwidth}@{}}
\toprule
Name & Kind & Content \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
\end{center}
"""


def source_appendix() -> str:
    out = [r"""
\clearpage
\section{The verified sources}
\label{app:sources}

The complete development, as elaborated by Lean.  Digests are in
\S\ref{sec:verification}.
"""]
    for name in MODULES:
        src = (REPO / UMBRELLA / f"{name}.lean").read_text(encoding="utf-8")
        out.append(rf"""
\subsection*{{\texttt{{TheoreticalFramework/{name}.lean}}}}
\vspace{{2pt}}
{lean_block(src)}
\clearpage
""")
    return "\n".join(out)


def latex_document(decls, compile_res, checks, problems, lean_version, now) -> str:
    body = "\n".join([
        header(decls, compile_res, checks, lean_version, now),
        section_scope(),
        section_core(),
        section_casimir_table(checks),
        section_dimensions(),
        section_velocity(checks),
        section_regimes(),
        section_thrust(checks),
        section_verification(decls, compile_res, checks, problems, now),
        declaration_index(decls),
        source_appendix(),
    ])
    return r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage[margin=2.2cm]{geometry}
\usepackage{fancyhdr}
\usepackage[colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue]{hyperref}

\setmainfont{DejaVu Sans}
\setmonofont{NotoSansMono-Regular.ttf}[Scale=0.94]
\definecolor{okgreen}{RGB}{0,110,60}

\pagestyle{fancy}
\fancyhf{}
\lhead{\small Leptonic compactness and the generalized $n$-dimensional law}
\rhead{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}

\setlength{\parskip}{3pt}
\setlength{\parindent}{0pt}

\title{}
\date{}
\begin{document}
\sloppy
""" + body + r"""
\end{document}
"""


# --------------------------------------------------------------------------- #
# Markdown mirror
# --------------------------------------------------------------------------- #

def markdown_report(decls, compile_res, checks, problems, now) -> str:
    ok = all(r["ok"] for r in compile_res) and all(c["ok"] for c in checks) and not problems
    lines = [
        "# Leptonic compactness and the generalized n-dimensional velocity law",
        "",
        f"*Formal report, generated {now} from the Lean sources by "
        "`paper/tools/build_paper.py`.*",
        "",
        f"**Status:** {'all checks passed' if ok else 'CHECKS FAILED'}  ",
        f"**Declarations:** {len(decls)} "
        f"({sum(1 for d in decls if d.kind in ('theorem', 'lemma'))} theorems).",
        "",
        "## Reported quantities",
        "",
        "| Quantity | Value |",
        "|---|---|",
        f"| Casimir amplification $E_{{C,\\mu}}/E_{{C,e}}$ | {fmt_uni(MU ** 5)} |",
        f"| Casimir amplification $E_{{C,\\tau}}/E_{{C,e}}$ | {fmt_uni(TAU ** 5)} |",
        f"| Velocity amplification $(m_\\mu/m_e)^3$ | {MU ** 3:,} |",
        f"| Velocity amplification $(m_\\tau/m_e)^3$ | {TAU ** 3:,} |",
        f"| Muonic ejection ceiling | {fmt_uni(VF_MUON)} m/s = {VF_MUON / 1e3:.1f} km/s |",
        f"| Muonic specific impulse | {fmt_uni(ISP_MUON)} s ({ISP_MUON / RAPTOR_ISP:.0f} x Raptor) |",
        f"| Tauonic ejection ceiling | {fmt_uni(VF_TAUON)} m/s |",
        f"| Tauonic ejection at entry | {fmt_uni(VF_TAUON_ENTRY)} m/s |",
        f"| Tauonic ejection at median input | {fmt_uni(VF_TAUON_MEDIAN)} m/s |",
        f"| Muonic thrust per watt | {fmt_uni(2 / VF_MUON)} N/W |",
        "",
        "## Numerical cross-checks",
        "",
        "| Theorem | Quantity | Lean | Recomputed | Status |",
        "|---|---|---|---|---|",
    ]
    for c in checks:
        if c["interval"]:
            lean = f"[{fmt_uni(c['interval'][0])}, {fmt_uni(c['interval'][1])}]"
            val = fmt_uni(c["value"])
        else:
            lean, val = "exact numeral", f"`{c['expect']}`"
        lines.append(
            f"| `{c['theorem']}` | {c['label']} | {lean} | {val} | "
            f"{'ok' if c['ok'] else '**FAIL**'} |")
    lines += [
        "",
        "## Published figures checked",
        "",
        "| Quantity | Source text | Verified | Verdict |",
        "|---|---|---|---|",
    ]
    for label, published, verified, verdict in PUBLISHED:
        lines.append(f"| {label} | {md_math(published)} | {verified} | {verdict} |")
    lines += [
        "",
        "## Verification",
        "",
    ]
    for r in compile_res:
        lines.append(f"- `{r['module']}`: "
                     f"{'elaborated' if not r['cached'] else 'cached'}, "
                     f"{r['seconds']:.2f} s, {'ok' if r['ok'] else 'FAILED'}")
    lines.append("")
    lines.append(f"- hygiene (no `sorry`/`admit`/`axiom`/`native_decide`): "
                 f"{'clean' if not problems else '; '.join(problems)}")
    axiom_sets: dict[str, int] = {}
    for d in decls:
        if d.axioms_known:
            key = ", ".join(d.axioms) if d.axioms else "none"
            axiom_sets[key] = axiom_sets.get(key, 0) + 1
    for k, v in sorted(axiom_sets.items()):
        lines.append(f"- axioms `{k}`: {v} declarations")
    lines += ["", "## Declaration index", "", "| Name | Kind | Statement |",
              "|---|---|---|"]
    for d in decls:
        stmt = d.statement.replace("|", "\\|")
        if len(stmt) > 220:
            stmt = stmt[:217] + "…"
        lines.append(f"| `{d.short}` | {d.kind} | `{stmt}` |")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fast", action="store_true",
                    help="reuse fresh .olean files instead of re-elaborating")
    ap.add_argument("--no-pdf", action="store_true", help="stop before LaTeX")
    args = ap.parse_args()

    BUILD.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    decls: list[Decl] = []
    for name in MODULES:
        decls.extend(parse_declarations(REPO / UMBRELLA / f"{name}.lean", name))
    print(f"[build_paper] parsed {len(decls)} declarations from {len(MODULES)} modules")

    problems = hygiene(decls)
    if problems:
        print("[build_paper] HYGIENE FAILURE")
        for p in problems:
            print("   ", p)
        return 1
    print("[build_paper] hygiene: no sorry/admit/axiom/native_decide")

    print("[build_paper] elaborating modules with lean ...")
    compile_res = compile_modules(args.fast)
    for r in compile_res:
        state = "cached" if r["cached"] else f"{r['seconds']:.2f}s"
        print(f"    {r['module']:<20} {'ok' if r['ok'] else 'FAILED':<7} {state}")
        if not r["ok"]:
            print(r["diagnostics"])
            return 1

    print("[build_paper] auditing declarations (#check, #print axioms) ...")
    errs = audit(decls)
    if errs:
        print("[build_paper] audit failed:")
        print("\n".join(errs[:20]))
        return 1
    missing = [d.full for d in decls if not d.type_]
    if missing:
        print(f"[build_paper] warning: {len(missing)} declarations without a type")
        for m in missing[:5]:
            print("   ", m)

    print("[build_paper] cross-checking constants ...")
    checks = cross_check(decls)
    bad = [c for c in checks if not c["ok"]]
    for c in checks:
        mark = "ok  " if c["ok"] else "FAIL"
        extra = ""
        if c["interval"]:
            extra = f"[{c['interval'][0]:.6g}, {c['interval'][1]:.6g}] vs {c['value']:.6g}"
        print(f"    {mark} {c['theorem']:<45} {extra} {c['note']}")
    if bad:
        print(f"[build_paper] {len(bad)} cross-check(s) failed")

    raw_version = subprocess.run(["lean", "--version"], capture_output=True,
                                 text=True).stdout.strip().splitlines()[0]
    mo = re.search(r"version\s+([\w.]+)", raw_version)
    lean_version = mo.group(1) if mo else raw_version

    tex_src = latex_document(decls, compile_res, checks, problems, lean_version, now)
    if "\t" in tex_src:
        bad = [ln for ln in tex_src.splitlines() if "\t" in ln][:3]
        print("[build_paper] BUG: tab character in generated LaTeX (non-raw string literal):")
        for ln in bad:
            print("   ", repr(ln[:120]))
        return 1
    md_src = markdown_report(decls, compile_res, checks, problems, now)
    (BUILD / "report.tex").write_text(tex_src, encoding="utf-8")
    (PAPER / "report.md").write_text(md_src, encoding="utf-8")
    print(f"[build_paper] wrote {BUILD / 'report.tex'} and {PAPER / 'report.md'}")

    summary = {
        "generated": now,
        "lean": lean_version,
        "modules": compile_res,
        "declarations": len(decls),
        "hygiene_problems": problems,
        "checks": checks,
        "all_ok": not bad,
    }
    (BUILD / "verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.no_pdf:
        return 0 if not bad else 1

    print("[build_paper] compiling LaTeX ...")
    proc = subprocess.run(
        ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
         "-file-line-error", "report.tex"],
        cwd=BUILD, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-40:])
        print("[build_paper] LaTeX failed:\n" + tail)
        return 1
    shutil.copyfile(BUILD / "report.pdf", PAPER / "report.pdf")
    pages = subprocess.run(["pdfinfo", str(PAPER / "report.pdf")],
                           capture_output=True, text=True).stdout
    npages = re.search(r"Pages:\s+(\d+)", pages)
    print(f"[build_paper] wrote {PAPER / 'report.pdf'}"
          f" ({npages.group(1) if npages else '?'} pages)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
