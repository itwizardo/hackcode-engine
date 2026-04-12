"""MCP Server: Web Application Testing tools."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .base import run_tool, format_result, check_tool


app = Server("hackcode-web")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="gobuster",
            description="Directory/file/DNS/vhost brute forcing. Essential for web content discovery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                    "wordlist": {"type": "string", "description": "Path to wordlist", "default": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"},
                    "mode": {"type": "string", "description": "Mode: dir, dns, vhost, fuzz", "default": "dir", "enum": ["dir", "dns", "vhost", "fuzz"]},
                    "extensions": {"type": "string", "description": "File extensions to search for (e.g., 'php,html,txt,bak')"},
                    "flags": {"type": "string", "description": "Additional flags"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="ffuf",
            description="Fast web fuzzer. More flexible than gobuster for fuzzing parameters, headers, and POST data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL with FUZZ keyword (e.g., 'http://target/FUZZ')"},
                    "wordlist": {"type": "string", "description": "Path to wordlist", "default": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-mc 200,301 -fc 404' to filter by status code)"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="nikto",
            description="Web server vulnerability scanner. Checks for dangerous files, outdated software, misconfigurations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target URL or host:port"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-Tuning x' for specific tests)"},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="sqlmap",
            description="Automatic SQL injection detection and exploitation. Can dump databases, extract data, get shells.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL with parameter (e.g., 'http://target/page?id=1')"},
                    "data": {"type": "string", "description": "POST data (e.g., 'user=admin&pass=test')"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '--dbs' to enumerate databases, '--dump' to dump tables, '--os-shell' for OS shell)", "default": "--batch"},
                    "level": {"type": "integer", "description": "Test level 1-5 (higher = more tests)", "default": 1},
                    "risk": {"type": "integer", "description": "Risk level 1-3 (higher = more aggressive)", "default": 1},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="wpscan",
            description="WordPress vulnerability scanner. Enumerates plugins, themes, users, and known vulnerabilities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "WordPress site URL"},
                    "enumerate": {"type": "string", "description": "What to enumerate: vp (vuln plugins), ap (all plugins), vt (vuln themes), u (users)", "default": "vp,vt,u"},
                    "flags": {"type": "string", "description": "Additional flags"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="nuclei",
            description="Template-based vulnerability scanner. Fast scanning with community-maintained templates for CVEs and misconfigs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target URL"},
                    "templates": {"type": "string", "description": "Template tags to use (e.g., 'cve,misconfig,exposure')"},
                    "severity": {"type": "string", "description": "Filter by severity (e.g., 'critical,high')"},
                    "flags": {"type": "string", "description": "Additional flags"},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="searchsploit",
            description="Search ExploitDB offline database for known exploits matching a service/version.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'Apache 2.4.49', 'WordPress 5.8')"},
                    "flags": {"type": "string", "description": "Flags: --json for JSON output, --www for URLs, -x <id> to examine exploit"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="curl_custom",
            description="Custom HTTP requests with full control over method, headers, data, and cookies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                    "method": {"type": "string", "description": "HTTP method", "default": "GET", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]},
                    "headers": {"type": "string", "description": "Headers as 'Key: Value' separated by newlines"},
                    "data": {"type": "string", "description": "Request body data"},
                    "cookie": {"type": "string", "description": "Cookie string"},
                    "follow_redirects": {"type": "boolean", "description": "Follow redirects", "default": True},
                    "flags": {"type": "string", "description": "Additional curl flags (e.g., '-k' to ignore SSL, '-x proxy')"},
                },
                "required": ["url"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "gobuster":
        err = check_tool("gobuster")
        if err:
            return [TextContent(type="text", text=err)]
        mode = arguments.get("mode", "dir")
        cmd = ["gobuster", mode, "-u", arguments["url"], "-w", arguments.get("wordlist", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")]
        if arguments.get("extensions"):
            cmd.extend(["-x", arguments["extensions"]])
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=600)

    elif name == "ffuf":
        err = check_tool("ffuf")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["ffuf", "-u", arguments["url"], "-w", arguments.get("wordlist", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")]
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=600)

    elif name == "nikto":
        err = check_tool("nikto")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["nikto", "-h", arguments["target"]]
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=600)

    elif name == "sqlmap":
        err = check_tool("sqlmap")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["sqlmap", "-u", arguments["url"]]
        if arguments.get("data"):
            cmd.extend(["--data", arguments["data"]])
        cmd.extend(["--level", str(arguments.get("level", 1))])
        cmd.extend(["--risk", str(arguments.get("risk", 1))])
        flags = arguments.get("flags", "--batch")
        cmd.extend(flags.split())
        result = run_tool(cmd, timeout=600)

    elif name == "wpscan":
        err = check_tool("wpscan")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["wpscan", "--url", arguments["url"]]
        if arguments.get("enumerate"):
            cmd.extend(["--enumerate", arguments["enumerate"]])
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=300)

    elif name == "nuclei":
        err = check_tool("nuclei")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["nuclei", "-u", arguments["target"]]
        if arguments.get("templates"):
            cmd.extend(["-tags", arguments["templates"]])
        if arguments.get("severity"):
            cmd.extend(["-severity", arguments["severity"]])
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        result = run_tool(cmd, timeout=600)

    elif name == "searchsploit":
        err = check_tool("searchsploit", "exploitdb")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["searchsploit"]
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        cmd.extend(arguments["query"].split())
        result = run_tool(cmd, timeout=30)

    elif name == "curl_custom":
        cmd = ["curl", "-s", "-i"]
        method = arguments.get("method", "GET")
        cmd.extend(["-X", method])
        if arguments.get("headers"):
            for header in arguments["headers"].split("\n"):
                header = header.strip()
                if header:
                    cmd.extend(["-H", header])
        if arguments.get("data"):
            cmd.extend(["-d", arguments["data"]])
        if arguments.get("cookie"):
            cmd.extend(["-b", arguments["cookie"]])
        if arguments.get("follow_redirects", True):
            cmd.append("-L")
        if arguments.get("flags"):
            cmd.extend(arguments["flags"].split())
        cmd.append(arguments["url"])
        result = run_tool(cmd, timeout=30)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return [TextContent(type="text", text=format_result(result))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
