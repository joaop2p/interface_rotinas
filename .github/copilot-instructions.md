# Gerenciador de Rotinas - AI Coding Instructions

## Architecture Overview

This is a Python desktop application built with **Flet** for GUI and **SQLModel** for database operations. The app manages and executes Python scripts (routines) organized by categories.

### Core Components

- **Entry Point**: `main.py` → `lib/app/myapp.py` → `PageManager` (singleton pattern)
- **Routing**: `PageManager` handles SPA-style navigation with `Routes` constants
- **Views**: All inherit from `ViewTemplate` abstract base with `get_view()` and `set_page()` methods
- **Data Layer**: Controller → Service → DAO pattern with SQLModel/SQLite
- **Database**: SQLite with foreign keys enabled, auto-created triggers for `dt_modified`

### Database Models & Relationships

```python
# One-to-many: Category → Routines
Category: category_id (PK), category_name (unique), icon
Routine: routine_id (PK), routine_name, directory_path, description, category_id (FK), dt_created, dt_modified
```

## Critical Patterns

### 1. View Lifecycle
- Views use **async loading** with `_page.run_task()` for data operations
- All views must call `set_page()` before `get_view()`
- Use `ft.Ref[ComponentType]()` for dynamic content updates

### 2. Singleton Components
- `DatabaseConfig`: Thread-safe database connection manager
- `PageManager`: Handles all navigation and view state
- `LoggerConfig`: Centralized logging with in-memory capture for UI terminal

### 3. Routine Execution
Use `RoutineRunner` service for executing Python scripts:
```python
runner = RoutineRunner()
runner.run(script_path, on_line=callback_func, hide_console=True)
```

### 4. Real-time Log Display
Views subscribe to logs via `InMemoryLogHandler` with terminal-like output:
```python
self._page.pubsub.subscribe(lambda m: self._update_terminal(m["text"]))
```

## Development Commands

```powershell
# Run application
python main.py

# Database is auto-created at: C:\users\{user}\AppData\Local\Scripts Hub\database\rotinas.sqlite
```

## File Organization Rules

- **Controllers**: Thin validation layer, delegate to Services
- **Services**: Business logic, coordinate between Controllers and DAOs  
- **DAOs**: Direct database operations using SQLModel Sessions
- **Views**: UI components in `views/` with reusable widgets in `views/widgets/`
- **Models**: `db/models.py` for SQLModel tables, `interfaces/` for abstractions

## Key Conventions

1. **Error Handling**: Use specific exceptions (e.g., `CategoryInUseError`)
2. **Logging**: All components get logger via `logging.getLogger(component_name)`
3. **Constants**: Centralized in `AppConstants`, `SQLConstants`, `LogMessages`
4. **Async Operations**: Use `asyncio.Task` for long-running operations in views
5. **File Validation**: Scripts must have Python extensions from `AppConstants.PYTHON_EXTENSIONS`

## Integration Points

- **Flet UI Framework**: All UI built with Flet components and async patterns
- **SQLite Database**: Foreign keys enabled, automatic timestamp triggers
- **File System**: Python script execution with real-time output capture
- **Windows Integration**: Desktop app with local AppData storage

## Navigation Flow

Home (`/home`) → Add Category (`/add_category`) / Add Routine (`/add_routine`) / Routine Details (`/routine_details`)

Routes managed by `PageManager` singleton with dynamic view instantiation for forms.