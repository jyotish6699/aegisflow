import asyncio
from pathlib import Path

import pytest

from observation.core.enums import ProviderType
from observation.providers.filesystem.provider import FilesystemProvider


async def collect_observation(
    provider: FilesystemProvider,
    observation_type: str,
    timeout: float = 1.0,
):
    deadline = asyncio.get_running_loop().time() + timeout

    while asyncio.get_running_loop().time() < deadline:
        observations = [
            observation
            async for observation in provider.observe()
        ]

        for observation in observations:
            if observation.observation_type == observation_type:
                return observation

        await asyncio.sleep(0.01)

    return None


@pytest.mark.asyncio
async def test_filesystem_provider_real_modify_emits_file_modified(
    tmp_path: Path,
) -> None:
    """
    A real filesystem modification should produce a file.modified
    observation with the expected provider and metadata.
    """

    test_file = tmp_path / "test.txt"

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.write_text("initial")

    created = await collect_observation(
        provider,
        "file.created",
    )

    assert created is not None

    test_file.write_text("updated")

    modified = await collect_observation(
        provider,
        "file.modified",
    )

    await provider.stop()

    assert modified is not None
    assert modified.provider == ProviderType.FILESYSTEM
    assert modified.observation_type == "file.modified"

    assert modified.metadata.source == "filesystem"

    assert modified.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_real_file_lifecycle(
    tmp_path: Path,
) -> None:
    """
    A real file lifecycle should produce file.created,
    file.modified, and file.deleted observations.
    """

    test_file = tmp_path / "test.txt"

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.write_text("initial")

    created = await collect_observation(
        provider,
        "file.created",
    )

    assert created is not None
    assert created.provider == ProviderType.FILESYSTEM
    assert created.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }

    test_file.write_text("updated")

    modified = await collect_observation(
        provider,
        "file.modified",
    )

    assert modified is not None
    assert modified.provider == ProviderType.FILESYSTEM
    assert modified.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }

    test_file.unlink()

    deleted = await collect_observation(
        provider,
        "file.deleted",
    )

    await provider.stop()

    assert deleted is not None
    assert deleted.provider == ProviderType.FILESYSTEM
    assert deleted.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }