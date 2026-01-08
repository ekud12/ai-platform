#!/usr/bin/env python3
"""
Gemini Tool Bindings for Wiggum.

This module defines the tools that Gemini can call during autonomous execution.
Each tool is a Python function that gets registered with the Gemini API.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None


class WiggumTools:
    """
    Tool implementations for Wiggum.

    These tools are bound to Gemini's function calling API,
    allowing the LLM to read/write files and execute commands.
    """

    def __init__(self, workspace_root: Path, dry_run: bool = False, verbose: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.blocked_paths = [".git", "node_modules", ".env"]
        self.execution_log: list[dict] = []

    def _log(self, action: str, details: dict):
        """Log tool execution."""
        entry = {"action": action, **details}
        self.execution_log.append(entry)
        if self.verbose:
            print(f"  [TOOL] {action}: {details}")

    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is allowed for operations."""
        path_obj = Path(path)

        # Check against blocked paths
        for blocked in self.blocked_paths:
            if blocked in str(path_obj):
                return False

        # Must be within workspace
        try:
            resolved = (self.workspace_root / path_obj).resolve()
            resolved.relative_to(self.workspace_root.resolve())
            return True
        except ValueError:
            return False

    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to workspace root."""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return self.workspace_root / path_obj

    # --- File Operations ---

    def read_file(self, path: str) -> ToolResult:
        """
        Read the contents of a file.

        Args:
            path: Path to the file (relative to workspace or absolute)

        Returns:
            ToolResult with file contents or error
        """
        self._log("read_file", {"path": path})

        if not self._is_path_allowed(path):
            return ToolResult(False, "", f"Path not allowed: {path}")

        resolved = self._resolve_path(path)

        if not resolved.exists():
            return ToolResult(False, "", f"File not found: {path}")

        if not resolved.is_file():
            return ToolResult(False, "", f"Not a file: {path}")

        try:
            content = resolved.read_text(encoding="utf-8")
            return ToolResult(True, content)
        except Exception as e:
            return ToolResult(False, "", str(e))

    def write_file(self, path: str, content: str) -> ToolResult:
        """
        Write content to a file. Creates parent directories if needed.

        Args:
            path: Path to the file (relative to workspace or absolute)
            content: Content to write

        Returns:
            ToolResult with success status
        """
        self._log("write_file", {"path": path, "content_length": len(content)})

        if not self._is_path_allowed(path):
            return ToolResult(False, "", f"Path not allowed: {path}")

        resolved = self._resolve_path(path)

        if self.dry_run:
            return ToolResult(True, f"[DRY RUN] Would write {len(content)} bytes to {path}")

        try:
            # Create parent directories
            resolved.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            resolved.write_text(content, encoding="utf-8")
            return ToolResult(True, f"Successfully wrote {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def append_file(self, path: str, content: str) -> ToolResult:
        """
        Append content to a file.

        Args:
            path: Path to the file
            content: Content to append

        Returns:
            ToolResult with success status
        """
        self._log("append_file", {"path": path, "content_length": len(content)})

        if not self._is_path_allowed(path):
            return ToolResult(False, "", f"Path not allowed: {path}")

        resolved = self._resolve_path(path)

        if self.dry_run:
            return ToolResult(True, f"[DRY RUN] Would append {len(content)} bytes to {path}")

        try:
            with open(resolved, "a", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(True, f"Successfully appended {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def list_directory(self, path: str = ".") -> ToolResult:
        """
        List contents of a directory.

        Args:
            path: Directory path (default: workspace root)

        Returns:
            ToolResult with directory listing
        """
        self._log("list_directory", {"path": path})

        resolved = self._resolve_path(path)

        if not resolved.exists():
            return ToolResult(False, "", f"Directory not found: {path}")

        if not resolved.is_dir():
            return ToolResult(False, "", f"Not a directory: {path}")

        try:
            entries = []
            for entry in sorted(resolved.iterdir()):
                entry_type = "dir" if entry.is_dir() else "file"
                entries.append(f"{entry_type}: {entry.name}")

            return ToolResult(True, "\n".join(entries))
        except Exception as e:
            return ToolResult(False, "", str(e))

    def file_exists(self, path: str) -> ToolResult:
        """
        Check if a file or directory exists.

        Args:
            path: Path to check

        Returns:
            ToolResult with exists status
        """
        self._log("file_exists", {"path": path})

        resolved = self._resolve_path(path)
        exists = resolved.exists()
        file_type = "directory" if resolved.is_dir() else "file" if resolved.is_file() else "unknown"

        return ToolResult(True, json.dumps({"exists": exists, "type": file_type}))

    # --- Shell Operations ---

    def run_command(self, command: str, working_dir: Optional[str] = None) -> ToolResult:
        """
        Execute a shell command.

        Args:
            command: Command to execute
            working_dir: Working directory (default: workspace root)

        Returns:
            ToolResult with command output
        """
        self._log("run_command", {"command": command, "working_dir": working_dir})

        # Block dangerous commands
        dangerous_patterns = [
            "rm -rf", "rmdir /s", "del /s",
            "git push", "git commit",
            "sudo", "runas",
            "curl | sh", "wget | sh",
        ]

        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return ToolResult(False, "", f"Blocked dangerous command pattern: {pattern}")

        cwd = self._resolve_path(working_dir) if working_dir else self.workspace_root

        if self.dry_run:
            return ToolResult(True, f"[DRY RUN] Would execute: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]: {result.stderr}"

            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=f"Exit code: {result.returncode}" if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", "Command timed out after 120 seconds")
        except Exception as e:
            return ToolResult(False, "", str(e))

    # --- Search Operations ---

    def search_files(self, pattern: str, path: str = ".") -> ToolResult:
        """
        Search for files matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.cs")
            path: Starting directory

        Returns:
            ToolResult with matching files
        """
        self._log("search_files", {"pattern": pattern, "path": path})

        resolved = self._resolve_path(path)

        try:
            matches = list(resolved.glob(pattern))
            # Make paths relative to workspace
            relative_matches = [
                str(m.relative_to(self.workspace_root))
                for m in matches
                if self._is_path_allowed(str(m.relative_to(self.workspace_root)))
            ]

            return ToolResult(True, "\n".join(relative_matches[:100]))  # Limit to 100 results
        except Exception as e:
            return ToolResult(False, "", str(e))

    def search_content(self, pattern: str, path: str = ".", file_pattern: str = "*") -> ToolResult:
        """
        Search for content within files (like grep).

        Args:
            pattern: Text or regex pattern to search
            path: Directory to search in
            file_pattern: File glob pattern to filter

        Returns:
            ToolResult with matching lines
        """
        self._log("search_content", {"pattern": pattern, "path": path, "file_pattern": file_pattern})

        resolved = self._resolve_path(path)

        try:
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            results = []

            for file_path in resolved.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                if not self._is_path_allowed(str(file_path.relative_to(self.workspace_root))):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.splitlines(), 1):
                        if regex.search(line):
                            rel_path = file_path.relative_to(self.workspace_root)
                            results.append(f"{rel_path}:{i}: {line.strip()}")

                            if len(results) >= 50:  # Limit results
                                results.append("... (truncated)")
                                return ToolResult(True, "\n".join(results))
                except:
                    continue

            return ToolResult(True, "\n".join(results) if results else "No matches found")
        except Exception as e:
            return ToolResult(False, "", str(e))

    # --- Tool Declarations for Gemini API ---

    @staticmethod
    def get_tool_declarations() -> list[dict]:
        """
        Get Gemini function declarations for all tools.

        Returns:
            List of function declarations for Gemini API
        """
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file from the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file (relative to workspace root)"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file. Creates parent directories if needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file (relative to workspace root)"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "append_file",
                "description": "Append content to an existing file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path (default: workspace root)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "file_exists",
                "description": "Check if a file or directory exists",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to check"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "run_command",
                "description": "Execute a shell command. Dangerous commands are blocked.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute"
                        },
                        "working_dir": {
                            "type": "string",
                            "description": "Working directory (optional)"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files matching a glob pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern (e.g., '**/*.cs')"
                        },
                        "path": {
                            "type": "string",
                            "description": "Starting directory (default: workspace root)"
                        }
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "search_content",
                "description": "Search for text within files (like grep)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Text or regex pattern to search"
                        },
                        "path": {
                            "type": "string",
                            "description": "Directory to search in"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "File glob pattern (e.g., '*.cs')"
                        }
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "task_complete",
                "description": "Signal that the current task is complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Brief summary of what was accomplished"
                        },
                        "files_changed": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of files that were created or modified"
                        }
                    },
                    "required": ["summary"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, args: dict) -> ToolResult:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool

        Returns:
            ToolResult from the tool execution
        """
        tool_map: dict[str, Callable] = {
            "read_file": lambda a: self.read_file(a.get("path", "")),
            "write_file": lambda a: self.write_file(a.get("path", ""), a.get("content", "")),
            "append_file": lambda a: self.append_file(a.get("path", ""), a.get("content", "")),
            "list_directory": lambda a: self.list_directory(a.get("path", ".")),
            "file_exists": lambda a: self.file_exists(a.get("path", "")),
            "run_command": lambda a: self.run_command(a.get("command", ""), a.get("working_dir")),
            "search_files": lambda a: self.search_files(a.get("pattern", ""), a.get("path", ".")),
            "search_content": lambda a: self.search_content(
                a.get("pattern", ""), a.get("path", "."), a.get("file_pattern", "*")
            ),
            "task_complete": lambda a: ToolResult(True, json.dumps({
                "status": "complete",
                "summary": a.get("summary", ""),
                "files_changed": a.get("files_changed", [])
            })),
        }

        if tool_name not in tool_map:
            return ToolResult(False, "", f"Unknown tool: {tool_name}")

        try:
            return tool_map[tool_name](args)
        except Exception as e:
            return ToolResult(False, "", f"Tool execution error: {str(e)}")
