#!/usr/bin/env python3
"""Render layout illustrations from theme assets; no running desktop needed.

Requires PyGObject, Pycairo, Pango and librsvg. The nine-slice margins and
highlight placement model Classic UI with the Overlay offset fix applied;
this is not a live IME capture or a check of the installed Fcitx5 renderer.
"""

import argparse
import configparser
import html
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
gi.require_version("Rsvg", "2.0")
from gi.repository import Pango, PangoCairo, Rsvg

ROOT = Path(__file__).resolve().parents[1]


def color(cr, value):
    cr.set_source_rgb(*(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)))


def layout(cr, text, font="Noto Sans CJK SC 10", markup=False):
    result = PangoCairo.create_layout(cr)
    PangoCairo.context_set_resolution(result.get_context(), 96)
    result.set_font_description(Pango.FontDescription.from_string(font))
    result.set_single_paragraph_mode(True)
    if markup:
        result.set_markup(text, -1)
    else:
        result.set_text(text, -1)
    return result


def text(cr, value, x, y, fill, font="Noto Sans CJK SC 10"):
    color(cr, fill)
    cr.move_to(x, y)
    PangoCairo.show_layout(cr, layout(cr, value, font))


class Theme:
    def __init__(self, name, font="Noto Sans CJK SC Regular 10px"):
        self.font = font
        self.directory = ROOT / name
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.optionxform = str
        self.config.read(self.directory / "theme.conf", encoding="utf-8")
        self.assets = {}
        for path in self.directory.glob("*.svg"):
            element = ET.parse(path).getroot()
            width, height = (float(element.attrib[key]) for key in ("width", "height"))
            surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (0, 0, width, height))
            viewport = Rsvg.Rectangle()
            viewport.x, viewport.y, viewport.width, viewport.height = 0, 0, width, height
            Rsvg.Handle.new_from_file(str(path)).render_document(cairo.Context(surface), viewport)
            self.assets[path.name] = (surface, width, height)

    def margins(self, section):
        return tuple(self.config.getint(section, key) for key in ("Left", "Right", "Top", "Bottom"))

    def icon(self, cr, filename, x, y, alpha=1):
        cr.set_source_surface(self.assets[filename][0], x, y)
        cr.paint_with_alpha(alpha)

    def background(self, cr, section, x, y, width, height):
        config = self.config[section]
        surface, sw, sh = self.assets[config["Image"]]
        left, right, top, bottom = self.margins(section + "/Margin")
        if width < left + right or height < top + bottom:
            raise ValueError(f"Panel too small for nine-slice margins: {section}")
        sx, sy = (0, left, sw - right, sw), (0, top, sh - bottom, sh)
        dx, dy = (0, left, width - right, width), (0, top, height - bottom, height)
        scale_x, scale_y = cr.get_target().get_device_scale()
        # Classic UI snaps tile boundaries to device pixels at fractional DPI.
        dx = [(math.floor if i % 2 == 0 else math.ceil)((x + edge) * scale_x) / scale_x
              for i, edge in enumerate(dx)]
        dy = [(math.floor if i % 2 == 0 else math.ceil)((y + edge) * scale_y) / scale_y
              for i, edge in enumerate(dy)]
        for row in range(3):
            for column in range(3):
                cr.save()
                cr.rectangle(dx[column], dy[row], dx[column + 1] - dx[column], dy[row + 1] - dy[row])
                cr.clip()
                cr.translate(dx[column], dy[row])
                cr.scale((dx[column + 1] - dx[column]) / (sx[column + 1] - sx[column]),
                         (dy[row + 1] - dy[row]) / (sy[row + 1] - sy[row]))
                cr.set_source_surface(surface, -sx[column], -sy[row])
                cr.paint()
                cr.restore()
        if config.get("Overlay"):
            # Model the corrected, background-relative Center Left overlay.
            overlay = config["Overlay"]
            _, ow, oh = self.assets[overlay]
            if config.getboolean("HideOverlayIfOversize", fallback=False) and (ow > width or oh > height):
                return
            self.icon(cr, overlay, x + config.getint("OverlayOffsetX", 0),
                      y + math.floor((height - oh) / 2) + config.getint("OverlayOffsetY", 0))

    def panel(self, cr, x, y, candidates, preedit="", vertical=False, selected=0):
        cfg = self.config["InputPanel"]
        content_l, content_r, content_t, content_b = self.margins("InputPanel/ContentMargin")
        text_l, text_r, text_t, text_b = self.margins("InputPanel/TextMargin")
        hi_l, hi_r, hi_t, hi_b = self.margins("InputPanel/Highlight/Margin")
        layouts = []
        for index, candidate in enumerate(candidates):
            label_key = "HighlightCandidateLabelColor" if index == selected else "CandidateLabelColor"
            label_color = self.config["InputPanel/" + label_key]["Value"]
            word_color = cfg["HighlightCandidateColor" if index == selected else "NormalColor"]
            markup = (f'<span foreground="{label_color}">{index + 1}. </span>'
                      f'<span foreground="{word_color}">{html.escape(candidate)}</span>')
            layouts.append(layout(cr, markup, self.font, markup=True))
        sizes = [item.get_pixel_size() for item in layouts]
        line_h = max(h for _, h in sizes)
        row_h = line_h + text_t + text_b
        prev = self.config["InputPanel/PrevPage"]["Image"]
        next_ = self.config["InputPanel/NextPage"]["Image"]
        buttons_w = self.assets[prev][1] + self.assets[next_][1]
        cells_w = [w + text_l + text_r for w, _ in sizes]
        content_w = (max(cells_w) if vertical else sum(cells_w)) + buttons_w
        if preedit:
            content_w = max(content_w, layout(cr, preedit, self.font).get_pixel_size()[0] + text_l + text_r)
        width = content_l + content_r + content_w
        height = content_t + content_b + row_h * ((len(candidates) if vertical else 1) + bool(preedit))
        self.background(cr, "InputPanel/Background", x, y, width, height)
        tx, ty = x + content_l + text_l, y + content_t + text_t
        if preedit:
            text(cr, preedit, tx, ty, cfg["NormalColor"], self.font)
            ty += row_h
        for index, item in enumerate(layouts):
            if index == selected:
                hi_w = content_w - text_l - text_r if vertical else sizes[index][0]
                self.background(cr, "InputPanel/Highlight", tx - hi_l, ty - hi_t,
                                hi_w + hi_l + hi_r, line_h + hi_t + hi_b)
            cr.move_to(tx, ty + (line_h - sizes[index][1]) / 2)
            PangoCairo.show_layout(cr, item)
            if vertical:
                ty += row_h
            else:
                tx += cells_w[index]
        button_x = x + width - content_r - buttons_w
        last_top = y + height - content_b - text_b - line_h - hi_t
        for filename, alpha in ((prev, 0.3), (next_, 1)):
            _, iw, ih = self.assets[filename]
            self.icon(cr, filename, button_x,
                      last_top + math.floor((line_h + hi_t + hi_b - ih) / 2), alpha)
            button_x += iw
        return width, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=float, default=2)
    parser.add_argument("--font", default="Noto Sans CJK SC Regular 10px")
    parser.add_argument("--palette", choices=("default", "vermilion"), default="default")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.scale) or not 0.5 <= args.scale <= 4:
        parser.error("--scale must be between 0.5 and 4")
    vermilion = args.palette == "vermilion"
    theme_names = (("win11-vermilion", "win11-vermilion-dark") if vermilion
                   else ("win11-light", "win11-dark"))
    output = args.output or ROOT / "preview" / ("vermilion.png" if vermilion else "themes.png")
    width, height = 1000, 540
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, math.ceil(width * args.scale), math.ceil(height * args.scale))
    surface.set_device_scale(args.scale, args.scale)
    cr = cairo.Context(surface)
    for index, name in enumerate(theme_names):
        theme = Theme(name, args.font)
        x = index * 500
        dark = index == 1
        backdrop = ("#211a19" if dark else "#f3ece6") if vermilion else ("#171a20" if dark else "#e9eef4")
        color(cr, backdrop)
        cr.rectangle(x, 0, 500, height)
        cr.fill()
        title_color = "#f5f5f5" if dark else "#1a1a1a"
        muted = "#aab4c2" if dark else "#566273"
        text(cr, theme.config["Metadata"]["Name"], x + 24, 23, title_color, "Noto Sans 17")
        text(cr, "fcitx5-win11-themes", x + 24, 57, muted, "Noto Sans 10")
        text(cr, "横排候选 / Horizontal", x + 24, 104, muted)
        theme.panel(cr, x + 16, 135, ["你", "泥", "尼", "拟", "呢", "倪", "逆"], selected=2 if vermilion else 0)
        text(cr, "预编辑行 / Preedit", x + 24, 209, muted)
        theme.panel(cr, x + 16, 237, ["你好", "你号", "拟好", "倪皓", "逆耗"], preedit="ni hao", selected=1 if vermilion else 0)
        text(cr, "竖排候选 / Vertical", x + 24, 339, muted)
        theme.panel(cr, x + 16, 366, ["微软拼音", "微软", "微缩", "微风"], vertical=True, selected=1)
        text(cr, f"{args.font} · layout illustration", x + 24, 513, muted, "Noto Sans 8")
    output.parent.mkdir(parents=True, exist_ok=True)
    surface.write_to_png(str(output))
    print(output)


if __name__ == "__main__":
    main()
