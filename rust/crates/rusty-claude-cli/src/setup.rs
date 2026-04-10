use std::env;
use std::fs;
use std::io::{self, Write};
use std::path::PathBuf;
use std::process::Command;

const GREEN: &str = "\x1b[38;2;0;255;65m";
const DIM: &str = "\x1b[90m";
const BOLD: &str = "\x1b[1m";
const RESET: &str = "\x1b[0m";
const RED: &str = "\x1b[91m";

const BANNER: &str = "\x1b[38;2;0;255;65m
 ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗
 ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ███████║███████║██║     █████╔╝ ██║     ██║   ██║██║  ██║█████╗
 ██╔══██║██╔══██║██║     ██╔═██╗ ██║     ██║   ██║██║  ██║██╔══╝
 ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╗╚██████╔╝██████╔╝███████╗
 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
\x1b[0m";

struct Model {
    key: &'static str,
    id: &'static str,
    name: &'static str,
    size: &'static str,
    min_ram: u64,
}

const MODELS: &[Model] = &[
    Model { key: "a", id: "tripolskypetr/qwen3.5-uncensored-aggressive:4b",   name: "Qwen3.5-4B Uncensored",             size: "~3GB",  min_ram: 4  },
    Model { key: "b", id: "tripolskypetr/qwen3.5-uncensored-aggressive:8b",   name: "Qwen3.5-8B Uncensored",             size: "~5GB",  min_ram: 8  },
    Model { key: "c", id: "tripolskypetr/qwen3.5-uncensored-aggressive:14b",  name: "Qwen3.5-14B Uncensored",            size: "~9GB",  min_ram: 12 },
    Model { key: "d", id: "tripolskypetr/qwen3.5-uncensored-aggressive:32b",  name: "Qwen3.5-32B Uncensored",            size: "~19GB", min_ram: 24 },
    Model { key: "e", id: "tripolskypetr/qwen3.5-uncensored-aggressive:35b",  name: "Qwen3.5-35B-A3B Uncensored (MoE)",  size: "~21GB", min_ram: 24 },
    Model { key: "f", id: "vaultbox/qwen3.5-uncensored:35b",                  name: "Qwen3.5-35B Uncensored + Vision",   size: "~23GB", min_ram: 32 },
];

const BREW_TOOLS: &[&str] = &[
    "nmap", "masscan", "whois", "gobuster", "nikto", "hydra",
    "john-jumbo", "hashcat", "sqlmap", "whatweb", "ffuf",
    "binwalk", "exiftool", "socat", "netcat",
];

const PIP_TOOLS: &[&str] = &["impacket", "wpscan", "dnsrecon"];

fn config_dir() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    PathBuf::from(home).join(".config").join("hackcode")
}

fn config_path() -> PathBuf {
    config_dir().join("config.json")
}

fn extra_path() -> String {
    let current = env::var("PATH").unwrap_or_default();
    format!("/opt/homebrew/bin:/usr/local/bin:/Applications/Ollama.app/Contents/Resources:{current}")
}

fn which(cmd: &str) -> bool {
    Command::new("which")
        .arg(cmd)
        .env("PATH", extra_path())
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

fn exec(cmd: &str) -> String {
    Command::new("/bin/bash")
        .args(["-c", cmd])
        .env("PATH", extra_path())
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_default()
}

fn run_cmd(cmd: &str) -> bool {
    Command::new("/bin/bash")
        .args(["-l", "-c", cmd])
        .env("PATH", extra_path())
        .env("HOMEBREW_NO_AUTO_UPDATE", "1")
        .stdin(std::process::Stdio::inherit())
        .stdout(std::process::Stdio::inherit())
        .stderr(std::process::Stdio::inherit())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn ask(prompt: &str) -> String {
    print!("{prompt}");
    io::stdout().flush().ok();
    let mut input = String::new();
    io::stdin().read_line(&mut input).ok();
    input.trim().to_string()
}

fn get_ram_gb() -> u64 {
    #[cfg(target_os = "macos")]
    {
        let output = exec("sysctl -n hw.memsize 2>/dev/null");
        output.parse::<u64>().unwrap_or(0) / 1024 / 1024 / 1024
    }
    #[cfg(not(target_os = "macos"))]
    {
        let output = exec("grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}'");
        output.parse::<u64>().unwrap_or(0) / 1024 / 1024
    }
}

fn get_gpu() -> String {
    #[cfg(target_os = "macos")]
    {
        let cpu = exec("sysctl -n machdep.cpu.brand_string 2>/dev/null");
        if cpu.is_empty() { "Unknown".to_string() } else { cpu }
    }
    #[cfg(not(target_os = "macos"))]
    {
        let gpu = exec("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null");
        if gpu.is_empty() { "CPU only".to_string() } else { gpu }
    }
}

fn missing_tools(tools: &[&str]) -> Vec<String> {
    tools.iter()
        .filter(|t| {
            let binary = if **t == "john-jumbo" { "john" } else { t };
            !which(binary)
        })
        .map(|t| t.to_string())
        .collect()
}

pub fn run_setup() -> Result<(), Box<dyn std::error::Error>> {
    println!("{BANNER}");
    println!("{GREEN}[HackCode]{RESET} First-run setup\n");

    // Detect hardware
    let ram_gb = get_ram_gb();
    let gpu = get_gpu();

    println!("  {DIM}GPU:{RESET}  {gpu} ({ram_gb}GB)");
    println!("  {DIM}Platform:{RESET} {} ({})", env::consts::OS, env::consts::ARCH);
    println!();

    // Step 1: Check Ollama
    println!("{GREEN}[Step 1/3]{RESET} {BOLD}AI Backend{RESET}");
    if which("ollama") {
        println!("  Ollama {GREEN}✓{RESET} installed");
    } else {
        println!("  Ollama {RED}✗{RESET} not found");
        let answer = ask("  Install Ollama now? [Y/n] ");
        if answer.to_lowercase() != "n" {
            run_cmd("curl -fsSL https://ollama.ai/install.sh | sh");
        }
    }
    println!();

    // Step 2: Model selection
    println!("{GREEN}[Step 2/3]{RESET} {BOLD}AI Model{RESET}");
    // Pick the largest model that fits in available RAM.
    let recommended = MODELS.iter().rev().find(|m| m.min_ram <= ram_gb).unwrap_or(&MODELS[0]);
    println!("  {GREEN}Recommended:{RESET} {BOLD}{}{RESET} ({})", recommended.name, recommended.size);
    println!();
    for m in MODELS {
        let rec = if m.key == recommended.key {
            format!(" {GREEN}(recommended){RESET}")
        } else {
            String::new()
        };
        println!("  {BOLD}[{}]{RESET} {:35} {DIM}{:8} min {}GB RAM{RESET}{rec}", m.key, m.name, m.size, m.min_ram);
    }
    println!("  {BOLD}[s]{RESET} Skip model download");
    println!();

    let choice = ask(&format!("  {GREEN}>{RESET} "));
    let choice = if choice.is_empty() { recommended.key.to_string() } else { choice };

    let model_id = MODELS.iter()
        .find(|m| m.key == choice)
        .map(|m| m.id)
        .unwrap_or(recommended.id);

    if choice != "s" && which("ollama") {
        println!("\n  Pulling {BOLD}{model_id}{RESET}...");
        run_cmd(&format!("ollama pull \"{model_id}\""));

        // Create hackcode-uncensored alias with native Qwen3.5 renderer
        let modelfile = format!(
            "FROM {model_id}\nRENDERER qwen3.5\nPARSER qwen3.5\nPARAMETER stop \"<|im_start|>\"\nPARAMETER stop \"<|im_end|>\"\nPARAMETER stop \"<|endoftext|>\"\nPARAMETER temperature 0.7\nPARAMETER num_ctx 32768\n"
        );
        let modelfile_path = config_dir().join("Modelfile");
        let _ = fs::write(&modelfile_path, &modelfile);
        run_cmd(&format!("ollama create hackcode-uncensored -f \"{}\"", modelfile_path.display()));
        println!("  {GREEN}✓{RESET} Model ready as {BOLD}hackcode-uncensored{RESET}");
    }
    let model_id = "hackcode-uncensored";
    println!();

    // Step 3: Security tools
    println!("{GREEN}[Step 3/3]{RESET} {BOLD}Security Tools{RESET}");

    let is_macos = cfg!(target_os = "macos");

    if is_macos && which("brew") {
        let missing = missing_tools(BREW_TOOLS);
        if missing.is_empty() {
            println!("  {GREEN}✓{RESET} All Homebrew tools installed");
        } else {
            println!("\n  Missing: {}", missing.join(", "));
            println!("  {DIM}Command: brew install {}{RESET}", missing.join(" "));
            let answer = ask(&format!("\n  Install {} tools via Homebrew? [Y/n] ", missing.len()));
            if answer.to_lowercase() != "n" {
                for (i, pkg) in missing.iter().enumerate() {
                    println!("  {GREEN}[{}/{}]{RESET} Installing {BOLD}{pkg}{RESET}...", i + 1, missing.len());
                    run_cmd(&format!("brew install {pkg}"));
                }
            }
        }

        if which("pip3") {
            let missing_pip = missing_tools(PIP_TOOLS);
            if !missing_pip.is_empty() {
                println!("\n  Missing pip tools: {}", missing_pip.join(", "));
                let answer = ask("  Install via pip? [Y/n] ");
                if answer.to_lowercase() != "n" {
                    run_cmd(&format!("pip3 install {}", missing_pip.join(" ")));
                }
            }
        }
    } else if which("apt") {
        println!("  {DIM}Install tools with: sudo apt install nmap gobuster nikto hydra sqlmap ...{RESET}");
    }

    // Save config
    let config = format!(
        "{{\n  \"model\": \"{model_id}\",\n  \"baseURL\": \"http://localhost:11434/v1\"\n}}\n"
    );
    let dir = config_dir();
    fs::create_dir_all(&dir)?;
    fs::write(config_path(), &config)?;

    let config_path_display = config_path().display().to_string();

    println!("\n{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}");
    println!("{GREEN}[HackCode]{RESET} Setup complete!\n");
    println!("  {DIM}Config:{RESET}  {config_path_display}");
    println!("  {DIM}Model:{RESET}   {model_id}\n");
    println!("  {BOLD}hackcode{RESET}          {DIM}# Start hacking{RESET}");
    println!("  {BOLD}hackcode --help{RESET}   {DIM}# Show all commands{RESET}");
    println!("  {BOLD}hackcode --setup{RESET}  {DIM}# Re-run this setup{RESET}");
    println!("{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n");

    Ok(())
}
