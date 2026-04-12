"""MCP Server: Password Attack tools."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .base import run_tool, format_result, check_tool


app = Server("hackcode-passwords")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="hydra",
            description="Online password brute force tool. Supports SSH, FTP, HTTP, SMB, RDP, MySQL, and 50+ protocols.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target host or IP"},
                    "service": {"type": "string", "description": "Service to attack (ssh, ftp, http-get, http-post-form, smb, rdp, mysql, etc.)"},
                    "username": {"type": "string", "description": "Username or file with usernames (-L)"},
                    "wordlist": {"type": "string", "description": "Password wordlist path", "default": "/usr/share/wordlists/rockyou.txt"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-t 4' for threads, '-f' to stop on first match)"},
                },
                "required": ["target", "service"],
            },
        ),
        Tool(
            name="john",
            description="John the Ripper password cracker. Cracks hashes from /etc/shadow, SAM, NTDS.dit, and more.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hash_file": {"type": "string", "description": "Path to file containing hashes"},
                    "wordlist": {"type": "string", "description": "Wordlist path (omit for default modes)"},
                    "format": {"type": "string", "description": "Hash format (e.g., 'raw-md5', 'raw-sha256', 'NT', 'bcrypt')"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '--show' to display cracked)"},
                },
                "required": ["hash_file"],
            },
        ),
        Tool(
            name="hashcat",
            description="GPU-accelerated password cracker. Fastest hash cracking for large wordlists.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hash": {"type": "string", "description": "Hash string or path to hash file"},
                    "mode": {"type": "integer", "description": "Hash type mode (0=MD5, 100=SHA1, 1000=NTLM, 1800=sha512crypt, 3200=bcrypt)"},
                    "wordlist": {"type": "string", "description": "Wordlist path", "default": "/usr/share/wordlists/rockyou.txt"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-r rules/best64.rule' for rules)"},
                },
                "required": ["hash", "mode"],
            },
        ),
        Tool(
            name="hashid",
            description="Identify hash algorithm type. Useful before cracking to determine the correct mode.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hash": {"type": "string", "description": "Hash string to identify"},
                },
                "required": ["hash"],
            },
        ),
        Tool(
            name="cewl",
            description="Custom wordlist generator that spiders a website and extracts words for targeted password attacks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL to spider"},
                    "depth": {"type": "integer", "description": "Spider depth", "default": 2},
                    "min_length": {"type": "integer", "description": "Minimum word length", "default": 5},
                },
                "required": ["url"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "hydra":
        err = check_tool("hydra")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["hydra"]
        username = arguments.get("username", "")
        if username:
            if username.startswith("/") or username.startswith("./"):
                cmd.extend(["-L", username])
            else:
                cmd.extend(["-l", username])
        cmd.extend(["-P", arguments.get("wordlist", "/usr/share/wordlists/rockyou.txt")])
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        cmd.extend([arguments["target"], arguments["service"]])
        result = run_tool(cmd, timeout=600)

    elif name == "john":
        err = check_tool("john")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["john"]
        if arguments.get("wordlist"):
            cmd.extend(["--wordlist=" + arguments["wordlist"]])
        if arguments.get("format"):
            cmd.extend(["--format=" + arguments["format"]])
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        cmd.append(arguments["hash_file"])
        result = run_tool(cmd, timeout=600)

    elif name == "hashcat":
        err = check_tool("hashcat")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["hashcat", "-m", str(arguments["mode"]), arguments["hash"], arguments.get("wordlist", "/usr/share/wordlists/rockyou.txt")]
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=600)

    elif name == "hashid":
        err = check_tool("hashid")
        if err:
            return [TextContent(type="text", text=err)]
        result = run_tool(["hashid", arguments["hash"]], timeout=10)

    elif name == "cewl":
        err = check_tool("cewl")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["cewl", "-d", str(arguments.get("depth", 2)), "-m", str(arguments.get("min_length", 5)), arguments["url"]]
        result = run_tool(cmd, timeout=120)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return [TextContent(type="text", text=format_result(result))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
