"""Manim scenes for the explainer video (Manim Community Edition 0.22).

Each scene reads the clip lengths in build/timing.json. A beat starts with
self.beat() and ends with self.done(), which waits until the line and a short
pause have played. The real start time of every beat is written to
build/marks/<scene>.json, and tools/assemble.py places the clips there, so the
voice stays in step with the picture even if an animation runs long.

The wormhole pictures and the curves of scene 7 are drawings. The numbers that
the narration says, the bars of scene 4, the two curves and the points of the
plane in scene 5, and the ranges of scenes 6 and 7 come from the paper
(Maeda 2026, version 1.1).

Render one scene:  manim render -r 1920,1080 --fps 30 tools/video.py S1
"""
import json
import math
from pathlib import Path

import numpy as np
from manim import *

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
TIMING = json.loads((BUILD / "timing.json").read_text(encoding="utf-8"))
GAP = 0.45  # pause after each line, in seconds

config.background_color = "#0e1014"
FONT = "CMU Serif"

C_SHEET = "#7FA7C9"   # space and the wormhole
C_KEY = "#F4D345"     # key statements, the short path
C_TT = "#FF9F43"      # energy equation (tt)
C_RR = "#83C167"      # pull along the tunnel (rr)
C_TH = "#58C4DD"      # pressure around the tunnel (theta-theta)
C_VAC = "#C58AE6"     # the quantum vacuum
C_POS = "#E8C11C"     # B > 0
C_NEG = "#B48EF0"     # B < 0
C_OK = "#83C167"
C_BAD = "#FC6255"
C_DIM = "#A3A9B1"
C_FAINT = "#5B616A"

TOP = 3.25           # y of scene headings; the bottom of the frame stays free for subtitles


def T(s, size=34, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def head(s):
    return T(s, 40).move_to([0, TOP, 0])


def note(s):
    """Small grey note in the top right corner (the bottom is kept free for subtitles)."""
    return T(s, 22, C_FAINT).to_corner(UR, buff=0.35)


def glow(point, color, r=0.12, layers=4, spread=0.8, alpha=0.07):
    g = VGroup()
    for i in range(layers, 0, -1):
        g.add(Dot(point, radius=r * (1 + spread * i), color=color, fill_opacity=alpha))
    g.add(Dot(point, radius=r, color=color))
    return g


def check(size=0.35, color=C_OK):
    p = VMobject(color=color, stroke_width=6)
    p.set_points_as_corners([[-0.5, 0, 0], [-0.15, -0.38, 0], [0.55, 0.45, 0]])
    return p.scale(size / 0.9)


def cross(size=0.3, color=C_BAD):
    a = Line([-1, -1, 0], [1, 1, 0], color=color, stroke_width=6)
    b = Line([-1, 1, 0], [1, -1, 0], color=color, stroke_width=6)
    return VGroup(a, b).scale(size / 2)


def box(mob, color=C_DIM, buff=0.22, r=0.12):
    return SurroundingRectangle(mob, color=color, buff=buff, corner_radius=r, stroke_width=2)


# ---------------------------------------------------------------- pictures (drawings, not data)

def funnel(cx=0.0, cy=0.0, h=1.7, w0=0.32, w1=0.85, color=C_SHEET, sw=3):
    """Side view of a wormhole tunnel: two walls, the two mouths, and the throat (a drawing)."""
    def off(t):
        return w0 + (w1 - w0) * (t / h) ** 2
    left = ParametricFunction(lambda t: [cx - off(t), cy + t, 0], t_range=[-h, h, 0.02], color=color,
                              stroke_width=sw)
    right = ParametricFunction(lambda t: [cx + off(t), cy + t, 0], t_range=[-h, h, 0.02], color=color,
                               stroke_width=sw)
    top = Ellipse(width=2 * w1, height=0.34, color=color, stroke_width=sw).move_to([cx, cy + h, 0])
    bot = Ellipse(width=2 * w1, height=0.34, color=color, stroke_width=sw, stroke_opacity=0.6).move_to(
        [cx, cy - h, 0])
    throat = Ellipse(width=2 * w0, height=0.13, color=C_KEY, stroke_width=sw + 1).move_to([cx, cy, 0])
    return VGroup(left, right, top, bot), throat


def folded_space(cx, h=1.7, w1=0.85, x_fold=-5.0, x_end=6.6, color=C_SHEET):
    """Two sheets of space joined by a fold on the left (a drawing)."""
    s = VGroup(
        Line([x_fold, h, 0], [cx - w1, h, 0], color=color, stroke_width=3),
        Line([cx + w1, h, 0], [x_end, h, 0], color=color, stroke_width=3),
        Line([x_fold, -h, 0], [cx - w1, -h, 0], color=color, stroke_width=3, stroke_opacity=0.6),
        Line([cx + w1, -h, 0], [x_end, -h, 0], color=color, stroke_width=3, stroke_opacity=0.6),
        Arc(radius=h, start_angle=PI / 2, angle=PI, arc_center=[x_fold, 0, 0], color=color, stroke_width=3),
    )
    return s


def flicker(dots, seed=1):
    """Give each dot a slow random flicker, like a picture of vacuum fluctuations (a drawing)."""
    rng = np.random.default_rng(seed)
    for d in dots:
        d.ph = rng.uniform(0, 2 * np.pi)
        d.w = rng.uniform(1.2, 3.0)
        d.tt = 0.0

        def upd(m, dt):
            m.tt += dt
            m.set_opacity(0.15 + 0.75 * abs(math.sin(m.w * m.tt + m.ph)))
        d.add_updater(upd)


def log_axis(lo, hi, x0, x1, y, labels, color=C_DIM, size=24):
    """A horizontal axis in powers of ten; returns (group, X) with X(value) -> x."""
    def X(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)
    g = VGroup(Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=2.5))
    for v, lab in labels:
        g.add(Line([X(v), y - 0.09, 0], [X(v), y + 0.09, 0], color=color, stroke_width=2.5))
        g.add(T(lab, size, color).move_to([X(v), y - 0.38, 0]))
    return g, X


