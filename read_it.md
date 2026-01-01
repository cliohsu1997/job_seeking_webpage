# Read It First

**Cursor Rule:** Before starting or continuing a conversation, read this file to stay aligned on context, priorities, and rules.

## Mandatory First Steps

1. Read `conversation_cursor/progress/latest.md` to identify main tasks (phases) in progress
2. Read corresponding to-do list in `conversation_cursor/to-do-list/` (format: `YYYY-MM-DD_phase-name.md`)
3. After reading the to-do list, find and read the corresponding proposal document in `conversation_cursor/dates/YYYY-MM-DD/` (proposals typically named with verbs like `design-`, `create-`, etc.)
4. Read `conversation_cursor/structure/latest.md` for project structure
5. Check the folder closest to today in `conversation_cursor/dates/YYYY-MM-DD/` for context
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
**Preferred method**: Use `poetry run` (no need to activate virtual environment):
```bash
poetry run python script.py
poetry run python -m module_name
poetry run python scripts/scraper/check_config/verify_urls.py
```

**Alternative method**: Activate virtual environment first:
```bash
# Windows PowerShell
.\environment\python\venv\Scripts\Activate.ps1

# Windows CMD
.\environment\python\venv\Scripts\activate.bat

# Then run
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
- **CRITICAL SEPARATION RULE**: 
  - **Progress file** (`conversation_cursor/progress/latest.md`): Contains ONLY high-level accomplishments and next steps. NO detailed task lists. Keep it concise and strategic.
  - **To-do lists** (`conversation_cursor/to-do-list/YYYY-MM-DD_phase-name.md`): Contains ALL detailed, actionable tasks with checkboxes. This is where all specific work items live.
  - **When updating**: Move detailed tasks from progress to to-do lists. Progress should reference the to-do list, not duplicate its content.
- Progress = high-level stages; To-do = actionable subtasks
- **After completing any task**: Check `conversation_cursor/progress/latest.md` to see which phase/step it belongs to, then update the corresponding to-do list to mark the task as complete

### Test Structure
- Tests in `tests/` with subfolders matching phase names (e.g., `tests/setup-project/`, `tests/load-data-collection/`)

### Git & File Management
- **Commits**: Each commit = one minimum complete task
- **.gitkeep files**: Only keep essential ones. Remove when folders contain actual files.
- **Git Pager**: For scripts/automation, use commands that don't trigger the pager:
  - `git status --porcelain` - Machine-readable status
  - `git log --oneline` - Compact one-line log
  - `git --no-pager <command>` - Disable pager for specific command

### End of Conversation/Task
- Reorganize structure/progress/to-do files to show:
  - What's accomplished
  - What's next
  - Update progress with "What We've Accomplished" and "What's Next"
  - Ensure to-do list names match phase names
  - Clean up unnecessary files (including .gitkeep)

### Documentation & README Files
- **README Connection Rule**: Whenever a README file is created or updated, it MUST be connected to the root `README.md`
- The root README serves as the navigation hub - all documentation should be discoverable from there
- Update the root README's "Documentation Map" section when adding new README files
- Keep README files succinct and focused - use the root README to show how documents connect
- If a README becomes too long, split it and update the root README to reference both

### Communication
- Keep workflow conversational
- **Token Usage**: Monitor token usage and remind the user when approaching token limits (e.g., when usage exceeds 80% of available tokens)
