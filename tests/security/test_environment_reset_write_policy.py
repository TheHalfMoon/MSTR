from __future__ import annotations

import pytest

import mstr_qualify.environment.reset as reset_module
from mstr_qualify.environment import EffectEnvelope, EnvironmentResetError


@pytest.mark.parametrize("filesystem_writes", ["NONE", "TEMP_ONLY"])
def test_clean_reset_requires_worktree_write_policy(filesystem_writes: str) -> None:
    effects = EffectEnvelope(
        network_access="NONE",
        allowed_hosts=(),
        secret_access=False,
        allowed_secret_ids=(),
        filesystem_writes=filesystem_writes,
        subprocess_execution=True,
        authority_id=None,
    )

    with pytest.raises(EnvironmentResetError, match="requires worktree write authority"):
        reset_module._assert_reset_write_policy(effects)


def test_clean_reset_accepts_worktree_write_policy() -> None:
    effects = EffectEnvelope(
        network_access="NONE",
        allowed_hosts=(),
        secret_access=False,
        allowed_secret_ids=(),
        filesystem_writes="WORKTREE_AND_TEMP",
        subprocess_execution=True,
        authority_id=None,
    )

    reset_module._assert_reset_write_policy(effects)
