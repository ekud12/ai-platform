#!/usr/bin/env python3
"""
Agent invocation wrapper for Wiggum.

Handles loading agent prompts, invoking Gemini API with tools,
and processing agent responses.
"""

import json
import time
from pathlib import Path
from typing import Optional, Generator
from dataclasses import dataclass, field

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
except ImportError:
    raise ImportError("google-generativeai package required. Run: pip install google-generativeai")

from .config import WiggumConfig
from .tools import WiggumTools, ToolResult


@dataclass
class AgentResponse:
    """Response from an agent invocation."""
    success: bool
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    error: Optional[str] = None
    raw_response: Optional[GenerateContentResponse] = None


class AgentInvoker:
    """
    Handles agent loading and invocation with Gemini API.

    Integrates with:
    - loader.py for agent prompt loading
    - tools.py for tool execution
    - Gemini function calling API
    """

    def __init__(self, config: WiggumConfig, tools: WiggumTools):
        self.config = config
        self.tools = tools

        # Configure Gemini
        genai.configure(api_key=config.api_key)

        # Create tool declarations
        self.tool_declarations = genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            k: genai.protos.Schema(
                                type=self._map_type(v.get("type", "string")),
                                description=v.get("description", "")
                            )
                            for k, v in t["parameters"].get("properties", {}).items()
                        },
                        required=t["parameters"].get("required", [])
                    )
                )
                for t in WiggumTools.get_tool_declarations()
            ]
        )

        # Import loader
        import sys
        tools_path = config.gemini_root / "tools"
        if str(tools_path) not in sys.path:
            sys.path.insert(0, str(tools_path))

        from loader import load_agent, load_manifest
        self.load_agent = load_agent
        self.load_manifest = load_manifest

    def _map_type(self, type_str: str) -> int:
        """Map JSON schema type to Gemini proto type."""
        type_map = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_map.get(type_str, genai.protos.Type.STRING)

    def get_available_agents(self) -> list[str]:
        """Get list of available agent names from manifest."""
        manifest = self.load_manifest()
        return list(manifest.get("agents", {}).keys())

    def invoke_agent(
        self,
        agent_name: str,
        task: str,
        context: str = "",
        max_tool_rounds: int = 10
    ) -> AgentResponse:
        """
        Invoke an agent with a task.

        Args:
            agent_name: Name of agent from manifest (e.g., 'coder-dotnet')
            task: The task to perform
            context: Additional context (e.g., spec content)
            max_tool_rounds: Maximum rounds of tool calling

        Returns:
            AgentResponse with results
        """
        # Load agent system prompt
        try:
            system_prompt = self.load_agent(agent_name)
        except ValueError as e:
            return AgentResponse(
                success=False,
                content="",
                error=f"Failed to load agent '{agent_name}': {str(e)}"
            )

        # Create model with tools
        model = genai.GenerativeModel(
            model_name=self.config.model_name,
            system_instruction=system_prompt,
            tools=[self.tool_declarations],
        )

        # Build user message
        user_message = f"TASK:\n{task}"
        if context:
            user_message = f"CONTEXT:\n{context}\n\n{user_message}"

        # Start chat for multi-turn tool calling
        chat = model.start_chat(history=[])

        all_tool_calls = []
        all_tool_results = []
        all_files_changed = []
        final_content = ""

        try:
            # Initial request
            response = chat.send_message(user_message)

            for round_num in range(max_tool_rounds):
                # Check for function calls
                if not response.candidates:
                    break

                candidate = response.candidates[0]

                # Check if there are function calls to process
                function_calls = []
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)

                if not function_calls:
                    # No more function calls, extract final text
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_content += part.text
                    break

                # Process function calls
                function_responses = []
                for fc in function_calls:
                    tool_name = fc.name
                    tool_args = dict(fc.args) if fc.args else {}

                    if self.config.verbose:
                        print(f"    [TOOL CALL] {tool_name}({json.dumps(tool_args)[:100]}...)")

                    # Execute tool
                    result = self.tools.execute_tool(tool_name, tool_args)

                    all_tool_calls.append({"name": tool_name, "args": tool_args})
                    all_tool_results.append(result)

                    # Track file changes
                    if tool_name in ["write_file", "append_file"] and result.success:
                        all_files_changed.append(tool_args.get("path", ""))

                    # Check for task_complete signal
                    if tool_name == "task_complete" and result.success:
                        result_data = json.loads(result.output)
                        all_files_changed.extend(result_data.get("files_changed", []))
                        final_content = result_data.get("summary", "Task completed")

                        return AgentResponse(
                            success=True,
                            content=final_content,
                            tool_calls=all_tool_calls,
                            tool_results=all_tool_results,
                            files_changed=list(set(all_files_changed)),
                        )

                    # Build function response
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tool_name,
                                response={"result": result.output if result.success else result.error}
                            )
                        )
                    )

                # Send function responses back to model
                response = chat.send_message(function_responses)

            # Return final response
            return AgentResponse(
                success=True,
                content=final_content,
                tool_calls=all_tool_calls,
                tool_results=all_tool_results,
                files_changed=list(set(all_files_changed)),
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                tool_calls=all_tool_calls,
                tool_results=all_tool_results,
                files_changed=list(set(all_files_changed)),
                error=str(e)
            )

    def invoke_planner(self, spec_content: str) -> Optional[dict]:
        """
        Invoke the planner agent to generate an execution plan.

        Args:
            spec_content: Feature specification content

        Returns:
            Plan dictionary or None if failed
        """
        # Use planning model
        model = genai.GenerativeModel(
            model_name=self.config.planning_model,
            system_instruction=self.load_agent("planner"),
            generation_config={"response_mime_type": "application/json"}
        )

        try:
            response = model.generate_content(f"SPECIFICATION:\n{spec_content}")
            plan_text = response.text

            # Parse JSON
            clean = plan_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)

        except Exception as e:
            if self.config.verbose:
                print(f"    [ERROR] Planner failed: {str(e)}")
            return None

    def invoke_reviewer(self, agent_name: str, code_changes: str, task: str) -> dict:
        """
        Invoke a reviewer agent to validate code changes.

        Args:
            agent_name: Reviewer agent name (e.g., 'reviewer-dotnet')
            code_changes: The code that was written/modified
            task: Original task description

        Returns:
            Review result dict with status, issues, etc.
        """
        model = genai.GenerativeModel(
            model_name=self.config.model_name,
            system_instruction=self.load_agent(agent_name),
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
ORIGINAL TASK:
{task}

CODE CHANGES TO REVIEW:
{code_changes}

Review the code against all applicable rules and provide your verdict.
"""

        try:
            response = model.generate_content(prompt)
            clean = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "issues": []
            }

    def invoke_meta(self, all_changes: str, all_reviews: list[dict]) -> dict:
        """
        Invoke the meta agent for final approval.

        Args:
            all_changes: Summary of all changes made
            all_reviews: List of all review results

        Returns:
            Meta verdict dict
        """
        model = genai.GenerativeModel(
            model_name=self.config.model_name,
            system_instruction=self.load_agent("meta"),
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
ALL CHANGES MADE:
{all_changes}

REVIEW RESULTS:
{json.dumps(all_reviews, indent=2)}

Provide final verdict on whether these changes should be approved.
"""

        try:
            response = model.generate_content(prompt)
            clean = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)

        except Exception as e:
            return {
                "verdict": "ERROR",
                "error": str(e),
                "reason": "Failed to invoke meta agent"
            }
