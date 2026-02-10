{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs =
    { self, nixpkgs }:
    let
      inherit (nixpkgs.lib) genAttrs;

      forAllSystems = genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllPkgs = function: forAllSystems (system: function pkgs.${system});

      pkgs = forAllSystems (
        system:
        (import nixpkgs {
          inherit system;
          overlays = [ ];
        })
      );
    in
    {
      devShells = forAllPkgs (
        pkgs: with pkgs.lib; {
          default = pkgs.mkShell rec {
            nativeBuildInputs = with pkgs; [
              python312Packages.ipython
              uv
            ];
            buildInputs = with pkgs; [
              python313Packages.fastapi
              python313Packages.uvicorn
              python313Packages.requests
              python313Packages.sqlalchemy
              python312Packages.pydantic
              python313Packages.psycopg2
              python312Packages.websockets
            ];

            LD_LIBRARY_PATH = makeLibraryPath buildInputs;
          };
        }
      );
    };
}
