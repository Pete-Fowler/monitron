#!/usr/bin/python3
import os
import re
import subprocess
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")

from gi.repository import Gtk as gtk, AppIndicator3 as appindicator


def main():
  indicator = appindicator.Indicator.new(
    "customtray", "semi-starred-symbolic", appindicator.IndicatorCategory.APPLICATION_STATUS
  )
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  indicator.set_menu(menu())
  gtk.main()


def get_session_type():
  """Return 'wayland' or 'x11' based on environment."""
  s = os.environ.get("XDG_SESSION_TYPE") or os.environ.get("WAYLAND_DISPLAY")
  if s and s.lower().startswith("wayland"):
    return "wayland"
  return "x11"


def get_connected_outputs():
  """Return list of connected outputs using xrandr. Returns [] if xrandr not available or on Wayland."""
  try:
    out = subprocess.check_output(["xrandr", "--query"], text=True)
  except Exception:
    return []

  connected = []
  for line in out.splitlines():
    m = re.match(r"^(\S+)\s+connected", line)
    if m:
      connected.append(m.group(1))
  return connected


def run_xrandr(args):
  try:
    subprocess.check_call(["xrandr"] + args)
    subprocess.call(["notify-send", "Monitron", "Display configuration applied"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError as e:
    subprocess.call(["notify-send", "Monitron", f"xrandr failed: {e.returncode}"])


def use_only(output):
  outputs = get_connected_outputs()
  if output not in outputs:
    subprocess.call(["notify-send", "Monitron", f"Output {output} not connected"])
    return
  args = []
  for out in outputs:
    if out == output:
      args += ["--output", out, "--auto", "--primary"]
    else:
      args += ["--output", out, "--off"]
  run_xrandr(args)


def extend_two(a, b, position="right-of"):
  # position can be right-of, left-of, above, below
  args = ["--output", a, "--auto", "--primary", "--output", b, "--auto", f"--{position}", a]
  run_xrandr(args)


def mirror(a, b):
  args = ["--output", a, "--auto", "--primary", "--output", b, "--auto", "--same-as", a]
  run_xrandr(args)


def open_gnome_displays(_=None):
  # On Wayland GNOME, programmatic xrandr calls won't work; open settings instead
  subprocess.Popen(["gnome-control-center", "display"])


def autodetect(_=None):
  st = get_session_type()
  if st == "wayland":
    open_gnome_displays()
    return
  outputs = get_connected_outputs()
  if len(outputs) >= 2:
    extend_two(outputs[0], outputs[1])
  elif len(outputs) == 1:
    use_only(outputs[0])
  else:
    subprocess.call(["notify-send", "Monitron", "No connected displays found"]) 


def menu():
  menu = gtk.Menu()

  command_one = gtk.MenuItem(label="My Notes")
  command_one.connect("activate", note)
  menu.append(command_one)

  menu.append(gtk.SeparatorMenuItem())

  st = get_session_type()
  if st == "wayland":
    itm = gtk.MenuItem(label="Wayland session detected (GNOME)")
    itm.set_sensitive(False)
    menu.append(itm)
    open_disp = gtk.MenuItem(label="Open GNOME Display Settings")
    open_disp.connect("activate", open_gnome_displays)
    menu.append(open_disp)
  else:
    outputs = get_connected_outputs()
    if not outputs:
      ni = gtk.MenuItem(label="No displays detected")
      ni.set_sensitive(False)
      menu.append(ni)
    else:
      for out in outputs:
        mi = gtk.MenuItem(label=f"Use only {out}")
        mi.connect("activate", lambda w, o=out: use_only(o))
        menu.append(mi)

      if len(outputs) >= 2:
        a, b = outputs[0], outputs[1]
        mi_ext = gtk.MenuItem(label=f"Extend: {a} -> {b}")
        mi_ext.connect("activate", lambda w, x=a, y=b: extend_two(x, y, "right-of"))
        menu.append(mi_ext)

        mi_mirror = gtk.MenuItem(label=f"Mirror: {a} <-> {b}")
        mi_mirror.connect("activate", lambda w, x=a, y=b: mirror(x, y))
        menu.append(mi_mirror)

  menu.append(gtk.SeparatorMenuItem())

  autod = gtk.MenuItem(label="Auto-detect")
  autod.connect("activate", autodetect)
  menu.append(autod)

  exittray = gtk.MenuItem(label="Exit Tray")
  exittray.connect("activate", quit)
  menu.append(exittray)

  menu.show_all()
  return menu


def note(_):
  editor = os.environ.get("EDITOR", "gedit")
  try:
    subprocess.Popen([editor, os.path.expanduser("~/Documents/notes.txt")])
  except Exception:
    subprocess.Popen(["gedit", os.path.expanduser("~/Documents/notes.txt")])


def quit(_=None):
  gtk.main_quit()


if __name__ == "__main__":
  main()