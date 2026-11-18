#!/usr/bin/env python3
"""Layout (plan) and airflow (section) SVGs for the single-case Pithos unit: bottom-panel pull-fan design.

The nyacom case is UNMODIFIED and its shared face (case-fan opening + slotted cover) is pressed flat against the INSIDE of the vented
bottom panel on thin 3 mm bumper pads (NOT a seal). NO internal shunt, hood or collar. The Noctua NF-A14x25 G2 pull fan is bolted to the
OUTER face of the panel over a round hole; slot area outside the hole is blocked by the panel. The ONLY shunt is a printed external hood
over the fan that sends the hot exhaust away from the intake windows. Case lies on its LID (panel UP) or stands upright (panel sideways).
Coordinates of the nyacom features come from the STL files (tools/nyacom_measure.py): envelope 175 x 125 x 339 mm, 118 mm case-fan opening at
265 mm from the I/O end, eight 76 x 6 mm slanted slots (neo cover) at 18 mm pitch. Board, PSU, adapters and printed parts are SCHEMATIC."""
import os, textwrap, math
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "diagrams")
BLUE, RED, ORG, GRN, GRY, BRN = "#1f6feb", "#d1242f", "#e07b00", "#1a7f37", "#6e7781", "#92400e"
NYL, NYW, NYT = 339, 175, 125          # nyacom length (x), width (y), thickness normal to the shared face (STL, measured)
# local x offsets inside the nyacom case, measured from the I/O end (front panel outer face) of the nyacom case
FRONT_PANEL, REAR_BODY0, REAR_PANEL0 = 12, 202, 327
FAN_C, FAN_D = 265.0, 118               # case-fan opening centre (x) and diameter, centred across the width (STL, measured)
SLOT_X0, SLOT_PITCH, SLOT_N = 43.5, 18, 8   # neo cover: slot centres at x = 43.5 + 18 k from the I/O end, across-width centre 110.5 (STL, measured)
SLOT_Y = 110.5                          # slot centre line measured from one long edge of the 175 mm width (mirror image possible)
SLOT_LEN, SLOT_WID, SLOT_ANG = 76.0, 6.0, 120.0   # each slot 76 x 6 mm, long axis 120 deg from the length axis (30 deg off the width axis)
SLOT_A, SLOT_B = 23, 190                # projected extent of the slot field along the length (167 mm)
HOLE_X, HOLE_Y = 106.5, 111.5           # best hole centre for the 130 mm hole (x from the I/O end, y across the width)
PAD = 3                              # thin 3 mm bumper pads between the nyacom face and the panel (vibration only, NOT a seal)
_clip = [0]

CASES = {
 "single": dict(L=514, W=289, H=144, S=1.25, name="Single unit: Apache 5800 (HF 64819)", fan="NF-A14x25 G2 PWM", fan_sz=140, fan_t=25, pad=0,
            hole=130, boards=[(6, 181)], x0=80, hood_h=60, seam=None, win_b=(195, 275, 185, 265)),
 "apache4800": dict(L=454, W=327, H=168, S=1.25, name="Single unit, tight alternative: Apache 4800 (HF 64250)", fan="NF-A14x25 G2 PWM", fan_sz=140, fan_t=25, pad=0,
            hole=130, boards=[(10, 185)], x0=60, hood_h=60, seam=None, win_b=(200, 290, 215, 305)),
}

def svg(w, h, body, title):
    mk = lambda i, c: (f'<marker id="{i}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{c}"/></marker>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="12">\n<title>{title}</title>\n<rect width="{w}" height="{h}" fill="#fff"/>\n'
            f'<defs>{mk("ab", BLUE)}{mk("ar", RED)}{mk("ao", ORG)}{mk("ag", GRN)}</defs>\n' + body + '\n</svg>\n')

def wrap_lines(items, width):
    out = []
    for t in items: out += textwrap.wrap(t, width) or [""]
    return out

