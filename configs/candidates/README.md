# Candidate Configurations

Candidate configuration files consumed by T008 are local `.json` records that must validate against `schemas/candidate-record.schema.json` (`mstr.candidate.v1`).

A candidate config is evidence metadata only. It may identify an upstream model, exact revision, architecture/tokenizer facts, rights evidence, runtime/quantization notes, and source URLs, but loading it does **not** download weights, accept gated terms, contact a provider, execute a model, or admit the candidate.

T012+ source-specific tasks are responsible for populating and reviewing candidate records. T006 independently recomputes primary rights eligibility; a permissive-looking `decision` field cannot bypass that gate.
