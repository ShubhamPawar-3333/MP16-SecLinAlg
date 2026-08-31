# Data-flow notes

See SDD 7 (Figures 2 and 3) for the diagrams.

- **Plaintext path:** caller -> Field -> Vector/Matrix -> linalg -> result. No sharing.
- **Secure path:** caller shares inputs -> local adds / public scaling stay shared
  -> each shared x shared multiply opens only the masks `d`, `e` -> final
  reconstruct. Secret inputs are never opened (SDD 12.4).
- **Boundary rule:** reconstruction happens only at the very end, or on `d`/`e`.
  Any other `reconstruct()` call in `secure/` is a bug -- covered by review and
  the privacy tests.
