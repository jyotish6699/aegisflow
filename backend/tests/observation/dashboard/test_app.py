from textual.widgets import Footer, Header, Static

from observation.dashboard.ui.app import DashboardApp


def test_dashboard_app_composes_required_shell() -> None:
    app = DashboardApp()

    async def run_test() -> None:
        async with app.run_test():
            assert app.query_one(Header)
            assert app.query_one(Footer)

            assert app.query_one("#project-info")
            assert app.query_one("#git-provider")
            assert app.query_one("#terminal-provider")
            assert app.query_one("#filesystem-provider")
            assert app.query_one("#observations")
            assert app.query_one("#terminal-log")

    import asyncio

    asyncio.run(run_test())
