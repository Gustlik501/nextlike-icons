#!/usr/bin/env python3
"""Validate advertised directories, aliases, PNG headers and required coverage."""
import configparser
from pathlib import Path
import struct
import sys

REQUIRED = """
folder folder-open user-home user-desktop folder-documents folder-download
folder-music folder-pictures folder-videos folder-templates folder-publicshare
user-trash user-trash-full computer drive-harddisk drive-removable-media
network-workgroup text-x-generic text-x-script application-x-executable
image-x-generic audio-x-generic video-x-generic package-x-generic
application-x-archive application-pdf inode-directory go-previous go-next go-up
go-home view-refresh edit-find document-open list-add
""".split()
# Five extra icons make the visual sheet exactly 40 cells.
EXTRA = "document-save edit-copy edit-paste edit-delete preferences-desktop-display".split()


def inspect(theme):
    theme = theme.resolve()
    index = configparser.ConfigParser(interpolation=None)
    index.read(theme / "index.theme")
    assert index["Icon Theme"]["Name"] == "Nextlike"
    assert index["Icon Theme"]["Inherits"] == "Papirus,hicolor"
    dirs = index["Icon Theme"]["Directories"].split(",")
    assert "actions/48" in dirs and "status/24" not in dirs
    icons = {}
    for directory in dirs:
        assert directory in index and (theme / directory).is_dir(), directory
        assert int(index[directory]["Size"]) > 0
        for path in sorted((theme / directory).glob("*.png")):
            assert path.is_file(), f"Broken alias: {path}"
            assert path.resolve().is_relative_to(theme), f"External alias: {path}"
            header = path.read_bytes()[:24]
            assert header[:8] == b"\x89PNG\r\n\x1a\n", path
            width, height = struct.unpack(">II", header[16:24])
            assert 0 < width <= 512 and 0 < height <= 512, (path, width, height)
            icons[path.stem] = path
    # Check every link, including any not advertised by index.theme.
    for path in theme.rglob("*"):
        if path.is_symlink():
            assert path.exists() and path.resolve().is_relative_to(theme), path
    return theme, icons


if __name__ == "__main__":
    theme, icons = inspect(Path(sys.argv[1]))
    print("name\tlookup\tpath\tresolved-target")
    missing = []
    for name in REQUIRED:
        path = icons.get(name)
        if path is None:
            missing.append(name)
            print(f"{name}\tfallback\t-\t-")
        else:
            print(f"{name}\tNextlike\t{path.relative_to(theme)}\t{path.resolve().relative_to(theme)}")
    print(f"# Native coverage: {len(REQUIRED) - len(missing)}/{len(REQUIRED)}")
    assert not missing, f"Required icons fall back: {missing}"
