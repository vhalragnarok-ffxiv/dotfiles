# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import socket
import subprocess
import json

from libqtile import qtile, hook
from libqtile.config import Click, Drag, Group, KeyChord, Key, Match, Screen, KeyChord
from libqtile import layout, bar, hook
from libqtile import widget
from libqtile.widget import StatusNotifier
from libqtile import config
from libqtile.layout import  base
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.backend.wayland import InputConfig
from typing import List
from libqtile.backend.wayland import InputConfig
from qtile_extras import widget as extra_widget
from qtile_extras.widget.decorations import BorderDecoration
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras.widget.decorations import PowerLineDecoration


mod = "mod4"
terminal = guess_terminal()

#Autostart
@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.Popen([home])

#Dracula Colors....
colors = [["#282A36", "#282A36"],
          ["#1c1f24", "#1c1f24"],
          ["#F8F8F2", "#F8F8F2"],
          ["#FF5555", "#FF5555"],
          ["#50FA7B", "#50FA7B"],
          ["#FFB86C", "#FFB86C"],
          ["#8BE9FD", "#8BE9FD"],
          ["#BD93F9", "#BD93F9"],
          ["#6272A4", "#6272A4"],
          ["#BD93F9", "#BD93F9"]]

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "shift"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "shift"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("ulauncher"), desc="Spawn a command using a prompt widget"),
    Key([], "Print", lazy.spawn("flameshot gui"), desc="Flameshot Screenshot"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(
        border_focus = colors[4],
        border_normal = colors[8],
        border_width=2,
        num_columns=3,
        margin = 4),
    #layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]



widget_defaults = dict(
    font="Ubuntu Nerd",
    fontsize=14,
    padding=0,
    background=colors[2],
)
extension_defaults = widget_defaults.copy()

rd = RectDecoration(
    use_widget_background=True,
    radius=12,
    filled=True,
    colour='#00000000',
    group=True,
    clip=True,
    #padding_x=-5,
)
rd_dec = {"decorations": [rd]}

screens = [
    Screen(
        top=bar.Bar([
              
              # Separators allow for extra padding around widgets so it looks good
            widget.Spacer(background = '#00000000'),
            extra_widget.Sep(linewidth = 0, padding=9, background = colors[0], **rd_dec),
            widget.GroupBox(
                    #    font = "Sans Bold",
                       font = "Ubuntu Nerd",
                       fontsize = 13,
                       markup = True,
                       margin_y = 4,
                       margin_x = 2,
                       padding_y = 3,
                       padding_x = 7,
                       borderwidth = 2,
                       active = colors[2],
                       inactive = '#696969', 
                       rounded = False,
                       highlight_color = colors[1],
                       highlight_method = "line",
                       this_current_screen_border = colors[6],
                       this_screen_border = colors [4],
                       other_current_screen_border = colors[6],
                       other_screen_border = colors[4],
                       foreground = colors[2],
                       background = colors[0],
                       **rd_dec
                       ),
            extra_widget.Sep(linewidth = 0, padding=9, background = colors[0], **rd_dec),
            widget.Spacer( background = '#00000000'),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
              #widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
              #widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
              #widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
            extra_widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
            widget.Volume(
                       foreground = colors[0],
                       background = colors[7],
                       fmt = ' 󰕾   {}',
                       padding = 5,
                       **rd_dec,
                       mouse_callbacks={
                       "Button1": lazy.spawn("pavucontrol")
                       }
                       ),
            extra_widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
            #extra_widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
              #widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
              #widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
              #widget.Sep(linewidth = 0, padding=9, background = colors[7], **rd_dec),
            extra_widget.Sep(linewidth = 0, padding=7, background = '#00000000'),
            extra_widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
            widget.Clock(
                       foreground = colors[2],
                       background = colors[8],
                       format = "   %I:%M %p ",
                       **rd_dec
                       ),
             
            widget.Sep(linewidth = 0, padding=9, background = colors[8], **rd_dec),
            widget.Sep(
                        linewidth = 0,
                        foreground = '#00000000',
                        background = '#00000000',
                        padding = 4),
            widget.StatusNotifier(
                       background = colors[0],
                       #icon_theme = "Sardi-Flat-Arc",
                       icon_size = 16,
                       # The following options are for the StatusNotfier from qtile-extras
                       highlight_colour = '308dcd', # 308dcd is a darker shade of 51afef that looks closer to the way 51afef is rendered on the WindowName widget
                       menu_background = '282c34',
                       menu_font = 'Ubuntu Bold',
                       menu_fontsize = 11,
                       menu_foreground = 'dfdfdf',
                       # The padding is for either version of the StatusNotifier widget
                       padding = 1,
                       **rd_dec
                        ),
            widget.Systray(
                       background = colors[0],
                       icon_size = 16,
                       padding = 1,
                       **rd_dec
                       ),
   
            ],
            24,
            background="00000000",
            margin = [5, 5, 5, 5],
            
        ),
        wallpaper="/home/vhal/Pictures/wallpaper.png",
        wallpaper_mode="fill"
    )
]


# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    border_focus = colors[4],
        border_normal = colors[8],
        border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

