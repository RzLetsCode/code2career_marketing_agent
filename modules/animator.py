import os
import re
import json
import asyncio
import textwrap
import subprocess
from typing import List, Dict, Any
import edge_tts

from config.settings import settings
from core.logger import logger
from modules.strategist import CarouselPost, Slide


MANIM_SCENE_TEMPLATE = r"""import os
import json
import numpy as np
from manim import *

# Native 9:16 vertical resolution for Instagram Reels & LinkedIn Mobile
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30


class HumanTouchArchitectureReel(Scene):
    def _build_bespoke_stage_canvas(self, slide_info: dict, accent_color: str):
        # Dynamically constructs a bespoke, 2-beat interactive simulation driven by slide_info
        # Beat 1 (alpha: 0.0 -> 0.45) = Naive Bottleneck / Uncalibrated State
        # Beat 2 (alpha: 0.45 -> 1.0) = Optimized Architecture / Mathematical Convergence
        canvas_center = np.array([0.0, 0.25, 0.0])
        base_group = VGroup()

        archetype = slide_info.get("visual_archetype", "topology_flow")
        nodes = slide_info.get("visual_nodes", ["Ingress", "Processor", "Vector Index", "LLM Sink"])
        while len(nodes) < 4:
            nodes.append(f"Module 0{len(nodes)+1}")

        formula_str = slide_info.get("math_formula", "f(x) = Wx + b")
        metric_lbl = slide_info.get("metric_label", "System Telemetry")
        metric_before = slide_info.get("metric_before", "Bottleneck State")
        metric_after = slide_info.get("metric_after", "Optimized State")

        # Main Simulation Viewport Frame
        frame = RoundedRectangle(
            corner_radius=0.22,
            width=8.1,
            height=4.25,
            color="#1e293b",
            fill_color="#080c14",
            fill_opacity=0.94,
            stroke_width=2.2
        ).move_to(canvas_center)
        base_group.add(frame)

        # Top-Left: Formula Callout Badge
        formula_badge = RoundedRectangle(
            corner_radius=0.1,
            width=4.3,
            height=0.46,
            color=accent_color,
            fill_color="#0f172a",
            fill_opacity=0.95,
            stroke_width=1.5
        ).move_to(frame.get_corner(UL) + RIGHT * 2.3 + DOWN * 0.36)
        formula_txt = Text(formula_str[:34], font_size=13, color=accent_color).move_to(formula_badge.get_center())
        base_group.add(formula_badge, formula_txt)

        # Normalized progress tracker alpha: sweeps 0.0 -> 1.0 over exact slide audio duration
        tracker = ValueTracker(0.0)

        # Helper that builds the Top-Right Live Beat Status + Bottom Telemetry HUD inside always_redraw
        def _build_hud_overlay(alpha: float) -> VGroup:
            is_optimized = alpha >= 0.46
            state_col = "#10b981" if is_optimized else "#ef4444"
            state_title = "BEAT 2 // PRODUCTION FIX" if is_optimized else "BEAT 1 // NAIVE BOTTLENECK"
            metric_val = metric_after if is_optimized else metric_before

            status_pill = RoundedRectangle(
                corner_radius=0.1,
                width=3.2,
                height=0.46,
                color=state_col,
                fill_color="#0f172a",
                fill_opacity=0.95,
                stroke_width=1.8
            ).move_to(frame.get_corner(UR) + LEFT * 1.75 + DOWN * 0.36)
            status_dot = Dot(color=state_col, radius=0.055).move_to(status_pill.get_left() + RIGHT * 0.22)
            status_txt = Text(state_title, font_size=11, color=state_col).next_to(status_dot, RIGHT, buff=0.1)

            # Bottom Live Telemetry Bar inside Canvas
            hud_bar = RoundedRectangle(
                corner_radius=0.1,
                width=7.6,
                height=0.52,
                color=state_col,
                fill_color="#0f172a",
                fill_opacity=0.92,
                stroke_width=1.5
            ).move_to(frame.get_bottom() + UP * 0.38)
            hud_txt = Text(
                f"{metric_lbl}:  {metric_val}",
                font_size=13,
                color=WHITE
            ).move_to(hud_bar.get_center())

            return VGroup(status_pill, status_dot, status_txt, hud_bar, hud_txt)

        # =====================================================================
        # ARCHETYPE 1: BESPOKE SYSTEM TOPOLOGY FLOW (Custom Named Components)
        # =====================================================================
        if archetype == "topology_flow":
            pos_list = [
                canvas_center + LEFT * 2.5 + UP * 0.65,
                canvas_center + RIGHT * 0.0 + UP * 0.65,
                canvas_center + RIGHT * 2.5 + UP * 0.65,
                canvas_center + RIGHT * 0.0 + DOWN * 0.55,
            ]
            static_nodes = VGroup()
            for idx in range(4):
                b = RoundedRectangle(
                    corner_radius=0.14,
                    width=2.1,
                    height=0.72,
                    color="#334155",
                    fill_color="#111827",
                    fill_opacity=0.9,
                    stroke_width=2
                ).move_to(pos_list[idx])
                t = Text(nodes[idx][:16], font_size=12, color="#e2e8f0").move_to(b.get_center())
                static_nodes.add(VGroup(b, t))
            base_group.add(static_nodes)

            def _update_topology():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                is_opt = alpha >= 0.46
                flow_col = "#10b981" if is_opt else "#ef4444"

                # Connect nodes with live status lines
                l1 = Arrow(pos_list[0] + RIGHT * 1.05, pos_list[1] - RIGHT * 1.05, buff=0.05, color=flow_col, stroke_width=3)
                l2 = Arrow(pos_list[1] + RIGHT * 1.05, pos_list[2] - RIGHT * 1.05, buff=0.05, color=flow_col, stroke_width=3)
                l3 = Arrow(pos_list[1] + DOWN * 0.36, pos_list[3] + UP * 0.36, buff=0.05, color=accent_color if is_opt else "#475569", stroke_width=3)

                # Active highlight ring around the bottleneck/optimized core node
                focus_idx = 3 if is_opt else 1
                ring = SurroundingRectangle(static_nodes[focus_idx], color=flow_col, buff=0.06, corner_radius=0.16, stroke_width=3.5)

                # Animated packet traveling across the topology
                sub_t = (alpha * 3.0) % 1.0
                pkt_pos = (1.0 - sub_t) * (pos_list[0] + RIGHT * 1.05) + sub_t * (pos_list[2] - RIGHT * 1.05)
                pkt = Dot(pkt_pos, color=YELLOW if is_opt else "#ef4444", radius=0.09)

                return VGroup(l1, l2, l3, ring, pkt, hud)

            return base_group, always_redraw(_update_topology), tracker

        # =====================================================================
        # ARCHETYPE 2: GEOMETRIC VECTOR SUBSPACE (Live Cosine Alignment)
        # =====================================================================
        elif archetype == "vector_subspace":
            axes = Axes(
                x_range=[0, 4, 1],
                y_range=[0, 3, 1],
                x_length=3.7,
                y_length=2.1,
                axis_config={"color": "#475569", "stroke_width": 2, "include_tip": True, "tip_width": 0.14, "tip_height": 0.14}
            ).move_to(canvas_center + LEFT * 1.6 + DOWN * 0.05)

            origin_pt = axes.coords_to_point(0, 0)
            target_ang = 0.42
            noise_ang = 1.35
            v_len = 2.6

            k_plus_end = origin_pt + np.array([v_len * np.cos(target_ang), v_len * np.sin(target_ang), 0])
            k_minus_end = origin_pt + np.array([v_len * 0.82 * np.cos(noise_ang), v_len * 0.82 * np.sin(noise_ang), 0])

            vec_k1 = Arrow(origin_pt, k_plus_end, buff=0, color="#10b981", stroke_width=3.5)
            vec_k2 = Arrow(origin_pt, k_minus_end, buff=0, color="#ef4444", stroke_width=2.5)
            lbl_k1 = Text(nodes[1][:14], font_size=12, color="#10b981").next_to(k_plus_end, RIGHT, buff=0.08)
            lbl_k2 = Text(nodes[2][:14], font_size=11, color="#ef4444").next_to(k_minus_end, UP, buff=0.06)
            base_group.add(axes, vec_k1, vec_k2, lbl_k1, lbl_k2)

            def _update_vector():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                ang = 1.28 - alpha * (1.28 - 0.44)
                q_end = origin_pt + np.array([v_len * np.cos(ang), v_len * np.sin(ang), 0])
                q_arr = Arrow(origin_pt, q_end, buff=0, color="#38bdf8", stroke_width=4.5)
                q_lbl = Text(nodes[0][:12], font_size=12, color="#38bdf8").next_to(q_end, UP, buff=0.06)

                diff = abs(ang - target_ang)
                cos_val = float(np.cos(diff))
                arc = Arc(radius=0.75, start_angle=min(ang, target_ang), angle=max(0.02, diff), arc_center=origin_pt, color=YELLOW, stroke_width=3)

                p_pos = canvas_center + RIGHT * 2.25 + UP * 0.05
                c_col = "#10b981" if cos_val > 0.90 else "#f59e0b"
                c_box = RoundedRectangle(corner_radius=0.12, width=2.7, height=1.35, color=c_col, fill_color="#0f172a", fill_opacity=0.9, stroke_width=2).move_to(p_pos)
                t_ang = Text(f"Angle θ: {np.degrees(diff):4.1f}°", font_size=13, color="#cbd5e1").move_to(p_pos + UP * 0.28)
                t_cos = Text(f"cos(θ) = {cos_val:0.3f}", font_size=16, color=c_col).move_to(p_pos + DOWN * 0.22)

                return VGroup(q_arr, q_lbl, arc, c_box, t_ang, t_cos, hud)

            return base_group, always_redraw(_update_vector), tracker

        # =====================================================================
        # ARCHETYPE 3: PROBABILITY DISTRIBUTION (Softmax / Reranker Morphing)
        # =====================================================================
        elif archetype == "probability_dist":
            base_line = Line(canvas_center + LEFT * 3.5 + DOWN * 0.75, canvas_center + RIGHT * 1.4 + DOWN * 0.75, color="#475569", stroke_width=2)
            base_group.add(base_line)

            flat_p = np.array([0.24, 0.28, 0.25, 0.23])
            sharp_p = np.array([0.05, 0.81, 0.09, 0.05])

            def _update_probs():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                curr_p = (1.0 - alpha) * flat_p + alpha * sharp_p
                temp = 2.40 - alpha * 2.15

                bars = VGroup()
                for idx in range(4):
                    p = float(curr_p[idx])
                    bh = max(0.16, p * 1.95)
                    col = "#10b981" if (idx == 1 and alpha >= 0.46) else ("#38bdf8" if idx == 1 else "#334155")
                    b = RoundedRectangle(corner_radius=0.06, width=0.82, height=bh, color=col, fill_color=col, fill_opacity=0.82, stroke_width=2)
                    x_p = -2.85 + idx * 1.18
                    b.move_to(np.array([x_p, canvas_center[1] - 0.75 + bh / 2.0, 0]))
                    pt = Text(f"{int(round(p*100))}%", font_size=12, color=WHITE).next_to(b, UP, buff=0.05)
                    lt = Text(nodes[idx][:10], font_size=11, color="#94a3b8").next_to(b, DOWN, buff=0.08)
                    bars.add(VGroup(b, pt, lt))

                p_pos = canvas_center + RIGHT * 2.55 + UP * 0.05
                t_box = RoundedRectangle(corner_radius=0.12, width=2.3, height=1.35, color="#a855f7", fill_color="#0f172a", fill_opacity=0.9, stroke_width=2).move_to(p_pos)
                t1 = Text(f"Temp T: {temp:0.2f}", font_size=13, color="#e2e8f0").move_to(p_pos + UP * 0.28)
                t2 = Text(f"Peak:   {int(round(curr_p[1]*100))}%", font_size=15, color="#10b981").move_to(p_pos + DOWN * 0.22)

                return VGroup(bars, t_box, t1, t2, hud)

            return base_group, always_redraw(_update_probs), tracker

        # =====================================================================
        # ARCHETYPE 4: SCALING COMPLEXITY CURVE (O(N^2) vs O(log N) Tracer)
        # =====================================================================
        elif archetype == "scaling_curve":
            axes = Axes(
                x_range=[0, 5, 1],
                y_range=[0, 10, 2],
                x_length=4.5,
                y_length=2.0,
                axis_config={"color": "#475569", "stroke_width": 2, "include_tip": False}
            ).move_to(canvas_center + LEFT * 1.3 + DOWN * 0.02)

            c_bad = axes.plot(lambda x: 0.42 * (x ** 2) + 0.4, x_range=[0, 4.5], color="#ef4444", stroke_width=3.5)
            c_good = axes.plot(lambda x: 1.2 * np.log(x + 1) + 0.4, x_range=[0, 4.5], color="#10b981", stroke_width=3.5)
            l_bad = Text(nodes[0][:14], font_size=11, color="#ef4444").move_to(axes.coords_to_point(3.1, 8.2))
            l_good = Text(nodes[1][:14], font_size=11, color="#10b981").move_to(axes.coords_to_point(3.4, 3.2))
            base_group.add(axes, c_bad, c_good, l_bad, l_good)

            def _update_curve():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                xv = 0.4 + alpha * 4.1
                yb = 0.42 * (xv ** 2) + 0.4
                yg = 1.2 * np.log(xv + 1) + 0.4

                pb = axes.coords_to_point(xv, yb)
                pg = axes.coords_to_point(xv, yg)
                gap = DashedLine(pg, pb, color=YELLOW, stroke_width=2.5)
                db = Dot(pb, color="#ef4444", radius=0.085)
                dg = Dot(pg, color="#10b981", radius=0.085)

                p_pos = canvas_center + RIGHT * 2.4 + UP * 0.05
                s_box = RoundedRectangle(corner_radius=0.12, width=2.5, height=1.35, color="#10b981", fill_color="#0f172a", fill_opacity=0.9, stroke_width=2).move_to(p_pos)
                gain = max(1.0, (yb * 85.0) / max(1.0, yg * 12.0))
                t1 = Text(f"Load Scale: {xv:3.1f}x", font_size=13, color="#cbd5e1").move_to(p_pos + UP * 0.28)
                t2 = Text(f"Gain:       {gain:4.1f}x", font_size=16, color=YELLOW).move_to(p_pos + DOWN * 0.22)

                return VGroup(gap, db, dg, s_box, t1, t2, hud)

            return base_group, always_redraw(_update_curve), tracker

        # =====================================================================
        # ARCHETYPE 5: STORAGE TIERS (L1 Hot Cache vs Cold Index Lookup)
        # =====================================================================
        elif archetype == "storage_tiers":
            tiers = VGroup()
            widths = [3.6, 5.0, 6.4]
            t_cols = ["#10b981", "#38bdf8", "#64748b"]
            for idx in range(3):
                tb = RoundedRectangle(
                    corner_radius=0.12,
                    width=widths[idx],
                    height=0.58,
                    color=t_cols[idx],
                    fill_color="#111827",
                    fill_opacity=0.88,
                    stroke_width=2
                ).move_to(canvas_center + UP * (0.75 - idx * 0.72))
                tt = Text(f"TIER 0{idx+1} // {nodes[idx][:18]}", font_size=12, color=WHITE).move_to(tb.get_center())
                tiers.add(VGroup(tb, tt))
            base_group.add(tiers)

            def _update_tiers():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                is_opt = alpha >= 0.46
                active_tier = 0 if is_opt else 2
                hl_col = "#10b981" if is_opt else "#ef4444"
                ring = SurroundingRectangle(tiers[active_tier], color=hl_col, buff=0.06, corner_radius=0.14, stroke_width=3.5)
                tag_str = "L1 SEMANTIC HIT (O(1))" if is_opt else "COLD DISK SCAN (O(N))"
                tag = Text(tag_str, font_size=12, color=hl_col).next_to(ring, RIGHT, buff=0.15)
                return VGroup(ring, tag, hud)

            return base_group, always_redraw(_update_tiers), tracker

        # =====================================================================
        # ARCHETYPE 6: TOKEN STREAM & SLIDING CONTEXT WINDOW
        # =====================================================================
        else:
            tok_boxes = VGroup()
            short_tokens = [n[:8] for n in nodes[:4]] + ["CTX_01", "CTX_02", "OVERLAP", "SINK"]
            for idx, tk in enumerate(short_tokens[:7]):
                bx = RoundedRectangle(corner_radius=0.08, width=0.95, height=0.62, color="#334155", fill_color="#1e293b", fill_opacity=0.85)
                tx = Text(tk[:8], font_size=11, color="#e2e8f0").move_to(bx.get_center())
                grp = VGroup(bx, tx).move_to(canvas_center + LEFT * 3.15 + RIGHT * (idx * 1.05) + UP * 0.35)
                tok_boxes.add(grp)
            base_group.add(tok_boxes)

            def _update_tokens():
                alpha = tracker.get_value()
                hud = _build_hud_overlay(alpha)
                pos = alpha * 4.0
                x_c = -3.15 + (pos + 1.0) * 1.05
                win = RoundedRectangle(
                    corner_radius=0.12,
                    width=2.95,
                    height=0.82,
                    color=accent_color,
                    stroke_width=3.5,
                    fill_color=accent_color,
                    fill_opacity=0.14
                ).move_to(canvas_center + RIGHT * x_c + UP * 0.35)

                v1 = 0.25 + 0.45 * np.sin(alpha * 6.28)
                v2 = 0.88 - 0.30 * np.cos(alpha * 6.28)
                reg = Text(
                    f"Active Context Tensor: [{v1:+0.2f}, {v2:+0.2f}] -> Boundary Preserved",
                    font_size=12,
                    color=accent_color
                ).move_to(canvas_center + DOWN * 0.45)

                return VGroup(win, reg, hud)

            return base_group, always_redraw(_update_tokens), tracker

    def construct(self):
        self.camera.background_color = "#07090e"

        data_path = os.path.join(os.path.dirname(__file__), "scene_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        hook_seg = payload["hook"]
        slides_data = payload["slides"]
        cta_seg = payload["cta"]

        grid = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-9, 9, 1],
            background_line_style={"stroke_color": "#162032", "stroke_width": 1, "stroke_opacity": 0.35},
            axis_config={"stroke_opacity": 0}
        )
        self.add(grid)

        brand_header = Text(
            "CODE2CAREER_AI // PRINCIPAL ARCHITECT STORYBOARD",
            font_size=14,
            color="#64748b"
        ).to_edge(UP, buff=0.38)
        self.add(brand_header)

        # =====================================================================
        # PHASE 1: HOOK SCENE WITH LIVE PHASE-SHIFTING WAVEPACKET
        # =====================================================================
        pillar_badge = RoundedRectangle(corner_radius=0.15, width=4.8, height=0.55, color="#38bdf8", fill_opacity=0.15)
        pillar_text = Text(hook_seg["pillar"], font_size=17, color="#38bdf8").move_to(pillar_badge.get_center())
        pillar_group = VGroup(pillar_badge, pillar_text).move_to(UP * 2.5)

        hook_title = Text(hook_seg["title_wrapped"], font_size=32, color=WHITE, line_spacing=1.25).move_to(UP * 0.4)
        accent_line = Line(LEFT * 2.8, RIGHT * 2.8, color="#38bdf8", stroke_width=4).next_to(hook_title, DOWN, buff=0.45)

        hook_axes = Axes(x_range=[-3, 3, 1], y_range=[-1.2, 1.2, 1], x_length=6.2, y_length=1.7, axis_config={"stroke_opacity": 0}).move_to(DOWN * 2.3)
        phase_tracker = ValueTracker(0.0)
        hook_wave = always_redraw(
            lambda: hook_axes.plot(
                lambda x: np.sin(2.4 * x - phase_tracker.get_value()) * np.exp(-0.22 * (x ** 2)),
                color="#38bdf8",
                stroke_width=4
            )
        )

        self.play(
            FadeIn(pillar_group, shift=DOWN * 0.3),
            FadeIn(hook_title, scale=0.95),
            GrowFromCenter(accent_line),
            FadeIn(hook_wave),
            run_time=1.0
        )
        self.play(
            phase_tracker.animate.set_value(6.28),
            run_time=max(0.3, float(hook_seg["duration"]) - 1.5),
            rate_func=linear
        )

        compact_title = Text(hook_seg["compact_title"], font_size=18, color="#38bdf8").next_to(brand_header, DOWN, buff=0.2)
        self.play(
            ReplacementTransform(hook_title, compact_title),
            FadeOut(pillar_group),
            FadeOut(accent_line),
            FadeOut(hook_wave),
            run_time=0.5
        )

        # =====================================================================
        # PHASE 2: TOP SYSTEM PROGRESS PIPELINE + MIDDLE BESPOKE CANVAS + BOTTOM INSPECTOR
        # =====================================================================
        num_nodes = len(slides_data)
        node_groups = VGroup()
        node_boxes = []
        arrows = VGroup()

        coords = [
            [-2.2, 5.45, 0],
            [ 2.2, 5.45, 0],
            [ 2.2, 4.05, 0],
            [-2.2, 4.05, 0],
            [ 0.0, 2.75, 0]
        ]
        palette = ["#38bdf8", "#a855f7", "#10b981", "#f59e0b", "#ec4899"]

        for i, s in enumerate(slides_data):
            pos = coords[i] if i < len(coords) else [0, 2.75, 0]
            col = palette[i % len(palette)]
            b = RoundedRectangle(corner_radius=0.15, width=3.4, height=0.84, color=col, fill_opacity=0.12, stroke_width=2)
            num_badge = Text(f"0{i+1}", font_size=13, color=col).move_to(b.get_corner(UL) + RIGHT * 0.32 + DOWN * 0.22)
            lbl = Text(s["node_label"], font_size=14, color=WHITE).move_to(b.get_center() + DOWN * 0.04)
            grp = VGroup(b, num_badge, lbl).move_to(pos)
            node_groups.add(grp)
            node_boxes.append((b, col))

        for i in range(num_nodes - 1):
            arr = Arrow(
                node_groups[i].get_center(),
                node_groups[i + 1].get_center(),
                buff=0.65,
                color="#475569",
                stroke_width=2.5,
                max_tip_length_to_length_ratio=0.14
            )
            arrows.add(arr)

        inspector_bg = RoundedRectangle(
            corner_radius=0.25,
            width=8.1,
            height=4.55,
            color="#1e293b",
            fill_color="#0f172a",
            fill_opacity=0.95,
            stroke_width=2.5
        ).move_to(DOWN * 4.65)

        inspector_header_line = Line(
            inspector_bg.get_left() + UP * 1.2,
            inspector_bg.get_right() + UP * 1.2,
            color="#1e293b",
            stroke_width=2
        )
        self.add(node_groups, arrows, inspector_bg, inspector_header_line)

        current_inspector_content = None
        current_canvas_base = None
        current_canvas_dyn = None

        for i, s in enumerate(slides_data):
            seg_duration = float(s["duration"])
            active_box, active_col = node_boxes[i]

            new_canvas_base, new_canvas_dyn, sim_tracker = self._build_bespoke_stage_canvas(s, active_col)

            stage_tag = Text(f"[ {s['tag']} ]", font_size=15, color=active_col).move_to(inspector_bg.get_top() + DOWN * 0.4)
            stage_head = Text(s["headline"], font_size=19, color=WHITE, line_spacing=1.15).move_to(inspector_bg.get_top() + DOWN * 1.1)
            stage_detail = Text(s["detail"], font_size=16, color="#cbd5e1", line_spacing=1.28).move_to(inspector_bg.get_center() + DOWN * 0.5)

            progress_track = Line(
                inspector_bg.get_left() + RIGHT * 0.6 + DOWN * 1.88,
                inspector_bg.get_right() + LEFT * 0.6 + DOWN * 1.88,
                color="#334155",
                stroke_width=6
            )
            progress_fill = Line(
                progress_track.get_start(),
                progress_track.get_start() + RIGHT * 0.01,
                color=active_col,
                stroke_width=6
            )

            new_inspector = VGroup(stage_tag, stage_head, stage_detail, progress_track, progress_fill)

            transition_time = 0.65
            restore_time = 0.1
            hold_time = max(0.4, seg_duration - transition_time - restore_time)

            anims = [
                active_box.animate.set_fill(active_col, opacity=0.38).set_stroke(active_col, width=4.0),
                node_groups[i].animate.scale(1.06),
                inspector_bg.animate.set_stroke(active_col, width=3)
            ]

            for j in range(num_nodes):
                if j != i:
                    other_box, other_col = node_boxes[j]
                    anims.append(other_box.animate.set_fill(other_col, opacity=0.07).set_stroke(other_col, width=1.5))

            if current_inspector_content is not None:
                anims.append(FadeOut(current_inspector_content, shift=UP * 0.15))
            if current_canvas_base is not None:
                anims.append(FadeOut(current_canvas_base))
            if current_canvas_dyn is not None:
                self.remove(current_canvas_dyn)

            anims.append(FadeIn(new_inspector, shift=UP * 0.15))
            anims.append(FadeIn(new_canvas_base))

            if i > 0 and (i - 1) < len(arrows):
                anims.append(arrows[i - 1].animate.set_color(active_col))

            self.play(*anims, run_time=transition_time)
            self.add(new_canvas_dyn)

            # Drive the 2-Beat Simulation (Beat 1 Bottleneck -> Beat 2 Fix) across exact audio hold_time
            if i > 0 and (i - 1) < len(arrows):
                packet = Dot(color=YELLOW, radius=0.11).move_to(arrows[i - 1].get_start())
                self.add(packet)
                self.play(
                    MoveAlongPath(packet, arrows[i - 1]),
                    sim_tracker.animate.set_value(1.0),
                    progress_fill.animate.put_start_and_end_on(progress_track.get_start(), progress_track.get_end()),
                    run_time=hold_time,
                    rate_func=linear
                )
                self.remove(packet)
            else:
                self.play(
                    sim_tracker.animate.set_value(1.0),
                    progress_fill.animate.put_start_and_end_on(progress_track.get_start(), progress_track.get_end()),
                    run_time=hold_time,
                    rate_func=linear
                )

            self.play(node_groups[i].animate.scale(1 / 1.06), run_time=restore_time)
            current_inspector_content = new_inspector
            current_canvas_base = new_canvas_base
            current_canvas_dyn = new_canvas_dyn

        # =====================================================================
        # PHASE 3: CALL TO ACTION SCENE
        # =====================================================================
        if current_canvas_dyn is not None:
            self.remove(current_canvas_dyn)

        self.play(
            FadeOut(node_groups),
            FadeOut(arrows),
            FadeOut(inspector_bg),
            FadeOut(inspector_header_line),
            FadeOut(current_inspector_content),
            FadeOut(current_canvas_base),
            run_time=0.6
        )

        cta_card = RoundedRectangle(
            corner_radius=0.3,
            width=7.6,
            height=4.2,
            color="#f59e0b",
            fill_color="#0f172a",
            fill_opacity=0.95,
            stroke_width=3.5
        ).move_to(ORIGIN)
        cta_title = Text("GET THE PRODUCTION BLUEPRINT", font_size=21, color="#f59e0b").move_to(cta_card.get_top() + DOWN * 0.8)
        cta_kw = Text(f"COMMENT '{cta_seg['keyword']}'", font_size=34, color=WHITE).move_to(cta_card.get_center())
        cta_sub = Text(
            "Full GitHub Repository + System Architecture PDF\nsent directly to your DMs.",
            font_size=17,
            color="#94a3b8",
            line_spacing=1.25
        ).move_to(cta_card.get_bottom() + UP * 0.85)

        cta_group = VGroup(cta_card, cta_title, cta_kw, cta_sub)
        self.play(FadeIn(cta_group, scale=0.92), run_time=0.8)
        self.wait(max(0.4, float(cta_seg["duration"]) - 1.4))
"""