class Beats(Scene):
    SID = None

    def setup(self):
        self.lines = TIMING[self.SID]
        self.k = -1
        self.marks = []
        self._note = None

    def set_note(self, s, at=None):
        """Show one small note (top right corner, or with its left edge at the point `at`);
        a new note replaces the old one, None removes it."""
        if self._note is not None:
            self.remove(self._note)
            self._note = None
        if s:
            if at is None:
                self._note = note(s)
            else:
                lines = s.split("\n")
                g = VGroup(*[T(x, 22, C_FAINT) for x in lines]).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
                self._note = g.move_to(at, aligned_edge=LEFT)
            self.add(self._note)

    def beat(self):
        self.k += 1
        self.t0 = self.renderer.time
        self.marks.append(round(self.t0, 4))

    def done(self, extra=0.0):
        end = self.t0 + self.lines[self.k]["dur"] + GAP + extra
        rem = end - self.renderer.time
        if rem < -0.05:
            print(f"[{self.SID} line {self.lines[self.k]['id']}] picture runs {-rem:.2f} s past the line")
        if rem > 1 / 30:
            self.wait(rem)

    def tear_down(self):
        assert len(self.marks) == len(self.lines), (self.SID, len(self.marks), len(self.lines))
        out = BUILD / "marks"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{self.SID}.json").write_text(
            json.dumps({"marks": self.marks, "end": round(self.renderer.time, 4)}), encoding="utf-8")

    def fade_all(self, run_time=0.6):
        mobs = [m for m in self.mobjects]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        for m in mobs:
            m.clear_updaters()
        self._note = None


# ---------------------------------------------------------------- 1. a tunnel through space

