# B003 Drift Detector Custom-Merge Proof Repair

**State:** MAINTENANCE_REPAIR_CANDIDATE
**Canonical base:** `7da90d2d9cb16a8ebd6c5ede390139831370e861`

## Defect evidence

B025 closeout diagnostic run `33249421768` proved that a genuine GitHub two-parent guarded merge can be rejected as `git.pr_merge_unverifiable` when the merge commit subject omits the pull-request number, even though canonical task/evidence identities bind the exact PR, final head, and merge SHA.

The detector already verifies commit existence, final-head ancestry, recorded identity equality, and merge presence on canonical main. The missing local proof was exact merge topology for custom-subject merge commits.

## Repair boundary

The fallback is fail-closed and applies only when all recorded task/evidence identities agree and the recorded merge is exactly a two-parent merge whose second parent equals the recorded final implementation head. Subject-based PR discovery remains authoritative when present. Squash subjects containing `(#PR)` continue through the existing path. Rebase/cherry-pick history without PR-bearing subject or exact second-parent merge topology remains unverifiable.

Regression coverage proves both a valid custom-subject two-parent merge and a falsified recorded final head that is merely an ancestor rather than exact parent two.

```text
TASK_STATE_MUTATION = NONE
MODEL_EXECUTION = NONE
MODEL_WEIGHT_ACCESS = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
PRODUCTION_RELEASE = NONE
```
