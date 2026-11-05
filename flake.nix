{
  description = "Nextlike: personal-use OPENSTEP/GNUstep icon theme";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      mkPkgs = system: import nixpkgs {
        inherit system;
        # Only this personal-use, non-redistributable package is allowed here.
        config.allowUnfreePredicate = pkg:
          nixpkgs.lib.getName pkg == "nextlike-icons";
      };
    in
    {
      packages = forAllSystems (system:
        let
          package = (mkPkgs system).callPackage ./package.nix { };
        in
        {
          default = package;
          nextlike-icons = package;
        });

      overlays.default = final: prev: {
        nextlike-icons = final.callPackage ./package.nix { };
      };

      checks = forAllSystems (system: {
        theme = self.packages.${system}.default;
      });

      devShells = forAllSystems (system:
        let pkgs = mkPkgs system;
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              (python3.withPackages (ps: [ ps.pygobject3 ps.pillow ]))
              gtk3 gobject-introspection imagemagick
              xvfb-run dbus thunar xdotool liberation_ttf
            ];
          };
        });
    };
}