class S1(Beats):
    SID = "s1"

    def construct(self):
        # Title card (no voice); its frame at 2.4 s is the poster.
        t1 = T("Can the quantum vacuum alone", 60)
        t2 = T("hold a wormhole open?", 60).next_to(t1, DOWN, buff=0.25)
        sub = T("A plain-language guide to a 2026 research paper", 28, C_FAINT).next_to(t2, DOWN, buff=0.6)
        card = VGroup(t1, t2, sub).move_to(UP * 0.6)
        walls0, th0 = funnel(0, -2.25, h=0.75, w0=0.18, w1=0.55)
        self.play(FadeIn(VGroup(t1, t2), shift=UP * 0.2), Create(walls0), Create(th0), run_time=1.1)
        self.play(FadeIn(sub), run_time=0.6)
        self.wait(1.6)
        self.play(FadeOut(card), FadeOut(walls0), FadeOut(th0), run_time=0.6)

        cx, h = 2.4, 1.7
        sheets = folded_space(cx, h)
        walls, throat = funnel(cx, 0, h)
        A, B = np.array([4.7, h, 0]), np.array([4.7, -h, 0])
        da = Dot(A, color=WHITE, radius=0.09)
        db = Dot(B, color=WHITE, radius=0.09)
        la = T("here", 26, C_DIM).next_to(da, UP, buff=0.2)
        lb = T("there", 26, C_DIM).next_to(db, DOWN, buff=0.2)

        # 1.1 a tunnel through space joins two far places by a short path
        self.beat()
        self.play(Create(sheets), run_time=1.2)
        self.play(FadeIn(da), FadeIn(db), FadeIn(la), FadeIn(lb), run_time=0.5)
        long_path = VMobject(stroke_color=C_DIM, stroke_width=4)
        pts = [A + [0, 0.12, 0], [-5.0, h + 0.12, 0]]
        arc_pts = [[-5.0 + (h + 0.12) * math.cos(a), (h + 0.12) * math.sin(a), 0]
                   for a in np.linspace(PI / 2, 3 * PI / 2, 40)]
        pts = pts + arc_pts + [[-5.0, -h - 0.12, 0], B + [0, -0.12, 0]]
        long_path.set_points_as_corners(pts)
        long_d = DashedVMobject(long_path, num_dashes=70)
        ll = T("the long way", 26, C_DIM).move_to([-2.0, h + 0.5, 0])
        self.play(Create(long_d), FadeIn(ll), run_time=1.4)
        self.play(Create(walls), run_time=1.0)
        short = VMobject(stroke_color=C_KEY, stroke_width=6)
        short.set_points_smoothly([A, [cx + 0.9, h - 0.05, 0], [cx, h - 0.4, 0], [cx, 0, 0], [cx, -h + 0.4, 0],
                                   [cx + 0.9, -h + 0.05, 0], B])
        sl = T("a short path", 26, C_KEY).move_to([5.3, 0, 0])
        self.play(Create(short), FadeIn(sl), run_time=1.2)
        self.set_note("a drawing")
        self.done()

        # 1.2 Einstein's theory allows such shapes; the narrowest part is the throat
        self.beat()
        self.play(Create(throat), run_time=0.6)
        tl = T("throat", 30, C_KEY).move_to([cx - 1.55, 0, 0])
        ta = Arrow(tl.get_right(), [cx - 0.36, 0, 0], buff=0.1, color=C_KEY, stroke_width=4, tip_length=0.18)
        self.play(FadeIn(tl), GrowArrow(ta), run_time=0.7)
        self.done()

        # 1.3 a throat does not stay open by itself
        self.beat()
        thin, th_thin = funnel(cx, 0, h, w0=0.04)
        wide, th_wide = funnel(cx, 0, h)
        self.play(FadeOut(short), FadeOut(sl), run_time=0.4)
        self.play(Transform(walls, thin), Transform(throat, th_thin), run_time=1.0)
        self.play(Transform(walls, wide), Transform(throat, th_wide), run_time=1.0)
        q = T("?", 56, C_KEY).move_to([cx + 0.95, 0, 0])
        self.play(FadeIn(q, scale=0.6), run_time=0.4)
        self.done()

        # 1.4 a 2026 paper asks one narrow question
        self.beat()
        pic = VGroup(sheets, walls, throat, da, db, la, lb, long_d, ll, tl, ta, q)
        self.set_note(None)
        self.play(pic.animate.fade(0.85), run_time=0.6)
        p1 = T("A 2026 research paper asks one narrow question:", 36).move_to([0, 0.9, 0])
        self.play(FadeIn(p1, shift=UP * 0.15), run_time=0.8)
        self.done()

        # 1.5 the question
        self.beat()
        q1 = T("Can the quantum vacuum alone", 50, C_KEY).next_to(p1, DOWN, buff=0.5)
        q2 = T("hold a wormhole throat open?", 50, C_KEY).next_to(q1, DOWN, buff=0.2)
        self.play(FadeIn(q1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(q2, shift=UP * 0.15), run_time=0.7)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 2. what could hold a throat open

class S2(Beats):
    SID = "s2"

    def construct(self):
        self.play(FadeIn(head("What could hold a throat open")), run_time=0.5)
        cx = -4.3
        walls, throat = funnel(cx, -0.3, h=2.0, w0=0.42, w1=1.15)

        # 2.1 Morris and Thorne (1988): the source needs a property ordinary matter does not have
        self.beat()
        self.play(Create(walls), Create(throat), run_time=1.0)
        src = glow([cx, -0.3, 0], C_KEY, r=0.1, layers=4, spread=0.9)
        self.play(FadeIn(src), run_time=0.5)
        a1 = T("Morris and Thorne, 1988:", 30, C_DIM).move_to([1.9, 1.75, 0])
        a2 = T("at the throat, the source needs a property", 32).next_to(a1, DOWN, buff=0.35)
        a3 = T("that ordinary matter does not have", 32).next_to(a2, DOWN, buff=0.12)
        self.play(FadeIn(a1), run_time=0.4)
        self.play(FadeIn(a2), FadeIn(a3), run_time=0.8)
        self.done()

        # 2.2 null energy condition, exotic
        self.beat()
        b1 = T("it must violate the null energy condition", 30, C_KEY).next_to(a3, DOWN, buff=0.6)
        b2 = T("an “exotic” source", 34, C_KEY).next_to(b1, DOWN, buff=0.3)
        self.play(FadeIn(b1), run_time=0.7)
        self.play(FadeIn(b2, scale=0.9), run_time=0.6)
        self.done()

        # 2.3 the vacuum is not empty; in curved spacetime it carries energy and pressure
        self.beat()
        self.play(FadeOut(VGroup(a1, a2, a3, b1, b2)), run_time=0.5)
        rng = np.random.default_rng(5)
        dots = VGroup(*[Dot([rng.uniform(-1.6, 6.4), rng.uniform(-1.7, 1.5), 0], radius=0.05, color=C_DIM)
                        for _ in range(140)])
        flicker(dots, 2)
        v1 = T("the vacuum is not completely empty", 32).move_to([2.0, 2.35, 0])
        self.play(FadeIn(dots), FadeIn(v1), run_time=1.0)
        v2 = T("in curved spacetime it carries a small energy and pressure", 24, C_DIM).next_to(v1, DOWN,
                                                                                               buff=0.2)
        self.play(FadeIn(v2), run_time=0.7)
        self.set_note("a picture")
        self.done()

        # 2.4 in some places it can have the unusual sign: the standard candidate
        self.beat()
        some = [d for i, d in enumerate(dots) if i % 4 == 0]
        self.play(*[d.animate.set_color(C_VAC) for d in some], run_time=0.8)
        c1 = T("in some places: the unusual sign", 30, C_VAC).move_to([2.4, -2.45, 0])
        self.play(FadeIn(c1), run_time=0.5)
        self.play(src.animate.set_color(C_VAC), throat.animate.set_color(C_VAC), run_time=0.6)
        c2 = T("the standard candidate", 30, C_VAC).next_to(walls, DOWN, buff=0.3)
        self.play(FadeIn(c2), run_time=0.5)
        self.done()

        # 2.5 semiclassical: classical shape, vacuum stress as source, through Einstein's equations
        self.beat()
        for d in dots:
            d.clear_updaters()
        self.set_note(None)
        self.play(FadeOut(VGroup(dots, v1, v2, c1, c2, walls, throat, src)), run_time=0.6)
        lhs = VGroup(T("shape of spacetime", 34), T("(classical)", 26, C_DIM)).arrange(DOWN, buff=0.15)
        rhs = VGroup(T("stress of the vacuum", 34, C_VAC), T("(quantum, averaged)", 26, C_DIM)).arrange(
            DOWN, buff=0.15)
        eq = T("=  8π ×", 40)
        row = VGroup(lhs, eq, rhs).arrange(RIGHT, buff=0.5).move_to([0, 0.1, 0])
        bl, br = box(lhs, C_SHEET), box(rhs, C_VAC)
        cap = T("Einstein's equations, semiclassical form", 30, C_KEY).next_to(row, UP, buff=0.8)
        self.play(FadeIn(lhs), Create(bl), run_time=0.7)
        self.play(FadeIn(eq), FadeIn(rhs), Create(br), run_time=0.8)
        self.play(FadeIn(cap), run_time=0.5)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 3. the test

class S3(Beats):
    SID = "s3"

    def construct(self):
        self.play(FadeIn(head("The test")), run_time=0.5)
        cx, cy = -4.4, -0.35
        walls, throat = funnel(cx, cy, h=2.0, w0=0.45, w1=1.15, color=C_DIM)

        # 3.1 a fixed throat shape, tested
        self.beat()
        self.play(Create(walls), Create(throat), run_time=1.0)
        fl = T("a fixed shape", 30, C_DIM).next_to(walls, DOWN, buff=0.35)
        self.play(FadeIn(fl), run_time=0.4)
        n1 = T("not built: tested", 34, C_KEY).move_to([2.2, 1.9, 0])
        self.play(FadeIn(n1), run_time=0.6)
        self.done()

        # 3.2 one kind of field
        self.beat()
        f1 = T("one quantum field:", 30, C_DIM).move_to([2.2, 1.05, 0])
        f2 = T("massless scalar, conformal coupling", 32).next_to(f1, DOWN, buff=0.2)
        f3 = T("state: the static vacuum", 32).next_to(f2, DOWN, buff=0.2)
        self.play(FadeIn(f1), FadeIn(f2), run_time=0.8)
        self.play(FadeIn(f3), run_time=0.6)
        self.done()

        # 3.3 the full vacuum stress at the throat: a long numerical calculation
        self.beat()
        waves = VGroup()
        for i in range(7):
            k = 2.0 + 1.1 * i
            y0 = -1.9 + 0.62 * i
            w = ParametricFunction(
                lambda t, k=k, y0=y0: [6.2 - t * (6.2 - cx), y0 + (cy - y0) * t + 0.12 * (1 - t) * math.sin(
                    k * 6 * t), 0], t_range=[0, 0.98, 0.005], color=C_VAC, stroke_width=2, stroke_opacity=0.7)
            waves.add(w)
        self.play(FadeOut(VGroup(n1, f1, f2, f3)), run_time=0.4)
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.12), run_time=1.6)
        g = glow([cx, cy, 0], C_VAC, r=0.12, layers=4, spread=0.9)
        self.play(FadeIn(g), throat.animate.set_color(C_VAC), run_time=0.5)
        m1 = T("the full vacuum stress at the throat", 32, C_VAC).move_to([2.0, 2.4, 0])
        m2 = T("(a long numerical calculation)", 26, C_DIM).next_to(m1, DOWN, buff=0.15)
        self.play(FadeIn(m1), FadeIn(m2), run_time=0.6)
        self.done()

        # 3.4 three equations, one for each direction
        self.beat()
        self.play(FadeOut(waves), FadeOut(m1), FadeOut(m2), run_time=0.5)
        e0 = T("At the throat, can Einstein's equations hold?", 32).move_to([2.0, 2.3, 0])
        e1 = T("three equations, one for each direction", 28, C_DIM).next_to(e0, DOWN, buff=0.2)
        self.play(FadeIn(e0), run_time=0.5)
        self.play(FadeIn(e1), run_time=0.5)
        self.done()

        # 3.5 energy, pull along the tunnel, pressure around it; all three at the same time
        self.beat()
        en = glow([cx, cy, 0], C_TT, r=0.12, layers=4, spread=0.9)
        up = Arrow([cx, cy + 0.15, 0], [cx, cy + 1.35, 0], buff=0, color=C_RR, stroke_width=6,
                   max_tip_length_to_length_ratio=0.2)
        dn = Arrow([cx, cy - 0.15, 0], [cx, cy - 1.35, 0], buff=0, color=C_RR, stroke_width=6,
                   max_tip_length_to_length_ratio=0.2)
        ring = Ellipse(width=1.6, height=0.42, color=C_TH, stroke_width=5).move_to([cx, cy, 0])
        rarr = Arrow([cx + 0.3, cy - 0.2, 0], [cx + 0.72, cy - 0.06, 0], buff=0, color=C_TH, stroke_width=5,
                     max_tip_length_to_length_ratio=0.5)
        self.play(FadeOut(g), FadeIn(en), run_time=0.4)
        rows = VGroup(
            VGroup(Dot(color=C_TT, radius=0.1), T("energy", 30, C_TT)).arrange(RIGHT, buff=0.25),
            VGroup(Dot(color=C_RR, radius=0.1), T("pull along the tunnel", 30, C_RR)).arrange(RIGHT, buff=0.25),
            VGroup(Dot(color=C_TH, radius=0.1), T("pressure around it", 30, C_TH)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, buff=0.38, aligned_edge=LEFT).move_to([0.6, 0.2, 0])
        self.play(FadeIn(rows[0]), run_time=0.4)
        self.play(GrowArrow(up), GrowArrow(dn), FadeIn(rows[1]), run_time=0.6)
        self.play(Create(ring), GrowArrow(rarr), FadeIn(rows[2]), run_time=0.6)
        br = Brace(rows, RIGHT, color=C_KEY)
        al = T("all three at once", 30, C_KEY).next_to(br, RIGHT, buff=0.2)
        self.play(GrowFromCenter(br), FadeIn(al), run_time=0.6)
        self.done()

        # 3.6 N identical copies of the field
        self.beat()
        nn = T("× N identical copies of the field", 30).move_to([2.0, -1.55, 0])
        self.play(FadeIn(nn), run_time=0.6)
        self.done()

        # 3.7 one free length, set to the Planck length
        self.beat()
        self.play(FadeOut(VGroup(e0, e1, rows, br, al, nn)), run_time=0.5)
        l1 = T("one free length, ℓ", 34).move_to([2.0, 1.4, 0])
        l2 = T("ℓ = the Planck length ≈ 1.6 × 10⁻³⁵ m", 34, C_KEY).next_to(l1, DOWN, buff=0.35)
        self.play(FadeIn(l1), run_time=0.5)
        self.play(FadeIn(l2), run_time=0.6)
        self.done()

        # 3.8 throat radius from 1 to 1,000 Planck lengths; 42 fixed shapes
        self.beat()
        ax, X = log_axis(0, 3, -0.3, 5.6, -0.4, [(1, "1"), (10, "10"), (100, "100"), (1000, "1000")])
        win = Rectangle(width=X(1000) - X(1), height=0.32, stroke_width=0, fill_color=C_KEY,
                        fill_opacity=0.35).move_to([(X(1) + X(1000)) / 2, -0.4, 0])
        axl = T("throat radius, in Planck lengths", 26, C_DIM).move_to([2.65, -1.35, 0])
        self.play(Create(ax), FadeIn(axl), run_time=0.8)
        self.play(FadeIn(win), run_time=0.5)
        grid = VGroup(*[Dot(radius=0.06, color=C_DIM) for _ in range(42)]).arrange_in_grid(3, 14, buff=0.18)
        grid.move_to([2.65, -2.3, 0])
        gl = T("42 fixed shapes", 28).next_to(grid, LEFT, buff=0.35)
        self.play(LaggedStart(*[FadeIn(d) for d in grid], lag_ratio=0.02), FadeIn(gl), run_time=1.0)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 4. an approximation and the full answer

class S4(Beats):
    SID = "s4"

    def construct(self):
        self.play(FadeIn(head("An approximation and the full answer")), run_time=0.5)
        y0, k = -0.1, 0.2          # zero line and scale (scene units per 10⁻⁵ ħ/b₀⁴)
        xs = [-1.2, 1.4, 4.0]
        approx = [-3.05, -4.55, -4.87]
        full = [7.55, 9.50, 8.03]

        # 4.1 three smooth throats: an older approximation and the full calculation
        self.beat()
        zero = Line([-2.0, y0, 0], [5.6, y0, 0], color=C_DIM, stroke_width=2)
        names = VGroup(*[T(n, 26, C_DIM).move_to([x + 0.35, -1.75, 0])
                         for n, x in zip(["throat W1", "throat W2", "throat W3"], xs)])
        self.play(Create(zero), FadeIn(names), run_time=0.9)
        unit = T("radial stress at the throat (units of 10⁻⁵ ħ/b₀⁴)", 22, C_FAINT).move_to([0, 2.7, 0])
        self.play(FadeIn(unit), run_time=0.4)
        self.done()

        # 4.2 the approximation keeps a local part; it has the sign a throat needs (tension)
        self.beat()
        bars_a = VGroup()
        for x, v in zip(xs, approx):
            r = Rectangle(width=0.62, height=abs(v) * k, stroke_width=0, fill_color=C_TT, fill_opacity=0.9)
            r.move_to([x, y0 - abs(v) * k / 2, 0])
            bars_a.add(r)
        vals_a = VGroup(*[T(f"{v:+.2f}".replace("-", "−"), 22, C_TT).next_to(b, DOWN, buff=0.08)
                          for b, v in zip(bars_a, approx)])
        self.play(LaggedStart(*[GrowFromEdge(b, UP) for b in bars_a], lag_ratio=0.2), run_time=1.0)
        self.play(FadeIn(vals_a), run_time=0.4)
        la = T("local part only (the approximation)", 26, C_TT).move_to([-3.2, -2.4, 0])
        ten = T("below zero: tension, what a throat needs", 24, C_DIM).move_to([3.4, -2.4, 0])
        self.play(FadeIn(la), FadeIn(ten), run_time=0.6)
        self.done()

        # 4.3 the full calculation has the opposite sign; the left-out part is at least 94 per cent
        self.beat()
        bars_f = VGroup()
        for x, v in zip(xs, full):
            r = Rectangle(width=0.62, height=v * k, stroke_width=0, fill_color=WHITE, fill_opacity=0.85)
            r.move_to([x + 0.7, y0 + v * k / 2, 0])
            bars_f.add(r)
        vals_f = VGroup(*[T(f"+{v:.2f}", 22, WHITE).next_to(b, UP, buff=0.08) for b, v in zip(bars_f, full)])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_f], lag_ratio=0.2), run_time=1.0)
        self.play(FadeIn(vals_f), run_time=0.4)
        lf = VGroup(T("full calculation", 28), T("left-out part:", 22, C_DIM),
                    T("at least 94% of the total", 22, C_DIM)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        lf.move_to([-4.9, 1.45, 0])
        self.play(FadeIn(lf), run_time=0.6)
        self.done()

        # 4.4 the full stress is a pressure; the approximation's sign does not decide
        self.beat()
        pr = T("above zero: pressure", 24, C_DIM).move_to([-4.9, 0.35, 0])
        self.play(FadeIn(pr), run_time=0.4)
        xx = VGroup(*[cross(0.26).next_to(t, UP, buff=0.15) for t in vals_f])
        self.play(LaggedStart(*[Create(c) for c in xx], lag_ratio=0.2), run_time=0.8)
        self.done()

        # 4.5 the earlier self-consistent solutions themselves are not tested
        self.beat()
        nt = T("The 1997 solutions that used this approximation were not tested.", 24, C_FAINT)
        nt.move_to([0, -2.95, 0])
        self.play(FadeIn(nt), run_time=0.6)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 5. one number decides the size limit

class S5(Beats):
    SID = "s5"

    def construct(self):
        self.play(FadeIn(head("One number decides the size limit")), run_time=0.5)

        # 5.1 the stress changes with size through a logarithm; one number B sets how strongly
        self.beat()
        f1 = T("stress at the throat  =  t(1)  −  2 B ln(ℓ / size)", 36).move_to([0, 1.6, 0])
        self.play(FadeIn(f1), run_time=0.9)
        lab = T("B: one number at the throat", 30, C_KEY).next_to(f1, DOWN, buff=0.45)
        self.play(FadeIn(lab), run_time=0.5)
        self.done()

        # 5.2 a short formula; only two properties of the shape
        self.beat()
        f2 = T("B  ∝  4 − (1 − β)² (1 − Φ)²", 44, C_KEY).move_to([0, 0.0, 0])
        self.play(FadeIn(f2, shift=UP * 0.15), run_time=0.8)
        self.done()

        # 5.3 beta: how fast the tunnel opens out; Phi: how fast the rate of clocks changes
        self.beat()
        d1 = T("β : how fast the tunnel opens out at the throat", 28, C_DIM).move_to([0, -1.2, 0])
        d2 = T("Φ : how fast the rate of clocks changes there", 28, C_DIM).next_to(d1, DOWN, buff=0.25)
        self.play(FadeIn(d1), run_time=0.6)
        self.play(FadeIn(d2), run_time=0.6)
        self.done()

        # 5.4 the plane of the two properties: B > 0 between the curves, B < 0 outside
        self.beat()
        self.play(FadeOut(VGroup(f1, lab, d1, d2)), f2.animate.scale(0.62).move_to([3.9, 2.45, 0]),
                  run_time=0.7)
        axes = Axes(x_range=[-3.5, 1, 1], y_range=[-2.5, 6.5, 2], x_length=6.2, y_length=5.4,
                    axis_config={"color": C_DIM, "stroke_width": 2, "include_ticks": True},
                    tips=False).move_to([-2.6, -0.25, 0])
        xl = T("β", 30, C_DIM).next_to(axes.x_axis, RIGHT, buff=0.15)
        yl = T("Φ", 30, C_DIM).next_to(axes.y_axis, UP, buff=0.12)

        def lo(b):
            return max(-2.5, -(1 + b) / (1 - b))

        def hi(b):
            return min(6.5, (3 - b) / (1 - b))
        bs = np.linspace(-3.5, 0.999, 300)
        poly = [axes.c2p(b, lo(b)) for b in bs] + [axes.c2p(b, hi(b)) for b in bs[::-1]]
        region = Polygon(*poly, stroke_width=0, fill_color=C_POS, fill_opacity=0.22)
        c_lo = axes.plot(lambda b: -(1 + b) / (1 - b), x_range=[-3.5, 0.4286], color=WHITE, stroke_width=3)
        c_hi = axes.plot(lambda b: (3 - b) / (1 - b), x_range=[-3.5, 0.636], color=WHITE, stroke_width=3)
        self.play(Create(axes), FadeIn(xl), FadeIn(yl), run_time=0.8)
        self.play(Create(c_lo), Create(c_hi), run_time=1.0)
        self.play(FadeIn(region), run_time=0.5)
        lp = T("B > 0", 30, C_POS).move_to(axes.c2p(0.45, 3.0))
        ln1 = T("B < 0", 30, C_NEG).move_to(axes.c2p(-2.4, 5.2))
        ln2 = T("B < 0", 30, C_NEG).move_to(axes.c2p(0.2, -2.05))
        self.play(FadeIn(lp), FadeIn(ln1), FadeIn(ln2), run_time=0.6)
        fam = VGroup(*[Dot(axes.c2p(b, p), radius=0.06, color=C_POS)
                       for b in (-1, -0.5, 0, 0.5, 0.75) for p in (0, 0.5)]
                     + [Dot(axes.c2p(b, 1.5), radius=0.06, color=C_POS) for b in (-1, -0.5, 0, 0.5)])
        face = VGroup()
        for b in (-0.5, -1, -2, -3):
            curve = 2 * b / (1 - b)
            for p in (-0.5, curve, curve - 0.5):
                face.add(Square(0.13, stroke_width=0, fill_color=C_NEG, fill_opacity=1).move_to(axes.c2p(b, p)))
        face.add(Square(0.13, stroke_width=0, fill_color=C_NEG, fill_opacity=1).move_to(axes.c2p(0, -1.5)))
        self.play(LaggedStart(*[FadeIn(d) for d in fam], *[FadeIn(s) for s in face], lag_ratio=0.03),
                  run_time=1.0)
        key = VGroup(
            VGroup(Dot(radius=0.06, color=C_POS), T("main family (B > 0 side)", 22, C_DIM)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.13, stroke_width=0, fill_color=C_NEG, fill_opacity=1),
                   T("13 shapes of scene 7 (B < 0)", 22, C_DIM)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.4, 1.35, 0])
        self.play(FadeIn(key), run_time=0.4)
        self.done()

        # 5.5 B > 0: only throats smaller than a cap; B < 0: only throats larger than a floor
        self.beat()

        def bar(y, x_cut, left, color, text):
            line = Line([0.8, y, 0], [6.4, y, 0], color=C_DIM, stroke_width=2)
            seg = Line([0.8 if left else x_cut, y, 0], [x_cut if left else 6.4, y, 0], color=color,
                       stroke_width=10)
            tick = Line([x_cut, y - 0.18, 0], [x_cut, y + 0.18, 0], color=WHITE, stroke_width=4)
            lab = T(text, 26, color).move_to([3.6, y + 0.45, 0])
            return VGroup(line, seg, tick, lab)
        b1 = bar(-0.3, 3.0, True, C_POS, "B > 0: only below a cap")
        b2 = bar(-1.9, 3.0, False, C_NEG, "B < 0: only above a floor")
        sz = T("throat size →", 22, C_FAINT).move_to([5.6, -2.55, 0])
        self.play(FadeIn(b1), run_time=0.7)
        self.play(FadeIn(b2), FadeIn(sz), run_time=0.7)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 6. where B is positive

