# Threat model

**Honest-but-curious.** Every party follows the protocol exactly but may inspect
everything it receives. Parties hold at most n-1 shares between them. No active
tampering, no dropped messages, no timing side channels. All parties run in one
process; the model is what would hold if they were separate (SDD 12.1).

**Out of scope:** malicious parties, n-of-n collusion, real triple generation,
network adversaries. The SP-4 write-up must say so plainly.
