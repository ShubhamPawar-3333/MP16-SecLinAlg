# Why n-1 shares reveal nothing

s_1 .. s_{n-1} are independent and uniform on Z_p; s_n = v - sum(s_i).

Take any n-1 of the shares:
- if it is exactly {s_1 .. s_{n-1}}, those are uniform and independent of v;
- if it includes s_n, the one missing share s_j (j < n) is uniform and appears
  in s_n as a one-time pad: for every candidate secret v' there is exactly one
  s_j consistent with what was observed.

Either way the marginal distribution of any n-1 shares is identical for every
secret, so they carry no information. SS-3 checks this empirically (SDD 12.3).
