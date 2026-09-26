from pathlib import Path

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

    import asyncio

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

    import asyncio

    asyncio.run(run_test())


def test_dashboard_app_renders_empty_observation_and_log_state() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")
            terminal_log = app.query_one("#terminal-log")

            assert "Waiting for observations..." in str(
                observations.render()
            )
            assert "Waiting for terminal output..." in str(
                terminal_log.render()
            )

    import asyncio

    asyncio.run(run_test())


def test_dashboard_app_preserves_observation_and_terminal_log_content() -> None:
    state = create_dashboard_state()

    state.observations.append(
        type(
            "ObservationEntry",
            (),
            {"rendered_message": "main changed"},
        )()
    )
    state.terminal_log.append("pytest executed")

    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            observations = app.query_one("#observations")
            terminal_log = app.query_one("#terminal-log")

            assert "main changed" in str(observations.render())
            assert "pytest executed" in str(terminal_log.render())

    import asyncio

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

    import asyncio

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

    import asyncio

    asyncio.run(run_test())


def test_dashboard_app_refreshes_observations_and_terminal_log() -> None:
    state = create_dashboard_state()
    app = DashboardApp(state)

    async def run_test() -> None:
        async with app.run_test():
            state.observations.append(
                type(
                    "ObservationEntry",
                    (),
                    {"rendered_message": "src/main.py updated"},
                )()
            )
            state.terminal_log.append("pytest executed")

            app.refresh_state()

            observations = app.query_one("#observations")
            terminal_log = app.query_one("#terminal-log")

            assert "src/main.py updated" in str(
                observations.render()
            )
            assert "pytest executed" in str(
                terminal_log.render()
            )

    import asyncio

    asyncio.run(run_test())


