# T002 — Universal Distribution / Install / Privacy Contract

**Task:** MSTR-000 / T002  
**Status:** COMPLETE_CANDIDATE  
**Contract ID:** `MSTR-DIST-v0`  
**Canonical base:** `8427d22aaf5a8ad5d70d264f9ef4e2241cfe063f`  
**Authority:** Product/distribution requirements only. This document does not choose a backbone, runtime implementation, or release host.

## 1. Purpose

MSTR's primary release must be usable by ordinary laptop owners as a genuinely local tool. "Open weights" is insufficient if first launch requires a cloud account, development toolchain, hidden model download, telemetry, or a complicated source build.

T002 freezes the minimum distribution, installation, offline, privacy, update, and user-data behavior that every primary MSTR release path must satisfy.

## 2. Primary local-use invariant

```text
PROVIDER_ACCOUNT_REQUIRED = NO
API_KEY_REQUIRED = NO
SUBSCRIPTION_REQUIRED = NO
ACTIVATION_SERVER_REQUIRED = NO
CLOUD_INFERENCE_REQUIRED = NO
NETWORK_REQUIRED_AFTER_LOCAL_ARTIFACT_ACQUISITION = NO
TELEMETRY_DEFAULT = OFF
USER_CODE_UPLOAD_DEFAULT = NEVER
TRAIN_ON_USER_CODE_DEFAULT = NEVER
BASIC_MODE_BUILD_FROM_SOURCE = NO
BASIC_MODE_DOCKER_REQUIRED = NO
BASIC_MODE_PYTHON_REQUIRED = NO
BASIC_MODE_NODE_REQUIRED = NO
```

A primary package that violates any invariant above is not the universal MSTR release, regardless of model quality.

## 3. Artifact acquisition versus local operation

MSTR distinguishes artifact **acquisition** from product **operation**.

### Acquisition

Users may obtain signed/checksummed MSTR artifacts from one or more distribution hosts. Network access is naturally required to download those artifacts unless they are transferred by another medium.

### Local operation

Once the required runtime and model artifacts exist locally:

- first launch must succeed with the network disconnected;
- ordinary coding, search, edit, and supported local verification must not require network access;
- no license activation handshake is permitted;
- no hidden provider-model fallback is permitted;
- no first-run dependency/model download is permitted unless the user explicitly selected an optional component and the UI/CLI clearly states it before network access.

`TTFI_LOCAL` from `MSTR-MEASURE-v0` starts with all required artifacts already local specifically so network variability cannot hide installation friction.

## 4. Primary packaging requirement

The primary user must not need to compile MSTR or assemble a Python/Node environment.

Every required platform lane must eventually provide either:

1. a platform-native installer/package; or
2. a portable self-contained archive/bundle with one obvious executable/launcher.

A source-build path may exist for developers but cannot be the only supported install method.

The package must include or explicitly co-package all runtime libraries needed for core MSTR operation except normal operating-system components.

## 5. Platform packaging lanes

T002 does not select final installer technology, but freezes required outcomes.

### Windows x86_64

- user-space installation/portable launch must be possible without a developer toolchain;
- no WSL requirement for basic inference/edit assistance;
- WSL may later be an optional verification backend for Linux-centric repository tasks;
- package signing is required for production release where a trusted signing path is available.

### Linux x86_64

- provide a self-contained binary/package path that does not require the user to create a Python/Node environment;
- avoid unnecessary distro-specific runtime dependencies;
- document the tested libc/runtime floor once selected;
- root privileges must not be required for the primary user-local install path.

### macOS arm64

- provide a native Apple Silicon package/bundle;
- no Homebrew/Python/Node prerequisite for basic use;
- notarization/code signing is required for production release where the project can obtain the required signing identity;
- Metal may accelerate inference but local operation must remain consistent with the U1 no-discrete-GPU product contract.

Secondary platform lanes inherit the same principles when they become supported.

## 6. Model/runtime packaging

The runtime and model may be shipped as one package or two explicitly paired artifacts. Either layout must satisfy:

- exact version compatibility manifest;
- cryptographic hashes for all required artifacts;
- no user-side conversion from BF16/FP16 to Q4 as part of ordinary installation;
- no temporary disk explosion outside the published installation envelope;
- no silent replacement of the selected local model with a remote model;
- deterministic detection of missing/incompatible model artifacts with a clear local error.

The primary release artifact should use the canonical Q4 profile chosen later by MSTR-000. Alternative quantizations are optional editions, not a prerequisite for ordinary users.

## 7. Disk / cache behavior

MSTR-owned persistent data must live in a documented application-data/cache location separate from user repositories.

The product must distinguish at least:

- runtime/model installation;
- global MSTR cache;
- per-repository index/cache;
- logs;
- optional downloaded components.

