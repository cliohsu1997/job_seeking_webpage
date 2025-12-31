# Read It First

**Cursor Rule:** Before starting or continuing a conversation, read this file to stay aligned on context, priorities, and rules.

## Mandatory First Steps

1. Read `conversation_cursor/progress/latest.md` to identify main tasks (phases) in progress
2. Read corresponding to-do list in `conversation_cursor/to-do-list/` (format: `YYYY-MM-DD_phase-name.md`)
3. After reading the to-do list, find and read the corresponding proposal document in `conversation_cursor/dates/YYYY-MM-DD/` (proposals typically named with verbs like `design-`, `create-`, etc.)
4. Read `conversation_cursor/structure/latest.md` for project structure
5. Check today's dated folder in `conversation_cursor/dates/YYYY-MM-DD/` for context
6. Confirm new requests align with recorded goals to avoid duplicate work
7. Mention this file when summarizing updates

**Workflow**: Progress shows main tasks → To-do lists show subtasks → Proposals provide detailed design/strategy

### New Conversation Rule
**At the start of every new conversation**, provide a summary that includes:
1. **Current Progress**: What phase you're in, what's been accomplished, and what's next
2. **To-Do List**: Current tasks and their status
3. **Relevant Proposals**: Key proposals related to the current phase/work

This helps maintain context and alignment across conversations.

## Environment Information

- **Python**: `C:\Users\clioh\AppData\Local\Programs\Python\Python313\python.exe` (3.13.5)
- **Poetry**: `C:\Users\clioh\AppData\Roaming\pypoetry\venv\Scripts\poetry.exe`
- **Virtual Environment**: `./environment/python/venv/`
- **Environment Tools**: `./environment/python/tools/` (all Poetry-related files: poetry.lock, pyproject.toml copy, configs)
- **Poetry Rule**: All Poetry-related files must be kept in `environment/python/tools/` (source of truth). Root `pyproject.toml` and `poetry.lock` are ignored in git - they exist locally for Poetry to function but are copies from tools/.

## Running Python

### Install/Update Dependencies
```bash
poetry install              # Install all dependencies (creates venv if needed)
poetry lock                 # Update lock file if pyproject.toml changed
poetry add package-name      # Add new dependency
poetry remove package-name   # Remove dependency
poetry update                # Update all dependencies
```
**Note**: After updating, copy `poetry.lock` to `environment/python/tools/` (source of truth).

### Activate Virtual Environment
```bash
# Windows PowerShell
.\environment\python\venv\Scripts\Activate.ps1

# Windows CMD
.\environment\python\venv\Scripts\activate.bat
```

### Run Python
After activating the virtual environment:
```bash
python script.py
python -m module_name
```

## Coding & Workflow Rules

### Code Formatting
- Break each argument on its own line
- Always explain code before implementing

### DRY Principle
- Avoid duplication; extract reusable functions/classes
- Reuse existing patterns; refactor similar code into shared modules
- Keep configuration centralized (e.g., `data/config/`)

### Workflow Structure
- Default flow: `load → transform → export`

### Phase & File Naming
- **Phase names**: Start with verb, be informative (e.g., `setup-project`, `load-data-collection`)
- **To-do lists**: `YYYY-MM-DD_phase-name.md` (matches phase naming)
- **Proposals**: Name with verb (e.g., `design-scraping-strategy.md`)

### Progress & To-Do Lists
- Each to-do list = one complete phase task
- Use checkboxes `- [ ]` and `- [x]`
- When all tasks complete, mark phase complete in progress file
- Progress = high-level stages; To-do = actionable subtasks
- **After completing any task**: Check `conversation_cursor/progress/latest.md` to see which phase/step it belongs to, then update the corresponding to-do list to mark the task as complete

### Test Structure
- Tests in `tests/` with subfolders matching phase names (e.g., `tests/setup-project/`, `tests/load-data-collection/`)

### Git & File Management
- **Commits**: Each commit = one minimum complete task
- **.gitkeep files**: Only keep essential ones. Remove when folders contain actual files.

### End of Conversation/Task
- Reorganize structure/progress/to-do files to show:
  - What's accomplished
  - What's next
  - Update progress with "What We've Accomplished" and "What's Next"
  - Ensure to-do list names match phase names
  - Clean up unnecessary files (including .gitkeep)

### Communication
- Keep workflow conversational
- **Token Usage**: Monitor token usage and remind the user when approaching token limits (e.g., when usage exceeds 80% of available tokens)
