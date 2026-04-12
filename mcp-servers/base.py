"""Base utilities for HackCode MCP tool wrappers."""

import subprocess
import shutil
import json
import time
from typing import Optional


def is_installed(binary: str) -> bool:
    """Check if a binary is available on PATH."""
    return shutil.which(binary) is not None


def run_tool(
    command: list[str],
    timeout: int = 300,
    input_data: Optional[str] = None,
) -> dict:
    """Run a security tool and return structured output.

    Returns:
        dict with keys: success, command, stdout, stderr, exit_code, duration_seconds
    """
    cmd_str = " ".join(command)
    start = time.time()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=input_data,
        )
        duration = round(time.time() - start, 2)

        return {
            "success": result.returncode == 0,
            "command": cmd_str,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "duration_seconds": duration,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "command": cmd_str,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "exit_code": -1,
            "duration_seconds": timeout,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "command": cmd_str,
            "stdout": "",
            "stderr": f"Tool not found: {command[0]}. Install with: sudo apt install {command[0]}",
            "exit_code": -1,
            "duration_seconds": 0,
        }
    except Exception as e:
        return {
            "success": False,
            "command": cmd_str,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "duration_seconds": round(time.time() - start, 2),
        }


def format_result(result: dict) -> str:
    """Format a tool result for AI consumption."""
    parts = []
    parts.append(f"Command: {result['command']}")
    parts.append(f"Status: {'SUCCESS' if result['success'] else 'FAILED'} (exit code {result['exit_code']})")
    parts.append(f"Duration: {result['duration_seconds']}s")

    if result["stdout"]:
        parts.append(f"\n--- Output ---\n{result['stdout']}")
    if result["stderr"] and not result["success"]:
        parts.append(f"\n--- Errors ---\n{result['stderr']}")

    return "\n".join(parts)


def check_tool(binary: str, package: Optional[str] = None) -> str:
    """Check if a tool is installed, return error message if not."""
    if is_installed(binary):
        return ""
    pkg = package or binary
    return f"Error: {binary} is not installed. Install with: sudo apt install {pkg}"
