# The multiplication boundary (SP-4)

| Operation | Cost | Needs |
|-----------|------|-------|
| add shared + shared | local, free | linearity of sharing |
| public scalar x shared | local, free | linearity of sharing |
| shared x shared | one Beaver triple + open two masks | trusted dealer (this scope) |

**Where a real MPC protocol would be required beyond this scope:** generating
Beaver triples without a trusted dealer, security against malicious parties, and
actual networking between separate party processes (SDD 8.5, 12.1).