class S6(Beats):
    SID = "s6"

    def construct(self):
        self.play(FadeIn(head("Where B is positive: 21 shapes")), run_time=0.5)
        y = -1.2
        ax, X = log_axis(-3, 3, -5.8, 5.8, y, [(1e-3, "0.001"), (1e-2, "0.01"), (0.1, "0.1"), (1, "1"),
                                                (10, "10"), (100, "100"), (1000, "1000")])
        axl = T("throat radius, in Planck lengths", 24, C_DIM).move_to([0, y - 0.95, 0])
        pl = DashedLine([X(1), y - 0.1, 0], [X(1), 2.5, 0], color=C_KEY, dash_length=0.1)
        pll = T("Planck length", 24, C_KEY).move_to([X(1) + 1.05, 2.45, 0])

        # 6.1 on all 21 shapes the cap lies below the Planck length
        self.beat()
        self.play(Create(ax), FadeIn(axl), run_time=0.8)
        self.play(Create(pl), FadeIn(pll), run_time=0.5)
        caps = Rectangle(width=X(0.29) - X(0.0017), height=0.34, stroke_width=0, fill_color=C_POS,
                         fill_opacity=0.35).move_to([(X(0.0017) + X(0.29)) / 2, y + 2.1, 0])
        cl = T("caps of the 21 shapes: 0.0017 to 0.29", 24, C_POS).next_to(caps, UP, buff=0.15)
        self.play(FadeIn(caps), FadeIn(cl), run_time=0.8)
        self.done()

        # 6.2 one copy, main family of 15: solved at about 0.01 to 0.05; more copies do not raise the cap
        self.beat()
        sol = Rectangle(width=X(0.054) - X(0.010), height=0.34, stroke_width=0, fill_color=C_RR,
                        fill_opacity=0.8).move_to([(X(0.010) + X(0.054)) / 2, y + 0.85, 0])
        sl = T("pull equation solved: 0.010 to 0.054", 24, C_RR).next_to(sol, UP, buff=0.15)
        sl2 = T("(one copy; the 15 shapes of the main family)", 20, C_DIM).next_to(sol, DOWN, buff=0.12)
        self.play(FadeIn(sol), FadeIn(sl), FadeIn(sl2), run_time=0.8)
        mc = T("more copies do not raise the cap", 26).move_to([3.1, 0.9, 0])
        self.play(FadeIn(mc), run_time=0.5)
        self.done()

        # 6.3 below the Planck length the calculation is not expected to apply
        self.beat()
        sh = Rectangle(width=X(1) - X(1e-3) + 0.3, height=3.6, stroke_width=0, fill_color=GREY_D,
                       fill_opacity=0.35).move_to([(X(1e-3) - 0.3 + X(1)) / 2, y + 1.85, 0])
        s1 = T("below the Planck length:", 24, C_DIM).move_to([X(1) + 2.9, 1.3, 0])
        s2 = T("calculation not expected to apply;", 24, C_DIM).next_to(s1, DOWN, buff=0.1)
        s3 = T("no physical meaning given", 24, C_DIM).next_to(s2, DOWN, buff=0.1)
        self.play(FadeOut(mc), FadeIn(sh), run_time=0.6)
        self.play(FadeIn(VGroup(s1, s2, s3)), run_time=0.6)
        self.done()

        # 6.4 the energy equation changes sign near one point, about 0.05; the third equation fails there
        self.beat()
        pt = Dot([X(0.052), y, 0], radius=0.11, color=C_TT)
        e1 = T("energy equation changes sign near here (about 0.05)", 22, C_TT).move_to([X(0.052) + 0.6,
                                                                                       y - 1.0, 0])
        th = VGroup(T("third equation there:", 22, C_TH), cross(0.22)).arrange(RIGHT, buff=0.2)
        th.next_to(e1, DOWN, buff=0.15)
        self.play(FadeOut(axl), run_time=0.3)
        ar = Arrow(e1.get_top(), pt.get_bottom(), buff=0.06, color=C_TT, stroke_width=3, tip_length=0.15)
        self.play(FadeIn(pt, scale=0.5), FadeIn(e1), GrowArrow(ar), run_time=0.8)
        self.play(FadeIn(th), run_time=0.5)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 7. where B is negative

