#!/bin/sh
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
input-remapper-control --command stop-all && input-remapper-control --command autoload &&
xset -s off &&
xset -dpms &&
wired &