class AnimationEngine:
    """
    Human-Touch Storyboard Animation Engine (9:16 Vertical).
    Translates Azure OpenAI's bespoke per-slide storyboard metadata (visual_archetype,
    visual_nodes, metric_before, metric_after, math_formula) into a 2-Beat narrative
    simulation locked to exact TTS segment durations.
    """

    def __init__(
        self,
        output_dir: str = settings.slides_output_dir,
        voice: str = "en-US-ChristopherNeural"
    ):
        self.output_dir = os.path.abspath(output_dir)
        self.temp_dir = os.path.join(self.output_dir, "manim_work")
        self.voice = voice
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    async def _synthesize_segment(self, text: str, out_path: str):
        communicate = edge_tts.Communicate(text=text, voice=self.voice, rate="+8%")
        await communicate.save(out_path)

    def _get_audio_duration(self, audio_path: str) -> float:
        try:
            from moviepy.editor import AudioFileClip
        except ImportError:
            from moviepy import AudioFileClip

        clip = AudioFileClip(audio_path)
        duration = float(clip.duration)
        clip.close()
        return duration

    def _extract_short_node_title(self, headline: str, fallback: str) -> str:
        clean = re.sub(r"[^a-zA-Z0-9\s\-/]", "", headline).strip()
        words = [w for w in clean.split() if len(w) > 2 or w.isupper()]
        if not words:
            return fallback
        return " ".join(words[:3]).title()[:22]

    def _smart_fallback_metadata(self, idx: int, slide: Slide) -> Dict[str, Any]:
        """Provides intelligent fallback storyboard metadata if a slide was created without AI Director fields."""
        text_blob = f"{slide.headline} {slide.content}".lower()
        archetypes = ["token_stream", "vector_subspace", "scaling_curve", "probability_dist", "storage_tiers"]
        default_arch = archetypes[idx % len(archetypes)]

        if any(w in text_blob for w in ["vector", "cosine", "embed", "dot", "subspace"]):
            default_arch = "vector_subspace"
        elif any(w in text_blob for w in ["softmax", "rerank", "attention", "probabil", "logit"]):
            default_arch = "probability_dist"
        elif any(w in text_blob for w in ["cache", "tier", "redis", "memory", "storage"]):
            default_arch = "storage_tiers"
        elif any(w in text_blob for w in ["chunk", "token", "window", "stream", "split"]):
            default_arch = "token_stream"
        elif any(w in text_blob for w in ["latency", "scale", "quadratic", "hnsw", "graph"]):
            default_arch = "scaling_curve"

        arch = getattr(slide, "visual_archetype", None) or default_arch
        nodes = getattr(slide, "visual_nodes", None) or ["Ingress API", "Core Engine", "Vector Index", "LLM Output"]
        return {
            "visual_archetype": arch,
            "visual_nodes": [str(n)[:16] for n in nodes[:4]],
            "metric_label": getattr(slide, "metric_label", None) or "Stage Telemetry",
            "metric_before": getattr(slide, "metric_before", None) or "Naive: Bottleneck",
            "metric_after": getattr(slide, "metric_after", None) or "Optimized: 18x Faster",
            "math_formula": getattr(slide, "math_formula", None) or "Complexity: O(N²) -> O(log N)",
        }

    def _wrap_text(self, text: str, width: int = 36, max_lines: int = 4) -> str:
        clean = re.sub(r"\s+", " ", text or "").strip()
        lines = textwrap.wrap(clean, width=width)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1][: max(0, width - 3)] + "..."
        return "\n".join(lines)

    def _build_synchronized_segments(self, carousel: CarouselPost) -> List[Dict[str, Any]]:
        segments: List[Dict[str, Any]] = []

        hook_narration = f"{carousel.topic}. Let's walk through the production bottlenecks and exact architectural fixes."
        hook_audio = os.path.join(self.temp_dir, "seg_00_hook.mp3")
        asyncio.run(self._synthesize_segment(hook_narration, hook_audio))

        compact = re.sub(r"\s+", " ", carousel.topic).strip()
        if len(compact) > 42:
            compact = compact[:39] + "..."

        segments.append({
            "type": "hook",
            "audio_path": hook_audio,
            "duration": self._get_audio_duration(hook_audio),
            "title_wrapped": self._wrap_text(carousel.topic, width=24, max_lines=3),
            "compact_title": compact,
            "pillar": carousel.pillar.upper()[:28],
        })

        for idx, slide in enumerate(carousel.slides[:5]):
            narration = (
                slide.voiceover.strip()
                if getattr(slide, "voiceover", None)
                else f"{slide.headline}. {slide.content}"
            )
            audio_path = os.path.join(self.temp_dir, f"seg_{idx+1:02d}_slide.mp3")
            asyncio.run(self._synthesize_segment(narration, audio_path))

            detail_source = (
                slide.content
                if getattr(slide, "content", None) and len(slide.content.strip()) > 15
                else narration
            )

            meta = self._smart_fallback_metadata(idx, slide)

            segments.append({
                "type": "slide",
                "index": idx,
                "audio_path": audio_path,
                "duration": self._get_audio_duration(audio_path),
                "tag": getattr(slide, "tag", f"STAGE 0{idx+1}").upper()[:26],
                "node_label": self._extract_short_node_title(slide.headline, f"Stage {idx+1}"),
                "headline": self._wrap_text(slide.headline, width=28, max_lines=2),
                "detail": self._wrap_text(detail_source, width=36, max_lines=4),
                **meta,
            })

        cta_narration = (
            f"Comment {carousel.trigger_keyword} below and I will send you the full production repository and architecture blueprint."
        )
        cta_audio = os.path.join(self.temp_dir, "seg_99_cta.mp3")
        asyncio.run(self._synthesize_segment(cta_narration, cta_audio))
        segments.append({
            "type": "cta",
            "audio_path": cta_audio,
            "duration": self._get_audio_duration(cta_audio),
            "keyword": carousel.trigger_keyword.upper()[:18],
        })

        return segments

    def _write_manim_files(self, segments: List[Dict[str, Any]]) -> str:
        payload = {
            "hook": segments[0],
            "slides": [s for s in segments if s["type"] == "slide"],
            "cta": segments[-1],
        }

        json_path = os.path.join(self.temp_dir, "scene_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        script_path = os.path.join(self.temp_dir, "render_scene.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(MANIM_SCENE_TEMPLATE)

        return script_path

    def render_animated_reel(self, carousel: CarouselPost, output_filename: str = "carousel_reel.mp4") -> str:
        logger.info("AnimationEngine: Synthesizing 2-beat voiceover segments for human-like storyboard...")
        segments = self._build_synchronized_segments(carousel)
        total_audio = sum(s["duration"] for s in segments)
        logger.info(f"AnimationEngine: Compiled {len(segments)} segments (Total duration: {total_audio:.2f}s)")

        script_path = self._write_manim_files(segments)
        output_video_path = os.path.join(self.output_dir, output_filename)

        cmd = [
            "manim",
            "-ql",
            "--fps", "30",
            "-r", "1080,1920",
            "--media_dir", self.temp_dir,
            script_path,
            "HumanTouchArchitectureReel"
        ]

        logger.info("AnimationEngine: Rendering 9:16 bespoke storyboard via Manim...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Manim stderr:\n{result.stderr}")
            raise RuntimeError(f"Manim render failed: {result.stderr[-500:]}")

        raw_manim_video = None
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file == "HumanTouchArchitectureReel.mp4":
                    raw_manim_video = os.path.join(root, file)
                    break
            if raw_manim_video:
                break

        if not raw_manim_video:
            raise FileNotFoundError("Compiled HumanTouchArchitectureReel.mp4 not found.")

        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
        except ImportError:
            from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips

        audio_clips = [AudioFileClip(s["audio_path"]) for s in segments]
        full_audio = concatenate_audioclips(audio_clips)

        video_clip = VideoFileClip(raw_manim_video)

        if hasattr(video_clip, "with_audio"):
            final_clip = video_clip.with_audio(full_audio)
        else:
            video_clip.audio = full_audio
            final_clip = video_clip

        final_clip.write_videofile(
            output_video_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            bitrate="4500k",
            logger=None
        )

        video_clip.close()
        full_audio.close()
        for c in audio_clips:
            c.close()
        final_clip.close()

        logger.info(f"AnimationEngine: Human-touch storyboard reel saved -> {output_video_path}")
        return output_video_path

    def render_test_reel(
        self,
        custom_topic: str = "Why Multi-Agent RAG Collapses Under 10k Concurrent Users",
        output_filename: str = "test_manim_reel.mp4"
    ) -> str:
        """
        Tests all 5 distinct visual archetypes (topology_flow, token_stream, vector_subspace,
        probability_dist, storage_tiers) with realistic Beat 1 -> Beat 2 telemetry transitions.
        """
        mock_carousel = CarouselPost(
            topic=custom_topic,
            pillar="Architecture Teardown",
            trigger_keyword="AGENTSCALE",
            caption="Production multi-agent RAG teardown.",
            slides=[
                Slide(
                    slide_num=1,
                    tag="STAGE 01 // INGRESS",
                    headline="Async Event Bus vs Sync Blocking",
                    content="Synchronous agent handoffs block worker threads under burst traffic. Decouple tool calls behind a partitioned Kafka or Redis stream.",
                    voiceover="In a naive setup, synchronous agent calls block threads and trigger HTTP 429 timeouts. By decoupling requests through a partitioned Redis stream, worker throughput scales elastically.",
                    visual_type="topology_flow",
                    visual_archetype="topology_flow",
                    visual_nodes=["FastAPI Ingress", "Sync ThreadLock", "vLLM Cluster", "Redis AsyncBus"],
                    metric_label="Ingress P99 Latency",
                    metric_before="2,450 ms (Thread Starvation)",
                    metric_after="19 ms (Async Redis Stream)",
                    math_formula="Throughput: λ_max = N_workers / W_sync"
                ),
                Slide(
                    slide_num=2,
                    tag="STAGE 02 // CHUNKING",
                    headline="Semantic Sliding Window Overlap",
                    content="Hard 512-token boundaries slice right through function definitions. Sliding windows with 15% overlap preserve full syntax trees.",
                    voiceover="Hard token splits sever code blocks in half, destroying context. Sliding attention windows with a fifteen percent token overlap preserve complete syntax boundaries.",
                    visual_archetype="token_stream",
                    visual_nodes=["AST_Header", "def_auth()", "jwt_verify", "return_200"],
                    metric_label="Context Recall@5",
                    metric_before="61.4% (Broken AST Splits)",
                    metric_after="94.8% (15% Sliding Overlap)",
                    math_formula="L_chunk = W_size - S_stride"
                ),
                Slide(
                    slide_num=3,
                    tag="STAGE 03 // EMBEDDING",
                    headline="Hypersphere Cosine Alignment",
                    content="Out-of-domain queries drift toward orthogonal noise vectors. Fine-tuned Matryoshka adapters rotate query projections onto the target key subspace.",
                    voiceover="Without domain adaptation, query embeddings drift toward noisy orthogonal vectors. Applying a lightweight linear adapter rotates the query vector directly into alignment with the target key.",
                    visual_archetype="vector_subspace",
                    visual_nodes=["Query Vec q", "Target Key k+", "Orthogonal k-", "Subspace W"],
                    metric_label="Angular Alignment",
                    metric_before="cos(θ) = 0.34 (High Drift)",
                    metric_after="cos(θ) = 0.96 (Locked Match)",
                    math_formula="cos(θ) = (Q · K) / (||Q|| ||K||)"
                ),
                Slide(
                    slide_num=4,
                    tag="STAGE 04 // RERANKING",
                    headline="Cross-Encoder Softmax Sharpening",
                    content="Bi-encoder retrieval returns flat, noisy candidate scores. A local Cross-Encoder applies temperature scaling to isolate the true answer passage.",
                    voiceover="Raw vector retrieval assigns nearly flat probabilities across noisy documents. Passing candidates through a cross-encoder sharpens the softmax distribution onto the exact answer passage.",
                    visual_archetype="probability_dist",
                    visual_nodes=["Noise_Chunk", "True_Spec*", "Stale_Doc", "Log_Snippet"],
                    metric_label="Top-1 Precision",
                    metric_before="28% Confidence (Flat Noise)",
                    metric_after="81% Confidence (Sharp Peak)",
                    math_formula="P(y_i) = exp(z_i/T) / Σ exp(z_j/T)"
                ),
                Slide(
                    slide_num=5,
                    tag="STAGE 05 // CACHING",
                    headline="L1 Semantic Cache vs Cold Scan",
                    content="Re-running full LLM synthesis for recurring intents wastes GPU cycles. L1 Redis semantic caching serves verified answers in 14 milliseconds.",
                    voiceover="Hitting cold disk indexes on every repeat query burns GPU budget and spikes tail latency. Intercepting queries at Tier One in Redis returns verified answers in fourteen milliseconds.",
                    visual_archetype="storage_tiers",
                    visual_nodes=["L1 Redis Semantic Cache", "L2 HNSW Memory Graph", "L3 Cold Parquet Store", "LLM Gateway"],
                    metric_label="End-to-End Cost & Latency",
                    metric_before="1,180 ms // $0.042 per req",
                    metric_after="14 ms // $0.001 per req",
                    math_formula="E[T] = p_hit·T_L1 + (1 - p_hit)·T_LLM"
                ),
            ]
        )
        logger.info(f"AnimationEngine: Running 5-archetype human-touch storyboard test -> '{custom_topic}'")
        return self.render_animated_reel(mock_carousel, output_filename=output_filename)