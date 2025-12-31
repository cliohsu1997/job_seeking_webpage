# Read It First

**Cursor Rule:** Before starting or continuing a conversation, read this file to stay aligned on context, priorities, and rules.

## Mandatory First Steps

1. Read the latest entries in `conversation_cursor/progress/latest.md` to understand the high-level pipeline and identify the **main tasks** (phases) in progress
2. For each main task identified in progress, read the corresponding **to-do list** in `conversation_cursor/to-do-list/` (named as `YYYY-MM-DD_phase-name.md`, e.g., `2025-12-31_project-setup.md`) to see the **subtasks** (small checkable tasks) that need to be completed
3. Read the latest entry in `conversation_cursor/structure/latest.md` to understand project structure
4. Check today's dated folder in `conversation_cursor/dates/YYYY-MM-DD/` for any relevant context
5. Confirm that any new request aligns with previously recorded goals to avoid duplicate work
6. Mention this file when summarizing updates so the user knows the rule is being followed

**Workflow**: Progress shows main tasks → To-do lists show subtasks for each main task

## Environment Information

### Python Location
- **Path**: `C:\Users\clioh\AppData\Local\Programs\Python\Python313\python.exe`
- **Version**: Python 3.13.5

### Poetry Location
- **Path**: `C:\Users\clioh\AppData\Roaming\pypoetry\venv\Scripts\poetry.exe`
- **Virtual Environment**: Configured to use `./environment/python/venv/` folder
- **Environment Tools**: Lock files and configs stored in `./environment/python/tools/`
- **Configuration**: All Poetry and environment management tools/configurations are kept in the `environment/` folder
  - `environment/python/tools/`: Environment management tool configs (poetry.lock, etc.)
  - `environment/python/venv/`: Actual virtual environment

## Coding & Workflow Rules

### Code Formatting
- Break each argument out on its own line when writing or explaining code snippets
- Always explain the code in the cursor window before implementing or sharing it

### DRY Principle (Don't Repeat Yourself)
- Avoid code duplication; extract common functionality into reusable functions/classes
- Reuse existing code patterns and utilities rather than rewriting similar logic
- When similar code appears multiple times, refactor into shared modules
- Keep configuration in centralized locations (e.g., `data/config/`) rather than hardcoding

### Default Workflow Structure
- Preserve the `load → transform → export` structure as the default flow for any coding work

### Task Management
- When analysis is involved, summarize the resulting tasks into discrete, small items stored inside today's dated folder (e.g., `conversation_cursor/dates/YYYY-MM-DD`)
- Create a proposal for new work inside today's dated folder. Name the file starting with a verb (for example `create-cursor-rule.md`) so it clearly states the action
- To-do lists should be named as `YYYY-MM-DD_phase-name.md` (e.g., `2025-12-31_project-setup.md`, `2025-12-31_load-data-collection.md`) where the phase name corresponds to the phase in progress
- To-do lists contain explicit tasks in the order they should be finished

### Progress and To-Do List Relationship
- **Each to-do list corresponds to a complete task in progress**
- The to-do list contains many small, checkable tasks (use checkboxes `- [ ]` and `- [x]`)
- When ALL tasks in a to-do list are completed, mark the corresponding task as complete in the progress file
- Progress file shows high-level pipeline stages; to-do lists break down each stage into actionable items
- Example: If progress shows "Phase 1: LOAD - Data Collection", the corresponding to-do list will have all the small tasks needed to complete Phase 1
- **When starting a new conversation**: Check progress to identify main tasks, then check the corresponding to-do list to see subtasks

### Progress Tracking
- After writing execution files and testing them, log updates with finer subsections:
  - **Progress**: High-level pipeline overview (what stages have been completed)
  - **Structure**: Project organization and folder structure changes
  - **To-Do List**: Explicit tasks with clear order and completion status

### Git Workflow
- Commit changes as a separate, explicit task after completing work
- **Each commit should represent a minimum complete task** - group related changes that form one logical, complete unit of work
- Use descriptive commit messages that reflect the work done
- Example: If you update documentation and reorganize files, these could be separate commits if they're independent tasks, or one commit if they're part of completing one task

### End of Conversation/Task Rule
- **Before finishing a conversation or completing a task**: Reorganize structure, progress, and to-do list files to:
  - Clearly show what has been accomplished
  - Clearly show what's next
  - Update progress with "What We've Accomplished" and "What's Next" sections
  - Ensure to-do list names match phase names (format: `YYYY-MM-DD_phase-name.md`)
  - Clean up any unnecessary files (e.g., .gitkeep files that are no longer needed)
- This ensures the next conversation starts with a clear understanding of the current state

### Communication Style
- Keep the workflow conversational; treat each exchange as part of that dialogue
