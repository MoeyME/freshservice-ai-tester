# PySide6 App - Quick Start Guide

## 🚀 Launch the New App (2 Steps)

### Step 1: Install Dependencies

```bash
cd "c:\Cursor Projects\Ticket Generation"
pip install -r pyside6_app/requirements.txt
```

**Wait for:** ~30 seconds while PySide6, qfluentwidgets, and pydantic install.

### Step 2: Run

```bash
python run_pyside6_app.py
```

**That's it!** The modern UI should launch.

---

## ✨ What You'll See

### On First Launch:

1. **Frameless Window** with acrylic/mica background
2. **Light Theme** (auto-detects Windows theme)
3. **Three Columns:**
   - Left: Microsoft & Freshservice connection cards
   - Center: Placeholder (Phase 2 coming)
   - Right: Placeholder (Phase 2 coming)
4. **Footer:** Status bar with "Confirm & Send" button (disabled)

### If You Have `.env` File:

The app will **automatically migrate** your old configuration:
- Client ID, Tenant ID, Sender, Recipient
- Freshservice Domain
- Email count, wait time
- Ticket counter

**Migration happens once.** After that, it uses:
`%APPDATA%\ITTicketEmailGenerator\appstate.json`

---

## 🎨 Test Theme Toggle

1. Click the **moon icon** (🌙) in the title bar OR top navigation
2. Watch the UI switch between light and dark mode
3. Close and reopen → theme preference is saved

---

## 🔌 Test Connection Cards

### Microsoft Card:
1. Enter Client ID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
2. Enter Tenant ID (same format)
3. Enter Sender Email: `your.email@company.com`
4. Enter Recipient Email: `recipient@company.com`
5. Enter Claude Key: `sk-ant-...`
6. **Values auto-save as you type!**

### Freshservice Card:
1. Enter Domain: `yourcompany.freshservice.com`
   - Must end with `.freshservice.com` or validation fails
2. Enter API Key
3. **Values auto-save!**

### Eye Icons:
- Click 👁️ next to Client ID / Claude Key / API Key to show/hide

---

## 📁 Where Is Data Stored?

**State File:**
```
C:\Users\YourName\AppData\Roaming\ITTicketEmailGenerator\appstate.json
```

**Backup (automatic):**
```
C:\Users\YourName\AppData\Roaming\ITTicketEmailGenerator\appstate.backup.json
```

**Crash Logs (if any errors):**
```
C:\Users\YourName\AppData\Roaming\ITTicketEmailGenerator\crash.log
```

---

## 🐛 Troubleshooting

### Error: "No module named 'PySide6'"

**Fix:**
```bash
pip install PySide6
```

### Error: "No module named 'qfluentwidgets'"

**Fix:**
```bash
pip install PyQt-Fluent-Widgets
```

### Error: "No module named 'pydantic'"

**Fix:**
```bash
pip install pydantic
```

### App Won't Start

1. Check Python version:
   ```bash
   python --version
   ```
   **Need:** Python 3.10 or higher

2. Reinstall all dependencies:
   ```bash
   pip install -r pyside6_app/requirements.txt --force-reinstall
   ```

3. Check crash log:
   ```
   %APPDATA%\ITTicketEmailGenerator\crash.log
   ```

### Window Looks Weird / No Acrylic Effect

**Requirements for full visual effects:**
- Windows 10 version 1809 or later
- Windows 11 (best experience)

**On older Windows:**
- App still works, just no blur effects
- Theme toggle still works

---

## 🔄 Switch Back to Old App

The old tkinter version still works!

**Run:**
```bash
python main.py
```

**Note:** Both apps can coexist. They use different storage:
- **Old:** `.env`, `ticket_counter.json`, local logs
- **New:** `%APPDATA%\ITTicketEmailGenerator\appstate.json`

---

## 📚 What Works Right Now (Phase 1)

✅ **Working:**
- Modern UI with theme toggle
- Connection card inputs
- Real-time validation
- Auto-save to state file
- Migration from old `.env`
- Window geometry persistence

❌ **Not Yet (Coming in Phase 2-6):**
- Email generation
- Draft review table
- Sending emails
- Verification
- Activity log
- Settings dialog
- Help system

**See full roadmap:** [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)

---

## 🎯 Quick Feature Test

### Test #1: Theme Persistence
1. Toggle theme to dark
2. Close app
3. Reopen → should remember dark mode ✓

### Test #2: Input Auto-Save
1. Enter Client ID
2. Close app
3. Reopen → Client ID still there ✓

### Test #3: Validation
1. Enter invalid email: `notanemail`
2. Should not save to state ✓
3. Enter valid email: `test@example.com`
4. Saves immediately ✓

### Test #4: Window Geometry
1. Resize window
2. Move window
3. Close & reopen → same position/size ✓

---

## 📖 Full Documentation

- **Architecture:** [REDESIGN_SPEC.md](REDESIGN_SPEC.md) (60+ pages)
- **Phase 1 Summary:** [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)
- **App README:** [pyside6_app/README.md](pyside6_app/README.md)

---

## 🚧 Development Status

**Current:** Phase 1 Complete (Foundation) ✅
**Next:** Phase 2 (Generation & Review) - Starting now

**Want to contribute?** See Phase 2 tasks in [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)

---

## ❓ Questions?

**Check:**
1. [pyside6_app/README.md](pyside6_app/README.md) - Full docs
2. [REDESIGN_SPEC.md](REDESIGN_SPEC.md) - Architecture details
3. Crash log (if errors)

**For Developers:**
- All code in `pyside6_app/` folder
- Entry point: `app.py`
- Main window: `widgets/main_window.py`
- State management: `state/models.py` + `state/store.py`

---

**Ready to use!** 🎉

To run: `python run_pyside6_app.py`
