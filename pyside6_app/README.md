# IT Ticket Email Generator - PySide6 Edition

Modern Windows desktop application for generating test emails for IT ticketing systems.

## Version 2.0.0

Complete redesign using PySide6 and qfluentwidgets with Windows 11 Fluent Design aesthetics.

---

## Features

### Phase 1 (Current - Foundation)

- ✅ **Modern UI**: Frameless window with acrylic effects, rounded corners, and shadow
- ✅ **Theme Support**: Auto light/dark theme matching OS, with manual toggle
- ✅ **State Management**: Pydantic-based AppState with JSON persistence
- ✅ **Connection Cards**:
  - Microsoft 365 (Graph API) with OAuth flow
  - Freshservice API connection testing
  - Claude API configuration
- ✅ **Responsive Layout**: 12-column grid (3-6-3 split)
- ✅ **Input Validation**: Real-time validation for emails, GUIDs, domains
- ✅ **Configuration Migration**: Auto-migrate from tkinter .env files

### Coming in Phase 2-6

- Generation & Review cards
- Async email generation with progress
- Draft table with preview
- Preflight checks
- Confirm & Send workflow with hold-to-confirm
- Activity log with filters
- Settings dialog
- Keyboard shortcuts
- And more...

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Windows 10/11** (recommended for best visual effects)

### Setup

1. **Install dependencies:**

```bash
cd "c:\Cursor Projects\Ticket Generation"
pip install -r pyside6_app/requirements.txt
```

2. **Run the application:**

```bash
python run_pyside6_app.py
```

---

## Architecture

```
pyside6_app/
├── app.py                  # Bootstrap & exception handling
├── run_pyside6_app.py      # Launcher script
├── state/
│   ├── models.py           # Pydantic models for AppState
│   └── store.py            # State store with signals & persistence
├── widgets/
│   ├── main_window.py      # Main frameless window with grid layout
│   └── connection_cards.py # Microsoft & Freshservice cards
├── utils/
│   ├── theme.py            # Theme manager (light/dark)
│   └── validators.py       # Input validators (email, GUID, domain)
├── services/               # (Coming in Phase 2+)
├── assets/                 # (Icons, resources)
└── tests/                  # (Unit & integration tests)
```

---

## Configuration

### First Run

On first launch, the app will:
1. Check for existing `.env` file from tkinter version
2. Auto-migrate configuration to `%APPDATA%\ITTicketEmailGenerator\appstate.json`
3. Create default state if no migration needed

### State File Location

- **Windows**: `%APPDATA%\ITTicketEmailGenerator\appstate.json`
- **Backup**: `appstate.backup.json` (automatic on save)

### Secrets Storage

- API keys and secrets are stored **masked** (only last 4 chars) in JSON
- Full secrets stored in memory only during session
- Future: Will use Windows Credential Manager via `keyring` library

---

## Development

### Project Status

**Phase 1** (Week 1) - ✅ **COMPLETED**
- [x] Project structure
- [x] AppState model + persistence
- [x] Theme manager
- [x] Main window with frameless design
- [x] Connection cards (Microsoft + Freshservice)
- [x] Input validation
- [x] Migration from tkinter

**Phase 2** (Week 2) - 🚧 **NEXT**
- [ ] Generation card with quality settings
- [ ] Review card with draft table
- [ ] Draft detail sheet (slide-in)
- [ ] Export to CSV

**Phase 3** (Week 3) - ⏳ **PLANNED**
- [ ] Actions & preflight cards
- [ ] Confirm send dialog
- [ ] Email sending with progress
- [ ] Activity log

**Phase 4-6** (Weeks 4-6) - ⏳ **PLANNED**
- [ ] Settings dialog
- [ ] Keyboard shortcuts
- [ ] Log viewer
- [ ] Testing & packaging

### Testing

```bash
# Unit tests (coming soon)
pytest pyside6_app/tests/

# Run with debug logging
python run_pyside6_app.py --debug
```

### Code Style

- **Black** for formatting
- **MyPy** for type checking
- **PEP 8** compliance

---

## Signal/Slot Architecture

### State Store Signals

```python
state_changed: Signal(AppState)           # Any state change
drafts_changed: Signal(List[DraftEmail])  # Drafts list updated
connections_changed: Signal(ConnectionsState)  # Connection state updated
preflight_changed: Signal(PreflightState) # Preflight checks updated
```

### Widget Signals

```python
# MicrosoftCard
authenticate_clicked: Signal()            # User clicked authenticate

# FreshserviceCard
test_connection_clicked: Signal()         # User clicked test connection

# ThemeManager
theme_changed: Signal(bool)               # Theme changed (is_dark)
```

---

## Keyboard Shortcuts (Planned)

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+A` | Authenticate (Microsoft) |
| `Ctrl+T` | Test Freshservice Connection |
| `Ctrl+G` | Generate Drafts |
| `Ctrl+P` | Preview |
| `Ctrl+K` | Verify Tickets |
| `Ctrl+Enter` | Confirm & Send |
| `F1` | Help |
| `F12` | View Logs |
| `Ctrl+,` | Settings |

---

## Migration from Tkinter Version

The PySide6 version auto-migrates:

- `.env` file → `appstate.json` (connections config)
- `ticket_counter.json` → `appstate.generation.next_ticket_number`
- All existing features preserved + enhanced UI

To run **old tkinter version** (if needed):

```bash
python main.py
```

---

## Troubleshooting

### App won't start

1. Check Python version: `python --version` (need 3.10+)
2. Reinstall dependencies: `pip install -r pyside6_app/requirements.txt --force-reinstall`
3. Check crash log: `%APPDATA%\ITTicketEmailGenerator\crash.log`

### Theme not applying

1. Ensure Windows is on version 10 (1809+) or 11 for acrylic effects
2. Try manual theme toggle (not auto)

### State file corrupted

1. Delete `%APPDATA%\ITTicketEmailGenerator\appstate.json`
2. Restore from `appstate.backup.json` if available
3. Re-enter configuration

---

## Contributing

This is an internal Dahlsens IT tool. For issues or feature requests, contact the IT team.

---

## License

Proprietary - Dahlsens © 2025

---

## Credits

**Built with:**
- [PySide6](https://doc.qt.io/qtforpython-6/) - Qt for Python
- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Windows 11 Fluent Design components
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python) - Microsoft Authentication

**Original tkinter version by:** Mohammed El-Cheikh & Claude AI
**PySide6 redesign by:** Claude AI (claude.ai/code)
