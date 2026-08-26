# A001 — Loop Contract v0 Frozen

**Task:** MSTR-000A / A001
**Schema:** `schemas/mstr-loop-contract-v0.schema.json` (registered, byte-identical design source in both spec packages)

## Result

The canonical `mstr.loop-contract.v0` implementation contract is frozen from the planning schema. It covers:

- success/verifier: `success_requires_independent_verifier = true` (const); terminal classes limited to `VERIFIED_SUCCESS` / `RECOVERED_SUCCESS`
- recovery: no retry of same failed action without new evidence; failure classification required
- budgets: bounded max_steps, max_tool_calls, max_repairs, timeout_seconds
- effect envelope: declared by id; validated as non-empty string
- goal policy: ambiguity_behavior (clarify/escalate/bounded_inference) + require_acceptance_criteria
- trivial-task fast path: not present in the frozen schema (omitted from the planning design to keep the contract minimal; can be added via a governed amendment)

## Fixtures

- Valid: 1 instance covering all required fields
- Invalid: 5 fail-closed mutations (wrong schema_version, empty loop_id, zero max_steps, verifier_not_required=false, bad terminal class)
