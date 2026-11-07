"""Build index.html from tools/page.html: draw the figures, write the video transcript, fill the placeholders.

Usage: python tools/build_page.py
Reads tools/page.html, tools/narration.json and assets/video/chapters.json. Writes index.html at the site root.
Every figure has its English and Japanese labels side by side; the page shows one language at a time.
Every number in a label is the paper's (Maeda 2026, version 1.1). Figures 1 and 2 are drawings.
The curves of Figure 4 are the exact curves B = 0 of the paper's Eq. (10); the points are the grid points
of the paper's Sec. II A and Sec. VI a.
"""
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
W = 640  # width of every figure in SVG units


def esc(s):
    return html.escape(s, quote=True)


def t2(x, y, en, ja, cls="", anchor="start"):
    """One label in two languages: two text elements at the same place."""
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}"{a}{c} data-l="en" lang="en">{en}</text>'
            f'<text x="{x:.1f}" y="{y:.1f}"{a}{c} data-l="ja" lang="ja">{ja}</text>')


def t1(x, y, s, cls="", anchor="start"):
    """A label that is the same in both languages (numbers, symbols)."""
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}"{a}{c}>{s}</text>'


def tip(en, ja):
    """Hover text. site.js swaps it when the language changes."""
    return f'<title data-en="{esc(en)}" data-ja="{esc(ja)}">{esc(en)}</title>'


def figure(num, h, body, cap_en, cap_ja, aria_en, aria_ja):
    return (f'<figure class="fig">\n<div class="fig-scroll"><svg viewBox="0 0 {W} {h}" role="img" '
            f'aria-label="{esc(aria_en)}" data-aria-en="{esc(aria_en)}" data-aria-ja="{esc(aria_ja)}">'
            f'{body}</svg></div>\n<figcaption><span data-l="en" lang="en"><span class="fignum">Figure {num}.</span>'
            f'{cap_en}</span><span data-l="ja" lang="ja"><span class="fignum">図 {num}</span>'
            f'{cap_ja}</span></figcaption>\n</figure>')


def arrow_head(x, y, dx, dy, cls, size=9):
    """A filled triangle with its tip at (x, y), pointing along (dx, dy)."""
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    bx, by = x - ux * size, y - uy * size
    px, py = -uy * size * 0.55, ux * size * 0.55
    return (f'<path class="{cls}" d="M{x:.1f},{y:.1f} L{bx + px:.1f},{by + py:.1f} '
            f'L{bx - px:.1f},{by - py:.1f} Z"/>')


def wall_x(y, ym, h, half_mouth, half_throat):
    """Half width of the tunnel at height y: a catenary, narrowest at the throat (a drawing)."""
    a = h / math.acosh(half_mouth / half_throat)
    return half_throat * math.cosh((y - ym) / a)


def funnel(cx, ytop, ybot, half_mouth, half_throat):
    """Side view of a tunnel: two walls and the top and bottom mouths (a drawing)."""
    ym = (ytop + ybot) / 2
    h = ym - ytop
    s = []
    ys = [ytop + i * (ybot - ytop) / 80 for i in range(81)]
    for sgn in (-1, 1):
        pts = " L".join(f"{cx + sgn * wall_x(y, ym, h, half_mouth, half_throat):.1f},{y:.1f}" for y in ys)
        s.append(f'<path class="sheet" d="M{pts}"/>')
    s.append(f'<ellipse class="mouth" cx="{cx}" cy="{ytop}" rx="{half_mouth}" ry="7"/>')
    s.append(f'<ellipse class="mouth" cx="{cx}" cy="{ybot}" rx="{half_mouth}" ry="7"/>')
    return "".join(s), ym


# ---------------------------------------------------------------- Figure 1: a wormhole (a drawing)

