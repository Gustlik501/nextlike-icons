#!/usr/bin/env python3
"""Implement Radić's Nextlike 0.9.3 recipe, with documented lookup fixes.

Artwork is read exclusively from build-time sources; none is generated in git.
"""
import configparser
from pathlib import Path
import shutil
import subprocess
import sys

sources, out = map(Path, sys.argv[1:])
osdir = sources / "openstepicons-1.1/icons.tiff"
gsdir = sources / "gnustep-icons-1.0/icons"
wmdir = sources / "wmicons/share/WindowMaker/Pixmaps"
shutil.copytree(sources / "GNUstep", out, symlinks=True)


def convert(source, dest, *options, gamma=False):
    target = out / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    # Unlink first: writing through an upstream alias would alter its target.
    target.unlink(missing_ok=True)
    subprocess.run([
        "magick", str(source) + "[0]",
        *(["-gamma", "0.6"] if gamma else []),
        *options, "+repage", "-define", "png:exclude-chunks=date,time",
        str(target),
    ], check=True)


def link(dest, target):
    path = out / dest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    path.symlink_to(target)


# Ordered, explicit conversions from the recipe (48 is the nominal directory size).
for context, mapping in {
    "actions": {
        "edit-find": "WM.App-find",
        "edit-clear": "Installer.App-Delete",
        "edit-paste": "ProductFeedbackn",
        "edit-copy": "ProjectBuilder.App-Documents_color",
        "document-new": "ProjectBuilder.App-text_win",
        "document-save": "WM.App-floppy",
        "document-save-as": "WM.App-openFloppy",
        "process-stop": "WM.App-stop",
        "user-invisible": "WM.App-netUserAddress",
    },
    "apps": {
        "baloo": "WM.App-find",
        "system-shutdown": "Preferences.App-boot",
        "system-reboot": "WM.App-openRoot",
        "system-lock-screen": "Preferences.App-Password",
        "tools-check-spelling": "Interfacebuilder.App-fontmanager_nib",
        "help-contents": "Documentation-manual",
    },
    "categories": {"applications-internet": "WM.App-eunet"},
    "devices": {
        "computer": "WM.App-root",
        "input-mouse": "Preferences.App-Mouse",
        "input-keyboard": "Preferences.App-Keyboard-JTF",
        "video-display": "Preferences.App-Monitor",
        "camera-photo": "Grab.App-CameraNormal",
        "scanner": "PrintManager.App-queue",
    },
    "places": {"folder": "WM.App-folder", "network-workgroup": "WM.App-eunet"},
}.items():
    for name, source in mapping.items():
        convert(osdir / (source + ".tiff"), f"{context}/48/{name}.png", gamma=True)

for name, color, amount in [
    ("call-start", "green", 30),
    ("call-stop", "red", 30),
    # The published recipe overwrites call-stop with this blue version.
    ("call-stop", "blue", 10),
]:
    convert(osdir / "AuthServer.App-ISDNIcon.tiff", f"actions/48/{name}.png",
            "-fill", color, "-colorize", str(amount), gamma=True)
for status, color, amount in [
    ("available", "green", 60), ("away", "yellow", 80),
    ("busy", "orange", 60), ("idle", "blue", 40), ("offline", "#aaaaaa", 70),
]:
    convert(osdir / "WM.App-netUserAddress.tiff", f"actions/48/user-{status}.png",
            "-fill", color, "-colorize", str(amount), gamma=True)

for name, source in {
    "edit-find-replace": "Magnifier",
    "edit-delete": "M3Play_delete_song",
    "list-add": "MailIcon_box_add",
    "list-remove": "MailIcon_box_delete",
    "go-first": "tostart",
    "go-last": "toend",
    "media-playback-start": "play",
    "media-playback-pause": "pause",
    "media-seek-backward": "rwd",
    "media-seek-forward": "ffwd",
    "document-send": "MailIcon_send",
    "mail-unread": "MailIcon_forward",
    "mail-replied": "MailIcon_reply",
    "edit-select-all": "MultipleSelection",
    "edit-select": "gf_finger",
}.items():
    convert(gsdir / (source + ".tiff"), f"actions/48/{name}.png")
convert(gsdir / "MailIcon_forward.tiff", "actions/48/mail-read.png", "-grayscale", "Rec709Luma")
convert(gsdir / "PrefsIcon_Login.tiff", "apps/48/system-log-out.png")
convert(gsdir / "rwd.tiff", "actions/48/go-previous.png", "-crop", "12x+0+0")
convert(gsdir / "ffwd.tiff", "actions/48/go-next.png", "-crop", "12x+0+0")
convert(out / "actions/48/go-previous.png", "actions/48/go-up.png", "-rotate", "90")
convert(out / "actions/48/go-next.png", "actions/48/go-down.png", "-rotate", "90", "-flop")
convert(gsdir / "tostart.tiff", "actions/48/go-top.png", "-rotate", "90")
convert(gsdir / "toend.tiff", "actions/48/go-bottom.png", "-rotate", "90", "-flop")
convert(wmdir / "FolderOpen.xpm", "actions/48/document-open.png")
convert(wmdir / "harddrive.tif", "devices/48/drive-harddisk.png")

