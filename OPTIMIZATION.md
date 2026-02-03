# Session Optimization Guide

## Token Usage Optimization
- **Concise responses** by default - save details for files
- **Batch operations** when possible (multiple files, multiple checks)
- **Use files for complex analysis** - reference rather than repeat
- **Memory search first** - check existing knowledge before web searches

## Session Persistence Strategy
- **Sessions persist** in cache with `session-memory` hook enabled
- **Key files auto-load** each session (SOUL.md, USER.md, recent memory)
- **Sub-agent results persist** and can be referenced later
- **Git commits track progress** without needing session memory

## Configuration Optimizations Applied
- ✅ `compaction.mode: "safeguard"` - Efficient memory management
- ✅ `maxConcurrent: 4` - Parallel task processing
- ✅ `subagents.maxConcurrent: 8` - Background work capacity
- ✅ `session-memory` hook - Session persistence across restarts

## Best Practices for Efficiency
1. **File-first approach** - Write analysis to files, summarize in chat
2. **Batch operations** - Group similar tasks together
3. **Leverage persistence** - Build on previous work without re-doing
4. **Smart notifications** - Hourly summaries vs constant updates
5. **Auto-workflow integration** - Let git and cron handle routine tasks

## Memory Management
- **Daily files** for raw logs and activity
- **MEMORY.md** for curated long-term memory
- **Progress tracking** for project status
- **Configuration files** for settings and preferences

This approach maximizes efficiency while maintaining full capability.