class S7(Beats):
    SID = "s7"

    def construct(self):
        hd = head("Where B is negative: 13 shapes")
        self.play(FadeIn(hd), run_time=0.5)
        y = -0.9
        ax, X = log_axis(-1, 3, -5.4, 5.4, y, [(0.1, "0.1"), (1, "1"), (10, "10"), (100, "100"),
                                               (1000, "1000")])
        axl = T("throat radius, in Planck lengths", 24, C_DIM).move_to([0, y - 0.95, 0])

        # 7.1 13 shapes on one face, chosen so that the energy equation becomes simple
        self.beat()
        sq = VGroup(*[Square(0.2, stroke_width=0, fill_color=C_NEG, fill_opacity=1) for _ in range(13)])
        sq.arrange(RIGHT, buff=0.18).move_to([0, 1.9, 0])
        f1 = T("on one face, chosen so that the energy equation becomes simple", 26, C_DIM).next_to(sq, DOWN,
                                                                                                 buff=0.3)
        self.play(LaggedStart(*[FadeIn(s) for s in sq], lag_ratio=0.05), run_time=0.8)
        self.play(FadeIn(f1), run_time=0.6)
        self.done()

        # 7.2 at 12 of the 13 the sign of the stress is certain; there the pull equation has solutions over the
        # whole range; at least 59 to about 1,400 copies
        self.beat()
        s12 = T("12 of the 13: the sign of the stress is certain", 24, C_DIM).move_to([0, 0.72, 0])
        self.play(sq[12].animate.set_fill(opacity=0.3), FadeIn(s12), run_time=0.6)
        self.play(Create(ax), FadeIn(axl), run_time=0.7)
        band = Rectangle(width=X(1000) - X(1), height=0.34, stroke_width=0, fill_color=C_RR,
                         fill_opacity=0.8).move_to([(X(1) + X(1000)) / 2, y + 0.5, 0])
        bl = VGroup(T("pull equation: solutions", 26, C_RR), check(0.3)).arrange(RIGHT, buff=0.2)
        bl.next_to(band, UP, buff=0.15)
        self.play(FadeIn(band), FadeIn(bl), run_time=0.8)
        nn = T("needs at least 59 to about 1,400 copies (depends on the shape)", 22, C_DIM).move_to(
            [0.3, y - 1.5, 0])
        self.play(FadeIn(nn), run_time=0.5)
        self.done()

        # 7.3 on this face the energy error is C divided by the radial stress: its sign does not depend on size
        self.beat()
        self.play(FadeOut(VGroup(sq, f1, s12)), run_time=0.4)
        e1 = T("energy error  =  C  ÷  (radial stress)", 36, C_TT).move_to([0, 2.15, 0])
        e2 = T("so its sign does not change with the size", 26, C_DIM).next_to(e1, DOWN, buff=0.2)
        self.play(FadeIn(e1), run_time=0.7)
        self.play(FadeIn(e2), run_time=0.5)
        self.done()

        # 7.4 C < 0 at all 13 points, beyond its uncertainty: wherever the pull equation holds, energy fails
        self.beat()
        self.play(FadeOut(VGroup(e2, band, bl, nn, axl)), e1.animate.scale(0.75).move_to([-3.4, 2.6, 0]),
                  run_time=0.6)
        cneg = T("C < 0 at all 13 points", 30, C_TT).move_to([3.4, 2.6, 0])
        self.play(FadeIn(cneg), run_time=0.5)
        # a drawing of the two errors over the range (the shapes follow the paper's Figure 2)
        px0, px1, py0 = X(1), X(1000), -0.2
        zl = DashedLine([px0, py0, 0], [px1, py0, 0], color=C_FAINT, dash_length=0.08)
        zt0 = T("0", 22, C_FAINT).next_to(zl, LEFT, buff=0.15)

        def ex(t):
            return 1.7 / (1 + 9 * t)
        band_t = Polygon(*([[px0 + (px1 - px0) * t, py0 + 1.25 * ex(t), 0] for t in np.linspace(0, 1, 60)]
                           + [[px0 + (px1 - px0) * t, py0 + 0.78 * ex(t), 0] for t in np.linspace(1, 0, 60)]),
                         stroke_width=0, fill_color=C_TT, fill_opacity=0.22)
        cur_t = ParametricFunction(lambda t: [px0 + (px1 - px0) * t, py0 + ex(t), 0], t_range=[0, 1, 0.01],
                                   color=C_TT, stroke_width=5)
        self.play(Create(zl), FadeIn(zt0), FadeIn(band_t), Create(cur_t), run_time=1.2)
        nz = VGroup(T("energy error: never zero", 24, C_TT), cross(0.22)).arrange(RIGHT, buff=0.2)
        nz.move_to([X(30), 1.15, 0])
        self.play(FadeIn(nz), run_time=0.5)
        self.set_note("drawing; shapes as in\nthe paper's Figure 2", at=[-6.8, 1.0, 0])
        self.done()

        # 7.5 the third equation crosses zero at only three points; the energy equation fails there too
        self.beat()
        tz = math.log10(112) / 3

        def th(t):
            return 0.9 * (1 - t / tz) / (1 + 2.5 * t)
        cur_th = ParametricFunction(lambda t: [px0 + (px1 - px0) * t, py0 + th(t), 0], t_range=[0, 1, 0.01],
                                    color=C_TH, stroke_width=5)
        self.play(Create(cur_th), run_time=1.0)
        zt = Dot([px0 + (px1 - px0) * tz, py0, 0], radius=0.09, color=C_TH)
        lt = T("third equation: crosses zero (at 3 of the 13 shapes)", 22, C_TH).move_to([X(60), py0 - 0.4, 0])
        self.play(FadeIn(zt), FadeIn(lt), run_time=0.6)
        never = T("the three never hold together", 30, C_KEY).move_to([0, -2.1, 0])
        self.play(FadeIn(never), run_time=0.6)
        self.done()

        # 7.6 version 1.1: three more shapes with a positive mass far away; the energy equation fails too
        self.beat()
        v = VGroup(T("version 1.1: + 3 shapes with a positive mass far away", 26),
                   T("energy equation fails there too", 26, C_TT), cross(0.22)).arrange(RIGHT, buff=0.25)
        v.scale_to_fit_width(min(v.width, 12.6)).move_to([0, 3.25, 0])
        self.play(FadeOut(VGroup(e1, cneg, hd)), run_time=0.4)
        self.play(FadeIn(v), run_time=0.7)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 8. what the result says, and what it does not