def fig_wormhole():
    s = []
    yu, yl, cx, hm, ht = 52, 212, 300, 58, 14
    xf, xr = 96, 606
    # the two sheets of space, joined by a fold on the left (the long way round)
    s.append(f'<path class="sheet" d="M{cx - hm},{yu} H{xf} C{xf - 74},{yu} {xf - 74},{yl} {xf},{yl} H{cx - hm}"/>')
    s.append(f'<path class="sheet" d="M{cx + hm},{yu} H{xr}"/>')
    s.append(f'<path class="sheet" d="M{cx + hm},{yl} H{xr}"/>')
    walls, ym = funnel(cx, yu, yl, hm, ht)
    s.append(walls)
    s.append(f'<ellipse class="throat" cx="{cx}" cy="{ym}" rx="{ht}" ry="4"/>')
    ax, bx = 520, 520
    # the long way: along the top sheet, round the fold, back along the bottom sheet
    s.append(f'<path class="long-path" d="M{ax},{yu - 10} H{xf} C{xf - 92},{yu - 10} {xf - 92},{yl + 10} '
             f'{xf},{yl + 10} H{bx}"/>')
    # the short path: through the tunnel
    ys = [yu + i * (yl - yu) / 80 for i in range(81)]
    inner = " L".join(f"{cx + 0.45 * wall_x(y, ym, ym - yu, hm, ht):.1f},{y:.1f}" for y in ys)
    s.append(f'<path class="short-path" d="M{ax},{yu} L{inner} L{bx},{yl}"/>')
    s.append(f'<circle class="place dot" cx="{ax}" cy="{yu}" r="6"/>')
    s.append(f'<circle class="place dot" cx="{bx}" cy="{yl}" r="6"/>')
    s.append(t2(ax + 12, yu + 20, "here", "ここ", "ink bold"))
    s.append(t2(bx + 12, yl - 10, "there", "あそこ", "ink bold"))
    s.append(t2(392, ym - 6, "the short path,", "近道:", "ink", "start"))
    s.append(t2(392, ym + 11, "through the tunnel", "トンネルを通る", "", "start"))
    s.append(t2(108, ym - 22, "the long way,", "遠回り:", "ink", "start"))
    s.append(t2(108, ym - 5, "through ordinary space", "ふつうの空間を通る", "", "start"))
    s.append(f'<path class="leader" d="M{cx - ht - 6},{ym + 2} L218,{ym + 30}"/>')
    s.append(t2(212, ym + 44, "the throat", "喉", "ink bold", "end"))
    s.append(t2(212, ym + 60, "(the narrowest part)", "(いちばん細い所)", "small", "end"))
    return figure(
        1, 262, "".join(s),
        "A wormhole (a drawing, not a calculation). Space is drawn as two sheets that are far apart along ordinary "
        "space. The tunnel joins them by a short path. The narrowest part of the tunnel is the throat.",
        "ワームホール(計算ではなく絵)。空間を 2 枚の面として描きました。ふつうの空間を通ると、2 枚は遠く離れています。"
        "トンネルは、それらを近道でつなぎます。トンネルのいちばん細い所が喉です。",
        "Drawing: two sheets of space joined by a fold on the left. A tunnel joins 'here' on the top sheet to 'there' "
        "on the bottom sheet by a short path. The narrowest part of the tunnel is the throat.",
        "図: 左の折り返しでつながった 2 枚の空間の面。トンネルが、上の面の「ここ」と下の面の「あそこ」を近道でつなぐ。"
        "トンネルのいちばん細い所が喉。")


# ---------------------------------------------------------------- Figure 2: the three equations at the throat

