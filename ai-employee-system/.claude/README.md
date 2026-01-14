# .claude Directory

This directory contains Claude Code-specific files following [official Anthropic documentation](https://code.claude.com/docs/en/memory).

## Structure

```
.claude/
└── skills/              # Agent Skills (auto-loaded on demand)
    └── email-processing/
        ├── SKILL.md
        ├── HANDBOOK_REFERENCE.md
        ├── DASHBOARD_QUERIES.md
        ├── README.md
        └── scripts/
```

## Official Documentation

Based on [official Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices):

### What Belongs Here

✅ **skills/** - Agent Skills that Claude loads automatically when relevant
✅ **CLAUDE.md** - Main project instructions (optional, can be in root)
✅ **rules/** - Modular topic-specific instructions (if needed)
✅ **commands/** - Custom slash commands (if needed)

### What Should NOT Be Here

❌ Reference documentation → Move to `docs/`
❌ Configuration files → Move to root or `docs/`
❌ Working documents/drafts → Delete or archive
❌ Large files not frequently used → Keep elsewhere
❌ Sensitive information (API keys, credentials)

## Current Setup

Our project follows the official structure with:
- **Agent Skill**: `skills/email-processing/` - Email processing workflow automation
- **Project Memory**: `claude.md` (root) - Main project instructions
- **Reference Docs**: `docs/` (root) - Architecture, configuration, legacy workflows

## Memory Hierarchy

Per [official documentation](https://code.claude.com/docs/en/memory):

1. **Enterprise policy** (system-wide)
2. **Project memory** (`./claude.md` or `./.claude/CLAUDE.md`) ← We use root
3. **Project rules** (`./.claude/rules/*.md`) ← Not used currently
4. **User memory** (`~/.claude/CLAUDE.md`)
5. **Local project** (`./CLAUDE.local.md`)

## Skills Hot Reload

Claude Code 2.1.0+ supports hot reload - new or updated skills in `.claude/skills/` become available immediately without restarting.

## Additional Resources

- [Official Skills Documentation](https://www.anthropic.com/news/skills)
- [CLAUDE.md Usage Guide](https://claude.com/blog/using-claude-md-files)
- [Memory Management Docs](https://code.claude.com/docs/en/memory)

---

**Last Updated**: 2026-01-12
**Cleanup Date**: 2026-01-12
**Status**: ✅ Compliant with official Anthropic structure