for name in [
    "edit-find", "edit-find-replace", "document-edit", "document-print", "edit-delete",
    "edit-clear", "edit-paste", "edit-copy", "document-new", "document-save",
    "document-save-as", "list-add", "list-remove", "document-open",
]:
    link(f"actions/48/{name}-symbolic.png", f"{name}.png")
for name, target in {
    "find-location": "edit-find.png",
    "document-edit": "../../apps/48/accessories-text-editor.png",
    "document-print": "../../devices/48/printer.png",
    "go-home": "../../places/48/user-home.png",
    "tab-new": "list-add.png", "tab-new-symbolic": "list-add.png",
    "go-jump": "media-seek-forward.png",
    "media-skip-backward": "go-first.png", "media-skip-forward": "go-last.png",
    "mail-send": "document-send.png", "mail-reply-sender": "mail-replied.png",
    "mail-forward": "mail-unread.png", "mail-mark-read": "mail-read.png",
}.items():
    link(f"actions/48/{name}.png", target)

# Two overlapping user icons, in the order and offsets specified by the guide.
subprocess.run([
    "magick", "-size", "48x48", "xc:none",
    str(out / "actions/48/user-offline.png"), "-geometry", "+8+0", "-composite",
    str(out / "actions/48/user-invisible.png"), "-geometry", "+0+8", "-composite",
    "-define", "png:exclude-chunks=date,time", str(out / "actions/48/system-users.png"),
], check=True)

for name, target in {
    "ristretto": "gwenview.png", "preferences-desktop-display": "../../devices/48/video-display.png",
    "system-help": "help-contents.png", "qt5ct": "preferences-desktop-theme.png",
    "system-search": "../../actions/48/edit-find.png", "help-browser": "help-contents.png",
    "sylpheed": "internet-mail.png", "xed": "accessories-text-editor.png",
}.items():
    link(f"apps/48/{name}.png", target)
link("devices/48/media-floppy.png", "../../actions/48/document-save.png")
link("devices/48/drive-optical.png", "media-optical.png")

# Replace all non-symlink folder variants, then restore the recipe's exceptions.
for path in sorted((out / "places/48").glob("folder-*.png")):
    if not path.is_symlink():
        link(str(path.relative_to(out)), "folder.png")
for name, source in {
    "folder-downloads": "FolderLink.xpm", "folder-html": "FolderGlobe.xpm",
    "folder-bookmark": "FolderBooks.xpm",
}.items():
    convert(wmdir / source, f"places/48/{name}.png")
for name in ["folder-cloud", "folder-dropbox", "folder-gdrive", "folder-network",
             "folder-onedrive", "folder-owncloud", "folder-public", "folder-publicshare"]:
    link(f"places/48/{name}.png", "folder-html.png")
for name in ["bookmarks", "favorites", "folder-favorites"]:
    link(f"places/48/{name}.png", "folder-bookmark.png")
link("places/48/folder-download.png", "folder-downloads.png")
link("places/48/stock_folder.png", "folder.png")
link("mimetypes/48/inode-directory.png", "../../places/48/folder.png")

# Coverage/semantic improvements beyond the guide, using only its existing inputs.
# Preserve the real open-folder icon rather than aliasing it to the closed folder.
convert(osdir / "WM.App-openFolder.tiff", "places/48/folder-open.png", gamma=True)
# No new artwork: the forward/seek action also serves as the refresh action.
link("actions/48/view-refresh.png", "media-seek-forward.png")
for name in ["view-refresh", "go-previous", "go-next", "go-up", "go-down", "go-home"]:
    link(f"actions/48/{name}-symbolic.png", f"{name}.png")
# Thunar/GIO request modern MIME spellings, not just the generic audit names.
link("mimetypes/48/text-x-shellscript.png", "text-x-script.png")
for name in ["audio-wav", "audio-vnd.wave"]:
    link(f"mimetypes/48/{name}.png", "audio-x-wav.png")

index = configparser.ConfigParser(interpolation=None)
index.optionxform = str
index.read(out / "index.theme")
index["Icon Theme"]["Name"] = "Nextlike"
index["Icon Theme"]["Comment"] = "Based on GNUstep, with OPENSTEP artwork; personal use only"
index["Icon Theme"]["Inherits"] = "Papirus,hicolor"
dirs = index["Icon Theme"]["Directories"].split(",")
index["Icon Theme"]["Directories"] = ",".join(
    "actions/48" if d == "actions/24" else d for d in dirs if d != "status/24"
)
index["actions/48"] = dict(index["actions/24"])
index["actions/48"]["Size"] = "48"
index["actions/48"]["Type"] = "Scalable"
index.remove_section("actions/24")
index.remove_section("status/24")
with (out / "index.theme").open("w") as file:
    index.write(file, space_around_delimiters=False)