def fig_three():
    s = []
    cx, yt, yb = 132, 26, 224
    walls, cy = funnel(cx, yt, yb, 62, 16)
    s.append(walls)
    # pull along the tunnel (rr): arrows up and down
    s.append(f'<path class="rr" d="M{cx},{cy - 10} V{yt + 26}"/>')
    s.append(arrow_head(cx, yt + 18, 0, -1, "rr-head", 11))
    s.append(f'<path class="rr" d="M{cx},{cy + 10} V{yb - 26}"/>')
    s.append(arrow_head(cx, yb - 18, 0, 1, "rr-head", 11))
    # pressure around the tunnel (theta-theta): a ring with an arrow
    s.append(f'<ellipse class="th" cx="{cx}" cy="{cy}" rx="44" ry="11"/>')
    s.append(arrow_head(cx + 30, cy + 8.2, 1, -0.25, "th-head", 10))
    # energy (tt): a glowing dot
    s.append(f'<circle class="tt-glow" cx="{cx}" cy="{cy}" r="15"/>')
    s.append(f'<circle class="tt" cx="{cx}" cy="{cy}" r="6.5"/>')
    tx = 248
    s.append(t2(tx, 34, "At the throat, Einstein's equations have three parts:", "喉で、アインシュタイン方程式には三つの部分があります。",
                "ink bold"))
    rows = (("tt", "energy", "エネルギー", "tt"),
            ("rr", "pull along the tunnel", "トンネルに沿った引っ張り", "rr"),
            ("th", "pressure around the tunnel", "トンネルを回る向きの圧力", "θθ"))
    for i, (k, en, ja, lab) in enumerate(rows):
        y = 72 + i * 34
        s.append(f'<circle class="{"tt" if k == "tt" else k + "-head"}" cx="{tx + 7}" cy="{y - 5}" r="6"/>')
        s.append(t2(tx + 22, y, f"{en} ({lab})", f"{ja}({lab})", f"big {k}-t"))
    bx = 520
    s.append(f'<path class="brace" d="M{bx},{58} q8,0 8,10 v24 q0,8 8,8 q-8,0 -8,8 v24 q0,10 -8,10"/>')
    s.append(t2(bx + 16, 104, "all three", "三つ", "big bold key-t"))
    s.append(t2(bx + 16, 122, "at once", "同時に", "big bold key-t"))
    s.append(t2(tx, 182, "each part: curvature of the shape = 8π × N × vacuum stress",
                "それぞれ: 形の曲がり = 8π × N × 真空の応力", ""))
    s.append(t2(tx, 202, "N: the number of identical copies of the field",
                "N: 同じ場の個数", "small"))
    return figure(
        2, 246, "".join(s),
        "The test at the throat (a drawing). Einstein's equations have three parts at the throat: one for the energy "
        "(tt), one for the pull along the tunnel (rr), and one for the pressure around the tunnel (θθ). "
        "A real throat needs all three at the same time.",
        "喉での試し(絵)。喉では、アインシュタイン方程式は三つの部分に分かれます。エネルギー(tt)、トンネルに沿った引っ張り(rr)、"
        "トンネルを回る向きの圧力(θθ)です。本当の喉には、三つが同時に要ります。",
        "Drawing of a tunnel with a dot at the throat for the energy, arrows along the tunnel for the pull, and a ring "
        "around the throat for the pressure. Text: a throat needs all three equations at once.",
        "図: トンネルの喉に、エネルギーを表す点、トンネルに沿った引っ張りを表す矢印、喉を回る圧力を表す輪。"
        "喉には三つの式が同時に要る。")


# ---------------------------------------------------------------- Figure 3: Layer 1, approximation and full value

def fig_bars():
    s = []
    approx = (-3.05, -4.55, -4.87)
    full = (7.55, 9.50, 8.03)
    y0, k = 150, 10.5  # zero line, pixels per unit of 1e-5
    x_groups = (120, 262, 404)
    bw = 44
    s.append(f'<path class="zero" d="M70,{y0} H486"/>')
    s.append(t1(64, y0 + 4, "0", "small", "end"))
    for i, xg in enumerate(x_groups):
        a, f = approx[i], full[i]
        xa, xf = xg - bw - 3, xg + 3
        s.append(f'<rect class="bar-approx" x="{xa}" y="{y0}" width="{bw}" height="{-a * k:.1f}">'
                 f'{tip(f"local approximation: {a:+.2f}", f"局所近似: {a:+.2f}")}</rect>')
        s.append(f'<rect class="bar-full" x="{xf}" y="{y0 - f * k:.1f}" width="{bw}" height="{f * k:.1f}">'
                 f'{tip(f"full value: {f:+.2f}", f"省かない値: {f:+.2f}")}</rect>')
        s.append(t1(xa + bw / 2, y0 - a * k + 15, f"{a:+.2f}".replace("-", "−"), "small", "middle"))
        s.append(t1(xf + bw / 2, y0 - f * k - 6, f"{f:+.2f}", "small ink", "middle"))
        s.append(t2(xg, 240, f"smooth throat {i + 1}", f"なめらかな喉 {i + 1}", "ink", "middle"))
        s.append(t1(xg, 256, f"(W{i + 1})", "small", "middle"))
    lx = 500
    s.append(t2(lx, y0 - 70, "above 0: a pressure", "0 より上: 圧力", "ink bold"))
    s.append(t2(lx, y0 - 53, "(not what a throat", "(喉に要るものでは", "small"))
    s.append(t2(lx, y0 - 39, "needs)", "ない)", "small"))
    s.append(t2(lx, y0 + 34, "below 0: a tension", "0 より下: 張力", "ink bold"))
    s.append(t2(lx, y0 + 51, "(the sign that a", "(喉に要る", "small"))
    s.append(t2(lx, y0 + 65, "throat needs)", "符号)", "small"))
    # key
    s.append(f'<rect class="bar-approx" x="72" y="14" width="14" height="12"/>')
    s.append(t2(92, 25, "local approximation only", "局所近似だけ", ""))
    s.append(f'<rect class="bar-full" x="270" y="14" width="14" height="12"/>')
    s.append(t2(290, 25, "full calculation", "省かない計算", "ink"))
    return figure(
        3, 268, "".join(s),
        "Layer 1: the radial stress at the throat (T<sup>r</sup><sub>r</sub>, in units of 10<sup>−5</sup> ħ/b<sub>0</sub><sup>4</sup>) "
        "on three smooth throats, with ℓ equal to the throat radius. The local approximation alone is negative: a tension, the sign that a throat needs. "
        "The full calculation is positive: a pressure. The numbers are the paper's.",
        "第 1 層: 喉での動径の向きの応力(T<sup>r</sup><sub>r</sub>、単位は 10<sup>−5</sup> ħ/b<sub>0</sub><sup>4</sup>)を、"
        "三つのなめらかな喉で比べます(ℓ は喉の半径と同じ)。局所近似だけだと負、つまり張力で、喉に要る符号です。"
        "省かない計算では正、つまり圧力です。数は論文のものです。",
        "Bar chart. Smooth throat 1: approximation −3.05, full +7.55. Throat 2: −4.55 and +9.50. "
        "Throat 3: −4.87 and +8.03. Units of 10 to the minus 5.",
        "棒グラフ。なめらかな喉 1: 近似 −3.05、省かない値 +7.55。喉 2: −4.55 と +9.50。喉 3: −4.87 と +8.03。単位は 10 のマイナス 5 乗。")


