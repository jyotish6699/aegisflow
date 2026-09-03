import asyncio
from pathlib import Path
import pytest

from observation.core.enums import ProviderType
from observation.providers.filesystem.provider import FilesystemProvider


@pytest.mark.asyncio
async def test_filesystem_provider_has_correct_provider_type(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should identify itself as the Filesystem provider.
    """

    provider = FilesystemProvider(tmp_path)

    assert provider.provider_type == ProviderType.FILESYSTEM


@pytest.mark.asyncio
async def test_filesystem_provider_does_not_observe_before_start(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should not produce observations before start().
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_filesystem_provider_stops_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should stop producing observations after stop().
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()
    await provider.stop()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_created_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.created observation
    when a file is created inside the workspace.
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        if observations:
            observation = observations[0]
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.created"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_modified_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.modified observation
    when a file is modified inside the workspace.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.write_text("updated")

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        for item in observations:
            if item.observation_type == "file.modified":
                observation = item
                break

        if observation is not None:
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.modified"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_deleted_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.deleted observation
    when a file is deleted inside the workspace.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.unlink()

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        for item in observations:
            if item.observation_type == "file.deleted":
                observation = item
                break

        if observation is not None:
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.deleted"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }