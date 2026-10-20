"""Catch missing connector exports and ADK startup failures before deployment."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
try:
    ADK_AVAILABLE = importlib.util.find_spec("google.adk") is not None
except ModuleNotFoundError:
    ADK_AVAILABLE = False


class AgentStartupTests(unittest.TestCase):
    def test_agent_packages_and_public_connector_exports_import(self):
        # Run a fresh interpreter so a previous test cannot mask a broken import
        # by leaving an older, working module in sys.modules.
        result = subprocess.run(
            [sys.executable, "-c", "import tools; import agents; "
             "assert all(hasattr(tools, name) for name in tools.__all__)"],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(ADK_AVAILABLE, "Install requirements.txt for ADK startup checks")
    def test_adk_entrypoint_is_a_real_adk_agent(self):
        result = subprocess.run(
            [sys.executable, "-c", "from agent.agent import root_agent; "
             "from google.adk.agents import BaseAgent; "
             "assert isinstance(root_agent, BaseAgent), type(root_agent); "
             "assert len(root_agent.sub_agents) == 3"],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
            env={**os.environ, "BIGQUERY_MCP_MODE": "none"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(ADK_AVAILABLE, "Install requirements.txt for ADK runner checks")
    def test_chat_runner_can_build_tools_and_return_a_message(self):
        # Exercise the real ADK runner and tool declarations with an offline
        # model; no Gemini credentials, BigQuery requests, or cloud writes.
        from google.adk.models.base_llm import BaseLlm
        from google.adk.models.llm_response import LlmResponse
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        from agents.regime_orchestrator_agent import create_orchestrator_adk_pipeline
        import asyncio

        class DiagnosticModel(BaseLlm):
            model: str = "local-startup-test"

            async def generate_content_async(self, llm_request, stream=False):
                yield LlmResponse(content=types.Content(
                    role="model", parts=[types.Part(text="Startup chat succeeded.")]))

        async def run():
            agent = create_orchestrator_adk_pipeline(include_mcp_toolsets=False)
            for specialist in [agent, *agent.sub_agents]:
                specialist.model = DiagnosticModel()
            runner = InMemoryRunner(agent=agent, app_name="startup_test")
            try:
                session = await runner.session_service.create_session(
                    app_name="startup_test", user_id="local_test")
                replies = []
                async for event in runner.run_async(
                    user_id="local_test", session_id=session.id,
                    new_message=types.Content(role="user", parts=[types.Part(text="Hello")]),
                ):
                    if event.content and event.content.role == "model":
                        replies.extend(p.text for p in event.content.parts if p.text)
                return replies
            finally:
                await runner.close()

        self.assertIn("Startup chat succeeded.", asyncio.run(run()))


if __name__ == "__main__":
    unittest.main()
