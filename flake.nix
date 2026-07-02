{
  description = "Flake for ReAct-agent";
  inputs = {
    nixpkgs.url = "nixpkgs";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        name = "react-agent-shell";
        packages = with pkgs; [
          uv
          python3
        ];
      };
    };
}
