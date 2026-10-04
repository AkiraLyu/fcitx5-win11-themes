**English** | [中文](./README.md)

# fcitx5-win11-themes

Fcitx5 Classic User Interface themes adapted from [fcitx5-mellow-themes](https://github.com/sanweiya/fcitx5-mellow-themes), inspired by the Windows 11 Microsoft Pinyin candidate window.

Includes **Windows 11 Light** (`win11-light`) and **Windows 11 Dark** (`win11-dark`): 8 px outer corners, a thin border, soft shadow, neutral selection background and a short blue indicator on the left. Paging buttons work normally, and the indicator stays the same size for long candidates.

![Light and dark theme previews](./preview/themes.png)

The **Vermilion** variants retain the original Mellow Vermilion selection backgrounds and white selected text. A warm apricot indicator (`#FFE0B2`) provides a clear brightness contrast against the red:

| Theme | Directory | Selection background | Indicator | Indicator contrast |
| --- | --- | --- | --- | --- |
| Windows 11 Vermilion | `win11-vermilion` | `#C73E3A` | `#FFE0B2` | Approx. 3.96:1 |
| Windows 11 Vermilion Dark | `win11-vermilion-dark` | `#9E322E` | `#FFE0B2` | Approx. 5.61:1 |

![Vermilion light and dark previews](./preview/vermilion.png)

These layout illustrations use the actual theme SVGs, colors, margins and Pango text rendering. They show horizontal, preedit and vertical layouts; they are not Windows screenshots or checks of the installed Fcitx5 renderer. They model the corrected Overlay positioning. Actual dimensions depend on fonts, scaling and the input method.

## Install

Run in the project directory:

```sh
./install.sh
```

The script installs into `${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/themes/` without administrator privileges. It does not change your input method settings.

Manual alternative:

```sh
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/themes"
cp -r win11-light win11-dark win11-vermilion win11-vermilion-dark \
  "${XDG_DATA_HOME:-$HOME/.local/share}/fcitx5/themes/"
```

## Enable

Open **Fcitx5 Configuration → Addons → Classic User Interface → Configure**. Select **Windows 11 Light** as the theme and **Windows 11 Dark** as the dark theme. Enable following the system color scheme if desired.

For Vermilion, select **Windows 11 Vermilion** and **Windows 11 Vermilion Dark**, or set `Theme=win11-vermilion` and `DarkTheme=win11-vermilion-dark` manually.

For a closer match to Microsoft Pinyin:

- Disable the vertical candidate list and use seven Pinyin candidates per page.
- Use `Noto Sans CJK SC Regular 10px`. The `px` suffix specifies a pixel size. Fonts are not bundled.
- Enable the global “Preedit enabled by default” option so supporting applications can show preedit at the caret. Fcitx5 Pinyin may also display an auxiliary Pinyin row; this theme accommodates it.
- Disable following the system accent color to retain the selected palette.

For manual configuration, update the corresponding top-level options in `${XDG_CONFIG_HOME:-$HOME/.config}/fcitx5/conf/classicui.conf`. Preserve unrelated settings:

```ini
Vertical Candidate List=False
Font="Noto Sans CJK SC Regular 10px"
Theme=win11-light
DarkTheme=win11-dark
UseDarkTheme=True
UseAccentColor=False
```

Run `fcitx5-remote -r` to reload. To always use one variant, disable following the system color scheme and select that theme. Reopen the configuration tool if newly installed themes are not listed yet.

## Compatibility

Designed for Fcitx5 Classic User Interface on Wayland / X11, including HiDPI, with scalable SVG assets. Horizontal candidates are closest to Microsoft Pinyin; vertical lists retain full-width selection. Older Fcitx5 versions may ignore the newer label and comment color options.

The indicator uses Classic UI's Overlay feature and requires the Overlay coordinate offset fix in Fcitx5. An unpatched renderer draws it near the candidate window's top-left corner instead of following the selection; changing palettes does not resolve that issue.

Candidate content, label punctuation, preedit rows, page size and layout are controlled by the input method and client. A theme cannot add Windows clipboard, emoji or expanded candidate panels. Opaque surfaces and built-in shadows avoid depending on compositor blur support. Switch to Classic User Interface if a desktop panel such as Kimpanel is rendering your candidates.

## Editing and previews

All four themes are self-contained. `panel.svg` draws the surface, `highlight.svg` the selection background, `selection.svg` the indicator, and the remaining SVGs the paging and menu icons.

Candidate spacing is tuned for `Noto Sans CJK SC Regular 10px`: 4 / 5 px top / bottom text and highlight margins compensate for glyphs sitting slightly low in the line box. Panel content margins are 10 / 10 px vertically, including the shadow; left / right text margins are 11 / 7 px.

With Python 3, PyGObject, Pycairo, Pango and librsvg installed, regenerate previews using:

```sh
python3 tools/render-preview.py
python3 tools/render-preview.py --palette vermilion
```

Use `--font "Noto Sans CJK SC Regular 10px" --scale 1.25` to illustrate a particular font and scale.

References: [Microsoft Pinyin candidate window](https://support.microsoft.com/zh-cn/windows/hardware/input-devices/microsoft-simplified-chinese-ime) and [Fcitx5 theme layout documentation](https://fcitx-im.org/wiki/Fcitx_5_Theme).

## License

This project is derived from [fcitx5-mellow-themes](https://github.com/sanweiya/fcitx5-mellow-themes) and keeps its [BSD 2-Clause license](./LICENSE). The license file retains the upstream copyright notice for sanweiya; the themes, scripts and documentation added here are released under the same terms.

This project is not affiliated with Microsoft and ships no assets provided by Microsoft.
