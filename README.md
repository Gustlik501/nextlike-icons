# Nextlike icons

Personal-use NeXTSTEP/OPENSTEP-style freedesktop icon theme, implementing
[Strahinja Radić's Nextlike recipe](https://www.strahinja.org/tekstovi/softver/wmaker/)
(guide v0.9.3, 2025-11-14): gamma 0.6 for OPENSTEP TIFFs, GNUstep actions,
48px action directories, brown folders, and replacement devices.

**Includes proprietary NeXT/Apple artwork fetched at build time, for personal
use only. Do not publish built outputs, binary caches, screenshots, or source
artwork. Availability online is not a redistribution licence.** The resulting
package is marked `unfree`, with Hydra disabled and substitution disabled.
The build scripts do not change the running desktop.

## Build and contents

```sh
nix build
nix flake check
```

Nixpkgs is locked to `885ba4d038f10c3d17d7a92e8c3cc185b99c9158`.
Outputs: `packages.x86_64-linux.{default,nextlike-icons}`;
overlay attribute: `pkgs.nextlike-icons`.

- `$out/share/icons/Nextlike/index.theme`, context directories and PNG aliases
- `$out/share/icons/Nextlike/icon-theme.cache` (generated with GTK3)
- `$out/share/doc/nextlike-icons/coverage.tsv`, attribution and upstream notices

All **35/35 requested names** (counting both archive names separately) resolve
within Nextlike, without inheritance. The build validates every local alias,
PNG header and advertised directory. The TSV lists each name and target.
Uncovered names outside this list inherit **Papirus,hicolor**, both found in
the user's profiles; Adwaita icons were absent. Install Papirus on other systems.

## NixOS / Home Manager (declarative; apply yourself)

Add a local flake input `nextlike-icons.url = "path:/data/SSD1/dotfilesprojects/nextlike-icons";`
and `nextlike-icons.inputs.nixpkgs.follows = "nixpkgs";`, then:

```nix
# NixOS, or your Home Manager nixpkgs configuration:
nixpkgs.overlays = [ inputs.nextlike-icons.overlays.default ];
nixpkgs.config.allowUnfreePredicate = pkg:
  builtins.elem (pkgs.lib.getName pkg) [ "nextlike-icons" ];

# NixOS:
environment.systemPackages = [ pkgs.nextlike-icons pkgs.papirus-icon-theme ];

# Home Manager (instead of environment.systemPackages):
gtk.enable = true;
gtk.iconTheme = { name = "Nextlike"; package = pkgs.nextlike-icons; };
home.packages = [ pkgs.papirus-icon-theme ];
```

Merge the predicate with existing unfree allowances. With standalone HM this
goes in HM; with `useGlobalPkgs` use NixOS's nixpkgs configuration instead.
For manual GTK3 configuration, set `gtk-icon-theme-name=Nextlike` under
`[Settings]` in `~/.config/gtk-3.0/settings.ini`. `GTK_THEME` selects widget
styling, **not** the icon theme. In Thunar select icon view / normal (48px)
zoom (75% in Thunar 4.20) for the original-size artwork. No font is included or required.

## Sources and recipe adjustments

Every fetched archive is pinned by SHA-256 in `package.nix`:

- [GNUstep Icons 0.5 by abgr](https://www.gnome-look.org/p/1239539): declared
  GPLv3; original archive vendored because the OCS download is signed/expiring.
  See [vendor/README.md](vendor/README.md) for provenance and licence caveat.
- [OPENSTEP icons 1.1](http://www.aiei.ch/gnustep/icons/one/openstepicons-1.1.tar.gz):
  NeXT/Apple proprietary artwork. Upstream notices installed with the output.
  HTTP is necessary because the HTTPS certificate is invalid; the hash protects
  integrity. Neither this archive nor its derived PNGs is committed.
- [GNUstep TIFF icons 1.0](http://www.aiei.ch/gnustep/icons/two/gnustep-icons-1.0.tar.gz):
  Andrew Lindesay, LGPL 2.1-or-later; original licence/README installed.
- [OpenBSD 7.8 wmicons 1.0p1](https://ftp.openbsd.org/pub/OpenBSD/7.8/packages/amd64/wmicons-1.0p1.tgz):
  mixed-origin artwork, not assumed redistributable; fetched only. A versioned
  release replaces the recipe's mutable snapshots URL, using the same assets.

The conversion is scripted in `scripts/build-theme.py`. It removes symlinks
before overwriting icons (avoids clobbering their targets), selects TIFF frame 0,
clears crop offsets, and omits PNG timestamps. It preserves the recipe's final
blue `call-stop` overwrite and composite user icon. Changes beyond the recipe:
`folder-open` gets the actual gamma-corrected OPENSTEP open folder rather than a
closed-folder alias; `view-refresh` aliases the existing seek-forward action.
Navigation gets symbolic-name aliases, and concrete `text-x-shellscript` and
`audio-wav`/`audio-vnd.wave` MIME aliases avoid modern fallback icons observed
in Thunar.
No modern fallback artwork is copied into Nextlike. Packaging code is MIT
licensed ([LICENSE](LICENSE)); that does not relicense any artwork.

## Isolated verification

```sh
nix develop -c python3 scripts/visual-check.py result
```

This creates `.work/nextlike-sheet.png` (40 labelled cells, 48px rendering on
`#C0C0C0`), `.work/gtk-coverage.tsv`, `.work/thunar-mime-coverage.tsv`, and
`.work/nextlike-thunar.png`.
The helper runs GTK lookup and Thunar under its **own Xvfb and D-Bus session**,
with private HOME/XDG configuration and a memory GSettings backend; never the
live display or Thunar instance. It closes its own processes on exit. Generated
artwork and screenshots stay ignored in `.work/` and must not be published.
