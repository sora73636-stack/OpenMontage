"""Manim CE 0.22.1 — 10 s scientific diagram: why ice floats.

Original diagram, factual densities (liquid water ~1.00 g/cm3, ice ~0.92 g/cm3).
No LaTeX, no third-party assets.
"""

from manim import *

class IceFloats(Scene):
    def construct(self):
        title = Text("Why ice floats", font_size=54, color=WHITE).to_edge(UP, buff=0.6)
        sub = Text("Density decides what floats", font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.25)
        self.play(Write(title), FadeIn(sub, shift=UP * 0.2), run_time=1.2)
        self.wait(0.4)

        # beaker
        beaker = RoundedRectangle(width=3.2, height=3.6, corner_radius=0.12,
                                  stroke_color=GREY_B, stroke_width=4, fill_opacity=0)
        beaker.move_to(LEFT * 3.2 + DOWN * 0.5)
        water = Rectangle(width=2.95, height=2.3, stroke_width=0, fill_color=BLUE_D, fill_opacity=0.75)
        water.move_to(beaker.get_bottom() + UP * 1.25)
        self.play(Create(beaker), run_time=0.8)
        self.play(FadeIn(water, shift=UP * 0.3), run_time=0.8)

        # ice block
        ice = RoundedRectangle(width=1.35, height=1.1, corner_radius=0.08,
                               stroke_color=WHITE, stroke_width=3, fill_color=BLUE_E, fill_opacity=0.9)
        ice.move_to(beaker.get_top() + UP * 2.0)
        self.play(FadeIn(ice, shift=DOWN * 0.4), run_time=0.5)
        self.play(ice.animate.move_to(beaker.get_top() + DOWN * 0.15), run_time=1.4, rate_func=smooth)
        # bob
        self.play(ice.animate.shift(UP * 0.12), run_time=0.6, rate_func=there_and_back)

        # labels
        wlabel = VGroup(
            Text("liquid water", font_size=24, color=WHITE),
            Text("1.00 g/cm³", font_size=22, color=BLUE_C),
        ).arrange(DOWN, buff=0.1).next_to(beaker, RIGHT, buff=0.7)
        ilabel = VGroup(
            Text("ice", font_size=24, color=WHITE),
            Text("0.92 g/cm³", font_size=22, color=BLUE_C),
        ).arrange(DOWN, buff=0.1).next_to(ice, RIGHT, buff=0.8)
        self.play(FadeIn(wlabel, shift=LEFT * 0.2), run_time=0.7)
        self.play(FadeIn(ilabel, shift=LEFT * 0.2), run_time=0.7)

        arrow = Arrow(ORIGIN, RIGHT * 1.6, buff=0, stroke_width=6, color=YELLOW)
        arrow.next_to(VGroup(wlabel, ilabel), DOWN, buff=0.45)
        alabel = Text("less dense → floats", font_size=26, color=YELLOW).next_to(arrow, DOWN, buff=0.2)
        self.play(GrowArrow(arrow), FadeIn(alabel), run_time=0.9)
        self.wait(1.2)

        # final takeaway
        take = Text("Hydrogen bonds form an open lattice", font_size=26, color=GREY_B).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(take, shift=UP * 0.2), run_time=0.8)
        self.wait(1.0)