class M:
    def __init__(s, x0, y0, S, L, flip=False): s.x0, s.y0, s.S, s.L, s.flip = x0, y0, S, L, flip
    def X(s, mm): return s.x0 + ((s.L - mm) if s.flip else mm) * s.S
    def Y(s, mm): return s.y0 + mm * s.S
    def rect(s, xa, xb, ya, yb, **kw):
        a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
        x1, x2 = sorted((s.X(xa), s.X(xb)))
        return f'<rect x="{x1:.1f}" y="{s.Y(ya):.1f}" width="{x2-x1:.1f}" height="{(yb-ya)*s.S:.1f}" {a}/>'
    def text(s, x, y, t, anchor="middle", size=11, fill="#24292f", weight="normal"):
        return f'<text x="{s.X(x):.1f}" y="{s.Y(y):.1f}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" font-weight="{weight}">{t}</text>'
    def line(s, xa, ya, xb, yb, color, marker=None, dash=None, width=2):
        m = f' marker-end="url(#{marker})"' if marker else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<line x1="{s.X(xa):.1f}" y1="{s.Y(ya):.1f}" x2="{s.X(xb):.1f}" y2="{s.Y(yb):.1f}" stroke="{color}" stroke-width="{width}"{m}{d}/>'
    def badge(s, x, y, n, color="#24292f"):
        return (f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="9" fill="#fff" stroke="{color}" stroke-width="1.5"/>'
                f'<text x="{s.X(x):.1f}" y="{s.Y(y)+4:.1f}" text-anchor="middle" font-size="11" font-weight="bold" fill="{color}">{n}</text>')

def geometry(p):
    """Per-board dict of coordinates (mm, floor plan: x along length, y across width)."""
    out = []
    for (ya, yb) in p["boards"]:
        yc = (ya + yb) / 2
        x0 = p["x0"]
        d = dict(ya=ya, yb=yb, yc=yc, x0=x0, x1=x0+NYL)
        d["fan_cx"] = x0 + HOLE_X; d["fan_cy"] = ya + HOLE_Y     # pull-fan / hole centre
        h = p["fan_sz"]/2
        d["frame"] = (d["fan_cx"]-h, d["fan_cx"]+h, d["fan_cy"]-h, d["fan_cy"]+h)
        d["hole"] = (d["fan_cx"]-p["hole"]/2, d["fan_cx"]+p["hole"]/2)
        d["win_a"] = (x0+FAN_C-52.5, x0+FAN_C+52.5, yc-52.5, yc+52.5)       # over the nyacom case-fan opening
        d["win_b"] = p["win_b"]
        out.append(d)
    return out

def slot_poly(c, d, k):
    cx = d["x0"] + SLOT_X0 + SLOT_PITCH*k; cy = d["ya"] + SLOT_Y
    a = math.radians(SLOT_ANG); ux, uy = math.cos(a), math.sin(a); vx, vy = -uy, ux
    pts = []
    for sl, sw in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        x = cx + sl*SLOT_LEN/2*ux + sw*SLOT_WID/2*vx; y = cy + sl*SLOT_LEN/2*uy + sw*SLOT_WID/2*vy
        pts.append(f"{c.X(x):.1f},{c.Y(y):.1f}")
    return " ".join(pts)

