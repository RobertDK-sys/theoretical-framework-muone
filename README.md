# TheoreticalFramework

A Lean 4 development of the leptonic-compactness framework that connects the
muon magnetic anomaly to a propulsive velocity law for charged leptons, together
with the tool that turns it into a formal report and PDF.

## What is proved

| Claim | Theorem |
|---|---|
| Effective radius `r_ℓ = κ/m_ℓ` is decreasing in the mass | `effRadius_strictAnti` |
| Casimir energy of the internal geometry is quintic in the mass | `casimirEnergy_eq_quintic` |
| Amplification between leptons is the fifth power of the mass ratio | `casimirEnergy_ratio` |
| That ratio is independent of `κ`, the area coefficient and the Casimir prefactor | `CasimirAnsatz.energy_ratio_parameter_free` |
| `E_C(μ)/E_C(e) = 207⁵ = 380 059 617 807 ≈ 3.8 × 10¹¹` | `casimir_amplification_muon_general` |
| `E_C(τ)/E_C(e) = 3477⁵ = 508 186 885 683 281 157 ≈ 5.1 × 10¹⁷` | `casimir_amplification_tauon_general` |
| Generalized dimension `n = 5`, velocity exponent `n − 2 = 3` | `generalizedDimension_eq_five`, `velocityExponent_eq_three` |
| `vf² = v₂²·(m_ℓ/m₀)^(n−2)` for arbitrary `n` | `velocity_law` |
| `(207)³ = 8 869 743 ≈ 8.9 × 10⁶`, `(3477)³ ≈ 4.2 × 10¹⁰` | `muonAmplification_eq`, `tauonAmplification_eq` |
| Muonic ceiling `≈ 20 682 km/s`, `Isp ≈ 2.109 × 10⁶ s ≈ 5810 × Raptor` | `muonMaxEjection_bounds`, `muonImpulse_over_raptor` |
| Tauonic ceiling `4.2403 × 10¹² m/s` | `tauonMaxEjection_bounds` |
| The source's `1.34 × 10¹² m/s` is `√10` too small | `source_tauon_max_velocity_underestimates` |
| The two regimes tile one input interval and nest in the muonic output range | `regimes_tile`, `tauonic_window_nested_in_output` |
| The tauonic input ceiling *is* the muonic output ceiling | `chain_closes` |
| Amplification is a multiplicative character | `amplification_mul` |
| `T/P = 2/v_e` exactly; thrust is not fixed by the geometry | `thrust_to_power`, `thrust_not_determined` |

Everything is proved in Lean 4 against Mathlib, with no `sorry`, no `admit`, no
framework-specific axiom and no `native_decide`.  The axiom audit is part of the
build and is printed in the report.

## What is *not* proved — and is not claimed

* The geometric ansatz (`r_ℓ = κ/m_ℓ`, plate area proportional to `m²`) is a
  **postulate** of the framework, recorded as the structure `CasimirAnsatz` with
  free constants.  Only the parameter-freedom of the resulting ratio is proved.
* The velocity law is a **postulate** of the generalized kinematics.  Its
  consequences are proved; its truth is not addressable in Lean.
* `ThrustOptimizationConjecture` — the empirical thrust question — is a
  `def : Prop` that is *never asserted*.  `thrust_not_determined` proves that the
  geometry cannot settle it.
* The framework's central premise is in tension with measurement: attributing
  part of `a_μ` to a term scaling as `m⁵` over-predicts the generation dependence
  by roughly `10⁷` relative to the observed `(m_μ/m_e)²`.  The attached source
  notes say so themselves.  A correct formalization of a scaling law is not
  evidence for the postulate that produces it, and the report says so in §1.
* The tauonic ceiling is superluminal (`tauonMaxEjection_superluminal`).  That is
  a consequence of the law as written, not a technicality.

## Layout

```
TheoreticalFramework.lean            umbrella module
TheoreticalFramework/Basic.lean      effRadius, Casimir energy, quintic law, ratios
TheoreticalFramework/Leptons.lean    lepton data, 207⁵ and 3477⁵, field exponents
TheoreticalFramework/Dimensions.lean n = 5, the velocity law for general n, units
TheoreticalFramework/Velocity.lean   amplification factors, ejection velocities, Isp
TheoreticalFramework/Regimes.lean    regimes, continuity, thrust, the open question
paper/tools/build_paper.py           verify + audit + cross-check + typeset
paper/report.pdf                     the formal report (30 pages)
paper/report.md                      Markdown mirror of the report
paper/build/                         generated LaTeX, audit file, verification.json
```

## Building

```
make verify     # elaborate every module with lean
make paper      # full verification + audit + cross-check + PDF
make check      # same, reusing fresh .olean files, no LaTeX
```

`make paper` re-runs the verification, so the PDF cannot be stale with respect to
the sources: if a module fails to elaborate, the build stops before LaTeX.

Mathlib in this machine is prebuilt at `/opt/mathlib` and already on `LEAN_PATH`,
so the sources are checked by calling `lean` directly.  `lake build` would do the
same thing but needs a writable Mathlib build directory, which `/opt/mathlib` is
not; the `lakefile.toml` is there for a checkout where that is available.
