# Leptonic compactness and the generalized n-dimensional velocity law

*Formal report, generated 2026-11-05 13:39 UTC from the Lean sources by `paper/tools/build_paper.py`.*

**Status:** all checks passed  
**Declarations:** 142 (97 theorems).

## Reported quantities

| Quantity | Value |
|---|---|
| Casimir amplification $E_{C,\mu}/E_{C,e}$ | 3.8006×10¹¹ |
| Casimir amplification $E_{C,\tau}/E_{C,e}$ | 5.08187×10¹⁷ |
| Velocity amplification $(m_\mu/m_e)^3$ | 8,869,743 |
| Velocity amplification $(m_\tau/m_e)^3$ | 42,035,292,333 |
| Muonic ejection ceiling | 2.0682×10⁷ m/s = 20682.0 km/s |
| Muonic specific impulse | 2.10898×10⁶ s (5810 x Raptor) |
| Tauonic ejection ceiling | 4.24033×10¹² m/s |
| Tauonic ejection at entry | 1.42379×10⁹ m/s |
| Tauonic ejection at median input | 2.84757×10¹⁰ m/s |
| Muonic thrust per watt | 9.67023×10⁻⁸ N/W |

## Numerical cross-checks

| Theorem | Quantity | Lean | Recomputed | Status |
|---|---|---|---|---|
| `collisionVelocityMuonMax_bounds` | muonic collision ceiling v₂, m/s | [6,944, 6,945] | 6,944 | ok |
| `casimir_amplification_muon_order` | casimir amplification (m_μ/m_e)⁵ | [3.8×10¹¹, 4×10¹¹] | 3.8006×10¹¹ | ok |
| `casimir_amplification_tauon_order` | casimir amplification (m_τ/m_e)⁵ | [5.08×10¹⁷, 5.1×10¹⁷] | 5.08187×10¹⁷ | ok |
| `casimir_amplification_tauon_over_muon` | (m_τ/m_μ)⁵ | [1.3×10⁶, 1.34×10⁶] | 1.33712×10⁶ | ok |
| `muonAmplification_order` | velocity amplification 207³ | [8.8×10⁶, 8.9×10⁶] | 8.86974×10⁶ | ok |
| `tauonAmplification_order` | velocity amplification 3477³ | [4.2×10¹⁰, 4.21×10¹⁰] | 4.20353×10¹⁰ | ok |
| `tauon_over_muon_amplification` | 3477³/207³ | [4,730, 4,740] | 4,739 | ok |
| `muonMaxEjection_bounds` | muonic ejection ceiling, m/s | [2.0682×10⁷, 2.06821×10⁷] | 2.0682×10⁷ | ok |
| `muonMaxEjection_km_per_s` | muonic ejection ceiling, km/s | [2.068×10⁴, 2.07×10⁴] | 2.0682×10⁴ | ok |
| `muonSpecificImpulse_bounds` | muonic specific impulse, s | [2.108×10⁶, 2.109×10⁶] | 2.10898×10⁶ | ok |
| `muonImpulse_over_raptor` | Isp(muonic)/Isp(Raptor) | [5,800, 5,820] | 5,810 | ok |
| `tauonMaxEjection_bounds` | tauonic ejection ceiling, m/s | [4.2403×10¹², 4.2404×10¹²] | 4.24033×10¹² | ok |
| `tauonEntryEjection_bounds` | tauonic ejection at entry, m/s | [1.4237×10⁹, 1.4239×10⁹] | 1.42379×10⁹ | ok |
| `tauonMedianEjection_bounds` | tauonic ejection at median input, m/s | [2.8475×10¹⁰, 2.8476×10¹⁰] | 2.84757×10¹⁰ | ok |
| `source_tauon_max_velocity_underestimates` | (verified/source)² at the tauonic ceiling | [10.01, 10.02] | 10.01361 | ok |
| `source_tauon_max_velocity_factor` | verified/source at the tauonic ceiling | [3.164, 3.165] | 3.16443 | ok |
| `muonic_thrust_to_power_bounds` | muonic thrust per watt, N/W | [9.6×10⁻⁸, 9.7×10⁻⁸] | 9.67023×10⁻⁸ | ok |
| `muonic_thrust_to_power_shortfall` | v_e(muonic)/v_e(Raptor) | [5,800, 5,820] | 5,810 | ok |
| `domainBoundary_km_per_s` | domain boundary, km/s | [2.068×10⁴, 2.07×10⁴] | 2.0682×10⁴ | ok |
| `massRatioMuon_pow_five` | 207⁵ | exact numeral | `380059617807` | ok |
| `massRatioTauon_pow_five` | 3477⁵ | exact numeral | `508186885683281157` | ok |
| `muonAmplification_eq` | 207³ | exact numeral | `8869743` | ok |
| `tauonAmplification_eq` | 3477³ | exact numeral | `42035292333` | ok |
| `collisionVelocityMuonMax_eq` | 25 000 km/h in m/s | exact numeral | `62500 / 9` | ok |

