#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[38;2;0;255;65m'
DIM='\033[0;2m'
BOLD='\033[1m'
RED='\033[0;31m'
NC='\033[0m'

REPO="itwizardo/hackcode-engine"
INSTALL_DIR="${HOME}/.local/bin"

echo ""
echo -e "${GREEN} ██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗${NC}"
echo -e "${GREEN} ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝${NC}"
echo -e "${GREEN} ███████║███████║██║     █████╔╝ ██║     ██║   ██║██║  ██║█████╗  ${NC}"
echo -e "${GREEN} ██╔══██║██╔══██║██║     ██╔═██╗ ██║     ██║   ██║██║  ██║██╔══╝  ${NC}"
echo -e "${GREEN} ██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╗╚██████╔╝██████╔╝███████╗${NC}"
echo -e "${GREEN} ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝${NC}"
echo -e "${GREEN}  >> AI-Powered Hacking Terminal  |  100% Local  |  No Censorship <<${NC}"
echo ""

# ─── Detect platform ──────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)  PLATFORM="linux" ;;
    Darwin) PLATFORM="macos" ;;
    *)
        echo -e "${RED}Error: Unsupported OS: $OS${NC}"
        echo "HackCode supports Linux and macOS."
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64)   ARCH_NAME="x64" ;;
    arm64|aarch64)   ARCH_NAME="arm64" ;;
    *)
        echo -e "${RED}Error: Unsupported architecture: $ARCH${NC}"
        echo "HackCode supports x86_64 and arm64."
        exit 1
        ;;
esac

ARTIFACT="hackcode-${PLATFORM}-${ARCH_NAME}"
echo -e "${GREEN}[1/4]${NC} Detected: ${BOLD}${OS} ${ARCH}${NC} -> ${ARTIFACT}"

# ─── Try downloading pre-built binary ─────────────────────
echo -e "${GREEN}[2/4]${NC} Getting HackCode..."

INSTALLED=false

# Try GitHub Releases
TAG=$(curl -sL "https://api.github.com/repos/${REPO}/releases/latest" 2>/dev/null | grep '"tag_name"' | head -1 | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/' || true)

if [ -n "$TAG" ]; then
    DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${TAG}/${ARTIFACT}.tar.gz"
    TMPDIR=$(mktemp -d)
    trap 'rm -rf "$TMPDIR"' EXIT

    HTTP_CODE=$(curl -sL -w "%{http_code}" -o "$TMPDIR/${ARTIFACT}.tar.gz" "$DOWNLOAD_URL" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        cd "$TMPDIR"
        tar xzf "${ARTIFACT}.tar.gz"
        mkdir -p "$INSTALL_DIR"
        mv "$ARTIFACT" "$INSTALL_DIR/hackcode"
        chmod +x "$INSTALL_DIR/hackcode"
        echo -e "  ${GREEN}Downloaded ${TAG} ✓${NC}"
        INSTALLED=true
    fi
fi

# Fall back to building from source
if [ "$INSTALLED" = false ]; then
    echo -e "  ${DIM}No pre-built binary available. Building from source...${NC}"

    if ! command -v cargo &>/dev/null; then
        echo -e "  ${DIM}Installing Rust toolchain...${NC}"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        . "$HOME/.cargo/env"
    fi

    HACKCODE_SRC="${HOME}/.hackcode-src"
    if [ -d "$HACKCODE_SRC/.git" ]; then
        git -C "$HACKCODE_SRC" pull --quiet 2>/dev/null || true
    else
        [ -d "$HACKCODE_SRC" ] && rm -rf "$HACKCODE_SRC"
        git clone --quiet "https://github.com/${REPO}.git" "$HACKCODE_SRC"
    fi

    echo -e "  ${DIM}Building (takes ~2 minutes on first run)...${NC}"
    cd "$HACKCODE_SRC/rust"
    cargo build --release -p rusty-claude-cli 2>&1 | tail -5

    mkdir -p "$INSTALL_DIR"
    cp "target/release/hackcode" "$INSTALL_DIR/hackcode"
    chmod +x "$INSTALL_DIR/hackcode"
    echo -e "  ${GREEN}Built and installed ✓${NC}"
fi

# ─── Add to PATH ──────────────────────────────────────────
echo -e "${GREEN}[3/4]${NC} Adding hackcode to PATH..."

SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    zsh)  RC="${ZDOTDIR:-$HOME}/.zshrc" ;;
    bash) RC="$HOME/.bashrc" ; [ -f "$HOME/.bash_profile" ] && RC="$HOME/.bash_profile" ;;
    fish) RC="$HOME/.config/fish/config.fish" ;;
    *)    RC="" ;;
esac

if [ -n "$RC" ]; then
    if ! grep -Fq "$INSTALL_DIR" "$RC" 2>/dev/null; then
        echo "" >> "$RC"
        echo "# HackCode" >> "$RC"
        if [ "$SHELL_NAME" = "fish" ]; then
            echo "fish_add_path $INSTALL_DIR" >> "$RC"
        else
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$RC"
        fi
        echo -e "  ${GREEN}Added to $RC ✓${NC}"
    else
        echo -e "  ${DIM}Already in PATH ✓${NC}"
    fi
fi
export PATH="$INSTALL_DIR:$PATH"

# ─── Ollama ───────────────────────────────────────────────
echo -e "${GREEN}[4/4]${NC} Checking Ollama..."

OLLAMA_BIN=""
if command -v ollama &>/dev/null; then
    OLLAMA_BIN="ollama"
elif [ -x "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
    OLLAMA_BIN="/Applications/Ollama.app/Contents/Resources/ollama"
fi

if [ -n "$OLLAMA_BIN" ]; then
    echo -e "  ${GREEN}Ollama found ✓${NC}"

    # Pull default model if none exist
    MODEL_COUNT=$($OLLAMA_BIN list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
    if [ "$MODEL_COUNT" = "0" ]; then
        echo ""
        echo -e "  ${DIM}No models found. Pulling default model...${NC}"
        echo -e "  ${BOLD}Gemma 4 E4B Uncensored${NC} (~5GB download)"
        echo ""
        $OLLAMA_BIN pull "hf.co/HauhauCS/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive:Q4_K_M" || true
    fi
else
    echo -e "  ${RED}Ollama not found${NC}"
    if [ "$PLATFORM" = "macos" ]; then
        echo -e "  ${DIM}Install Ollama: https://ollama.ai/download${NC}"
        echo -e "  ${DIM}Or: brew install ollama${NC}"
    else
        echo -e "  ${DIM}Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
    fi
fi

# ─── Done ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}[HackCode]${NC} Installation complete!"
echo ""
echo -e "  ${BOLD}hackcode${NC}          ${DIM}# Start hacking${NC}"
echo -e "  ${BOLD}hackcode --help${NC}   ${DIM}# Show all commands${NC}"
echo ""
echo -e "  ${DIM}Open a new terminal or run:${NC}"
echo -e "  ${BOLD}export PATH=\"$INSTALL_DIR:\$PATH\"${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
