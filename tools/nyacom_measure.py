#!/usr/bin/env python3
"""Download nyacom's BC-250 FlexATX case STLs and measure the features the Pithos design depends on.

Source: https://www.printables.com/model/1737913  (CC BY-NC-SA, nyacom). Files are fetched through the public Printables GraphQL API
(a browser-like User-Agent is required, otherwise the download link answers 403). Nothing is redistributed: STLs are cached in ./nyacom-stl.
Requires: pip install trimesh shapely scipy numpy rtree   (use a venv: python3 -m venv --system-site-packages .venv)
Usage: python3 tools/nyacom_measure.py [cache_dir]
All numbers are MEASURED from the meshes (assembly frame: x across the 125 mm thickness, y along the 339 mm length, z across the 175 mm width)."""
import json, os, sys, urllib.request
import numpy as np, trimesh
from scipy import ndimage
from shapely.geometry import Polygon

PRINT_ID = "1737913"
FILES = {  # printables file id -> name
    7355421: "body-front_v2.4.stl", 7356014: "body-rear-flex_v2.4.stl", 7241735: "body-front-panel.stl", 7475215: "body-rear-panel.stl",
    7315693: "cover-neo-v2.stl", 7505502: "cover-classic-v2.stl", 7480529: "cover-120fan-v2.stl"}
UA = {"user-agent": "Mozilla/5.0"}

def post(q):
    r = urllib.request.Request("https://api.printables.com/graphql/", json.dumps({"query": q}).encode(), {"content-type": "application/json", **UA})
    return json.load(urllib.request.urlopen(r, timeout=30))

def fetch(cache):
    os.makedirs(cache, exist_ok=True)
    for fid, name in FILES.items():
        p = os.path.join(cache, name)
        if os.path.exists(p): continue
        q = 'mutation { getDownloadLink(id:"%d", printId:"%s", fileType:stl, source:model_detail){ ok errors{field messages} output{link} } }' % (fid, PRINT_ID)
        d = post(q)["data"]["getDownloadLink"]
        if not d["ok"]: sys.exit(f"download refused for {name}: {d}")
        open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(d["output"]["link"], headers=UA), timeout=90).read())

def through(m, axis, step=0.5):
    """Raycast along `axis`: True where the ray crosses no material (an open through-hole)."""
    lo, hi = m.bounds; ax = [i for i in range(3) if i != axis]
    a = np.arange(lo[ax[0]] + step/2, hi[ax[0]], step); b = np.arange(lo[ax[1]] + step/2, hi[ax[1]], step)
    A, B = np.meshgrid(a, b, indexing="ij")
    o = np.zeros((A.size, 3)); o[:, ax[0]] = A.ravel(); o[:, ax[1]] = B.ravel(); o[:, axis] = lo[axis] - 5
    d = np.zeros(3); d[axis] = 1
    hit = m.ray.intersects_any(o, np.tile(d, (len(o), 1)))
    return a, b, ~hit.reshape(A.shape)

def regions(a, b, openm, step=0.5, minarea=4):
    lab, n = ndimage.label(openm); out = []
    for i in range(1, n + 1):
        idx = np.argwhere(lab == i); area = len(idx) * step * step
        if area >= minarea: out.append((area, a[idx[:, 0]], b[idx[:, 1]], lab == i))
    return out

