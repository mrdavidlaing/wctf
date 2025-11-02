{
  description = "Hugo website development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            hugo
            go
          ];

          shellHook = ''
            echo "Hugo development environment loaded!"
            echo "Available commands:"
            echo "  hugo server -D --bind 0.0.0.0  # Start development server"
            echo "  hugo --minify                  # Build for production"
            echo "  make serve                     # Start dev server (if Makefile exists)"
            echo "  make build                     # Build site (if Makefile exists)"
            echo ""
            echo "Hugo version: $(hugo version)"
            echo "Go version: $(go version)"
          '';
        };
      });
}