Requirements:

1. the user can discover/report sizes of MSTR-owned data;
2. the user can clear generated indexes/caches without deleting source repositories;
3. uninstall must never delete user repositories or arbitrary workspace content;
4. temporary install/update artifacts must be cleaned after success or rollback;
5. the installer must fail cleanly before mutation when known free disk is insufficient for the required published peak.

T001 measures exact installed/cache/temporary bytes; T061 freezes final budgets.

## 8. Network policy

### Default

```text
NETWORK_MODE = LOCAL_ONLY
OUTBOUND_TELEMETRY = OFF
UPDATE_CHECK = OFF_UNLESS_USER_OPTS_IN
REMOTE_MODEL_FALLBACK = PROHIBITED
REMOTE_REPO_INDEXING = PROHIBITED
```

The primary runtime must not create required outbound network traffic during local tasks.

### Explicit optional network features

Future features may use network access only when all are true:

- the feature is not required for basic MSTR operation;
- the user explicitly enables/invokes it;
- destination/purpose is clear before first use;
- credentials are provided explicitly for that feature;
- local-only mode remains fully available afterward;
- enabling one network feature does not silently enable unrelated telemetry or code upload.

## 9. Telemetry and crash reporting

Telemetry is opt-in only.

Before any telemetry implementation ships, it must separately classify:

- operational metrics;
- crash reports;
- performance traces;
- user prompts;
- model outputs;
- file paths;
- source-code content;
- repository metadata.

Default behavior:

```text
USAGE_TELEMETRY = OFF
CRASH_UPLOAD = OFF
PROMPT_UPLOAD = OFF
OUTPUT_UPLOAD = OFF
SOURCE_CODE_UPLOAD = OFF
FILE_PATH_UPLOAD = OFF
REPOSITORY_METADATA_UPLOAD = OFF
```

If the user later opts into metrics, source code, prompts, outputs, secrets, and file contents remain excluded unless a separate explicit consent flow exists for a clearly defined research program. General telemetry consent is not consent to upload code.

## 10. Training on user activity

MSTR must not train on local user repositories, prompts, edits, or tool traces by default.

Any future opt-in data contribution program must be separate from product usage and must state:

- exactly what is collected;
- whether source code/content is included;
- retention period;
- intended training/evaluation use;
- deletion/withdrawal process where feasible;
- license/authority requirements for contributed code;
- whether third-party repository content can legally be contributed.

A checkbox hidden inside ordinary telemetry settings is insufficient consent for training-data contribution.

## 11. Workspace access

Basic MSTR repository operation must be scoped to an explicitly selected workspace/repository.

Default rules:

- do not recursively scan the user's home directory;
- do not enumerate unrelated repositories;
- do not read browser profiles, SSH directories, cloud credential stores, password stores, or OS keychains as part of normal repository assistance;
- generated indexes belong to the selected workspace scope;
- paths outside the selected workspace require an explicit user action/permission or a separately governed capability.

Detailed agent security/capability policy is deferred to T055/T056, but T002 establishes the privacy default.

## 12. Secrets

The local runtime may need repository tools that themselves use credentials, but MSTR must not treat secret discovery/exfiltration as normal context gathering.

Distribution/privacy contract:

- credentials are not uploaded by core local MSTR;
- logs must redact known configured secret fields where feasible;
- MSTR must not copy whole environment-variable sets into model context by default;
- package installers must not request unrelated credentials;
- optional cloud integrations must store credentials through a platform-appropriate secure mechanism rather than plain project files where feasible.

T055/T056 will formalize runtime enforcement and adversarial tests.

## 13. Update policy

Updates must preserve offline choice.

Required properties:

1. local operation continues without an update server;
2. update checks are explicit opt-in or user-invoked;
3. update metadata must not include repository contents/prompts;
4. downloaded update artifacts require integrity verification before activation;
5. interrupted/failed updates must roll back or leave the prior install usable;
6. model and runtime compatibility must be checked before switching versions;
7. release notes must state when model weights, runtime behavior, privacy behavior, or minimum hardware requirements change.

The project may recommend security updates, but cannot make the primary offline model unusable solely because the machine did not contact an activation/update server.

## 14. Artifact integrity / provenance surfaced to users

Every production package must expose a machine-readable version manifest with at least:

```text
MSTR_VERSION
MODEL_ID
MODEL_REVISION
MODEL_ARTIFACT_SHA256
QUANTIZATION_PROFILE
RUNTIME_VERSION
INTERACTION_CONTRACT_VERSION
MEASUREMENT_PROTOCOL_VERSION
BUILD_REVISION
PLATFORM_ARCH
```

Release distribution must publish cryptographic hashes. Code-signing/notarization should be used on platforms where the project can establish a trusted signing process.