class S8(Beats):
    SID = "s8"

    def construct(self):
        hd = head("What the result says, and what it does not")
        self.play(FadeIn(hd), run_time=0.5)

        # 8.1 the static vacuum of this one field does not, by itself, give a throat where the calculation applies
        self.beat()
        r = VGroup(T("For the shapes examined, the static vacuum of this one field", 32),
                   T("does not, by itself, give a throat", 32, C_KEY),
                   T("in the range where the calculation applies.", 32)).arrange(DOWN, buff=0.18)
        r.move_to([0, 1.7, 0])
        self.play(FadeIn(r, shift=UP * 0.15), run_time=1.0)
        self.play(Create(box(r, C_KEY, buff=0.3)), run_time=0.6)
        self.done()

        # 8.2 the free length changes sizes, not answers; a second constant gives no candidate on B < 0
        self.beat()
        a1 = T("changing ℓ changes the sizes, not the answers", 28, C_DIM).move_to([0, -0.15, 0])
        a2 = T("a second free constant, scanned: no candidate on the B < 0 shapes", 28, C_DIM).next_to(
            a1, DOWN, buff=0.25)
        self.play(FadeIn(a1), run_time=0.6)
        self.play(FadeIn(a2), run_time=0.6)
        self.done()

        # 8.3 same direction as earlier general arguments; no claim of priority
        self.beat()
        d1 = T("same direction as earlier general arguments:", 28).move_to([0, -1.55, 0])
        d2 = T("throats held open by quantum effects stay near the Planck scale", 26, C_DIM).next_to(
            d1, DOWN, buff=0.15)
        d3 = T("no claim of priority", 26, C_FAINT).next_to(d2, DOWN, buff=0.2)
        self.play(FadeIn(d1), FadeIn(d2), run_time=0.8)
        self.play(FadeIn(d3), run_time=0.4)
        self.done()

        # 8.4 not "impossible": one field, one state, fixed shapes, throat only
        self.beat()
        self.play(*[FadeOut(m) for m in self.mobjects if m is not hd and m is not self._note], run_time=0.5)
        n1 = VGroup(cross(0.3), T("not: “wormholes are impossible”", 34)).arrange(RIGHT, buff=0.3)
        n1.move_to([0, 2.0, 0])
        self.play(FadeIn(n1), run_time=0.6)
        tested = VGroup(*[T(s, 28, C_DIM) for s in ("one field", "one state", "fixed shapes", "the throat only")])
        tested.arrange(RIGHT, buff=0.55).next_to(n1, DOWN, buff=0.55)
        tl = T("tested:", 28).next_to(tested, LEFT, buff=0.35)
        self.play(FadeIn(tl), LaggedStart(*[FadeIn(t) for t in tested], lag_ratio=0.2), run_time=1.0)
        self.done()

        # 8.5 not examined; grids are samples
        self.beat()
        ne = VGroup(T("not examined:", 28),
                    T("other fields · other states · long throats", 28, C_DIM),
                    T("the full self-consistent shape · stability", 28, C_DIM)).arrange(DOWN, buff=0.15)
        ne.move_to([0, -0.4, 0])
        self.play(FadeIn(ne), run_time=0.8)
        gs = T("the grids of shapes are samples, not a proof", 28, C_KEY).next_to(ne, DOWN, buff=0.35)
        self.play(FadeIn(gs), run_time=0.5)
        self.done()

        # 8.6 reservation: conservation check near the throat; 24 shapes recalculated, every sign kept
        self.beat()
        rv = VGroup(T("reservation: a conservation check near the throat", 26, C_DIM),
                    T("24 shapes recalculated at finer settings: every sign kept", 26, C_DIM)).arrange(
            DOWN, buff=0.12).move_to([0, -2.75, 0])
        self.play(FadeIn(rv), run_time=0.7)
        self.done()
        self.fade_all()


