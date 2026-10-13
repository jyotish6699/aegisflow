from pathlib import Path
import asyncio

from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.state import (
    DashboardState,
    DashboardStatus,
    FilesystemProviderState,
    GitProviderState,
    ProjectState,
    ProviderStatus,
    TerminalProviderState,
)
from observation.dashboard.ui.app import DashboardApp


def create_dashboard_state() -> DashboardState:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
        repository="aegisflow",
    )

    return DashboardState(
        project=project,
        overall_status=DashboardStatus.RUNNING,
        git=GitProviderState(
            status=ProviderStatus.RUNNING,
            repository="aegisflow",
            branch="feature/observation-dashboard-v0",
        ),
        terminal=TerminalProviderState(
            status=ProviderStatus.RUNNING,
            shell="zsh",
            cwd=Path("/home/jyotish/dev/aegisflow"),
            active_session=True,
        ),
        filesystem=FilesystemProviderState(
            status=ProviderStatus.RUNNING,
            workspace=Path("/home/jyotish/dev/aegisflow"),
            event_type="file.modified",
        ),
    )


def test_dashboard_app_renders_project_state() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            project_info = app.query_one("#project-info")

            assert "aegisflow" in str(project_info.render())
            assert "/home/jyotish/dev/aegisflow" in str(
                project_info.render()
            )
            assert "feature/observation-dashboard-v0" in str(
                project_info.render()
            )
            assert "RUNNING" in str(project_info.render())

    asyncio.run(run_test())


def test_dashboard_app_renders_provider_states() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            git = app.query_one("#git-provider")
            terminal = app.query_one("#terminal-provider")
            filesystem = app.query_one("#filesystem-provider")

            assert "RUNNING" in str(git.render())
            assert "feature/observation-dashboard-v0" in str(
                git.render()
            )

            assert "RUNNING" in str(terminal.render())
            assert "zsh" in str(terminal.render())
            assert "/home/jyotish/dev/aegisflow" in str(
                terminal.render()
            )

            assert "RUNNING" in str(filesystem.render())
            assert "file.modified" in str(filesystem.render())

    asyncio.run(run_test())


def test_dashboard_app_renders_empty_observation_state() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()

            observations = app.query_one("#observations")

            assert not state.observations
            assert observations is not None

            assert "Waiting for observations..." in str(
                observations.lines
            )

    asyncio.run(run_test())


def test_dashboard_app_preserves_observation_content() -> None:
    state = create_dashboard_state()

    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": "main changed"},
        )()
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(120, 40)):
            observations = app.query_one("#observations")
            assert "main changed" in str(observations.lines)

    asyncio.run(run_test())


def test_dashboard_app_has_one_observation_stream() -> None:
    state = create_dashboard_state()
    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": "[stdout] HELLO"},
        )()
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(120, 40)):
            observations = app.query_one("#observations")

            assert "[stdout] HELLO" in str(observations.lines)
            assert not app.query("#terminal-log")

    asyncio.run(run_test())


def test_dashboard_app_preserves_manual_observation_scroll() -> None:
    state = create_dashboard_state()
    state.observations.extend(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": f"observation-{index}"},
        )()
        for index in range(30)
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(80, 20)) as pilot:
            observations = app.query_one("#observations")
            observations.scroll_home(animate=False, immediate=True)
            state.observations.append(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "new observation"},
                )()
            )

            app.refresh_state()

            assert observations.scroll_y == 0

            observations.scroll_end(animate=False, immediate=True)
            await pilot.pause()
            state.observations.append(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "latest observation"},
                )()
            )
            app.refresh_state()
            await pilot.pause()

            assert observations.is_vertical_scroll_end

    asyncio.run(run_test())


def test_dashboard_app_removes_evicted_observations_from_log() -> None:
    state = create_dashboard_state()
    state.max_observations = 2
    state.observations.extend(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": f"observation-{index}"},
        )()
        for index in range(2)
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(80, 20)):
            state.add_observation(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "observation-2"},
                )()
            )
            app.refresh_state()

            observations = app.query_one("#observations")
            rendered = str(observations.lines)

            assert "observation-0" not in rendered
            assert "observation-1" in rendered
            assert "observation-2" in rendered

    asyncio.run(run_test())


def test_dashboard_app_refreshes_project_and_git_state() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            state.project.name = "updated-project"
            state.git.branch = "main"
            state.overall_status = DashboardStatus.IDLE

            app.refresh_state()

            project_info = app.query_one("#project-info")
            git = app.query_one("#git-provider")

            assert "updated-project" in str(project_info.render())
            assert "main" in str(project_info.render())
            assert "IDLE" in str(project_info.render())
            assert "main" in str(git.render())

    asyncio.run(run_test())