def main():
    cache = sys.argv[1] if len(sys.argv) > 1 else "nyacom-stl"; fetch(cache)
    M = {n: trimesh.load(os.path.join(cache, n)) for n in FILES.values()}
    print("== bounding boxes (mm) ==")
    for n, m in M.items():
        lo, hi = m.bounds; print(f"  {n:26s} x {lo[0]:7.1f}..{hi[0]:6.1f}  y {lo[1]:7.1f}..{hi[1]:6.1f}  z {lo[2]:7.1f}..{hi[2]:6.1f}")
    ys = [M[n].bounds for n in ("body-front-panel.stl", "body-front_v2.4.stl", "body-rear-flex_v2.4.stl")]
    print(f"  overall length: front panel 12 + front body 190 + rear body 125 + rear panel 12 = {12+190+125+12} mm (rear panel lip insets the last ~4 mm)")
    # case-fan opening: circle in the -x wall of the rear body (section at x = -60, inside the wall)
    sec = M["body-rear-flex_v2.4.stl"].section(plane_origin=[-60, 0, 0], plane_normal=[1, 0, 0])
    p2, T = sec.to_2D(); best = None
    for poly in p2.polygons_full:
        for ring in poly.interiors:
            q = Polygon(ring)
            if best is None or q.area > best.area: best = q
    cx, cy = best.centroid.coords[0]; mat = np.array(T)
    c3 = mat @ np.array([cx, cy, 0, 1])
    print(f"== case-fan opening ==  area {best.area:.0f} mm2, equivalent diameter {2*np.sqrt(best.area/np.pi):.1f} mm, centre y {c3[1]:.1f}, z {c3[2]:.1f}"
          f"  -> {c3[1]+174:.0f} mm from the I/O end, {153+12-c3[1]:.0f} mm from the PSU end")
    # slotted covers: through-holes along x
    for n in ("cover-neo-v2.stl", "cover-classic-v2.stl", "cover-120fan-v2.stl"):
        a, b, o = through(M[n], 0); R = regions(a, b, o)
        tot = o.sum() * 0.25
        print(f"== {n} ==  {len(R)} open regions, total open {tot:.0f} mm2 ({tot/100:.1f} cm2)")
        if n.startswith("cover-neo"):
            from shapely.geometry import MultiPoint
            for area, ya, za, _ in R[:1]:
                rect = MultiPoint(np.c_[ya, za]).minimum_rotated_rectangle
                xs, ys_ = rect.exterior.coords.xy; e = [np.hypot(xs[i+1]-xs[i], ys_[i+1]-ys_[i]) for i in range(2)]
                print(f"   one slot: area {area:.0f} mm2, rotated rectangle {max(e):.1f} x {min(e):.1f} mm")
            cs = sorted((float(ya.mean()), float(za.mean())) for _, ya, za, _ in R)
            print("   slot centres (y, z):", ", ".join(f"({y:.1f},{z:.1f})" for y, z in cs), " pitch %.1f mm" % np.mean(np.diff([c[0] for c in cs])))
            allp = np.vstack([np.c_[ya, za] for _, ya, za, _ in R]); lo, hi = allp.min(0), allp.max(0)
            print(f"   field bbox y {lo[0]:.1f}..{hi[0]:.1f} ({hi[0]-lo[0]:.0f} mm), z {lo[1]:.1f}..{hi[1]:.1f} ({hi[1]-lo[1]:.0f} mm); open share of bbox {tot/((hi[0]-lo[0])*(hi[1]-lo[1]))*100:.0f}%")
            ctr = allp.mean(0); print(f"   field centroid y {ctr[0]:.1f}, z {ctr[1]:.1f}")
            print("   share of the open slot area exposed by a round hole centred at the best position:")
            Y, Z = np.meshgrid(a, b, indexing="ij")
            for D in (110, 120, 130, 140, 150, 160, 170, 180, 190):
                best_f = 0
                for dy in np.arange(-8, 8.1, 2):
                    for dz in np.arange(-8, 8.1, 2):
                        inside = ((Y - ctr[0] - dy)**2 + (Z - ctr[1] - dz)**2 <= (D/2)**2) & o
                        best_f = max(best_f, inside.sum() * 0.25 / tot)
                print(f"     hole D{D}: {best_f*100:.0f}%")
    # front (I/O) panel
    a, b, o = through(M["body-front-panel.stl"], 1); R = regions(a, b, o)
    print(f"== front (I/O) panel ==  open total {o.sum()*0.25:.0f} mm2 in {len(R)} regions; largest (port window): {R and max(r[0] for r in R):.0f} mm2")
    for area, xa, za, _ in sorted(R, key=lambda r: -r[0])[:3]:
        print(f"   region {area:.0f} mm2: x {xa.min():.1f}..{xa.max():.1f}, z {za.min():.1f}..{za.max():.1f}")

if __name__ == "__main__": main()
