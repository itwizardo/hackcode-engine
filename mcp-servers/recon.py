"""MCP Server: Reconnaissance & Information Gathering tools."""

import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .base import run_tool, format_result, check_tool


app = Server("hackcode-recon")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="nmap",
            description="Port scanning, service detection, OS fingerprinting, and NSE scripts. The most essential recon tool.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP, hostname, or CIDR range"},
                    "flags": {"type": "string", "description": "Additional nmap flags (e.g., '-sV -sC -O -p-' for full scan, '-sn' for ping sweep, '--script vuln' for vulnerability scripts)", "default": "-sV -sC"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 600},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="masscan",
            description="Ultra-fast port scanner for large IP ranges. Use for quick initial scans before detailed nmap.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP or CIDR range"},
                    "ports": {"type": "string", "description": "Port range (e.g., '0-65535', '80,443,8080')", "default": "1-1000"},
                    "rate": {"type": "integer", "description": "Packets per second", "default": 1000},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="whois",
            description="Domain/IP registration lookup. Returns registrant info, nameservers, creation/expiry dates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Domain name or IP address"},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="dig",
            description="DNS lookup tool. Query specific record types (A, AAAA, MX, NS, TXT, CNAME, SOA, ANY).",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name to query"},
                    "record_type": {"type": "string", "description": "DNS record type", "default": "ANY", "enum": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "ANY", "AXFR"]},
                    "server": {"type": "string", "description": "DNS server to query (optional)"},
                },
                "required": ["domain"],
            },
        ),
        Tool(
            name="whatweb",
            description="Web technology fingerprinting. Identifies CMS, frameworks, server software, JavaScript libraries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                    "aggression": {"type": "integer", "description": "Aggression level 1-4 (1=stealthy, 4=heavy)", "default": 1},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="wafw00f",
            description="Web Application Firewall detection and fingerprinting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="enum4linux",
            description="Windows/Samba enumeration. Extracts users, shares, groups, password policy, OS info via SMB/RPC.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP address"},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-a' for all, '-U' for users, '-S' for shares)", "default": "-a"},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="smbclient",
            description="SMB client for listing and accessing network shares. Test for null sessions and anonymous access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP address"},
                    "share": {"type": "string", "description": "Share name to connect to (omit for listing shares)"},
                    "username": {"type": "string", "description": "Username (empty for null session)", "default": ""},
                    "password": {"type": "string", "description": "Password (empty for null session)", "default": ""},
                    "command": {"type": "string", "description": "Command to run on share (e.g., 'dir', 'get file.txt')"},
                },
                "required": ["target"],
            },
        ),
        Tool(
            name="dnsrecon",
            description="DNS enumeration including zone transfers, brute force subdomain discovery, and record enumeration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Target domain"},
                    "type": {"type": "string", "description": "Scan type: std (standard), brt (brute force), axfr (zone transfer)", "default": "std"},
                },
                "required": ["domain"],
            },
        ),
        Tool(
            name="snmpwalk",
            description="SNMP enumeration. Walk the MIB tree to extract system info, interfaces, routes, running processes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP address"},
                    "community": {"type": "string", "description": "SNMP community string", "default": "public"},
                    "version": {"type": "string", "description": "SNMP version (1, 2c, 3)", "default": "2c"},
                },
                "required": ["target"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "nmap":
        err = check_tool("nmap")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["nmap"]
        flags = arguments.get("flags", "-sV -sC")
        cmd.extend(flags.split())
        cmd.append(arguments["target"])
        result = run_tool(cmd, timeout=arguments.get("timeout", 600))

    elif name == "masscan":
        err = check_tool("masscan")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["masscan", arguments["target"]]
        cmd.extend(["-p", arguments.get("ports", "1-1000")])
        cmd.extend(["--rate", str(arguments.get("rate", 1000))])
        result = run_tool(cmd, timeout=300)

    elif name == "whois":
        err = check_tool("whois")
        if err:
            return [TextContent(type="text", text=err)]
        result = run_tool(["whois", arguments["target"]], timeout=30)

    elif name == "dig":
        err = check_tool("dig", "dnsutils")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["dig"]
        if arguments.get("server"):
            cmd.append(f"@{arguments['server']}")
        cmd.append(arguments["domain"])
        cmd.append(arguments.get("record_type", "ANY"))
        result = run_tool(cmd, timeout=30)

    elif name == "whatweb":
        err = check_tool("whatweb")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["whatweb", f"--aggression={arguments.get('aggression', 1)}", arguments["url"]]
        result = run_tool(cmd, timeout=60)

    elif name == "wafw00f":
        err = check_tool("wafw00f")
        if err:
            return [TextContent(type="text", text=err)]
        result = run_tool(["wafw00f", arguments["url"]], timeout=30)

    elif name == "enum4linux":
        err = check_tool("enum4linux")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["enum4linux"]
        flags = arguments.get("flags", "-a")
        cmd.extend(flags.split())
        cmd.append(arguments["target"])
        result = run_tool(cmd, timeout=300)

    elif name == "smbclient":
        err = check_tool("smbclient")
        if err:
            return [TextContent(type="text", text=err)]
        target = arguments["target"]
        share = arguments.get("share")
        user = arguments.get("username", "")
        passwd = arguments.get("password", "")

        if share:
            cmd = ["smbclient", f"//{target}/{share}"]
        else:
            cmd = ["smbclient", "-L", target]

        if user:
            cmd.extend(["-U", f"{user}%{passwd}"])
        else:
            cmd.extend(["-N"])  # Null session

        command = arguments.get("command")
        result = run_tool(cmd, timeout=30, input_data=command)

    elif name == "dnsrecon":
        err = check_tool("dnsrecon")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["dnsrecon", "-d", arguments["domain"], "-t", arguments.get("type", "std")]
        result = run_tool(cmd, timeout=120)

    elif name == "snmpwalk":
        err = check_tool("snmpwalk", "snmp")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = ["snmpwalk", f"-v{arguments.get('version', '2c')}", "-c", arguments.get("community", "public"), arguments["target"]]
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