## Published figures checked

| Quantity | Source text | Verified | Verdict |
|---|---|---|---|
| Casimir amplification, muon | (207)⁵ ≈ 4 × 10¹¹ | 3.8006 × 10¹¹ | agrees at one significant figure |
| Casimir amplification, tauon | (3477)⁵ ≈ 5.1 × 10¹⁷ | 5.0819 × 10¹⁷ | agrees |
| Velocity amplification, muon | (207)³ ≈ 8.9 × 10⁶ | 8 869 743 = 8.87 × 10⁶ | agrees |
| Velocity amplification, tauon | (3477)³ ≈ 4.2 × 10¹⁰ | 42 035 292 333 = 4.20 × 10¹⁰ | agrees |
| Muonic ejection ceiling | ≈ 20 700 km/s | 20 682.0 km/s | agrees |
| Muonic specific impulse | ≈ 2 × 10⁶ s, 6000× Raptor | 2.1090 × 10⁶ s, 5810 × Raptor | agrees; 6000 is a rounding of 5810 |
| Tauonic ejection at entry | ≈ 1.42 × 10⁹ m/s | 1.4238 × 10⁹ m/s | agrees |
| Tauonic ejection at median input | ≈ 9.0 × 10¹⁰ m/s | 2.8476 × 10¹⁰ m/s | DISAGREES: source is √10 too small |
| Tauonic ejection ceiling | ≈ 1.34 × 10¹² m/s | 4.2403 × 10¹² m/s | DISAGREES: source is √10 too small |

## Verification

- `Basic`: elaborated, 2.13 s, ok
- `Leptons`: elaborated, 2.12 s, ok
- `Dimensions`: elaborated, 2.08 s, ok
- `Velocity`: elaborated, 2.43 s, ok
- `Regimes`: elaborated, 2.42 s, ok
- `TheoreticalFramework`: elaborated, 1.88 s, ok

- hygiene (no `sorry`/`admit`/`axiom`/`native_decide`): clean
- axioms `none`: 6 declarations
- axioms `propext, Classical.choice, Quot.sound`: 133 declarations

## Declaration index

