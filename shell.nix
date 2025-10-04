{
  pkgs ? import <nixpkgs> { },
}:

let
  python = pkgs.python3.withPackages (
    ps: with ps; [
      requests
      beautifulsoup4
      pytest
      curl-cffi
    ]
  );
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
}
