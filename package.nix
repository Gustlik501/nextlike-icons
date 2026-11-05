{ lib, stdenvNoCC, fetchurl, python3, imagemagick, gtk3 }:

let
  openstep = fetchurl {
    # HTTPS on www.aiei.ch has an invalid certificate; integrity is pinned here.
    url = "http://www.aiei.ch/gnustep/icons/one/openstepicons-1.1.tar.gz";
    hash = "sha256-7e1oeIKnbIjrToSg8wdTnA3ejLVmbkdztkGHZBN7uJo=";
  };
  gnustep = fetchurl {
    url = "http://www.aiei.ch/gnustep/icons/two/gnustep-icons-1.0.tar.gz";
    hash = "sha256-Ax3bYnHgkMq64kgox6WgqyAhpqEUOiHzWKBMT3bjCcc=";
  };
  wmicons = fetchurl {
    # Versioned release, not the recipe's mutable snapshots URL.
    url = "https://ftp.openbsd.org/pub/OpenBSD/7.8/packages/amd64/wmicons-1.0p1.tgz";
    hash = "sha256-54YwpKHY9WPp+McR1/cpj600HCVWXM3MW10lo6VU5co=";
  };
  base = fetchurl {
    name = "GNUstep-0.5.tar.gz";
    url = "file://${./vendor/GNUstep-0.5.tar.gz}";
    hash = "sha256-1kH1leCdHnm4Hq2CTM5UYfCtPbrn2JFKmiJ2hgJK0TE=";
  };
in
stdenvNoCC.mkDerivation {
  pname = "nextlike-icons";
  version = "0.9.3";
  dontUnpack = true;
  strictDeps = true;
  dontDropIconThemeCache = true;
  nativeBuildInputs = [ python3 imagemagick gtk3 ];

  buildPhase = ''
    runHook preBuild
    mkdir sources
    tar xf ${base} -C sources
    tar xf ${openstep} -C sources
    tar xf ${gnustep} -C sources
    mkdir sources/wmicons
    tar xf ${wmicons} -C sources/wmicons
    chmod -R u+w sources
    python3 ${./scripts/build-theme.py} sources Nextlike
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p "$out/share/icons" "$out/share/doc/nextlike-icons"
    cp -a Nextlike "$out/share/icons/"
    cp ${./README.md} "$out/share/doc/nextlike-icons/README.md"
    cp ${./LICENSE} "$out/share/doc/nextlike-icons/LICENSE"
    cp ${./vendor/README.md} "$out/share/doc/nextlike-icons/GNUstep-attribution.md"
    cp ${./vendor/COPYING.GPL-3.0} "$out/share/doc/nextlike-icons/"
    cp sources/gnustep-icons-1.0/LICENSE "$out/share/doc/nextlike-icons/COPYING.LGPL-2.1"
    cp sources/gnustep-icons-1.0/README.TXT "$out/share/doc/nextlike-icons/GNUstep-TIFF-README.txt"
    cp sources/openstepicons-1.1/{README,1-README.txt,openstep-question.txt,openstep-reply.txt} \
      "$out/share/doc/nextlike-icons/"
    gtk-update-icon-cache --force "$out/share/icons/Nextlike"
    gtk-update-icon-cache --validate "$out/share/icons/Nextlike"
    runHook postInstall
  '';

  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck
    python3 ${./scripts/check-theme.py} "$out/share/icons/Nextlike" \
      > "$out/share/doc/nextlike-icons/coverage.tsv"
    test -s "$out/share/icons/Nextlike/icon-theme.cache"
    gtk-update-icon-cache --validate "$out/share/icons/Nextlike"
    runHook postInstallCheck
  '';

  # Never offer these proprietary build products through Hydra/substituters.
  preferLocalBuild = true;
  allowSubstitutes = false;
  meta = {
    description = "Nextlike OPENSTEP-style icons (proprietary NeXT/Apple artwork; personal use only)";
    homepage = "https://www.strahinja.org/tekstovi/softver/wmaker/";
    license = lib.licenses.unfree;
    platforms = [ "x86_64-linux" ];
    hydraPlatforms = [ ];
  };
}
