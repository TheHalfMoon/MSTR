# Benchmark Manifests

T008 defines the repository-local `mstr.benchmark.v1` manifest contract used by the qualification harness before execution-oriented benchmark tasks are implemented.

Required fields:

```text
schema_version = mstr.benchmark.v1
benchmark_id
purpose
surface
task_ids
candidate_ids
seeds
sampling
timeout_seconds
verifier_policy
tools
network_policy
cache_requirements
comparison_policy
source_commit
```

`notes` is optional. Unknown top-level fields fail closed. Task IDs, candidate IDs, and seeds must be non-empty and unique; tools may be empty. `network_policy` is restricted to `disabled`, `loopback_only`, or `explicit_allowlist`.

T008 only loads local `.json` files and records their exact SHA-256. It does not fetch tasks, candidates, model artifacts, benchmark answers, or remote resources. Later tasks may add more specialized manifests through explicit versioned contracts rather than silently widening this one.