def plan(c, p, tag, cluster=False, title=True):
    L, W = p["L"], p["W"]
    o = [c.rect(0, L, 0, W, fill="#f6f8fa", stroke="#24292f", stroke_width=3)]
    G = geometry(p); d = G[0]; d0 = d
    S = c.S
    # nyacom footprint (docked on the panel, shared face down onto the panel)
    o.append(c.rect(d["x0"], d["x1"], d["ya"], d["yb"], fill="none", stroke=GRY, stroke_width=2, stroke_dasharray="3 3"))
    o.append(c.rect(d["x0"], d["x0"]+FRONT_PANEL, d["ya"]+8, d["yb"]-8, fill="#e5e7eb", stroke=GRY))
    o.append(c.rect(d["x0"]+FRONT_PANEL+6, d["x0"]+REAR_BODY0-6, d["ya"]+14, d["yb"]-14, fill="#e2e8f0", stroke="#475569", stroke_width=1.5))
    o.append(c.rect(d["x0"]+REAR_BODY0+4, d["x0"]+REAR_PANEL0-4, d["ya"]+14, d["yb"]-14, fill="#eef2ff", stroke=BLUE, stroke_width=1))
    o.append(c.rect(d["x0"]+215, d["x0"]+REAR_PANEL0, d["ya"]+50, d["yb"]-50, fill="none", stroke=BRN, stroke_width=1.5, stroke_dasharray="4 3"))
    # case-fan opening (measured: 118 mm circle, 265 mm from the I/O end, centred across the width)
    fcx, fcy = c.X(d["x0"]+FAN_C), c.Y(d["yc"])
    o.append(f'<circle cx="{fcx:.1f}" cy="{fcy:.1f}" r="{FAN_D/2*S:.1f}" fill="#dbeafe" fill-opacity="0.7" stroke="{BLUE}" stroke-width="1.5"/>')
    # slot field seen THROUGH the case: eight 76 x 6 mm slanted slots; grey = blocked by the panel, red = open through the hole
    _clip[0] += 1; cid = f"hole{_clip[0]}"
    hx, hy, hr = c.X(d["fan_cx"]), c.Y(d["fan_cy"]), p["hole"]/2*S
    o.append(f'<clipPath id="{cid}"><circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hr:.1f}"/></clipPath>')
    for k in range(SLOT_N):
        pts = slot_poly(c, d, k)
        o.append(f'<polygon points="{pts}" fill="#9ca3af" stroke="#4b5563" stroke-width="0.8"/>')
        o.append(f'<polygon points="{pts}" fill="#ef4444" stroke="none" clip-path="url(#{cid})"/>')
    o.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hr:.1f}" fill="none" stroke="{RED}" stroke-width="2.5"/>')
    # pull fan frame on the OUTER face of the panel (dashed) and hood outlets (-x toward the I/O end, -y toward the near wall)
    fa, fb, fy0, fy1 = d["frame"]
    o.append(c.rect(fa, fb, fy0, fy1, fill="none", stroke=RED, stroke_width=1.5, stroke_dasharray="2 3"))
    o.append(c.line(fa, d["fan_cy"], fa-26, d["fan_cy"], RED, marker="ar", width=3))
    o.append(c.line(d["fan_cx"], fy0, d["fan_cx"], fy0-24, RED, marker="ar", width=3))
    for w in ("win_a", "win_b"):
        xa, xb, ya_, yb_ = d[w]
        o.append(c.rect(xa, xb, ya_, yb_, fill="#dbeafe", fill_opacity="0.45", stroke=BLUE, stroke_width=2.5, stroke_dasharray="6 4"))
    o.append(c.text(d["x0"]+120, d["yc"]-48, "BC-250 + heatsink (schematic)", size=10, weight="bold"))
    o.append(c.text(d["x0"]+REAR_PANEL0-50, d["yc"]+4, "PSU (schematic)", size=9, fill=BRN))
    o.append(c.badge(d["x0"]+FAN_C, d["yc"]-30, 3, BLUE)); o.append(c.badge(d["fan_cx"]-40, d["fan_cy"]-60, 2, RED))
    o.append(c.badge(d["win_b"][0]+14, d["win_b"][2]+14, 4, BLUE))
    # cable clearances and hold-down brackets
    def dim(xa, xb, y, l1, l2):
        o.append(c.line(xa, y, xb, y, BRN, width=1.5))
        o.append(c.line(xa, y-4, xa, y+4, BRN, width=1.5)); o.append(c.line(xb, y-4, xb, y+4, BRN, width=1.5))
        o.append(c.text((xa+xb)/2, y-12, l1, size=9, fill=BRN)); o.append(c.text((xa+xb)/2, y-2, l2, size=9, fill=BRN, weight="bold"))
    dim(0, d["x0"], d["yc"]-40, "I/O end", f"{d['x0']:.0f} mm")
    dim(d["x1"], L, d["yc"]-40, "PSU/AC end", f"{L-d['x1']:.0f} mm")
    for hx_ in (d["x0"]+70, d["x0"]+230):
        o.append(c.rect(hx_, hx_+40, d["ya"]-5, d["ya"], fill="#d1d5db", stroke=GRY))
        o.append(c.rect(hx_, hx_+40, d["yb"], d["yb"]+5, fill="#d1d5db", stroke=GRY))
    o.append(c.badge(d["x0"]+FRONT_PANEL/2+3, d["ya"]+14, 1, "#24292f"))
    # I/O end wall (left) with the LAN jack; AC inlet on the long side wall at the PSU end
    o.append(c.rect(-14, 0, 40, W-40, fill="#fff7ed", stroke=ORG, stroke_width=2))
    o.append(f'<text x="{c.X(-8):.1f}" y="{c.Y(d["yc"])+4:.1f}" font-size="10" font-weight="bold" fill="{ORG}" text-anchor="end">LAN</text>')
    o.append(c.line(0, d["yc"], d["x0"], d["yc"], GRY, dash="6 3", width=1.5))
    acx, acy = L-35, W
    o.append(c.rect(L-50, L-20, W, W+14, fill="#fff7ed", stroke=ORG, stroke_width=2))
    o.append(f'<text x="{c.X(acx):.1f}" y="{c.Y(W)+26:.1f}" font-size="10" font-weight="bold" fill="{ORG}" text-anchor="middle">AC inlet</text>')
    o.append(c.badge(acx, W-16, 5, ORG))
    o.append(c.line(acx, acy, d["x1"], d["yc"], ORG, dash="5 3", width=1.5))
    if cluster:
        # Default 1G interlink uses the existing LAN jack (onboard 1G). No second jack in the default path.
        o.append(f'<text x="{c.X(-8):.1f}" y="{c.Y(d["yc"])+16:.1f}" font-size="8" font-weight="bold" fill="{GRN}" text-anchor="end">1G link</text>')
    return o, G

