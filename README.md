# nextlike-icons

A NeXTSTEP / OPENSTEP-style freedesktop icon theme for Linux desktops, built
reproducibly with Nix from
[Strahinja Radić's **Nextlike** recipe](https://www.strahinja.org/tekstovi/softver/wmaker/)
(guide v0.9.3, 2025-11-14). Expect 48 px full-colour objects, brown folders,
gamma-corrected OPENSTEP TIFFs and GNUstep action icons.

> [!CAUTION]
> **Personal use only.** The build downloads proprietary NeXT/Apple artwork
> from its original sources at build time. That artwork is not part of this
> repo and must not be redistributed, **so this README has no screenshots**,
> and you should not publish built outputs, binary caches or screenshots
> either. Something being available online doesn't make it licensed for
> redistribution. The package is marked `unfree`, with Hydra builds and
> substitution disabled.

The repo itself contains only packaging code (MIT) and one GPLv3 icon archive.
See [Sources](#sources).

## Install

```nix
# flake.nix
inputs.nextlike-icons = {
  url = "github:Gustlik501/nextlike-icons";
  inputs.nixpkgs.follows = "nixpkgs";
};

nixpkgs.overlays = [ inputs.nextlike-icons.overlays.default ];  # pkgs.nextlike-icons
nixpkgs.config.allowUnfreePredicate = pkg:
  builtins.elem (lib.getName pkg) [ "nextlike-icons" ];
```

Home Manager:

```nix
gtk.enable = true;
gtk.iconTheme = { name = "Nextlike"; package = pkgs.nextlike-icons; };
home.packages = [ pkgs.papirus-icon-theme ];   # fallback for names Nextlike doesn't cover
```

On NixOS without Home Manager, add both packages to
`environment.systemPackages` and set `gtk-icon-theme-name=Nextlike` in
`~/.config/gtk-3.0/settings.ini`. `GTK_THEME` selects the widget theme, not
the icon theme. If you use Home Manager with `useGlobalPkgs`, put the unfree
predicate in your NixOS nixpkgs config.

In Thunar, icon view at the normal (48 px) zoom shows the artwork at its
original size. In Thunar 4.20 that's the 75% zoom level.

## What gets installed

- `share/icons/Nextlike/` with `index.theme`, context directories, PNG aliases and `icon-theme.cache`
- `share/doc/nextlike-icons/coverage.tsv` (every requested icon name and its target), plus attribution and upstream notices

All 35 of the recipe's icon names resolve within Nextlike itself. Anything
else falls back to **Papirus**, then **hicolor**.

## Sources

Every archive is pinned by SHA-256 in `package.nix`:

| Source | License | In this repo? |
|---|---|---|
| [GNUstep Icons 0.5](https://www.gnome-look.org/p/1239539) by abgr | GPLv3, as declared by the uploader | **Vendored** (`vendor/`): the only download link is a signed, expiring URL. See [vendor/README.md](vendor/README.md) |
| [OPENSTEP icons 1.1](http://www.aiei.ch/gnustep/icons/one/openstepicons-1.1.tar.gz) | NeXT/Apple proprietary | No, fetched at build time. Plain HTTP because the site's certificate is invalid; the hash still guarantees integrity |
| [GNUstep TIFF icons 1.0](http://www.aiei.ch/gnustep/icons/two/gnustep-icons-1.0.tar.gz) by Andrew Lindesay | LGPL-2.1-or-later | No, fetched |
| [OpenBSD 7.8 wmicons 1.0p1](https://ftp.openbsd.org/pub/OpenBSD/7.8/packages/amd64/wmicons-1.0p1.tgz) | Mixed origin, not assumed redistributable | No, fetched. A versioned release stands in for the recipe's mutable snapshot URL |

<details>
<summary><b>How it differs from the recipe</b></summary>

The conversion lives in `scripts/build-theme.py`. It removes symlinks before
overwriting icons, so their targets aren't clobbered. It also takes TIFF frame
0, clears crop offsets and strips PNG timestamps. It keeps the recipe's final
blue `call-stop` overwrite and the composite user icon.

Additions on top of the recipe:

- `folder-open` uses the real gamma-corrected OPENSTEP open folder instead of an alias to the closed one.
- `view-refresh` aliases the existing seek-forward action.
- Symbolic-name aliases for navigation.
- `text-x-shellscript` and `audio-wav` / `audio-vnd.wave` aliases, so Thunar doesn't show modern fallbacks.

No modern fallback artwork is copied into the theme.

</details>

<details>
<summary><b>Verification</b></summary>

```sh
nix build
nix flake check
nix develop -c python3 scripts/visual-check.py result
```

The build validates every alias, PNG header and advertised directory.
`visual-check.py` renders a labelled contact sheet and checks GTK and Thunar
icon lookup. It runs everything in its own Xvfb and D-Bus session with a
throwaway HOME. Its output goes to the gitignored `.work/` directory and
**must not be published**.

</details>

## License

The packaging code is **MIT** ([LICENSE](LICENSE)). That does not relicense
any artwork: each icon set keeps its own license, as listed above.

---

Part of a small retro-desktop set for Hyprland:
[hypr-wmdeco](https://github.com/Gustlik501/hypr-wmdeco) ·
[irixium-gtk-theme](https://github.com/Gustlik501/irixium-gtk-theme) ·
[chicago95-cursors](https://github.com/Gustlik501/chicago95-cursors) ·
[misc-fixed-ttf](https://github.com/Gustlik501/misc-fixed-ttf) ·
**nextlike-icons**
