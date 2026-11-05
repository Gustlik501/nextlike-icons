#!/usr/bin/env python3
"""Create private visual evidence; never connect GTK/Thunar to the live session."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import wave
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / ".work"


def isolated(result):
    WORK.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="visual-", dir=WORK) as temporary:
        home = Path(temporary)
        for directory in ["config/gtk-3.0", "cache", "data", "state", "runtime", "samples"]:
            (home / directory).mkdir(parents=True, exist_ok=True)
        (home / "runtime").chmod(0o700)
        (home / "config/gtk-3.0/settings.ini").write_text(
            "[Settings]\ngtk-icon-theme-name=Nextlike\ngtk-theme-name=Adwaita\n"
            "gtk-font-name=Liberation Sans 10\ngtk-application-prefer-dark-theme=false\n"
        )
        preferences = home / "config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml"
        preferences.parent.mkdir(parents=True)
        preferences.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<channel name="thunar" version="1.0">
  <property name="last-view" type="string" value="ThunarIconView"/>
  <property name="last-window-width" type="int" value="1200"/>
  <property name="last-window-height" type="int" value="740"/>
  <property name="last-icon-view-zoom-level" type="string" value="THUNAR_ZOOM_LEVEL_75_PERCENT"/>
  <property name="misc-thumbnail-mode" type="string" value="THUNAR_THUMBNAIL_MODE_NEVER"/>
  <property name="misc-single-click" type="bool" value="false"/>
</channel>
''')
        from PIL import Image
        samples = home / "samples"
        for name in ["Documents", "Downloads", "Music", "Pictures", "Videos", "Projects", "Templates"]:
            (samples / name).mkdir()
        (samples / "Notes.txt").write_text("Nextlike isolated icon verification.\n")
        script = samples / "Script.sh"
        script.write_text("#!/bin/sh\nprintf 'Nextlike\\n'\n")
        script.chmod(0o755)
        Image.new("RGB", (64, 64), "#966c42").save(samples / "Picture.png")
        (samples / "Document.pdf").write_bytes(b"%PDF-1.4\n% Nextlike MIME icon sample\n%%EOF\n")
        with zipfile.ZipFile(samples / "Archive.zip", "w") as archive:
            archive.writestr("README.txt", "Nextlike sample\n")
        with wave.open(str(samples / "Sound.wav"), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b"\0\0" * 800)
        (samples / "Movie.mp4").write_bytes(b"\0\0\0\x18ftypmp42\0\0\0\0mp42isom")
        env = os.environ.copy()
        for key in ["DISPLAY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "DBUS_SESSION_BUS_PID",
                    "SESSION_MANAGER", "HYPRLAND_INSTANCE_SIGNATURE", "GTK_THEME", "GTK2_RC_FILES",
                    "XAUTHORITY", "DESKTOP_SESSION", "XDG_CURRENT_DESKTOP"]:
            env.pop(key, None)
        env.update({
            "HOME": str(home), "XDG_CONFIG_HOME": str(home / "config"),
            "XDG_CACHE_HOME": str(home / "cache"), "XDG_DATA_HOME": str(home / "data"),
            "XDG_STATE_HOME": str(home / "state"), "XDG_RUNTIME_DIR": str(home / "runtime"),
            "XDG_DATA_DIRS": str(result / "share") + ":" + env.get("XDG_DATA_DIRS", "")
                             + ":/etc/profiles/per-user/gustl/share:/run/current-system/sw/share",
            "GDK_BACKEND": "x11", "GSETTINGS_BACKEND": "memory", "NO_AT_BRIDGE": "1",
            "GIO_USE_VFS": "local", "GIO_USE_VOLUME_MONITOR": "unix", "GTK_USE_PORTAL": "0",
            "XDG_SESSION_TYPE": "x11", "XDG_CURRENT_DESKTOP": "XFCE",
        })
        command = ["xvfb-run", "-a", "-s", "-screen 0 1280x800x24 -nolisten tcp",
                   "dbus-run-session", "--", sys.executable, str(Path(__file__).resolve()),
                   "--inside", str(result), str(samples)]
        # Separate process group: on timeout only our test session is terminated.
        with (WORK / "visual-check.log").open("w") as log:
            process = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                status = process.wait(timeout=50)
            finally:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            if status:
                raise RuntimeError(f"Visual check failed ({status}); see .work/visual-check.log")


def inside(result, samples):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gio, Gtk
    from PIL import Image, ImageDraw, ImageFont
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("check_theme", ROOT / "scripts/check-theme.py")
    check = module_from_spec(spec)
    spec.loader.exec_module(check)
    theme_path, _ = check.inspect(result / "share/icons/Nextlike")
    Gtk.init([])
    settings = Gtk.Settings.get_default()
    assert settings.get_property("gtk-icon-theme-name") == "Nextlike"
    theme = Gtk.IconTheme.get_default()
    names = check.REQUIRED + check.EXTRA
    assert len(names) == 40
    sheet = Image.new("RGB", (1000, 640), "#C0C0C0")
    draw = ImageDraw.Draw(sheet)
    fonts = list(Path("/nix/store").glob("*-liberation-fonts-*/share/fonts/truetype/LiberationSans-Regular.ttf"))
    font = ImageFont.truetype(str(fonts[0]), 12) if fonts else ImageFont.load_default()
    rows = ["name\tGTK3-48px-path"]
    for number, name in enumerate(names):
        info = theme.lookup_icon(name, 48, Gtk.IconLookupFlags.FORCE_SIZE)
        assert info is not None, name
        path = Path(info.get_filename()).resolve()
        assert path.is_relative_to(theme_path), (name, path)
        rows.append(f"{name}\t{path}")
        pixbuf = info.load_icon()
        # Use GTK's renderer rather than assuming the PNG dimensions are 48px.
        png = WORK / f".render-{number}.png"
        pixbuf.savev(str(png), "png", [], [])
        icon = Image.open(png).convert("RGBA")
        x, y = (number % 8) * 125, (number // 8) * 128
        sheet.paste(icon, (x + (125 - icon.width) // 2, y + 8 + (48 - icon.height) // 2), icon)
        # Wrap on hyphens, keeping freedesktop names legible in compact cells.
        lines, line = [], ""
        for part in name.split("-"):
            candidate = line + ("-" if line else "") + part
            if draw.textlength(candidate, font=font) > 119 and line:
                lines.append(line + "-")
                line = part
            else:
                line = candidate
        lines.append(line)
        for offset, line in enumerate(lines):
            draw.text((x + (125 - draw.textlength(line, font=font)) / 2, y + 65 + offset * 14),
                      line, font=font, fill="#171717")
        png.unlink()
    sheet.save(WORK / "nextlike-sheet.png")
    (WORK / "gtk-coverage.tsv").write_text("\n".join(rows) + "\n")
    # Check the actual concrete GIO names for the sample files, not only generics.
    mime_rows = ["sample\tcontent-type\ticon-names\tGTK3-48px-path"]
    for sample in sorted(samples.iterdir()):
        info = Gio.File.new_for_path(str(sample)).query_info(
            "standard::icon,standard::content-type", Gio.FileQueryInfoFlags.NONE, None)
        names = info.get_icon().get_names()
        # Thunar can request the first concrete name directly, so do not let a
        # generic native alternative hide an inherited concrete MIME icon.
        chosen = theme.lookup_icon(names[0], 48, Gtk.IconLookupFlags.FORCE_SIZE)
        assert chosen is not None, sample
        path = Path(chosen.get_filename()).resolve()
        assert path.is_relative_to(theme_path), (sample.name, names, path)
        mime_rows.append(f"{sample.name}\t{info.get_content_type()}\t{','.join(names)}\t{path}")
    (WORK / "thunar-mime-coverage.tsv").write_text("\n".join(mime_rows) + "\n")
    subprocess.run(["thunar", "--version"], check=True, timeout=10)
    thunar = subprocess.Popen(["thunar", str(samples)], stdin=subprocess.DEVNULL)
    try:
        time.sleep(5)
        assert thunar.poll() is None, "Thunar exited early"
        windows = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--class", "Thunar"],
                                          text=True, timeout=5).split()
        assert windows, "No visible Thunar window"
        subprocess.run(["xdotool", "windowsize", windows[-1], "1200", "740"], check=True, timeout=5)
        subprocess.run(["xdotool", "windowmove", windows[-1], "20", "20"], check=True, timeout=5)
        time.sleep(1)
        subprocess.run(["magick", "import", "-window", "root", str(WORK / "nextlike-thunar.png")],
                       check=True, timeout=10)
    finally:
        thunar.terminate()
        try:
            thunar.wait(timeout=5)
        except subprocess.TimeoutExpired:
            thunar.kill()
            thunar.wait()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--inside":
        inside(Path(sys.argv[2]), Path(sys.argv[3]))
    elif len(sys.argv) == 2:
        isolated(Path(sys.argv[1]).resolve(strict=True))
        print("Created .work/nextlike-sheet.png, .work/nextlike-thunar.png and .work/gtk-coverage.tsv")
    else:
        sys.exit("Usage: nix develop -c python3 scripts/visual-check.py result")