A future SBOM is required before a production binary release, but the exact SBOM format/tool is not selected by T002.

## 15. License visibility

The installation/distribution bundle must make MSTR's license and required third-party notices available offline.

The product must not claim "free/open for everyone" if any required component imposes incompatible use or redistribution restrictions. Backbone rights are formally qualified in T003; T002 requires those results to be surfaced in the released artifact/notice set.

## 16. User-visible behavior for missing optional dependencies

A repository may require its own compiler, test runner, Docker, database, browser, or language runtime for **verification**. Absence of those tools must not prevent basic MSTR launch/inference/edit assistance.

Instead:

- MSTR detects the missing verifier/tool;
- explains what verification cannot run;
- does not silently install system packages;
- does not falsely claim verified completion;
- keeps basic local model assistance available.

This distinction is essential: MSTR itself must be easy to install even when a specific repository is complex.

## 17. No-silent-install rule

Core MSTR must never silently:

- install package managers;
- install Docker;
- modify shell startup files;
- install language SDKs;
- enable background daemons at system scope;
- create cloud accounts;
- upload repositories;
- accept third-party model/data licenses on the user's behalf.

Any optional installation action requires an explicit user request/confirmation and must state what changes.

## 18. Uninstall / data export

The production runtime must eventually provide a documented way to:

- locate MSTR configuration/state;
- locate model artifacts;
- locate per-repo caches/indexes;
- remove generated caches;
- uninstall the runtime/model;
- preserve user repositories/workspaces by default.

If future MSTR versions persist task memory, it must be included in the discoverable/exportable/deletable MSTR-owned state.

## 19. Privacy/offline qualification tests required later

Before release, the required lanes must prove at least:

### `OFFLINE_FIRST_RUN`

With required artifacts already local and outbound network blocked, install/launch and a fixed local coding smoke prompt succeed.

### `ZERO_REQUIRED_EGRESS`

During a fixed local task with network monitoring enabled, no required outbound connection occurs. Any OS noise must be distinguished from the MSTR process tree.

### `NO_ACCOUNT`

Fresh install succeeds with no provider/account credentials present.

### `NO_DEV_TOOLCHAIN_INSTALL`

Basic launch succeeds on a clean machine without Python, Node.js, Docker, or source-build tooling installed.

### `WORKSPACE_SCOPE`

Given a selected test workspace plus sentinel files outside it, default indexing/context does not read the external sentinels.

### `UNINSTALL_PRESERVES_REPO`

Uninstall/cache-clear removes only MSTR-owned state and preserves a checksummed fixture repository unchanged.

### `UPDATE_ROLLBACK`

When update installation is deliberately interrupted/corrupted, the last known-good installation remains usable or the update aborts before switching.

T056 may add adversarial privacy/security variants.

## 20. Installability reporting

Every tested release artifact must report:

- distribution URL/host only as metadata;
- artifact SHA256;
- compressed download bytes;
- installed bytes;
- temporary peak disk;
- user-visible prerequisite list;
- whether admin/root was required;
- TTFI_LOCAL under MSTR-MEASURE-v0;
- number/type of manual user actions required;
- network activity outcome;
- uninstall outcome.

Do not report "one-click" or "zero-config" unless the measured artifact actually demonstrates it.

## 21. Contract change rule

After primary-candidate user testing starts, any change that introduces required login, network access, new system-level prerequisite, telemetry default, remote fallback, or broader workspace access requires:

1. a versioned `MSTR-DIST` contract change;
2. explicit founder review;
3. repeat of affected offline/privacy/install qualification tests.

The universal-local invariant cannot be weakened silently by implementation convenience.

## 22. T002 result

```text
T002_RESULT = PASS
DISTRIBUTION_CONTRACT = MSTR-DIST-v0
LOCAL_ACCOUNTLESS_USE = REQUIRED
OFFLINE_AFTER_ARTIFACT_ACQUISITION = REQUIRED
TELEMETRY_DEFAULT = OFF
USER_CODE_UPLOAD_DEFAULT = NEVER
TRAIN_ON_USER_CODE_DEFAULT = NEVER
BASIC_RUNTIME_DEV_TOOLCHAIN_REQUIREMENT = NONE
BASIC_RUNTIME_DOCKER_REQUIREMENT = NONE
SOURCE_BUILD_REQUIRED_FOR_USERS = NO
REMOTE_MODEL_FALLBACK = PROHIBITED
WORKSPACE_SCOPE_DEFAULT = SELECTED_REPOSITORY
NO_SILENT_SYSTEM_INSTALL = REQUIRED
ARTIFACT_INTEGRITY_MANIFEST = REQUIRED
MODEL_WEIGHT_ACCESS = NONE
NEXT_TASK = T003_PRIMARY_BACKBONE_RIGHTS_GATE
```
