{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python3.withPackages (ps: with ps; [
    requests
    beautifulsoup4
    pytest
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
}