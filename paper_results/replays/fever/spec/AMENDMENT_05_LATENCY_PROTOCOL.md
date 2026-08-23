# Technical amendment 05: secondary measured-latency protocol

Date: 2026-07-30  
Timing: after pilot admission and before full-test outcome scoring.

The primary cost remains the preregistered qrel-independent operator-token
count.  To materialize the registered secondary hardware-qualified profile,
warm latency is measured on the registered 200-query pilot sample.

All candidate documents are loaded before timing.  Each paid route is warmed
once; GPU synchronization brackets every observation.  Per-query paid-route
order is deterministically shuffled with seed 20260730.  BM25 uses its
archived per-query search latency.  The report retains mean, median, and p95
and names the RTX 4070 Laptop GPU.  These values are a hardware profile, not a
universal cost.

No qrel or route quality is read by the latency script.
