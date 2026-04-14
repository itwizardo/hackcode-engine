#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[38;2;0;255;65m'
DIM='\033[0;2m'
BOLD='\033[1m'
RED='\033[0;31m'
NC='\033[0m'

REPO="itwizardo/hackcode"
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

    cd "$HACKCODE_SRC/rust"

    # Build with live progress — disable set -e around the pipe so
    # the while-subshell exit doesn't kill the script before cp runs.
    BUILD_LOG=$(mktemp)
    echo -e "  ${DIM}Compiling (~200 crates, this may take a few minutes)...${NC}"

    set +e
    cargo build --release -p rusty-claude-cli 2>&1 | tee "$BUILD_LOG" | {
        EST=200
        BUILT=0
        while IFS= read -r line; do
            case "$line" in
                *Compiling*)
                    BUILT=$((BUILT + 1))
                    PCT=$((BUILT * 100 / EST))
                    [ "$PCT" -gt 99 ] && PCT=99
                    CRATE=$(echo "$line" | sed 's/.*Compiling \([^ ]*\).*/\1/')
                    printf "\r  ${GREEN}[%3d%%]${NC} Compiling ${DIM}%-30s${NC}" "$PCT" "$CRATE"
                    ;;
                *Finished*)
                    printf "\r  ${GREEN}[100%%]${NC} Build complete %-40s\n" " "
                    ;;
            esac
        done
    }
    BUILD_EXIT=${PIPESTATUS[0]:-$?}
    set -e
    rm -f "$BUILD_LOG"

    if [ "$BUILD_EXIT" -ne 0 ] || [ ! -f "target/release/hackcode" ]; then
        echo ""
        echo -e "  ${RED}Build failed (exit code $BUILD_EXIT)${NC}"
        echo -e "  ${DIM}Check that Rust toolchain is up to date: rustup update${NC}"
        exit 1
    fi

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

# ─── Ollama + Model ───────────────────────────────────────
echo -e "${GREEN}[4/4]${NC} Setting up Ollama + AI model..."

OLLAMA_BIN=""
if command -v ollama &>/dev/null; then
    OLLAMA_BIN="ollama"
elif [ -x "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
    OLLAMA_BIN="/Applications/Ollama.app/Contents/Resources/ollama"
fi

if [ -n "$OLLAMA_BIN" ]; then
    echo -e "  ${GREEN}Ollama found ✓${NC}"

    # Check if hackcode-uncensored alias already exists
    if $OLLAMA_BIN list 2>/dev/null | grep -q "hackcode-uncensored"; then
        echo -e "  ${GREEN}hackcode-uncensored model ready ✓${NC}"
    else
        # Pick best model based on available RAM
        RAM_GB=8
        case "$PLATFORM" in
            macos) RAM_GB=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1073741824}') ;;
            linux) RAM_GB=$(awk '/MemTotal/{printf "%d", $2/1048576}' /proc/meminfo 2>/dev/null) ;;
        esac

        # Try models in order of preference (largest that fits → smallest fallback)
        BASE_MODEL=""
        MODEL_DESC=""
        if [ "$RAM_GB" -ge 24 ]; then
            BASE_MODEL="tripolskypetr/qwen3.5-uncensored-aggressive:35b"
            MODEL_DESC="Qwen3.5-35B-A3B MoE Uncensored (~21GB)"
        elif [ "$RAM_GB" -ge 8 ]; then
            BASE_MODEL="qwen3:8b"
            MODEL_DESC="Qwen3-8B (~5GB)"
        else
            BASE_MODEL="tripolskypetr/qwen3.5-uncensored-aggressive:4b"
            MODEL_DESC="Qwen3.5-4B Uncensored (~3GB)"
        fi

        echo ""
        echo -e "  ${DIM}RAM: ${RAM_GB}GB — pulling ${BOLD}${MODEL_DESC}${NC}"
        echo ""

        PULLED=false
        # Try primary pick, then fallbacks
        for TRY_MODEL in "$BASE_MODEL" "qwen3:8b" "tripolskypetr/qwen3.5-uncensored-aggressive:4b" "qwen3:4b"; do
            if $OLLAMA_BIN pull "$TRY_MODEL" 2>/dev/null; then
                BASE_MODEL="$TRY_MODEL"
                PULLED=true
                break
            fi
            echo -e "  ${DIM}$TRY_MODEL not available, trying next...${NC}"
        done

        if [ "$PULLED" = true ]; then
            # Create hackcode-uncensored alias via Modelfile
            HACKCODE_CFG="${HOME}/.config/hackcode"
            mkdir -p "$HACKCODE_CFG"
            cat > "${HACKCODE_CFG}/Modelfile" << MODELFILE
FROM ${BASE_MODEL}
PARAMETER temperature 0.7
PARAMETER num_ctx 32768
MODELFILE
            $OLLAMA_BIN create hackcode-uncensored -f "${HACKCODE_CFG}/Modelfile" 2>/dev/null
            echo -e "  ${GREEN}Model ready as ${BOLD}hackcode-uncensored${NC} ${GREEN}✓${NC}"
        else
            echo -e "  ${RED}Could not pull any model${NC}"
            echo -e "  ${DIM}Run: ollama pull qwen3:8b && hackcode --setup${NC}"
        fi
    fi
else
    echo -e "  ${RED}Ollama not found${NC} — required for local AI"
    if [ "$PLATFORM" = "macos" ]; then
        echo -e "  ${DIM}Install: brew install ollama  ${NC}or${DIM}  https://ollama.ai/download${NC}"
    else
        echo -e "  ${DIM}Install: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
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
