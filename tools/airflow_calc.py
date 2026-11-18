#!/usr/bin/env python3
"""Pithos single-unit airflow and fit estimate for the bottom-panel pull-fan design.
Geometry is MEASURED from nyacom's STL files (tools/nyacom_measure.py); fan numbers are Noctua datasheet values; the fan curve shape,
the discharge coefficient and every airflow/temperature result are ESTIMATES until the closed-case tissue and temperature tests are run.
Usage: python3 tools/airflow_calc.py"""
import math
RHO, RHO_CP, M3S_TO_CFM, CD = 1.2, 1.2 * 1005, 2118.88, 0.65   # CD: sharp-edged slot discharge coefficient [EST]
def cfm_needed(w, dT): return w / (RHO_CP * dT) * M3S_TO_CFM
def dT_for(w, cfm):    return w * 1.757 / cfm                     # kelvin rise at the exhaust, CFM = 1.757 W / dT

print("Heat load per unit (all wall power ends up as heat inside the case)")
LOADS = (("Bubo reading 112 W / 0.85 PSU efficiency", 112/0.85), ("sustained upper (HARDWARE doc)", 280), ("unlocked peak", 370))
for n, w in LOADS: print(f"  {n:45s} {w:4.0f} W  needs {cfm_needed(w,10):4.0f} CFM at +10 K, {cfm_needed(w,15):4.0f} CFM at +15 K")

# Open areas through the vent face (MEASURED, mm2). Round hole centred on the best spot, share of the cover's open area exposed.
COVERS = {   # name: {hole diameter mm: open mm2 through the hole}
  "neo (8 slanted 76x6 slots, supplied cover, 3588 mm2)": {110: 2592, 120: 2886, 130: 3089, 140: 3264, 190: 3588},
  "classic (about 115 holes, 8750 mm2)":                  {110: 5140, 120: 5790, 130: 6387, 140: 6924, 190: 8750},
}
# Noctua datasheets (noctua.at, Nov 17 2026): size mm, thick, CFM free air, mmH2O max static, dBA, W
FANS = {"NF-A14x25 G2 PWM": (140, 25, 91.58, 2.56, 24.8, 2.28, 130), "NF-A14 PWM": (140, 25, 82.52, 2.08, 24.6, 1.56, 130),
        "NF-A20 PWM": (200, 30, 86.46, 1.08, 18.1, 0.96, 190)}   # last = hole diameter that fits the frame

def operating_point(cfm_max, mmh2o, area_mm2, extra_k=0.0):
    """Linear fan curve P = Pmax (1 - Q/Qmax) against the slot-exit system curve P = rho/2 (Q/(CD A))^2 (1 + extra_k)."""
    pmax = mmh2o * 9.81; qmax = cfm_max / M3S_TO_CFM; a = area_mm2 * 1e-6
    k = RHO / 2 / (CD * a) ** 2 * (1 + extra_k)
    lo, hi = 0.0, qmax
    for _ in range(60):
        q = (lo + hi) / 2
        if pmax * (1 - q / qmax) > k * q * q: lo = q
        else: hi = q
    return q * M3S_TO_CFM, k * q * q / 9.81

print("\nPull fan alone through the vent face: operating point (slot-exit loss only, no case fan, no hood loss) [EST]")
print(f"{'fan / hole':34s}{'cover':9s}{'open cm2':>9s}{'CFM':>7s}{'mmH2O':>7s}{'+K at 132 W':>12s}{'+K at 280 W':>12s}")
for fn, (sz, th, cfm, mm, db, w, hole) in FANS.items():
    for cn, tab in COVERS.items():
        a = tab[hole] if hole in tab else None
        if a is None: continue
        q, p = operating_point(cfm, mm, a)
        print(f"{fn+', hole '+str(hole):34s}{cn.split()[0]:9s}{a/100:9.1f}{q:7.1f}{p:7.2f}{dT_for(112/.85,q):12.1f}{dT_for(280,q):12.1f}")
print("Recommended: NF-A14x25 G2 + 130 mm hole. NF-A20 loses on pressure (1.08 mmH2O); the 130 mm hole exposes 86% of the neo slot area.")
print("Series case fan: the nyacom P12 Pro case fan pushes through the same slots (curve UNVERIFIED), so the real total is higher than the pull fan alone.")

print("\nExternal hood outlet (2 open sides, 140 x 60 mm each) at 27 CFM")
a = 2 * 140 * 60e-6; v = 27 / M3S_TO_CFM / a; print(f"  {a*1e4:.0f} cm2, {v:.2f} m/s, {0.5*RHO*v*v:.2f} Pa (negligible)")
print("Intake windows: A 105 x 105 mm and B 80 x 80 mm behind 120 mm filter frames, 70% open [EST]")
for n, s in (("A", .105), ("B", .080)):
    a = s * s * .7; print(f"  window {n}: free area {a*1e4:.0f} cm2, face velocity at 40 CFM {40/M3S_TO_CFM/a:.2f} m/s")

print("\nFit: stack inside the base = nyacom 125 mm + 3 mm bumper pads = 128 mm; outside the panel = fan 25 + guard 4 + hood 60 = about 89 mm")
print("Length: interior length - nyacom (339 mm) - I/O clearance - PSU/AC clearance = spare. Minimum I/O 60 mm, PSU 55 mm; recommended 70-80 / 75-80 [EST plug sizes]")
CASESET = [("Apache 4800 (HF 64250), 454 x 327 x 168", 454, 327, 168), ("Apache 5800 (HF 64819), 514 x 289 x 144", 514, 289, 144),
           ("NANUK 935 (Canada), 521 x 287 x 191 (base 137)", 521, 287, 137)]
MIN_TOTAL, REC_TOTAL = 60 + 55, 80 + 95    # minimum and recommended I/O + PSU/AC end clearances
for n, L, W, H in CASESET:
    free = L - 339
    print(f"  {n:50s} free length {free} mm: margin over the minimum clearances {free-MIN_TOTAL:+d}, over the recommended {free-REC_TOTAL:+d}; "
          f"width strip beside the nyacom case {W-175} mm; stack 128 of {H} mm")
print("Mains at 120 V: sustained %.1f A, peak %.1f A (wall W as heat; PF ignored)" % (280/120, 370/120))