def legend_common(p):
    return ["1 nyacom case, UNMODIFIED (175 x 125 x 339 mm), its shared face pressed flat against the INSIDE of the vented panel on thin 3 mm bumper pads (NOT a seal). NO internal shunt, hood or collar. Grey brackets on the long sides are the hold-downs (never at the I/O or PSU end); brown dimensions are the cable clearances.",
            f"2 Pull fan {p['fan']} ({p['fan_sz']} mm), bolted to the OUTER face of the panel (frame dashed) over a round {p['hole']} mm hole (red circle). Eight 76 x 6 mm slanted slots: red = open through the hole, grey = blocked by the panel. Red arrows = outlets of the external deflector hood (toward the I/O end and the near wall), away from the intake windows.",
            "3 nyacom 118 mm case-fan opening (blue circle), under intake window A.   4 Intake windows: A 105 x 105 mm; B (cabin make-up) 80 x 80 mm; both behind 120 mm washable filters (blue dashed).",
            "5 ONE fused C14 AC inlet on the long side wall at the PSU end (keeps the PSU-end gap free for the C13 plug); orange dashed = mains to the PSU. Grey dashed = 1 GbE to the LAN jack."]

def plan_svg(key, fname):
    p = CASES[key]; pad = 56
    c = M(pad+14, 56, p["S"], p["L"])
    o, G = plan(c, p, key)
    w = int(p["L"]*p["S"] + 2*pad + 28)
    leg = wrap_lines(legend_common(p) + ["Slot field, case-fan opening and envelope are measured from nyacom's STL files (tools/nyacom_measure.py); board, PSU and printed parts are schematic. Seen from the lid side through the case, so the slot lean may be a mirror image of the real cover."], int((w-2*pad)/6.4)); h = int(p["W"]*p["S"] + 56 + 56 + 16*len(leg))
    o += [f'<text x="{pad}" y="{int(p["W"]*p["S"])+56+44+16*i}" font-size="12">{t}</text>' for i, t in enumerate(leg)]
    o.append(f'<text x="{(pad+14+p["L"]*p["S"]/2):.0f}" y="38" text-anchor="middle" font-size="13" font-weight="bold">{p["name"]}: floor plan from the lid side, looking at the panel inside (to scale)</text>')
    open(os.path.join(OUT, fname), "w").write(svg(w, h, "\n".join(o), f"Pithos {key} floor plan"))

def cluster_svg(fname):
    p = CASES["single"]; pad = 56; S = p["S"]*0.55
    w = int(2*p["L"]*S + 3*pad + 150)
    c1 = M(pad+14, 60, S, p["L"], flip=True); c2 = M(pad+14+p["L"]*S+150, 60, S, p["L"], flip=False)
    o1, G = plan(c1, p, "single", cluster=True, title=False); o2, _ = plan(c2, p, "single", cluster=True, title=False)
    o = o1 + o2
    o.append(f'<text x="{w/2:.0f}" y="24" text-anchor="middle" font-size="14" font-weight="bold">Two single units clustered (default 1G direct), floor plans to scale, I/O ends facing each other</text>')
    ya = c1.Y(G[0]["yc"])
    o.append(f'<line x1="{c1.X(-8):.1f}" y1="{ya:.1f}" x2="{c2.X(-8):.1f}" y2="{ya:.1f}" stroke="{GRN}" stroke-width="4"/>')
    o.append(f'<text x="{w/2:.0f}" y="{ya+22:.1f}" text-anchor="middle" font-size="11" fill="{GRN}" font-weight="bold">one Cat6 between the onboard 1G ports (via the LAN jacks)</text>')
    o.append(f'<text x="{w/2:.0f}" y="{ya+36:.1f}" text-anchor="middle" font-size="11" fill="{GRN}">1G direct link, RPC :50052; LAN via each board\'s Wi-Fi 7 adapter</text>')
    note = wrap_lines(["Each unit keeps its own AC inlet, bottom-panel pull fan and intake windows (the single-unit numbers apply per unit). The default cluster uses the onboard 1G ports; LAN is each board's Wi-Fi 7 adapter. Never run cluster traffic over Wi-Fi. USB 5GbE adapters are an optional upgrade. Keep 150 mm or more between units and 100 mm or more in front of each vented panel. Never stack one on the other."], 150)
    h = int(p["W"]*S + 60 + 60 + 16*len(note))
    o += [f'<text x="{pad}" y="{int(p["W"]*S)+60+44+16*i}" font-size="12">{t}</text>' for i, t in enumerate(note)]
    open(os.path.join(OUT, fname), "w").write(svg(w, h, "\n".join(o), "Pithos two single units clustered"))