# ---------------------------------------------------------------- Figure 4: the sign of B in the plane of the two properties

def fig_plane():
    s = []
    bx0, bx1, px0, px1 = -3.5, 1.0, 74, 610
    fy0, fy1, py0, py1 = 6.5, -2.5, 16, 320

    def X(b):
        return px0 + (b - bx0) / (bx1 - bx0) * (px1 - px0)

    def Y(f):
        return py0 + (fy0 - f) / (fy0 - fy1) * (py1 - py0)

    def lower(b):
        return -(1 + b) / (1 - b)

    def upper(b):
        return (3 - b) / (1 - b)

    # B > 0 between the curves (shaded), clipped to the frame
    bs = [bx0 + i * (bx1 - bx0) / 400 for i in range(400)]
    top = [(X(b), Y(min(upper(b), fy0))) for b in bs]
    bot = [(X(b), Y(max(lower(b), fy1))) for b in reversed(bs)]
    pts = top + [(X(bx1), Y(fy0)), (X(bx1), Y(fy1))] + bot
    s.append('<path class="pos-zone" d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ' Z"/>')
    for b in (-3, -2, -1, 0, 1):
        s.append(f'<path class="grid" d="M{X(b):.1f},{py0} V{py1}"/>')
        s.append(t1(X(b), py1 + 18, f"{b}".replace("-", "−"), "small", "middle"))
    for f in (-2, 0, 2, 4, 6):
        s.append(f'<path class="grid" d="M{px0},{Y(f):.1f} H{px1}"/>')
        s.append(t1(px0 - 8, Y(f) + 4, f"{f}".replace("-", "−"), "small", "end"))
    s.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="none" class="grid"/>')
    for fn, lim in ((lower, None), (upper, None)):
        seg = []
        for b in bs + [bx1 - 1e-3]:
            f = fn(b)
            if fy1 <= f <= fy0:
                seg.append(f"{X(b):.1f},{Y(f):.1f}")
        s.append('<path class="curve0" d="M' + " L".join(seg) + '"/>')
    # points of the grids (paper Sec. II A and Sec. VI a)
    wb = [(b, 0.0) for b in (-1, -0.5, 0, 0.5, 0.75)] + [(b, 0.5) for b in (-1, -0.5, 0, 0.5, 0.75)] + \
         [(b, 1.5) for b in (-1, -0.5, 0, 0.5)]
    for b, f in wb:
        s.append(f'<circle class="pt-wb" cx="{X(b):.1f}" cy="{Y(f):.1f}" r="5.5"/>')
    face = []
    for b in (-0.5, -1, -2, -3):
        curve = 2 * b / (1 - b)
        face += [(b, -0.5), (b, curve), (b, curve - 0.5)]
    face.append((0, -1.5))
    for b, f in face:
        cls = "pt-face-open" if (b, f) == (-0.5, -0.5) else "pt-face"
        s.append(f'<rect class="{cls}" x="{X(b) - 5:.1f}" y="{Y(f) - 5:.1f}" width="10" height="10"/>')
    for b, f in ((-1, 3), (0, 4), (0.5, 6)):
        x, y = X(b), Y(f)
        s.append(f'<path class="pt-ctl" d="M{x:.1f},{y - 7:.1f} L{x + 6.5:.1f},{y + 5:.1f} L{x - 6.5:.1f},{y + 5:.1f} Z"/>')
    # labels
    s.append(t2(X(0.62), Y(2.35), "B &gt; 0", "B &gt; 0", "big bold ink", "middle"))
    s.append(t2(X(0.62), Y(2.35) + 16, "cap", "上限", "", "middle"))
    s.append(t2(X(-1.0), Y(-2.25), "B &lt; 0: floor", "B &lt; 0: 下限", "big bold ink", "middle"))
    s.append(t2(X(-2.2), Y(3.3), "B &lt; 0: floor", "B &lt; 0: 下限", "big bold ink", "middle"))
    s.append(t1(X(-3.35), Y(5.85), "B ∝ 4 − (1 − β)² (1 − Φ₁b₀)²", "ink"))
    # key
    kx, ky = X(-3.35), Y(5.0)
    s.append(f'<circle class="pt-wb" cx="{kx + 5:.1f}" cy="{ky:.1f}" r="5.5"/>')
    s.append(t2(kx + 16, ky + 4, "main family of Layer 2 (14 points)", "第 2 層の主な族(14 点)", "small"))
    s.append(f'<rect class="pt-face" x="{kx:.1f}" y="{ky + 13:.1f}" width="10" height="10"/>')
    s.append(t2(kx + 16, ky + 22, "Layer 3: 13 shapes on one face", "第 3 層: 一つの面の上の 13 の形", "small"))
    s.append(f'<path class="pt-ctl" d="M{kx + 5:.1f},{ky + 29:.1f} L{kx + 11.5:.1f},{ky + 41:.1f} L{kx - 1.5:.1f},{ky + 41:.1f} Z"/>')
    s.append(t2(kx + 16, ky + 40, "controls (3)", "対照(3)", "small"))
    s.append(t2((px0 + px1) / 2, py1 + 38, "β: how fast the tunnel opens out at the throat",
                "β: 喉でトンネルがどれだけ速く広がるか", "", "middle"))
    s.append(f'<text x="18" y="{(py0 + py1) / 2:.1f}" transform="rotate(-90 18 {(py0 + py1) / 2:.1f})" '
             f'text-anchor="middle" data-l="en" lang="en">Φ₁b₀: how fast the rate of clocks changes there</text>')
    s.append(f'<text x="18" y="{(py0 + py1) / 2:.1f}" transform="rotate(-90 18 {(py0 + py1) / 2:.1f})" '
             f'text-anchor="middle" data-l="ja" lang="ja">Φ₁b₀: そこで時計の進み方がどれだけ速く変わるか</text>')
    return figure(
        4, py1 + 50, "".join(s),
        "The sign of B in the plane of the two throat properties. The two curves are B = 0 (exact, from the paper's "
        "formula). B is positive between them (shaded) and negative outside. The points are the shapes of the paper's "
        "grids at their places in this plane. Not drawn: the four controls and the six shapes with B &gt; 0 outside "
        "the main family. The paper's own Figure 1 is in Section 12.",
        "二つの喉の性質を軸にした平面での、B の符号。二本の曲線は B = 0 です(論文の式からの正確な曲線)。"
        "曲線のあいだ(色の付いた所)で B は正、外で負です。点は、論文の格子の形を、この平面の上の位置に置いたものです。"
        "描いていないもの: 族の外の四つの対照と、主な族の外の B &gt; 0 の六つの形。論文自身の図 1 は 12 節にあります。",
        "Plane with beta from minus 3.5 to 1 across and Phi one b zero from minus 2.5 to 6.5 up. Two curves where B is "
        "zero bound a shaded band where B is positive. The 14 points of the main family lie inside the band; the 13 "
        "Layer 3 shapes lie below the lower curve; three controls lie above the upper curve.",
        "横に β(−3.5〜1)、縦に Φ₁b₀(−2.5〜6.5)の平面。B = 0 の二本の曲線のあいだの帯で B は正。主な族の 14 点は帯の中、"
        "第 3 層の 13 の形は下の曲線より下、三つの対照は上の曲線より上。")


# ---------------------------------------------------------------- Figure 5: sizes on a log axis

def fig_sizes():
    s = []
    lo, hi, x0, x1 = -3, 3, 40, 616

    def X(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)

    ya = 236
    s.append(f'<rect class="below-p" x="{x0}" y="18" width="{X(1) - x0:.1f}" height="{ya - 18}"/>')
    s.append(t2((x0 + X(1)) / 2, 34, "below the Planck length:", "プランク長さより下:", "small ink", "middle"))
    s.append(t2((x0 + X(1)) / 2, 48, "the calculation is not expected to apply", "計算は当てはまらないと考えられる",
                "small", "middle"))
    s.append(f'<rect class="window" x="{X(1):.1f}" y="18" width="{X(1000) - X(1):.1f}" height="{ya - 18}"/>')
    s.append(t2((X(1) + X(1000)) / 2, 34, "the window searched: 1 to 1,000 Planck lengths",
                "探した窓: プランク長さの 1〜1000 倍", "small ink", "middle"))
    # B > 0 row
    yp = 92
    s.append(t2(x0 + 4, yp - 22, "B &gt; 0 (21 shapes)", "B &gt; 0(21 の形)", "bold ink"))
    s.append(f'<rect class="cap-band" x="{X(0.0017):.1f}" y="{yp - 8}" width="{X(0.29) - X(0.0017):.1f}" height="16" rx="3">'
             f'{tip("caps: 0.0017 to 0.29 Planck lengths", "上限: プランク長さの 0.0017〜0.29 倍")}</rect>')
    s.append(f'<rect class="sol-band" x="{X(0.010):.1f}" y="{yp - 4}" width="{X(0.054) - X(0.010):.1f}" height="8" rx="2">'
             f'{tip("solutions of the pull equation, main family, N = 1: 0.010 to 0.054", "主な族、N = 1 での引っ張りの式の解: 0.010〜0.054")}</rect>')
    s.append(t2(X(0.29) + 8, yp - 2, "caps: 0.0017–0.29", "上限: 0.0017〜0.29", "small ink"))
    s.append(t2(X(0.29) + 8, yp + 12, "solutions (N = 1): 0.010–0.054", "解(N = 1): 0.010〜0.054", "small"))
    xm = X(0.052)
    s.append(f'<path class="mark" d="M{xm:.1f},{yp + 10} l6,10 h-12 Z"/>')
    s.append(f'<path class="leader" d="M{xm:.1f},{yp + 22} V{yp + 34}"/>')
    s.append(t2(xm, yp + 46, "≈ 0.05: the energy equation changes sign; the third equation fails",
                "≈ 0.05: エネルギーの式が符号を変える。三つ目の式は成り立たない", "small", "start"))
    # B < 0 row
    yn = 178
    s.append(t2(x0 + 4, yn - 22, "B &lt; 0 (13 shapes on one face)", "B &lt; 0(一つの面の上の 13 の形)", "bold ink"))
    s.append(f'<rect class="floor-band" x="{X(0.27):.1f}" y="{yn - 8}" width="{X(0.82) - X(0.27):.1f}" height="16" rx="3">'
             f'{tip("floors: 0.27 to 0.82 Planck lengths", "下限: プランク長さの 0.27〜0.82 倍")}</rect>')
    s.append(f'<rect class="pull-band" x="{X(0.82):.1f}" y="{yn - 4}" width="{X(1000) - X(0.82):.1f}" height="8" rx="2"/>')
    s.append(arrow_head(x1 - 2, yn, 1, 0, "rr-head", 10))
    s.append(t2(X(0.27) - 6, yn + 4, "floors: 0.27–0.82", "下限: 0.27〜0.82", "small ink", "end"))
    s.append(t2(X(1.25), yn - 10, "pull equation: solutions, N ≥ 59 to about 1,400", "引っ張りの式: 解あり、N ≥ 59〜約 1400",
                "small rr-t"))
    s.append(f'<path class="fail-line" d="M{X(1):.1f},{yn + 16} H{X(1000):.1f}"/>')
    s.append(t2(X(1.25), yn + 32, "energy equation: fails throughout the window", "エネルギーの式: 窓の全体で成り立たない",
                "small ink"))
    # axis
    s.append(f'<path class="axis" d="M{x0},{ya} H{x1}"/>')
    for e in range(lo, hi + 1):
        x = X(10 ** e)
        lab = {-3: "0.001", -2: "0.01", -1: "0.1", 0: "1", 1: "10", 2: "100", 3: "1,000"}[e]
        s.append(f'<path class="axis" d="M{x:.1f},{ya - 4} v8"/>')
        s.append(t1(x, ya + 18, lab, "small", "middle"))
    s.append(t2((x0 + x1) / 2, ya + 38, "throat radius, in Planck lengths (each step: ten times larger)",
                "喉の半径(プランク長さを単位に。一目盛りごとに 10 倍)", "small", "middle"))
    return figure(
        5, ya + 48, "".join(s),
        "Sizes, in Planck lengths, on a scale where each step is ten times larger. Top: where B is positive, every cap "
        "lies below the Planck length. Bottom: where B is negative, the pull equation has solutions over the whole "
        "window, but the energy equation fails there. The numbers are the paper's (ℓ = Planck length).",
        "大きさ(プランク長さを単位に、一目盛りごとに 10 倍)。上: B が正の側では、上限は全てプランク長さより下です。"
        "下: B が負の側では、引っ張りの式は窓の全体で解を持ちますが、そこでエネルギーの式が成り立ちません。"
        "数は論文のものです(ℓ = プランク長さ)。",
        "Log axis from 0.001 to 1,000 Planck lengths. Region below 1 is shaded. B positive: caps 0.0017 to 0.29, "
        "solutions 0.010 to 0.054. B negative: floors 0.27 to 0.82, pull-equation solutions up to 1,000 with 59 to "
        "about 1,400 copies, and the energy equation fails throughout the window from 1 to 1,000.",
        "0.001〜1000 プランク長さの対数の軸。1 より下は影。B が正: 上限 0.0017〜0.29、解 0.010〜0.054。"
        "B が負: 下限 0.27〜0.82、引っ張りの式の解は 1000 まで(場は 59〜約 1400 個)、エネルギーの式は 1〜1000 の窓の全体で成り立たない。")


# ---------------------------------------------------------------- transcript and page

def clock(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def transcript(script, chapters):
    starts = {c["id"]: c["start"] for c in chapters["chapters"]}
    out = ['<ol class="chapters">']
    for sc in script["scenes"]:
        t = starts[sc["id"]]
        mm = clock(t)
        en = " ".join(line["en"] for line in sc["lines"])
        ja = "".join(line["ja"] for line in sc["lines"])
        out.append(
            f'<li><button type="button" data-seek="{t}" aria-label="Play from {mm}" data-aria-en="Play from {mm}" '
            f'data-aria-ja="{mm} から再生">{mm}</button>'
            f'<h3><span data-l="en" lang="en">{esc(sc["title"])}</span>'
            f'<span data-l="ja" lang="ja">{esc(sc["title_ja"])}</span></h3>\n'
            f'<p data-l="en" lang="en">{esc(en)}</p>\n<p data-l="ja" lang="ja">{esc(ja)}</p></li>')
    out.append("</ol>")
    return "\n".join(out)


def main():
    page = (HERE / "page.html").read_text(encoding="utf-8")
    script = json.loads((HERE / "narration.json").read_text(encoding="utf-8"))
    chapters = json.loads((ROOT / "assets" / "video" / "chapters.json").read_text(encoding="utf-8"))
    total = round(chapters["duration"])
    head, body = page.split("</head>", 1)
    fill = {
        "{{DURATION_EN}}": f"{total // 60} min {total % 60} s",
        "{{DURATION_JA}}": f"{total // 60} 分 {total % 60} 秒",
        "{{TRANSCRIPT}}": transcript(script, chapters),
        "{{FIG_WORMHOLE}}": fig_wormhole(),
        "{{FIG_THREE}}": fig_three(),
        "{{FIG_BARS}}": fig_bars(),
        "{{FIG_PLANE}}": fig_plane(),
        "{{FIG_SIZES}}": fig_sizes(),
    }
    for k, v in fill.items():
        assert k in body, k
        body = body.replace(k, v)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", body)
    assert not left, left
    (ROOT / "index.html").write_text(head + "</head>" + body, encoding="utf-8")
    print(f"index.html {len(head + body) / 1000:.0f} kB")


if __name__ == "__main__":
    main()
