# Contributing to HackCode

Thanks for wanting to contribute to HackCode. Whether it's a bug fix, new feature, or documentation improvement — all contributions are welcome.

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/hackcode.git ~/hackcode
cd ~/hackcode
bun install
```

### 2. Run locally

```bash
bun run dev
```

This starts HackCode directly from source. You need [Ollama](https://ollama.ai) running with at least one model pulled.

### 3. Project structure

```
src/
├── index.ts       # Main REPL loop, AI streaming, commands, config
├── prompt.ts      # System prompt and ASCII banner
├── tools.ts       # Built-in AI tools (bash, read, write, edit, grep, list)
├── setup.ts       # First-run wizard (hardware detection, model pull, tool install)
└── scanner.ts     # Security tool availability scanner
```

The entire app is 5 TypeScript files with 4 dependencies. Keep it that way.

## Guidelines

### Keep it simple

HackCode was rewritten from scratch to escape dependency hell (the previous version had 4,627 packages). We're not going back. Before adding a dependency, ask yourself if you really need it.

- **4 production dependencies** — `ai`, `@ai-sdk/openai-compatible`, `@ai-sdk/openai`, `zod`
- If your feature needs a new dependency, explain why in the PR
- Prefer standard library and built-in Node/Bun APIs

### Code style

- TypeScript, no build step — Bun runs `.ts` directly
- No classes unless genuinely needed — functions are fine
- No unnecessary abstractions — if it's used once, inline it
- Keep files focused — one file per concern

### What we're looking for

**High priority:**
- MCP server integration (connecting the existing Python MCP servers in `mcp-servers/`)
- New AI tools (e.g., network tools, screenshot analysis)
- Better error handling and edge cases
- Improvements to the system prompt for better tool chaining
- Support for more platforms (Windows/WSL, more Linux distros)

**Always welcome:**
- Bug fixes
- Performance improvements
- Better setup wizard UX
- New cheatsheets in `cheatsheets/`
- Documentation improvements

**Please don't:**
- Add React, Vue, or any UI framework — HackCode is a terminal app
- Rewrite the REPL to use a TUI library — we tried, it caused more problems than it solved
- Add cloud API support — HackCode is local-only by design
- Add telemetry or analytics of any kind

## How to Submit

### Bug reports

Open an issue with:
- What you expected to happen
- What actually happened
- Your OS, RAM, and which model you're using
- The error message (if any)

### Pull requests

1. Fork the repo
2. Create a branch (`git checkout -b fix/my-fix`)
3. Make your changes
4. Test it locally (`bun run dev`)
5. Push and open a PR against the `dev` branch

Keep PRs focused — one feature or fix per PR. Write a clear description of what changed and why.

### New AI tools

If you want to add a new tool the AI can use, add it to `src/tools.ts`. Follow the existing pattern:

```typescript
my_tool: tool({
  description: "What this tool does — be specific, the AI reads this",
  parameters: z.object({
    param: z.string().describe("What this parameter is for"),
  }),
  execute: async ({ param }) => {
    // Do the thing
    return "result string that the AI will read"
  },
}),
```

### New cheatsheets

Add a markdown file to `cheatsheets/` following the naming pattern `SKILL-<topic>.md`. Look at the existing ones for format.

## Running Tests

There are no tests yet. If you want to add a testing setup, that would be a great first contribution. Keep it minimal — `bun test` with no extra dependencies.

## Questions?

Open an issue or start a discussion. No question is too basic.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