def section_svg(key, fname, notes):
    p = CASES[key]; S = p["S"]; L, H = p["L"], p["H"]
    pad = 36; G = geometry(p)[0]
    PT = 5; FT = p["fan_t"]; GR = 4; HH = p["hood_h"]; OUTH = FT + GR + HH
    top = int(78 + (OUTH + PT)*S + 24)
    def Z(z): return top + z*S
    def X(x): return pad + x*S
    o = []
    o.append(f'<rect x="{X(0):.1f}" y="{Z(0):.1f}" width="{L*S:.1f}" height="{H*S:.1f}" fill="#f6f8fa" stroke="#24292f" stroke-width="3"/>')
    o.append(f'<text x="{pad}" y="22" text-anchor="start" font-size="13" font-weight="bold">{p["name"]}: section through window A, lying on its lid (panel up)</text>')
    fa, fb = G["hole"]; wa = G["win_a"]; wb = G["win_b"]
    def seg(a_, b_): return f'<rect x="{X(a_):.1f}" y="{Z(-PT):.1f}" width="{(b_-a_)*S:.1f}" height="{PT*S:.1f}" fill="#24292f"/>'
    cur = 0
    for a_, b_ in sorted([(fa, fb), (wa[0], wa[1])]):
        o.append(seg(cur, a_)); cur = b_
    o.append(seg(cur, L))
    o.append(f'<text x="{X(L)-4:.1f}" y="{Z(H)-8:.1f}" text-anchor="end" font-size="10" fill="{GRY}">top edge = vented bottom panel (faces up)</text>')
    # pull fan + guard + external deflector hood, all outside
    fh = p["fan_sz"]/2; fx0, fx1 = G["fan_cx"]-fh, G["fan_cx"]+fh
    o.append(f'<rect x="{X(fx0):.1f}" y="{Z(-PT-FT):.1f}" width="{(fx1-fx0)*S:.1f}" height="{FT*S:.1f}" fill="#fecaca" stroke="{RED}" stroke-width="1.5"/>')
    o.append(f'<text x="{X(G["fan_cx"]):.1f}" y="{Z(-PT-FT/2)+4:.1f}" text-anchor="middle" font-size="10">{p["fan_sz"]} mm pull fan, outer face</text>')
    o.append(f'<rect x="{X(fx0):.1f}" y="{Z(-PT-FT-GR):.1f}" width="{(fx1-fx0)*S:.1f}" height="{GR*S:.1f}" fill="#9ca3af" stroke="#4b5563"/>')
    ztop = -PT-OUTH
    o.append(f'<rect x="{X(fx0):.1f}" y="{Z(ztop):.1f}" width="{(fx1-fx0)*S:.1f}" height="{HH*S:.1f}" fill="#fef2f2" stroke="{RED}" stroke-width="2"/>')
    cxh = X(G["fan_cx"])
    o.append(f'<text x="{cxh:.1f}" y="{Z(ztop)+13:.1f}" text-anchor="middle" font-size="10" fill="{RED}">external deflector hood</text>')
    o.append(f'<text x="{cxh:.1f}" y="{Z(ztop)+25:.1f}" text-anchor="middle" font-size="10" fill="{RED}">(rain-shed, cap mount)</text>')
    o.append(f'<text x="{cxh:.1f}" y="{Z(ztop)+37:.1f}" text-anchor="middle" font-size="10" fill="{RED}">baffle walls toward the windows</text>')
    oy = Z(ztop)+HH*S-13; ox = cxh-60
    o.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="7" fill="#fff" stroke="{RED}" stroke-width="2"/><circle cx="{ox:.1f}" cy="{oy:.1f}" r="2.3" fill="{RED}"/>')
    o.append(f'<text x="{ox+12:.1f}" y="{oy+4:.1f}" font-size="10" fill="{RED}">outlet out of page (-y and -x)</text>')
    if True:
        o.append(f'<line x1="{X(fx0):.1f}" y1="{Z(ztop+HH*0.7):.1f}" x2="{X(fx0)-34:.1f}" y2="{Z(ztop+HH*0.7):.1f}" stroke="{RED}" stroke-width="3" marker-end="url(#ar)"/>')
    # thin bumper pads and the nyacom case, face pressed on the panel
    ny0 = PAD; ny1 = ny0 + NYT
    for px in (G["x0"]+20, G["x0"]+NYL-45):
        o.append(f'<rect x="{X(px):.1f}" y="{Z(0):.1f}" width="{25*S:.1f}" height="{PAD*S:.1f}" fill="#374151"/>')
    o.append(f'<path d="M{X(G["x0"]-30):.1f},{Z(1.5):.1f} L{X(G["x0"]+12):.1f},{Z(1.5):.1f}" stroke="{GRY}" stroke-width="2" stroke-dasharray="3 2" fill="none" marker-end="url(#ar)"/>')
    o.append(f'<rect x="{X(G["x0"]):.1f}" y="{Z(ny0):.1f}" width="{NYL*S:.1f}" height="{NYT*S:.1f}" fill="none" stroke="{GRY}" stroke-width="2" stroke-dasharray="3 3"/>')
    o.append(f'<rect x="{X(G["x0"]+REAR_BODY0+8):.1f}" y="{Z(ny0+2):.1f}" width="{(REAR_PANEL0-REAR_BODY0-16)*S:.1f}" height="{27*S:.1f}" fill="#bfdbfe" stroke="{BLUE}"/>')
    o.append(f'<text x="{X(G["x0"]+FAN_C):.1f}" y="{Z(ny0+17):.1f}" text-anchor="middle" font-size="10">case fan P12 Pro</text>')
    o.append(f'<rect x="{X(G["x0"]+FRONT_PANEL+6):.1f}" y="{Z(ny0+34):.1f}" width="{(REAR_BODY0-FRONT_PANEL-6+110)*S:.1f}" height="{52*S:.1f}" fill="#e2e8f0" stroke="#475569"/>')
    o.append(f'<text x="{X(G["x0"]+130):.1f}" y="{Z(ny0+62):.1f}" text-anchor="middle" font-size="10">BC-250 + stock heatsink</text>')
    o.append(f'<rect x="{X(G["x0"]+REAR_PANEL0-70):.1f}" y="{Z(ny0+70):.1f}" width="{66*S:.1f}" height="{40*S:.1f}" fill="#fde68a" stroke="{BRN}"/>')
    o.append(f'<text x="{X(G["x0"]+REAR_PANEL0-37):.1f}" y="{Z(ny0+92):.1f}" text-anchor="middle" font-size="10">PSU</text>')
    # slot field on the face: open part (inside the hole) red, blocked part grey
    sa, sb = G["x0"]+SLOT_A, G["x0"]+SLOT_B
    oa, ob = max(sa, fa), min(sb, fb)
    o.append(f'<line x1="{X(sa):.1f}" y1="{Z(ny0):.1f}" x2="{X(sb):.1f}" y2="{Z(ny0):.1f}" stroke="#6b7280" stroke-width="5"/>')
    o.append(f'<line x1="{X(oa):.1f}" y1="{Z(ny0):.1f}" x2="{X(ob):.1f}" y2="{Z(ny0):.1f}" stroke="{RED}" stroke-width="5"/>')
    o.append(f'<text x="{X(G["x0"]+SLOT_A+4):.1f}" y="{Z(ny0+14):.1f}" text-anchor="start" font-size="9" fill="#374151">slot field 167 mm (grey = blocked)</text>')
    # hold-down brackets: on the long sides (not in this section plane), clear of the I/O and PSU ends
    # cable clearance at the I/O end
    o.append(f'<line x1="{X(0):.1f}" y1="{Z(ny0+100):.1f}" x2="{X(G["x0"]):.1f}" y2="{Z(ny0+100):.1f}" stroke="{BRN}" stroke-width="1.5"/>')
    o.append(f'<text x="{X(G["x0"]/2):.1f}" y="{Z(ny0+100)-4:.1f}" text-anchor="middle" font-size="9" fill="{BRN}">I/O {G["x0"]:.0f} mm</text>')
    # dimensions: inside stack and outside protrusion
    dx = X(G["x0"]+NYL+16)
    stack = ny1
    o.append(f'<line x1="{dx:.1f}" y1="{Z(0):.1f}" x2="{dx:.1f}" y2="{Z(stack):.1f}" stroke="{BRN}" stroke-width="1.5"/>')
    o.append(f'<line x1="{dx-5:.1f}" y1="{Z(0):.1f}" x2="{dx+5:.1f}" y2="{Z(0):.1f}" stroke="{BRN}"/><line x1="{dx-5:.1f}" y1="{Z(stack):.1f}" x2="{dx+5:.1f}" y2="{Z(stack):.1f}" stroke="{BRN}"/>')
    o.append(f'<text x="{dx+6:.1f}" y="{Z(stack/2)+30:.1f}" font-size="10" fill="{BRN}">inside {stack:.0f} mm</text>')
    o.append(f'<text x="{dx+6:.1f}" y="{Z(stack/2)+42:.1f}" font-size="10" fill="{BRN}">of {H} mm</text>')
    ox2 = X(fx1+16)
    o.append(f'<line x1="{ox2:.1f}" y1="{Z(-PT):.1f}" x2="{ox2:.1f}" y2="{Z(ztop):.1f}" stroke="{BRN}" stroke-width="1.5"/>')
    o.append(f'<text x="{ox2+5:.1f}" y="{Z(ztop+HH/2)-30:.1f}" font-size="10" fill="{BRN}">outside</text><text x="{ox2+5:.1f}" y="{Z(ztop+HH/2)-18:.1f}" font-size="10" fill="{BRN}">+{OUTH+0:.0f} mm</text>')
    if p["seam"]:
        o.append(f'<line x1="{X(0):.1f}" y1="{Z(p["seam"]):.1f}" x2="{X(L):.1f}" y2="{Z(p["seam"]):.1f}" stroke="{GRY}" stroke-dasharray="8 4"/>')
        o.append(f'<text x="{X(4):.1f}" y="{Z(p["seam"])-4:.1f}" text-anchor="start" font-size="10" fill="{GRY}">lid / base seam (base {p["seam"]} mm, lid {H-p["seam"]} mm)</text>')
    # lid at the bottom with rubber feet
    o.append(f'<rect x="{X(0):.1f}" y="{Z(H):.1f}" width="{L*S:.1f}" height="{PT*S:.1f}" fill="#24292f"/>')
    for fx in (40, L-60):
        o.append(f'<rect x="{X(fx):.1f}" y="{Z(H)+PT*S:.1f}" width="{20*S:.1f}" height="{7*S:.1f}" fill="#374151"/>')
    o.append(f'<line x1="{X(0)-10:.1f}" y1="{Z(H)+PT*S+7*S:.1f}" x2="{X(L)+10:.1f}" y2="{Z(H)+PT*S+7*S:.1f}" stroke="{GRY}" stroke-width="2"/>')
    o.append(f'<text x="{X(L/2):.1f}" y="{Z(H)+PT*S+7*S+14:.1f}" text-anchor="middle" font-size="10" fill="{GRY}">protective rubber feet on the LID; the case rests on them (table or ground)</text>')
    # intake hoods (low, louvered) and transport caps
    def hood(xc, w_, color=BLUE):
        x0 = xc - w_/2
        o.append(f'<polygon points="{X(x0):.1f},{Z(-PT):.1f} {X(x0):.1f},{Z(-PT-26):.1f} {X(x0+w_):.1f},{Z(-PT-20):.1f} {X(x0+w_):.1f},{Z(-PT):.1f}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    hood((wa[0]+wa[1])/2, 115)
    o.append(f'<rect x="{X(fx0-2):.1f}" y="{Z(ztop-8):.1f}" width="{(fx1-fx0+4)*S:.1f}" height="{7*S:.1f}" fill="none" stroke="{ORG}" stroke-width="2" stroke-dasharray="5 3"/>')
    for xc in ((wa[0]+wa[1])/2,):
        o.append(f'<rect x="{X(xc-60):.1f}" y="{Z(-PT-26-8):.1f}" width="{120*S:.1f}" height="{6*S:.1f}" fill="none" stroke="{ORG}" stroke-width="2" stroke-dasharray="5 3"/>')
    o.append(f'<text x="{X(L/2):.1f}" y="{Z(ztop-12):.1f}" text-anchor="middle" font-size="10" fill="{ORG}">dashed orange: magnetic transport caps (fitted only when packed; reed interlock blocks power-on)</text>')
    # airflow arrows
    xa = (wa[0]+wa[1])/2; xb = (wb[0]+wb[1])/2
    for xm in (xa,):
        o.append(f'<line x1="{X(xm):.1f}" y1="{Z(-PT-40):.1f}" x2="{X(xm):.1f}" y2="{Z(-PT+10):.1f}" stroke="{BLUE}" stroke-width="3" marker-end="url(#ab)"/>')
        o.append(f'<text x="{X(xm):.1f}" y="{Z(-PT-56):.1f}" text-anchor="middle" font-size="11" fill="{BLUE}">cool air in</text>')
    o.append(f'<path d="M{X(xa):.1f},{Z(-PT+10):.1f} L{X(xa):.1f},{Z(ny0+10):.1f}" stroke="{BLUE}" stroke-width="2.5" fill="none" marker-end="url(#ab)"/>')
    o.append(f'<line x1="{X(xa):.1f}" y1="{Z(ny0+45):.1f}" x2="{X(G["x0"]+SLOT_B+20):.1f}" y2="{Z(ny0+45):.1f}" stroke="{ORG}" stroke-width="3" marker-end="url(#ao)"/>')
    o.append(f'<text x="{X(G["x0"]+150):.1f}" y="{Z(ny0+98):.1f}" text-anchor="middle" font-size="10" fill="{ORG}">case fan pushes air through the stock heatsink</text>')
    o.append(f'<path d="M{X(G["x0"]+SLOT_B-30):.1f},{Z(ny0+45):.1f} L{X(G["fan_cx"]+20):.1f},{Z(ny0+4):.1f}" stroke="{RED}" stroke-width="3" fill="none" marker-end="url(#ar)"/>')
    o.append(f'<line x1="{X(G["fan_cx"]):.1f}" y1="{Z(ny0+2):.1f}" x2="{X(G["fan_cx"]):.1f}" y2="{Z(-PT-FT-GR-6):.1f}" stroke="{RED}" stroke-width="3.5" marker-end="url(#ar)"/>')
    # footer notes
    w = int(L*S + 2*pad + 70)
    notes = wrap_lines(notes, int((w-2*pad)/6.4)); h = int(Z(H) + PT*S + 7*S + 38 + 16*len(notes))
    yy = int(Z(H) + PT*S + 7*S + 38)
    o += [f'<text x="{pad}" y="{yy+16*i}" font-size="12">{t}</text>' for i, t in enumerate(notes)]
    open(os.path.join(OUT, fname), "w").write(svg(w, h, "\n".join(o), f"Pithos {key} airflow section"))

section_svg("single", "single-airflow.svg", [
  "Estimates [EST] except the nyacom geometry (STL, measured). The eight 76 x 6 mm slots have only 35.9 cm2 of open area, so the slot exit is the main restriction; the Noctua NF-A14x25 G2 (91.6 CFM free air, 2.56 mmH2O) was chosen over the 200 mm NF-A20 (1.08 mmH2O) for its pressure. The 130 mm hole exposes about 86% of the open slot area.",
  "No internal shunt and no real seal: the nyacom face sits on thin 3 mm bumper pads against the inside of the panel, so the pull fan draws air out of the whole enclosure (case air, PSU heat) through the slots and the gaps, and make-up air leaks in through windows A and B. Dark pads under the case are the 3 mm bumpers; hold-down brackets sit on the long sides, out of this plane.",
  "Inside the base: 128 mm of 144 mm. Cable clearance: 80 mm at the I/O end, 95 mm at the PSU/AC end (Apache 5800). Outside the panel: fan 25 + guard 4 + hood 60 = about 89 mm; the hood's outlets face away from window A."])
plan_svg("single", "single-layout-top.svg"); plan_svg("apache4800", "single-layout-top-apache4800.svg"); cluster_svg("single-cluster-two-units-layout.svg")
print("ok")