# ---------------------------------------------------------------- 9. how the work was done

class S9(Beats):
    SID = "s9"

    def construct(self):
        self.play(FadeIn(head("How the work was done")), run_time=0.5)

        # 9.1 three layers, each closed after an independent review
        self.beat()
        layers = VGroup()
        for i, (name, sub) in enumerate((("Layer 1", "approximation vs full"), ("Layer 2", "B > 0 side"),
                                         ("Layer 3", "B < 0 side"))):
            bx = RoundedRectangle(width=3.2, height=1.3, corner_radius=0.15, color=C_SHEET, stroke_width=2.5)
            g = VGroup(bx, VGroup(T(name, 30), T(sub, 22, C_DIM)).arrange(DOWN, buff=0.1).move_to(bx))
            layers.add(g)
        layers.arrange(RIGHT, buff=0.75).move_to([0, 1.5, 0])
        arrows = VGroup(*[Arrow(layers[i].get_right(), layers[i + 1].get_left(), buff=0.08, color=C_DIM,
                                stroke_width=3, tip_length=0.16) for i in range(2)])
        self.play(LaggedStart(*[FadeIn(g) for g in layers], lag_ratio=0.3), run_time=1.0)
        self.play(FadeIn(arrows), run_time=0.3)
        rv = VGroup(*[VGroup(check(0.26), T("review", 22, C_OK)).arrange(RIGHT, buff=0.12).next_to(
            g, DOWN, buff=0.2) for g in layers])
        self.play(LaggedStart(*[FadeIn(r) for r in rv], lag_ratio=0.3), run_time=0.8)
        self.done()

        # 9.2 reviewers: AI sessions with no shared context; every number checked by machine
        self.beat()
        r1 = T("reviewers: AI sessions that shared no context with the writer", 26, C_DIM).move_to([0, -0.15, 0])
        r2 = T("every number checked by machine against frozen records", 26, C_DIM).next_to(r1, DOWN, buff=0.2)
        self.play(FadeIn(r1), run_time=0.6)
        self.play(FadeIn(r2), run_time=0.6)
        self.done()

        # 9.3 prepared with AI assistants; the author chose, decided and is responsible
        self.beat()
        a1 = T("computations and text: prepared with AI assistants", 26).move_to([0, -1.35, 0])
        a2 = T("the author: the question, every decision on direction, the responsibility", 26, C_KEY).next_to(
            a1, DOWN, buff=0.2)
        self.play(FadeIn(a1), run_time=0.6)
        self.play(FadeIn(a2), run_time=0.6)
        self.done()

        # 9.4 the author has not reproduced the computations; read title, abstract and scope statements
        self.beat()
        h1 = T("not reproduced by the author; the author read the title, the abstract and the scope statements",
               21, C_FAINT).move_to([0, -2.55, 0])
        self.play(FadeIn(h1), run_time=0.6)
        self.done()

        # 9.5 paper, scripts and records on Zenodo
        self.beat()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        e1 = T("Maeda (2026), version 1.1, Zenodo", 36).move_to([0, 0.9, 0])
        e2 = T("doi:10.5281/zenodo.23826753", 34, C_KEY).next_to(e1, DOWN, buff=0.3)
        e3 = T("paper · scripts · records", 28, C_DIM).next_to(e2, DOWN, buff=0.3)
        self.play(FadeIn(e1), FadeIn(e2), run_time=0.8)
        self.play(FadeIn(e3), run_time=0.5)
        self.done(extra=1.2)
        self.fade_all()