def test_dashboard_app_refreshes_provider_states() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            state.terminal.status = ProviderStatus.IDLE
            state.terminal.active_session = False
            state.terminal.cwd = Path("/tmp")

            state.filesystem.status = ProviderStatus.IDLE
            state.filesystem.event_type = "file.deleted"

            app.refresh_state()

            terminal = app.query_one("#terminal-provider")
            filesystem = app.query_one("#filesystem-provider")

            assert "IDLE" in str(terminal.render())
            assert "/tmp" in str(terminal.render())
            assert "NO" in str(terminal.render())

            assert "IDLE" in str(filesystem.render())
            assert "file.deleted" in str(filesystem.render())

    asyncio.run(run_test())


def test_dashboard_app_refreshes_observations() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            state.observations.append(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "src/main.py updated"},
                )()
            )

            app.refresh_state()
            await pilot.pause()

            observations = app.query_one("#observations")
            assert "src/main.py updated" in str(
                observations.lines
            )

    asyncio.run(run_test())


def test_dashboard_app_starts_and_stops_runtime_bridge() -> None:
    state = create_dashboard_state()

    class FakeBridge:
        def __init__(self) -> None:
            self.started = False
            self.stopped = False

        async def start(self) -> None:
            self.started = True

        async def stop(self) -> None:
            self.stopped = True

    bridge = FakeBridge()

    app = DashboardApp(
        state=state,
        bridge=bridge,
    )

    async def run_test() -> None:
        async with app.run_test():
            await asyncio.sleep(0)

            assert bridge.started is True

        assert bridge.stopped is True

    asyncio.run(run_test())


def test_dashboard_app_refreshes_from_runtime_bridge() -> None:
    state = create_dashboard_state()

    class FakeBridge:
        async def start(self) -> None:
            state.git.branch = "main"
            state.overall_status = DashboardStatus.RUNNING

        async def stop(self) -> None:
            pass

    bridge = FakeBridge()

    app = DashboardApp(
        state=state,
        bridge=bridge,
    )

    async def run_test() -> None:
        async with app.run_test():
            app.refresh_state()

            project_info = app.query_one("#project-info")

            assert "main" in str(project_info.render())
            assert "RUNNING" in str(project_info.render())

    asyncio.run(run_test())


def test_dashboard_app_appends_only_new_observations() -> None:
    state = create_dashboard_state()

    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": "first observation"},
        )()
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")

            assert "first observation" in str(
                observations.lines
            )

            state.observations.append(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "second observation"},
                )()
            )

            app.refresh_state()

            rendered = str(observations.lines)

            assert "first observation" in rendered
            assert "second observation" in rendered

    asyncio.run(run_test())


def test_dashboard_app_handles_observation_buffer_trimming() -> None:
    state = create_dashboard_state()

    state.max_observations = 2

    first = type(
        "ObservationEntry",
        (),
        {"rendered_message": "first"},
    )()

    second = type(
        "ObservationEntry",
        (),
        {"rendered_message": "second"},
    )()

    third = type(
        "ObservationEntry",
        (),
        {"rendered_message": "third"},
    )()

    state.observations.extend(
        [first, second]
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")

            assert "first" in str(observations.lines)
            assert "second" in str(observations.lines)

            state.observations = [second, third]

            app.refresh_state()

            rendered = str(observations.lines)

            assert "second" in rendered
            assert "third" in rendered

    asyncio.run(run_test())


def test_dashboard_app_formats_observation_with_timestamp_and_provider() -> None:
    from datetime import datetime

    state = create_dashboard_state()

    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {
                "timestamp": datetime(
                    2026,
                    10,
                    1,
                    23,
                    54,
                    2,
                ),
                "provider": "filesystem",
                "rendered_message": "src/main.py updated",
            },
        )()
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")

            rendered = str(observations.lines)

            assert "23:54:02" in rendered
            assert "FILESYSTEM" in rendered
            assert "src/main.py updated" in rendered

    asyncio.run(run_test())


def test_dashboard_app_preserves_actual_observation_message() -> None:
    from datetime import datetime

    state = create_dashboard_state()

    actual_command = "pytest tests/observation/dashboard/test_app.py -v"

    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {
                "timestamp": datetime(
                    2026,
                    10,
                    1,
                    23,
                    55,
                    10,
                ),
                "provider": "terminal",
                "rendered_message": (
                    f"{actual_command} executed successfully"
                ),
            },
        )()
    )

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")

            rendered = str(observations.lines)

            assert actual_command in rendered
            assert "executed successfully" in rendered

    asyncio.run(run_test())
    