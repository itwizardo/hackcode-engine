use std::process::Command;

const GREEN: &str = "\x1b[38;2;0;255;65m";
const DIM: &str = "\x1b[90m";
const BOLD: &str = "\x1b[1m";
const RESET: &str = "\x1b[0m";
const RED: &str = "\x1b[91m";
const YELLOW: &str = "\x1b[93m";

struct ToolCategory {
    name: &'static str,
    tools: &'static [(&'static str, &'static str)],
}

const CATEGORIES: &[ToolCategory] = &[
    ToolCategory {
        name: "Reconnaissance",
        tools: &[
            ("nmap", "Network scanner"),
            ("masscan", "Fast port scanner"),
            ("whois", "Domain lookup"),
            ("dnsrecon", "DNS enumeration"),
            ("whatweb", "Web fingerprint"),
            ("wafw00f", "WAF detection"),
        ],
    },
    ToolCategory {
        name: "Web Testing",
        tools: &[
            ("gobuster", "Directory brute-force"),
            ("ffuf", "Fast web fuzzer"),
            ("nikto", "Web vulnerability scanner"),
            ("sqlmap", "SQL injection"),
            ("wpscan", "WordPress scanner"),
            ("curl", "HTTP client"),
        ],
    },
    ToolCategory {
        name: "Exploitation",
        tools: &[
            ("hydra", "Login brute-force"),
            ("john", "Password cracker"),
            ("hashcat", "GPU hash cracker"),
            ("msfconsole", "Metasploit Framework"),
            ("searchsploit", "Exploit database"),
        ],
    },
    ToolCategory {
        name: "Network",
        tools: &[
            ("netcat", "Network utility"),
            ("socat", "Socket relay"),
            ("tcpdump", "Packet capture"),
            ("wireshark", "Protocol analyzer"),
            ("proxychains4", "Proxy chains"),
            ("ssh", "Secure shell"),
        ],
    },
    ToolCategory {
        name: "Forensics & Reverse Engineering",
        tools: &[
            ("binwalk", "Firmware analysis"),
            ("exiftool", "Metadata extractor"),
            ("strings", "String extractor"),
            ("file", "File type detection"),
            ("xxd", "Hex dump"),
            ("objdump", "Object file disassembler"),
        ],
    },
    ToolCategory {
        name: "Utilities",
        tools: &[
            ("python3", "Python 3"),
            ("pip3", "Python package manager"),
            ("git", "Version control"),
            ("jq", "JSON processor"),
            ("base64", "Base64 encode/decode"),
            ("openssl", "Crypto toolkit"),
        ],
    },
];

fn extra_path() -> String {
    let current = std::env::var("PATH").unwrap_or_default();
    format!("/opt/homebrew/bin:/usr/local/bin:/usr/sbin:{current}")
}

fn which(cmd: &str) -> bool {
    Command::new("which")
        .arg(cmd)
        .env("PATH", extra_path())
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

pub fn run_scanner() {
    println!("\n{GREEN}[HackCode]{RESET} {BOLD}Security Tool Scanner{RESET}\n");

    let mut total = 0u32;
    let mut found = 0u32;

    for cat in CATEGORIES {
        println!("  {GREEN}▸{RESET} {BOLD}{}{RESET}", cat.name);
        for (cmd, desc) in cat.tools {
            total += 1;
            let (icon, color) = if which(cmd) {
                found += 1;
                ("✓", GREEN)
            } else {
                ("✗", RED)
            };
            println!("    {color}{icon}{RESET} {cmd:20} {DIM}{desc}{RESET}");
        }
        println!();
    }

    let pct = if total > 0 { found * 100 / total } else { 0 };
    let color = if pct >= 80 {
        GREEN
    } else if pct >= 50 {
        YELLOW
    } else {
        RED
    };
    println!(
        "  {color}{found}/{total}{RESET} tools available ({color}{pct}%{RESET})\n"
    );

    if found < total {
        let missing: Vec<&str> = CATEGORIES
            .iter()
            .flat_map(|c| c.tools.iter())
            .filter(|(cmd, _)| !which(cmd))
            .map(|(cmd, _)| *cmd)
            .collect();

        if !missing.is_empty() && cfg!(target_os = "macos") && which("brew") {
            println!(
                "  {DIM}Install missing tools:{RESET}\n  {BOLD}brew install {}{RESET}\n",
                missing.join(" ")
            );
        }
    }
}
