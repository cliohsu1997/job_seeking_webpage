# Read It First

**Cursor Rule:** Before starting or continuing a conversation, read this file to stay aligned on context, priorities, and rules.

## Mandatory First Steps

1. Read the latest entries in `conversation_cursor/progress/latest.md` to understand the high-level pipeline
2. Read the latest entry in `conversation_cursor/structure/latest.md` to understand project structure
3. Read the most recent dated to-do list in `conversation_cursor/to-do-list/` (named as `YYYY-MM-DD_task.md`) to see explicit tasks and their order
4. Check today's dated folder in `conversation_cursor/dates/YYYY-MM-DD/` for any relevant context
5. Confirm that any new request aligns with previously recorded goals to avoid duplicate work
6. Mention this file when summarizing updates so the user knows the rule is being followed

## Coding & Workflow Rules

### Code Formatting
- Break each argument out on its own line when writing or explaining code snippets
- Always explain the code in the cursor window before implementing or sharing it

### Default Workflow Structure
- Preserve the `load → transform → export` structure as the default flow for any coding work

### Task Management
- When analysis is involved, summarize the resulting tasks into discrete, small items stored inside today's dated folder (e.g., `conversation_cursor/dates/YYYY-MM-DD`)
- Create a proposal for new work inside today's dated folder. Name the file starting with a verb (for example `create-cursor-rule.md`) so it clearly states the action
- To-do lists should be named as `YYYY-MM-DD_task.md` (not `latest.md`) and contain explicit tasks in the order they should be finished

### Progress Tracking
- After writing execution files and testing them, log updates with finer subsections:
  - **Progress**: High-level pipeline overview (what stages have been completed)
  - **Structure**: Project organization and folder structure changes
  - **To-Do List**: Explicit tasks with clear order and completion status

### Git Workflow
- Commit changes as a separate, explicit task after completing work
- Use descriptive commit messages that reflect the work done

### Communication Style
- Keep the workflow conversational; treat each exchange as part of that dialogue
