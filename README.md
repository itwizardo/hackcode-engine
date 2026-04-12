<p align="center">
  <img src="https://img.shields.io/badge/status-ALPHA-red?style=for-the-badge" alt="Alpha">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/platform-Kali%20Linux%20%7C%20macOS%20%7C%20Linux-blue?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/AI-100%25%20Local-purple?style=for-the-badge" alt="100% Local">
  <img src="https://img.shields.io/badge/engine-Rust-orange?style=for-the-badge" alt="Rust">
</p>

```
 ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗
 ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ███████║███████║██║     █████╔╝ ██║     ██║   ██║██║  ██║█████╗
 ██╔══██║██╔══██║██║     ██╔═██╗ ██║     ██║   ██║██║  ██║██╔══╝
 ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╗╚██████╔╝██████╔╝███████╗
 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
  >> AI-Powered Hacking Terminal  |  100% Local  |  No Censorship <<
```

# HackCode

**The AI-powered hacking terminal for penetration testers, security researchers, CTF players, and red teamers.**

HackCode is an open-source AI terminal built on a Rust engine forked from [Claw Code](https://github.com/antinomezco/claw-code). It runs **100% locally** with uncensored AI models via [Ollama](https://ollama.ai). No cloud APIs, no censorship, no data leaving your machine.

> **ALPHA SOFTWARE — Expect rough edges, missing features, and breaking changes. Contributions and bug reports welcome.**

> **LEGAL NOTICE:** This tool is built strictly for **authorized security testing, education, and research**. Using HackCode against systems without explicit written permission is **illegal** and may violate laws including the Computer Fraud and Abuse Act (CFAA), the Computer Misuse Act, and similar legislation worldwide. The developers accept **zero liability** for misuse. Always get written authorization before testing.

---

## Why HackCode?

- **Rust engine** — Fast, native binary. No Node.js, no Python runtime, no garbage collection
- **100% local** — Your prompts, targets, and results never leave your machine
- **Uncensored models** — Uses Qwen3.5 uncensored models that won't refuse security tasks
- **Tool-calling AI** — The model doesn't just chat — it runs `nmap`, reads files, chains tools automatically
- **Auto-setup** — First run installs Ollama, downloads the right model for your hardware, installs security tools
- **50+ built-in tools** — Bash, file read/write/edit, grep, glob, directory listing, and more
- **Security tool scanner** — Detects 35 security tools across 6 categories

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/itwizardo/hackcode/dev/install.sh | bash
```

Or build from source:

```bash
git clone https://github.com/itwizardo/hackcode.git
cd hackcode/rust
cargo build --release
cp target/release/hackcode ~/.local/bin/
```

## First Run

Just run `hackcode`. The setup wizard handles everything:

1. **Detects your hardware** — GPU, RAM, platform
2. **Installs Ollama** — If not already installed
3. **Downloads the best model** — Picks the largest uncensored model that fits your RAM
4. **Installs security tools** — nmap, gobuster, nikto, hydra, sqlmap, etc. via Homebrew/apt

```
$ hackcode

[HackCode] First-run setup

  GPU:  Apple M4 Max (48GB)
  Platform: macos (aarch64)

[Step 1/3] AI Backend
  Ollama ✓ installed

[Step 2/3] AI Model
  Recommended: Qwen3.5-35B-A3B Uncensored (MoE)

[Step 3/3] Security Tools
  ✓ All tools installed

[HackCode] Setup complete!
```

## Usage

```bash
hackcode              # Start the interactive REPL
hackcode --scan       # Scan for installed security tools
hackcode --setup      # Re-run the setup wizard
hackcode --help       # Show all commands
```

### Example Session

```
> scan 10.0.0.1

  ▶ bash  $ nmap -sV -sC 10.0.0.1
✓ bash
  PORT     STATE SERVICE  VERSION
  22/tcp   open  ssh      OpenSSH 8.9
  80/tcp   open  http     Apache 2.4.52
  443/tcp  open  ssl/http Apache 2.4.52
  3306/tcp open  mysql    MySQL 8.0.32

Found 4 open ports. Running whatweb for web fingerprinting...

  ▶ bash  $ whatweb http://10.0.0.1
✓ bash
  http://10.0.0.1 [200 OK] Apache[2.4.52], PHP[8.1.2], WordPress[6.4.2]

WordPress detected. Running wpscan...
```

The AI chains tools automatically — no manual prompting needed.

## Models

HackCode works with any Ollama model, but defaults to uncensored Qwen3.5 variants:

| Model | Size | RAM | Best for |
|-------|------|-----|----------|
| Qwen3.5-4B Uncensored | ~3GB | 4GB+ | Low-end machines |
| Qwen3.5-8B Uncensored | ~5GB | 8GB+ | Laptops |
| Qwen3.5-14B Uncensored | ~9GB | 12GB+ | Good balance |
| Qwen3.5-32B Uncensored | ~19GB | 24GB+ | High quality |
| **Qwen3.5-35B-A3B Uncensored (MoE)** | **~21GB** | **24GB+** | **Best — fast + smart** |
| Qwen3.5-35B Uncensored + Vision | ~23GB | 32GB+ | Image analysis |

The 35B-A3B MoE model is recommended — it uses only 3B active parameters per token (fast inference) while having 35B total parameters (high quality).

## Security Tool Scanner

```bash
hackcode --scan
```

Detects 35 tools across 6 categories:

- **Recon** — nmap, masscan, whois, dig, amass, subfinder, assetfinder
- **Web Testing** — gobuster, nikto, sqlmap, whatweb, wpscan, ffuf, dirb
- **Exploitation** — metasploit, impacket, crackmapexec, evil-winrm, responder
- **Password** — hydra, john, hashcat, medusa, ophcrack
- **Forensics** — binwalk, foremost, volatility, exiftool, steghide, strings
- **Utilities** — netcat, socat, proxychains, tor, sshuttle, tmux, jq, curl

## Configuration

Config lives at `~/.config/hackcode/config.json`:

```json
{
  "model": "hackcode-uncensored",
  "baseURL": "http://localhost:11434/v1"
}
```

Re-run setup anytime with `hackcode --setup`.

## Architecture

HackCode's engine is a Rust fork of [Claw Code](https://github.com/antinomezco/claw-code), which is itself a Rust implementation of Claude Code's architecture. The engine provides:

- **Streaming AI responses** with markdown rendering
- **Tool execution** — sandboxed bash, file operations, grep/glob
- **Session management** — auto-save, resume conversations
- **Ollama integration** — auto-start, model management, OpenAI-compatible API
- **Qwen3.5 native renderer** — proper tool-calling format, thinking mode handling

### Project Structure

```
hackcode/
├── rust/                    # Rust workspace
│   └── crates/
│       ├── rusty-claude-cli/  # CLI binary (main.rs, setup.rs, scanner.rs)
│       ├── runtime/           # Conversation loop, prompts, config
│       ├── api/               # Provider abstraction (Ollama, Anthropic, OpenAI)
│       ├── tools/             # 50+ built-in tools
│       ├── commands/          # Slash commands
│       └── plugins/           # MCP plugin system
├── cheatsheets/             # Security cheatsheets (SQLi, XSS, privesc, etc.)
├── mcp-servers/             # Python MCP security tool servers
├── Modelfile                # Ollama model configuration
├── Containerfile            # Container build
└── install.sh               # One-line installer
```

## Credits

- Engine forked from [Claw Code](https://github.com/antinomezco/claw-code) by [@antinomezco](https://github.com/antinomezco)
- Uncensored models by [tripolskypetr](https://ollama.com/tripolskypetr) and [vaultbox](https://ollama.com/vaultbox)

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built for authorized security testing only.</strong><br>
  <em>If you break the law, that's on you.</em>
</p>