| Name | Kind | Statement |
|---|---|---|
| `le_of_sq_le_sq` | theorem | `{a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (h : a ^ 2 ≤ b ^ 2) : a ≤ b` |
| `effRadius` | def | `(κ m : ℝ) : ℝ` |
| `effRadius_pos` | theorem | `{κ m : ℝ} (hκ : 0 < κ) (hm : 0 < m) : 0 < effRadius κ m` |
| `effRadius_div` | theorem | `{κ m₁ m₂ : ℝ} (hκ : κ ≠ 0) (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : effRadius κ m₁ / effRadius κ m₂ = m₂ / m₁ := by effRadius κ m₁ / effRadius κ m₂ = m₂ / m₁` |
| `effRadius_strictAnti` | theorem | `{κ : ℝ} (hκ : 0 < κ) : StrictAntiOn (effRadius κ) (Set.Ioi 0) := by StrictAntiOn (effRadius κ) (Set.Ioi 0)` |
| `casimirEnergy` | def | `(κ m : ℝ) : ℝ` |
| `casimirEnergy_eq_quintic` | theorem | `{κ m : ℝ} (hκ : κ ≠ 0) (hm : m ≠ 0) : casimirEnergy κ m = m ^ 5 / κ ^ 3 := by casimirEnergy κ m = m ^ 5 / κ ^ 3` |
| `casimirEnergy_ratio` | theorem | `{κ : ℝ} (hκ : κ ≠ 0) {m₁ m₂ : ℝ} (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : casimirEnergy κ m₁ / casimirEnergy κ m₂ = (m₁ / m₂) ^ 5 := by casimirEnergy κ m₁ / casimirEnergy κ m₂ = (m₁ / m₂) ^ 5` |
| `casimirEnergy_ratio_radii` | theorem | `{κ m₁ m₂ : ℝ} (hκ : κ ≠ 0) (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : casimirEnergy κ m₁ / casimirEnergy κ m₂ = (effRadius κ m₂ / effRadius κ m₁) ^ 5 := by casimirEnergy κ m₁ / casimirEnergy κ m₂ = (effRadius κ m₂ / effRadius κ m₁…` |
| `CasimirAnsatz` | structure | `` |
| `plateArea` | def | `(A : CasimirAnsatz) (m : ℝ) : ℝ` |
| `energy` | def | `(A : CasimirAnsatz) (m : ℝ) : ℝ` |
| `signedEnergy` | def | `(A : CasimirAnsatz) (C m : ℝ) : ℝ` |
| `energy_eq_quintic` | theorem | `(A : CasimirAnsatz) {m : ℝ} (hm : m ≠ 0) : A.energy m = A.areaCoeff * m ^ 5 / A.kappa ^ 3 := by A.energy m = A.areaCoeff * m ^ 5 / A.kappa ^ 3` |
| `energy_ratio` | theorem | `(A : CasimirAnsatz) {m₁ m₂ : ℝ} (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : A.energy m₁ / A.energy m₂ = (m₁ / m₂) ^ 5 := by A.energy m₁ / A.energy m₂ = (m₁ / m₂) ^ 5` |
| `energy_ratio_parameter_free` | theorem | `(A A' : CasimirAnsatz) {m₁ m₂ : ℝ} (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : A.energy m₁ / A.energy m₂ = A'.energy m₁ / A'.energy m₂ := by A.energy m₁ / A.energy m₂ = A'.energy m₁ / A'.energy m₂` |
| `signedEnergy_ratio` | theorem | `(A : CasimirAnsatz) {C m₁ m₂ : ℝ} (hC : C ≠ 0) (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : A.signedEnergy C m₁ / A.signedEnergy C m₂ = (m₁ / m₂) ^ 5 := by A.signedEnergy C m₁ / A.signedEnergy C m₂ = (m₁ / m₂) ^ 5` |
| `massElectronMeV` | def | `: ℝ` |
| `massMuonMeV` | def | `: ℝ` |
| `massTauonMeV` | def | `: ℝ` |
| `massRatioMuon` | def | `: ℝ` |
| `massRatioTauon` | def | `: ℝ` |
| `massRatioMuon_pos` | theorem | `: 0 < massRatioMuon` |
| `massRatioTauon_pos` | theorem | `: 0 < massRatioTauon` |
| `massRatioMuon_consistent` | theorem | `: \|massMuonMeV / massElectronMeV - massRatioMuon\| ≤ 0.25 := by \|massMuonMeV / massElectronMeV - massRatioMuon\| ≤ 0.25` |
| `massRatioTauon_consistent` | theorem | `: \|massTauonMeV / massElectronMeV - massRatioTauon\| ≤ 0.5 := by \|massTauonMeV / massElectronMeV - massRatioTauon\| ≤ 0.5` |
| `casimir_amplification_muon_general` | theorem | `{κ m₀ : ℝ} (hκ : κ ≠ 0) (hm : 0 < m₀) : casimirEnergy κ (massRatioMuon * m₀) / casimirEnergy κ m₀ = massRatioMuon ^ 5 := by casimirEnergy κ (massRatioMuon * m₀) / casimirEnergy κ m₀ = massRatioMuon ^ 5` |
| `casimir_amplification_tauon_general` | theorem | `{κ m₀ : ℝ} (hκ : κ ≠ 0) (hm : 0 < m₀) : casimirEnergy κ (massRatioTauon * m₀) / casimirEnergy κ m₀ = massRatioTauon ^ 5 := by casimirEnergy κ (massRatioTauon * m₀) / casimirEnergy κ m₀ = massRatioTauon ^ 5` |
| `massRatioMuon_pow_five` | theorem | `: massRatioMuon ^ 5 = 380059617807` |
| `massRatioTauon_pow_five` | theorem | `: massRatioTauon ^ 5 = 508186885683281157` |
| `casimir_amplification_muon_order` | theorem | `: (3.8 : ℝ) * 10 ^ 11 ≤ massRatioMuon ^ 5 ∧ massRatioMuon ^ 5 ≤ 4 * 10 ^ 11 := by (3.8 : ℝ) * 10 ^ 11 ≤ massRatioMuon ^ 5 ∧ massRatioMuon ^ 5 ≤ 4 * 10 ^ 11` |
| `casimir_amplification_tauon_order` | theorem | `: (5.08 : ℝ) * 10 ^ 17 ≤ massRatioTauon ^ 5 ∧ massRatioTauon ^ 5 ≤ (5.1 : ℝ) * 10 ^ 17 := by (5.08 : ℝ) * 10 ^ 17 ≤ massRatioTauon ^ 5 ∧ massRatioTauon ^ 5 ≤ (5.1 : ℝ) * 10 ^ 17` |
| `casimir_amplification_tauon_over_muon` | theorem | `: (1.3 : ℝ) * 10 ^ 6 ≤ (massRatioTauon / massRatioMuon) ^ 5 ∧ (massRatioTauon / massRatioMuon) ^ 5 ≤ (1.34 : ℝ) * 10 ^ 6 := by (massRatioTauon / massRatioMuon) ^ 5 ≤ (1.34 : ℝ) * 10 ^ 6` |
| `casimir_amplification_hierarchy` | theorem | `: (1 : ℝ) < massRatioMuon ^ 5 ∧ massRatioMuon ^ 5 < massRatioTauon ^ 5 := by (1 : ℝ) < massRatioMuon ^ 5 ∧ massRatioMuon ^ 5 < massRatioTauon ^ 5` |
| `fieldAmplificationSource` | def | `(m₁ m₂ : ℝ) : ℝ` |
| `fieldAmplificationPlate` | def | `(m₁ m₂ : ℝ) : ℝ` |
| `field_amplification_source` | theorem | `(κ m₁ m₂ : ℝ) (hκ : 0 < κ) (h₁ : 0 < m₁) (h₂ : 0 < m₂) : (casimirEnergy κ m₁ / (m₁ ^ 2 * effRadius κ m₁ ^ 3)) / (casimirEnergy κ m₂ / (m₂ ^ 2 * effRadius κ m₂ ^ 3)) = (m₁ / m₂) ^ 6 := by (casimirEnergy κ m₂ / (m₂ ^ 2 …` |
| `field_amplification_plate` | theorem | `(κ m₁ m₂ : ℝ) (hκ : 0 < κ) (h₁ : 0 < m₁) (h₂ : 0 < m₂) : (casimirEnergy κ m₁ / (m₁ ^ 2 * effRadius κ m₁)) / (casimirEnergy κ m₂ / (m₂ ^ 2 * effRadius κ m₂)) = (m₁ / m₂) ^ 4 := by (casimirEnergy κ m₂ / (m₂ ^ 2 * effRad…` |
| `field_amplification_muon_order` | theorem | `: (8.8 : ℝ) * 10 ^ 6 ≤ fieldAmplificationSource massRatioMuon 1 ∧ fieldAmplificationSource massRatioMuon 1 ≤ (8.9 : ℝ) * 10 ^ 6 := by fieldAmplificationSource massRatioMuon 1 ≤ (8.9 : ℝ) * 10 ^ 6` |
| `casimirMassExponent` | def | `: ℕ` |
| `generalizedDimension` | def | `: ℕ` |
| `generalizedDimension_eq_five` | theorem | `: generalizedDimension = 5` |
| `structuralTerm` | def | `(C m : ℝ) : ℝ` |
| `anomalousMoment` | def | `(aQED aEWHad C m : ℝ) : ℝ` |
| `structuralTerm_quintic` | theorem | `(C m : ℝ) : structuralTerm C m = C * (m : ℝ) ^ 5` |
| `structuralTerm_ratio` | theorem | `(C m₁ m₂ : ℝ) (hC : C ≠ 0) (h₁ : m₁ ≠ 0) (h₂ : m₂ ≠ 0) : structuralTerm C m₁ / structuralTerm C m₂ = (m₁ / m₂) ^ 5 := by structuralTerm C m₁ / structuralTerm C m₂ = (m₁ / m₂) ^ 5` |
| `velocityExponent` | def | `: ℕ` |
| `velocityExponent_eq_three` | theorem | `: velocityExponent = 3` |
| `velocityExponent_eq` | theorem | `(n : ℕ) (hn : n = generalizedDimension) : velocityExponent = n - 2 := by velocityExponent = n - 2` |
| `generalised_unit_exponents` | theorem | `(n : ℚ) (hn : n ≠ 0) : n * (2 / n) = 2` |
| `time_exponent_balance` | theorem | `(n : ℚ) : (n - 2) + 2 = n` |
| `GeneralisedVelocityRelation` | def | `(n : ℕ) (vn dt0 v2 : ℝ) : Prop` |
| `scale_substitution` | theorem | `(n : ℕ) {vn dt0 q v2 : ℝ} (h : vn * dt0 ^ (n - 2) = v2 ^ 2) : vn * (q * dt0) ^ (n - 2) = v2 ^ 2 * q ^ (n - 2) := by vn * (q * dt0) ^ (n - 2) = v2 ^ 2 * q ^ (n - 2)` |
| `generalisedVelocity` | def | `(n : ℕ) (v₂ r : ℝ) : ℝ` |
| `velocity_law` | theorem | `(n : ℕ) (v₂ r : ℝ) (hr : 0 ≤ r) : generalisedVelocity n v₂ r ^ 2 = v₂ ^ 2 * r ^ (n - 2) := by generalisedVelocity n v₂ r ^ 2 = v₂ ^ 2 * r ^ (n - 2)` |
| `generalisedVelocity_eq_mul` | theorem | `(n : ℕ) {v₂ r : ℝ} (hv : 0 ≤ v₂) : generalisedVelocity n v₂ r = v₂ * Real.sqrt (r ^ (n - 2)) := by generalisedVelocity n v₂ r = v₂ * Real.sqrt (r ^ (n - 2))` |
| `generalisedVelocity_nonneg` | theorem | `(n : ℕ) (v₂ r : ℝ) : 0 ≤ generalisedVelocity n v₂ r` |
| `generalisedVelocity_bounds` | theorem | `{n : ℕ} {v₂ r a b : ℝ} (hb : 0 ≤ b) (h₁ : a ^ 2 ≤ v₂ ^ 2 * r ^ (n - 2)) (h₂ : v₂ ^ 2 * r ^ (n - 2) ≤ b ^ 2) : a ≤ generalisedVelocity n v₂ r ∧ generalisedVelocity n v₂ r ≤ b := by a ≤ generalisedVelocity n v₂ r ∧ gene…` |
| `velocity_law_five` | theorem | `(v₂ r : ℝ) (hr : 0 ≤ r) : generalisedVelocity generalizedDimension v₂ r ^ 2 = v₂ ^ 2 * r ^ 3 := by generalisedVelocity generalizedDimension v₂ r ^ 2 = v₂ ^ 2 * r ^ 3` |
| `generalisedVelocity_five_eq_mul` | theorem | `{v₂ r : ℝ} (hv : 0 ≤ v₂) : generalisedVelocity generalizedDimension v₂ r = v₂ * Real.sqrt (r ^ 3) := by generalisedVelocity generalizedDimension v₂ r = v₂ * Real.sqrt (r ^ 3)` |
| `generalisedVelocity_mono` | theorem | `{n : ℕ} {v₂ r₁ r₂ : ℝ} (hr₁ : 0 ≤ r₁) (h : r₁ ≤ r₂) : generalisedVelocity n v₂ r₁ ≤ generalisedVelocity n v₂ r₂ := by generalisedVelocity n v₂ r₁ ≤ generalisedVelocity n v₂ r₂` |
| `generalisedVelocity_mono_v₂` | theorem | `{n : ℕ} {v₂ v₂' r : ℝ} (hv : 0 ≤ v₂) (h : v₂ ≤ v₂') (hr : 0 ≤ r) : generalisedVelocity n v₂ r ≤ generalisedVelocity n v₂' r := by generalisedVelocity n v₂ r ≤ generalisedVelocity n v₂' r` |
| `generalisedVelocity_zero` | theorem | `(n : ℕ) (r : ℝ) : generalisedVelocity n 0 r = 0` |
| `kmhToMs` | def | `(v : ℝ) : ℝ` |
| `kmhToMs_eq` | theorem | `(v : ℝ) : kmhToMs v = v * 1000 / 3600` |
| `standardGravity` | def | `: ℝ` |
| `standardGravity_pos` | theorem | `: 0 < standardGravity` |
| `speedOfLight` | def | `: ℝ` |
| `specificImpulse` | def | `(ve : ℝ) : ℝ` |
| `raptorSpecificImpulse` | def | `: ℝ` |
| `collisionVelocityMuonMax` | def | `: ℝ` |
| `collisionVelocityMuonMax_eq` | theorem | `: collisionVelocityMuonMax = 62500 / 9` |
| `collisionVelocityMuonMax_bounds` | theorem | `: 6944 ≤ collisionVelocityMuonMax ∧ collisionVelocityMuonMax ≤ 6945 := by 6944 ≤ collisionVelocityMuonMax ∧ collisionVelocityMuonMax ≤ 6945` |
| `muonAmplification` | def | `: ℝ` |
| `tauonAmplification` | def | `: ℝ` |
| `muonAmplification_eq` | theorem | `: muonAmplification = 8869743` |
| `tauonAmplification_eq` | theorem | `: tauonAmplification = 42035292333` |
| `muonAmplification_order` | theorem | `: (8.8 : ℝ) * 10 ^ 6 ≤ muonAmplification ∧ muonAmplification ≤ (8.9 : ℝ) * 10 ^ 6 := by (8.8 : ℝ) * 10 ^ 6 ≤ muonAmplification ∧ muonAmplification ≤ (8.9 : ℝ) * 10 ^ 6` |
| `tauonAmplification_order` | theorem | `: (4.2 : ℝ) * 10 ^ 10 ≤ tauonAmplification ∧ tauonAmplification ≤ (4.21 : ℝ) * 10 ^ 10 := by (4.2 : ℝ) * 10 ^ 10 ≤ tauonAmplification ∧ tauonAmplification ≤ (4.21 : ℝ) * 10 ^ 10` |
| `tauon_over_muon_amplification` | theorem | `: (4.73 : ℝ) * 10 ^ 3 ≤ tauonAmplification / muonAmplification ∧ tauonAmplification / muonAmplification ≤ (4.74 : ℝ) * 10 ^ 3 := by tauonAmplification / muonAmplification ≤ (4.74 : ℝ) * 10 ^ 3` |
| `muonMaxEjection` | def | `: ℝ` |
| `muonMaxEjection_sq` | theorem | `: muonMaxEjection ^ 2 = collisionVelocityMuonMax ^ 2 * massRatioMuon ^ 3 := by muonMaxEjection ^ 2 = collisionVelocityMuonMax ^ 2 * massRatioMuon ^ 3` |
| `muonMaxEjection_bounds` | theorem | `: (2.06820 : ℝ) * 10 ^ 7 ≤ muonMaxEjection ∧ muonMaxEjection ≤ (2.06821 : ℝ) * 10 ^ 7 := by muonMaxEjection ≤ (2.06821 : ℝ) * 10 ^ 7` |
| `muonMaxEjection_km_per_s` | theorem | `: (2.068 : ℝ) * 10 ^ 4 ≤ muonMaxEjection / 1000 ∧ muonMaxEjection / 1000 ≤ (2.07 : ℝ) * 10 ^ 4 := by muonMaxEjection / 1000 ≤ (2.07 : ℝ) * 10 ^ 4` |
| `muonMaxEjection_subluminal` | theorem | `: muonMaxEjection < speedOfLight` |
| `collisionVelocityMuonMax_subluminal` | theorem | `: collisionVelocityMuonMax < speedOfLight` |
| `muonSpecificImpulse_bounds` | theorem | `: (2.108 : ℝ) * 10 ^ 6 ≤ specificImpulse muonMaxEjection ∧ specificImpulse muonMaxEjection ≤ (2.109 : ℝ) * 10 ^ 6 := by specificImpulse muonMaxEjection ≤ (2.109 : ℝ) * 10 ^ 6` |
| `muonImpulse_over_raptor` | theorem | `: (5.80 : ℝ) * 10 ^ 3 ≤ specificImpulse muonMaxEjection / raptorSpecificImpulse ∧ specificImpulse muonMaxEjection / raptorSpecificImpulse ≤ (5.82 : ℝ) * 10 ^ 3 := by specificImpulse muonMaxEjection / raptorSpecificImp…` |
| `tauonicInputMax` | def | `: ℝ` |
| `tauonMaxEjection` | def | `: ℝ` |
| `tauonMaxEjection_sq` | theorem | `: tauonMaxEjection ^ 2 = tauonicInputMax ^ 2 * massRatioTauon ^ 3 := by tauonMaxEjection ^ 2 = tauonicInputMax ^ 2 * massRatioTauon ^ 3` |
| `tauonMaxEjection_bounds` | theorem | `: (4.2403 : ℝ) * 10 ^ 12 ≤ tauonMaxEjection ∧ tauonMaxEjection ≤ (4.2404 : ℝ) * 10 ^ 12 := by tauonMaxEjection ≤ (4.2404 : ℝ) * 10 ^ 12` |
| `tauonMaxEjection_superluminal` | theorem | `: speedOfLight < tauonMaxEjection` |
| `tauonicInputMax_subluminal` | theorem | `: tauonicInputMax < speedOfLight` |
| `sourceTauonMaxVelocity` | def | `: ℝ` |
| `sourceTauonMedianVelocity` | def | `: ℝ` |
| `source_tauon_max_velocity_underestimates` | theorem | `: (10.01 : ℝ) ≤ tauonMaxEjection ^ 2 / sourceTauonMaxVelocity ^ 2 ∧ tauonMaxEjection ^ 2 / sourceTauonMaxVelocity ^ 2 ≤ (10.02 : ℝ) := by tauonMaxEjection ^ 2 / sourceTauonMaxVelocity ^ 2 ≤ (10.02 : ℝ)` |
| `source_tauon_max_velocity_factor` | theorem | `: (3.164 : ℝ) ≤ tauonMaxEjection / sourceTauonMaxVelocity ∧ tauonMaxEjection / sourceTauonMaxVelocity ≤ (3.165 : ℝ) := by tauonMaxEjection / sourceTauonMaxVelocity ≤ (3.165 : ℝ)` |
| `tauonEntryEjection` | def | `: ℝ` |
| `tauonEntryEjection_bounds` | theorem | `: (1.4237 : ℝ) * 10 ^ 9 ≤ tauonEntryEjection ∧ tauonEntryEjection ≤ (1.4239 : ℝ) * 10 ^ 9 := by tauonEntryEjection ≤ (1.4239 : ℝ) * 10 ^ 9` |
| `tauonMedianEjection` | def | `: ℝ` |
| `tauonMedianEjection_bounds` | theorem | `: (2.8475 : ℝ) * 10 ^ 10 ≤ tauonMedianEjection ∧ tauonMedianEjection ≤ (2.8476 : ℝ) * 10 ^ 10 := by tauonMedianEjection ≤ (2.8476 : ℝ) * 10 ^ 10` |
| `amplification_mul` | theorem | `(r₁ r₂ : ℝ) : (r₁ * r₂) ^ velocityExponent = r₁ ^ velocityExponent * r₂ ^ velocityExponent := (r₁ * r₂) ^ velocityExponent = r₁ ^ velocityExponent * r₂ ^ velocityExponent` |
| `amplification_strictMono` | theorem | `: StrictMonoOn (fun r : ℝ => r ^ velocityExponent) (Set.Ioi 0) := by StrictMonoOn (fun r : ℝ => r ^ velocityExponent) (Set.Ioi 0)` |
| `tauon_amplification_factors` | theorem | `: tauonAmplification = muonAmplification * (massRatioTauon / massRatioMuon) ^ velocityExponent := by tauonAmplification = muonAmplification * (massRatioTauon / massRatioMuon) ^ velocityExponent` |
| `generalisedVelocity_ge_input` | theorem | `{n : ℕ} {v₂ r : ℝ} (hr : 1 ≤ r) : v₂ ≤ generalisedVelocity n v₂ r := by v₂ ≤ generalisedVelocity n v₂ r` |
| `one_le_massRatioMuon` | theorem | `: (1 : ℝ) ≤ massRatioMuon` |
| `one_le_massRatioTauon` | theorem | `: (1 : ℝ) ≤ massRatioTauon` |
| `PropulsiveRegime` | structure | `` |
| `amplification` | def | `(R : PropulsiveRegime) : ℝ` |
| `maxOutput` | def | `(R : PropulsiveRegime) : ℝ` |
| `window` | def | `(R : PropulsiveRegime) : Set ℝ` |
| `maxOutput_sq` | theorem | `(R : PropulsiveRegime) : R.maxOutput ^ 2 = R.inputUpper ^ 2 * R.massRatio ^ 3 := by R.maxOutput ^ 2 = R.inputUpper ^ 2 * R.massRatio ^ 3` |
| `inputUpper_le_maxOutput` | theorem | `(R : PropulsiveRegime) (h : 1 ≤ R.massRatio) : R.inputUpper ≤ R.maxOutput := R.inputUpper ≤ R.maxOutput` |
| `continuous_maxOutput` | theorem | `(R : PropulsiveRegime) : Continuous fun v₂ : ℝ => generalisedVelocity generalizedDimension v₂ R.massRatio := by Continuous fun v₂ : ℝ => generalisedVelocity generalizedDimension v₂ R.massRatio` |
| `continuous_in_massRatio` | theorem | `(R : PropulsiveRegime) (v₂ : ℝ) : Continuous fun r : ℝ => generalisedVelocity generalizedDimension v₂ r := by Continuous fun r : ℝ => generalisedVelocity generalizedDimension v₂ r` |
| `muonicRegime` | def | `: PropulsiveRegime` |
| `tauonicRegime` | def | `: PropulsiveRegime` |
| `muonicRegime_amplification` | theorem | `: muonicRegime.amplification = muonAmplification := by muonicRegime.amplification = muonAmplification` |
| `tauonicRegime_amplification` | theorem | `: tauonicRegime.amplification = tauonAmplification := by tauonicRegime.amplification = tauonAmplification` |
| `regimes_strictly_ordered` | theorem | `: muonicRegime.amplification < tauonicRegime.amplification := by muonicRegime.amplification < tauonicRegime.amplification` |
| `muonicRegime_maxOutput` | theorem | `: muonicRegime.maxOutput = muonMaxEjection` |
| `tauonicRegime_maxOutput` | theorem | `: tauonicRegime.maxOutput = tauonMaxEjection` |
| `windows_adjacent` | theorem | `: muonicRegime.inputUpper = tauonicRegime.inputLower` |
| `chain_closes` | theorem | `: tauonicRegime.inputUpper = muonicRegime.maxOutput` |
| `regimes_tile` | theorem | `: muonicRegime.window ∪ tauonicRegime.window = Set.Icc (0 : ℝ) tauonicRegime.inputUpper := by = Set.Icc (0 : ℝ) tauonicRegime.inputUpper` |
| `tauonic_window_nested_in_output` | theorem | `: tauonicRegime.window ⊆ Set.Ioc (0 : ℝ) muonicRegime.maxOutput := by tauonicRegime.window ⊆ Set.Ioc (0 : ℝ) muonicRegime.maxOutput` |
| `domainBoundary` | def | `: ℝ` |
| `domainBoundary_eq_muonic_output` | theorem | `: domainBoundary = muonicRegime.maxOutput` |
| `domainBoundary_km_per_s` | theorem | `: (2.068 : ℝ) * 10 ^ 4 ≤ domainBoundary / 1000 ∧ domainBoundary / 1000 ≤ (2.07 : ℝ) * 10 ^ 4 := by domainBoundary / 1000 ≤ (2.07 : ℝ) * 10 ^ 4` |
| `domainBoundary_subluminal` | theorem | `: domainBoundary < speedOfLight` |
| `regime_continuity` | theorem | `: muonicRegime.inputUpper = tauonicRegime.inputLower ∧ tauonicRegime.inputUpper = muonicRegime.maxOutput ∧ muonicRegime.window ∪ tauonicRegime.window = Set.Icc (0 : ℝ) tauonicRegime.inputUpper ∧ Continuous (fun v₂ : ℝ…` |
| `ThrusterDesign` | structure | `` |
| `raptorExhaustVelocity` | def | `: ℝ` |
| `thrust_to_power` | theorem | `(d : ThrusterDesign) : d.thrust / d.jetPower = 2 / d.exhaustVelocity := by d.thrust / d.jetPower = 2 / d.exhaustVelocity` |
| `thrust_eq_power` | theorem | `(d : ThrusterDesign) : d.thrust = 2 * d.jetPower / d.exhaustVelocity := by d.thrust = 2 * d.jetPower / d.exhaustVelocity` |
| `muonic_thrust_to_power_bounds` | theorem | `(d : ThrusterDesign) (h : d.exhaustVelocity = muonMaxEjection) : (96 : ℝ) / 10 ^ 9 ≤ d.thrust / d.jetPower ∧ d.thrust / d.jetPower ≤ (97 : ℝ) / 10 ^ 9 := by d.thrust / d.jetPower ≤ (97 : ℝ) / 10 ^ 9` |
| `muonic_thrust_to_power_shortfall` | theorem | `: (5.80 : ℝ) * 10 ^ 3 ≤ muonMaxEjection / raptorExhaustVelocity ∧ muonMaxEjection / raptorExhaustVelocity ≤ (5.82 : ℝ) * 10 ^ 3 := by muonMaxEjection / raptorExhaustVelocity ≤ (5.82 : ℝ) * 10 ^ 3` |
| `thrust_not_determined` | theorem | `(T : ℝ) (hT : 0 < T) : ∃ d : ThrusterDesign, d.exhaustVelocity = muonMaxEjection ∧ d.thrust = T := by ∃ d : ThrusterDesign, d.exhaustVelocity = muonMaxEjection ∧ d.thrust = T` |
| `ThrustOptimizationConjecture` | def | `(T P : ℝ) : Prop` |
| `thrust_optimization_satisfiable` | theorem | `(T : ℝ) (hT : 0 < T) : ThrustOptimizationConjecture T (T * muonMaxEjection / 2 + 1) := by ThrustOptimizationConjecture T (T * muonMaxEjection / 2 + 1)` |
| `thrust_optimization_is_empirical` | theorem | `(T P : ℝ) (hT : 0 < T) (hP : 0 < P) (hpower : T ≤ 2 * P / muonMaxEjection) : ThrustOptimizationConjecture T P := by ThrustOptimizationConjecture T P` |
