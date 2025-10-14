# IT Ticket Email Generator - PySide6 Redesign Specification
## Implementation Plan & Component Architecture

**Version:** 2.0
**Target Framework:** PySide6 (Qt 6) + qfluentwidgets
**Design System:** Windows 11 Fluent Design
**Status:** Architecture Phase - No Code Yet

---

## 1. COMPONENT TREE & OBJECT HIERARCHY

### 1.1 Application Shell
```
MainWindow (QFluentWindow)
├── TitleBar (FluentTitleBar)
│   ├── appTitleLabel (QLabel) - "IT Ticket Email Generator"
│   ├── themeToggleButton (TogglePushButton) - Light/Dark switch
│   ├── helpButton (TransparentToolButton) - "?"
│   ├── settingsButton (TransparentToolButton) - "☰"
│   └── windowControls (SystemButtonGroup) - Min/Max/Close
│
├── centralWidget (QWidget)
│   └── mainLayout (QGridLayout) - 12-column responsive grid
│       │
│       ├── leftDock (QWidget) - columns 0-2 (3/12)
│       │   └── leftDockLayout (QVBoxLayout)
│       │       ├── connectionsPanel (QScrollArea)
│       │       │   └── connectionsPanelContent (QWidget)
│       │       │       ├── microsoftCard (ElevatedCardWidget)
│       │       │       │   ├── msCardHeader (QLabel) - "Microsoft 365 (Graph)"
│       │       │       │   ├── msCardBody (QVBoxLayout)
│       │       │       │   │   ├── clientIdRow (QHBoxLayout)
│       │       │       │   │   │   ├── clientIdLabel (CaptionLabel)
│       │       │       │   │   │   ├── clientIdInput (PasswordLineEdit)
│       │       │       │   │   │   └── clientIdToggle (TransparentToolButton) - eye icon
│       │       │       │   │   ├── tenantIdRow (QHBoxLayout)
│       │       │       │   │   │   ├── tenantIdLabel (CaptionLabel)
│       │       │       │   │   │   └── tenantIdInput (LineEdit)
│       │       │       │   │   ├── senderEmailRow (QHBoxLayout)
│       │       │       │   │   │   ├── senderEmailLabel (CaptionLabel)
│       │       │       │   │   │   └── senderEmailInput (LineEdit) - email validator
│       │       │       │   │   ├── recipientEmailRow (QHBoxLayout)
│       │       │       │   │   │   ├── recipientEmailLabel (CaptionLabel)
│       │       │       │   │   │   └── recipientEmailInput (LineEdit) - email validator
│       │       │       │   │   ├── claudeKeyRow (QHBoxLayout)
│       │       │       │   │   │   ├── claudeKeyLabel (CaptionLabel)
│       │       │       │   │   │   ├── claudeKeyInput (PasswordLineEdit)
│       │       │       │   │   │   └── claudeKeyToggle (TransparentToolButton) - eye icon
│       │       │       │   │   └── msAuthRow (QHBoxLayout)
│       │       │       │   │       ├── authenticateButton (PrimaryPushButton)
│       │       │       │   │       ├── msAuthStatusBadge (InfoBadge) - Connected/Not Connected
│       │       │       │   │       └── msTokenExpiry (CaptionLabel) - countdown timer
│       │       │       │   └── msCardActions (CommandBar)
│       │       │       │       ├── copyClientIdAction (Action)
│       │       │       │       ├── signOutAction (Action)
│       │       │       │       └── testConnectionAction (Action)
│       │       │       │
│       │       │       └── freshserviceCard (ElevatedCardWidget)
│       │       │           ├── fsCardHeader (QLabel) - "Freshservice"
│       │       │           ├── fsCardBody (QVBoxLayout)
│       │       │           │   ├── fsDomainRow (QHBoxLayout)
│       │       │           │   │   ├── fsDomainLabel (CaptionLabel)
│       │       │           │   │   └── fsDomainInput (LineEdit) - domain validator
│       │       │           │   ├── fsApiKeyRow (QHBoxLayout)
│       │       │           │   │   ├── fsApiKeyLabel (CaptionLabel)
│       │       │           │   │   ├── fsApiKeyInput (PasswordLineEdit)
│       │       │           │   │   └── fsApiKeyToggle (TransparentToolButton)
│       │       │           │   └── fsTestRow (QHBoxLayout)
│       │       │           │       ├── fsTestButton (PushButton)
│       │       │           │       └── fsStatusBadge (InfoBadge) - Connected/Error
│       │       │           └── fsCardActions (CommandBar)
│       │       │               ├── copyApiKeyAction (Action)
│       │       │               └── clearCacheAction (Action)
│       │       └── spacer (QSpacerItem) - pushes cards to top
│       │
│       ├── centerWorkspace (QWidget) - columns 3-8 (6/12)
│       │   └── centerLayout (QVBoxLayout)
│       │       ├── generationCard (ElevatedCardWidget)
│       │       │   ├── genCardHeader (QLabel) - "Generation Settings"
│       │       │   ├── genCardBody (QFormLayout)
│       │       │   │   ├── emailCountRow
│       │       │   │   │   ├── emailCountLabel (CaptionLabel)
│       │       │   │   │   ├── emailCountSpinBox (SpinBox) - 1..1000
│       │       │   │   │   └── nextTicketLabel (CaptionLabel) - "Next: #XX"
│       │       │   │   ├── qualityRow
│       │       │   │   │   ├── qualityLabel (CaptionLabel)
│       │       │   │   │   └── qualityButtonGroup (QButtonGroup)
│       │       │   │   │       ├── basicRadio (RadioButton) - "Basic"
│       │       │   │   │       ├── realisticRadio (RadioButton) - "Realistic"
│       │       │   │   │       └── polishedRadio (RadioButton) - "Polished"
│       │       │   │   ├── waitTimeRow
│       │       │   │   │   ├── waitTimeLabel (CaptionLabel)
│       │       │   │   │   └── waitTimeSpinBox (SpinBox) - 0..5000ms
│       │       │   │   ├── modeRow
│       │       │   │   │   ├── modeLabel (CaptionLabel)
│       │       │   │   │   └── modeSegmented (SegmentedWidget) - Guided/Custom
│       │       │   │   └── customPromptRow (QVBoxLayout) - shown when Custom mode
│       │       │   │       ├── customPromptLabel (CaptionLabel)
│       │       │   │       ├── customPromptTextEdit (TextEdit) - expanding
│       │       │   │       ├── customPromptCharCount (CaptionLabel)
│       │       │   │       └── lintPromptButton (HyperlinkButton) - "Lint Prompt"
│       │       │   └── genCardActions (CommandBar)
│       │       │       ├── previewAction (PrimaryPushButton) - "Preview"
│       │       │       ├── generateDraftAction (PrimaryPushButton) - "Generate Draft"
│       │       │       └── clearAction (PushButton) - "Clear"
│       │       │
│       │       └── reviewCard (ElevatedCardWidget)
│       │           ├── reviewCardHeader (QHBoxLayout)
│       │           │   ├── reviewHeaderLabel (QLabel) - "Draft Review"
│       │           │   ├── spacer
│       │           │   └── reviewActions (CommandBar)
│       │           │       ├── selectAllAction (Action)
│       │           │       ├── selectNoneAction (Action)
│       │           │       ├── exportCsvAction (Action)
│       │           │       └── markReadyAction (Action)
│       │           ├── reviewTableView (TableWidget)
│       │           │   └── columns: [ID, Type, Priority, Category, Subject (truncated), Status, Recipient]
│       │           └── reviewProgressBar (IndeterminateProgressBar) - shown during generation
│       │
│       └── rightRail (QWidget) - columns 9-11 (3/12)
│           └── rightRailLayout (QVBoxLayout)
│               ├── actionsCard (ElevatedCardWidget)
│               │   ├── actionsCardHeader (QLabel) - "Actions"
│               │   └── actionsCardBody (QVBoxLayout)
│               │       ├── verifyButton (PrimaryPushButton) - "Verify Tickets"
│               │       └── viewLogsButton (PushButton) - "View Logs"
│               │
│               ├── preflightCard (ElevatedCardWidget)
│               │   ├── preflightCardHeader (QLabel) - "Preflight Checklist"
│               │   └── preflightCardBody (QVBoxLayout)
│               │       ├── authCheckItem (CheckBox) - "Auth ✓" (disabled, programmatic)
│               │       ├── fsCheckItem (CheckBox) - "Freshservice ✓"
│               │       ├── draftCheckItem (CheckBox) - "Drafts ready ✓"
│               │       ├── dryRunCheckItem (CheckBox) - "Dry-run complete ✓"
│               │       └── rateLimitCheckItem (CheckBox) - "Rate limit OK ✓"
│               │
│               ├── activityLogCard (ElevatedCardWidget) - collapsible
│               │   ├── logCardHeader (QHBoxLayout)
│               │   │   ├── logHeaderLabel (QLabel) - "Activity Log"
│               │   │   ├── spacer
│               │   │   └── logHeaderActions (CommandBar)
│               │   │       ├── filterAction (DropDownPushButton) - level filters
│               │   │       ├── searchAction (SearchLineEdit) - keyword filter
│               │   │       └── exportLogAction (Action) - export to file
│               │   └── logCardBody (QVBoxLayout)
│               │       ├── logTextEdit (TextEdit) - read-only, colored by level
│               │       └── logAutoScrollCheck (CheckBox) - "Auto-scroll"
│               │
│               └── toastArea (QWidget) - absolute positioning, stacking context
│                   └── toastStack (QVBoxLayout) - animated toasts appear here
│
└── stickyFooter (QWidget) - docked to bottom, elevation 8
    └── footerLayout (QHBoxLayout)
        ├── statusLabel (BodyLabel) - "Connected to FS ✓ | MS Auth ✖"
        ├── draftsCountLabel (CaptionLabel) - "Drafts: 0"
        ├── lastActionLabel (CaptionLabel) - "Last: Ready"
        ├── spacer
        └── confirmSendButton (PrimaryPushButton) - "Confirm & Send…" (disabled by default)
            └── confirmSendProgress (ProgressRing) - shown during send, replaces button
```

### 1.2 Modal Dialogs & Side Sheets

```
SettingsDialog (FluentWindow - modal)
├── settingsNav (NavigationInterface) - vertical tab bar
│   ├── generalTab (NavigationItem)
│   ├── networkTab (NavigationItem)
│   ├── shortcutsTab (NavigationItem)
│   ├── dataPrivacyTab (NavigationItem)
│   └── aboutTab (NavigationItem)
└── settingsContent (StackedWidget)
    ├── generalPage (QWidget)
    │   ├── themeCard (SettingCard) - Theme: Auto/Light/Dark
    │   ├── startupCard (SettingCard) - Launch on startup
    │   └── languageCard (SettingCard) - Language (future)
    ├── networkPage (QWidget)
    │   ├── proxyCard (SettingCard) - Proxy settings
    │   ├── timeoutCard (SettingCard) - Request timeout
    │   └── retryCard (SettingCard) - Retry attempts
    ├── shortcutsPage (QWidget)
    │   └── shortcutsTable (TableWidget) - Action, Current, Reassign button
    ├── dataPrivacyPage (QWidget)
    │   ├── storageInfoCard (InfoCard) - "Data stored in: %AppData%..."
    │   ├── clearDataButton (PushButton) - "Clear local data..."
    │   └── safeModeCard (SwitchSettingCard) - "Safe Mode (preview only)"
    └── aboutPage (QWidget)
        ├── appIcon (QLabel) - icon
        ├── appName (TitleLabel) - "IT Ticket Email Generator"
        ├── appVersion (CaptionLabel) - "v2.0.0"
        ├── copyrightLabel (CaptionLabel)
        └── licenseText (TextEdit) - read-only

ReviewDetailSheet (Drawer - right slide-in)
├── sheetHeader (QHBoxLayout)
│   ├── sheetTitle (SubtitleLabel) - "Email Preview"
│   ├── spacer
│   └── closeButton (TransparentToolButton) - "✕"
├── sheetBody (QScrollArea)
│   └── detailContent (QVBoxLayout)
│       ├── subjectCard (SimpleCardWidget)
│       │   ├── subjectLabel (CaptionLabel) - "Subject"
│       │   └── subjectValue (BodyLabel)
│       ├── detectedFieldsCard (SimpleCardWidget)
│       │   ├── fieldsLabel (SubtitleLabel) - "Detected Fields"
│       │   └── fieldsGrid (QGridLayout)
│       │       ├── typeField (field: Type)
│       │       ├── priorityField (Priority)
│       │       ├── impactField (Impact)
│       │       ├── urgencyField (Urgency)
│       │       ├── categoryField (Category)
│       │       ├── subcategoryField (Sub-Category)
│       │       ├── itemField (Item)
│       │       ├── siteField (Site - if present)
│       │       └── deviceField (Device - if present)
│       └── bodyCard (SimpleCardWidget)
│           ├── bodyLabel (CaptionLabel) - "Email Body"
│           └── bodyTextEdit (TextEdit) - read-only, selectable
└── sheetFooter (QHBoxLayout)
    ├── statusBadge (InfoBadge) - Draft/Ready/Error
    ├── spacer
    ├── markReadyButton (PushButton) - "Mark Ready"
    └── copyButton (PushButton) - "Copy"

ConfirmSendDialog (MessageBox - custom)
├── confirmIcon (QLabel) - warning icon
├── confirmTitle (SubtitleLabel) - "Confirm Send"
├── confirmMessage (BodyLabel) - "Sending X emails to Y..."
├── confirmCheckbox (CheckBox) - "I confirm this is a test environment"
├── holdToConfirmButton (PrimaryPushButton) - "Hold to Send (3s)"
│   └── holdProgress (ProgressRing) - circular progress during hold
└── cancelButton (PushButton) - "Cancel"

LogViewerDialog (FluentWindow - modal, resizable)
├── logViewerHeader (QHBoxLayout)
│   ├── logViewerTitle (SubtitleLabel) - "Activity Logs"
│   ├── spacer
│   └── logViewerActions (CommandBar)
│       ├── refreshAction (Action)
│       ├── clearAction (Action)
│       └── exportAction (Action)
├── logFilterBar (QHBoxLayout)
│   ├── levelFilterCombo (ComboBox) - All/Debug/Info/Warning/Error
│   ├── moduleFilterCombo (ComboBox) - All/Auth/Generator/Sender/Verifier
│   ├── timeRangeCombo (ComboBox) - Last hour/Today/All
│   └── searchBox (SearchLineEdit)
└── logTable (TableWidget)
    └── columns: [Timestamp, Level, Module, Message, Details (expandable)]

ToastNotification (TeachingTip - floating)
├── toastIcon (QLabel) - success/info/warning/error icon
├── toastTitle (StrongBodyLabel)
├── toastMessage (CaptionLabel)
└── toastActions (QHBoxLayout) - optional action buttons
```

---

## 2. SIGNAL/SLOT INTERACTION MAP

### 2.1 Authentication Flow

```
Signals                              Slots                                   Effects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
authenticateButton.clicked()    →   GraphAuthService.authenticate()      →  Launch OAuth flow (async)
                                 →   MainWindow.showLoadingSpinner()     →  Disable auth button, show progress

GraphAuthService.authSuccess     →   MainWindow.onAuthSuccess(token)     →  Store token securely
                                 →   msAuthStatusBadge.setSuccess()      →  Update badge: Connected ✓
                                 →   msTokenExpiry.startCountdown()      →  Show token expiry timer
                                 →   ToastService.success()              →  Show "Authenticated" toast
                                 →   PreflightChecker.updateAuthCheck()  →  Tick auth checkbox
                                 →   AppState.setMsAuthToken()           →  Persist to secure storage

GraphAuthService.authFailure     →   MainWindow.onAuthFailure(error)     →  Show error dialog
                                 →   msAuthStatusBadge.setError()        →  Update badge: Error ✖
                                 →   ToastService.error()                →  Show error toast with details
                                 →   LogService.logError()               →  Write to activity log

signOutAction.triggered()        →   GraphAuthService.signOut()          →  Clear token (async)
                                 →   msAuthStatusBadge.setDefault()      →  Reset badge: Not Connected
                                 →   msTokenExpiry.hide()                →  Hide timer
                                 →   AppState.clearMsAuthToken()         →  Clear from storage
                                 →   PreflightChecker.updateAuthCheck()  →  Un-tick auth checkbox
```

### 2.2 Freshservice Connection

```
Signals                              Slots                                   Effects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fsTestButton.clicked()           →   FreshserviceService.testConnection()→  Test API (async)
                                 →   fsTestButton.setDisabled(true)      →  Disable during test
                                 →   fsStatusBadge.setLoading()          →  Show loading state

FreshserviceService.testSuccess  →   MainWindow.onFsTestSuccess()        →  Enable verify button
                                 →   fsStatusBadge.setSuccess()          →  Update badge: Connected ✓
                                 →   ToastService.success()              →  Show "Connected" toast
                                 →   PreflightChecker.updateFsCheck()    →  Tick FS checkbox
                                 →   AppState.setFsConnected(true)       →  Persist connection state

FreshserviceService.testFailure  →   MainWindow.onFsTestFailure(error)   →  Show error details
                                 →   fsStatusBadge.setError()            →  Update badge: Error ✖
                                 →   ToastService.error()                →  Show error toast
                                 →   LogService.logError()               →  Write to activity log

fsDomainInput.textChanged()      →   DomainValidator.validate()          →  Real-time validation
                                 →   fsDomainInput.setValid/Invalid()    →  Show validation feedback

fsApiKeyInput.textChanged()      →   AppState.setFsApiKey()              →  Persist (masked) to storage
                                 →   PreflightChecker.recheckFs()        →  Re-validate connection
```

### 2.3 Generation & Review Flow

```
Signals                              Slots                                   Effects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
previewAction.clicked()          →   GeneratorService.generatePreview()  →  Generate 3 samples (async)
                                 →   reviewProgressBar.show()            →  Show progress
                                 →   previewAction.setDisabled(true)     →  Prevent double-click

GeneratorService.previewReady    →   ReviewTableView.populatePreviews()  →  Add rows to table
                                 →   reviewProgressBar.hide()            →  Hide progress
                                 →   ToastService.info()                 →  Show "Preview ready" toast
                                 →   LogService.logInfo()                →  Log to activity

generateDraftAction.clicked()    →   GeneratorService.generateDrafts()   →  Generate N drafts (async stream)
                                 →   reviewProgressBar.startIndeterminate()→ Show animated progress
                                 →   generateDraftAction.setDisabled()   →  Disable button
                                 →   clearAction.setDisabled()           →  Disable clear during generation

GeneratorService.draftGenerated  →   ReviewTableView.addDraftRow()       →  Stream results to table
                                 →   draftsCountLabel.increment()        →  Update footer counter
                                 →   LogService.logInfo()                →  Log each draft

GeneratorService.allDraftsReady  →   reviewProgressBar.hide()            →  Hide progress
                                 →   generateDraftAction.setEnabled()    →  Re-enable button
                                 →   clearAction.setEnabled()            →  Re-enable clear
                                 →   ToastService.success()              →  Show "X drafts ready" toast
                                 →   PreflightChecker.updateDraftCheck() →  Tick drafts checkbox
                                 →   AppState.setDrafts(draftList)       →  Persist drafts

GeneratorService.generationError →   MainWindow.onGenerationError(error) →  Show error dialog
                                 →   reviewProgressBar.hide()            →  Hide progress
                                 →   ToastService.error()                →  Show error toast
                                 →   LogService.logError()               →  Write to activity log

reviewTableView.rowClicked(row)  →   ReviewDetailSheet.show(row)         →  Slide-in detail sheet
                                 →   ReviewDetailSheet.populate(data)    →  Fill with row data

selectAllAction.triggered()      →   reviewTableView.selectAll()         →  Select all rows

exportCsvAction.triggered()      →   ExportService.exportToCsv()         →  Open file dialog, export selected
                                 →   ToastService.success()              →  Show "Exported X rows" toast

clearAction.clicked()            →   ReviewTableView.clear()             →  Clear all rows
                                 →   draftsCountLabel.setText("0")       →  Reset counter
                                 →   AppState.clearDrafts()              →  Clear from storage
                                 →   PreflightChecker.updateDraftCheck() →  Un-tick drafts checkbox
```

### 2.4 Verification & Sending Flow

```
Signals                              Slots                                   Effects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
verifyButton.clicked()           →   PreflightChecker.runAllChecks()     →  Validate all preflight conditions
                                 →   verifyButton.setDisabled(true)      →  Disable during check

PreflightChecker.allChecksPassed →   MainWindow.onPreflightPassed()      →  Enable confirmSendButton
                                 →   confirmSendButton.setEnabled(true)  →  Make primary CTA active
                                 →   preflightCardBody.tickAllBoxes()    →  Update checklist UI
                                 →   ToastService.success()              →  Show "Ready to send ✓" toast
                                 →   AppState.setPreflightPassed(true)   →  Persist state

PreflightChecker.checksFailed    →   MainWindow.onPreflightFailed(list)  →  Show error dialog with failures
                                 →   confirmSendButton.setDisabled()     →  Keep CTA disabled
                                 →   ToastService.warning()              →  Show "Preflight failed" toast
                                 →   LogService.logWarning()             →  Log failures

confirmSendButton.clicked()      →   ConfirmSendDialog.exec()            →  Show confirmation dialog

holdToConfirmButton.pressed()    →   holdToConfirmButton.startHoldTimer()→  Start 3s countdown with progress

holdToConfirmButton.holdComplete →   ConfirmSendDialog.accept()          →  Close dialog
                                 →   EmailSenderService.sendAll()        →  Send drafts (async stream)
                                 →   confirmSendButton.replaceWithProgress()→ Morph to progress ring
                                 →   stickyFooter.showSendProgress()     →  Update footer status

EmailSenderService.emailSent     →   ReviewTableView.updateRowStatus()   →  Mark row as "Sent ✓"
                                 →   confirmSendProgress.increment()     →  Update progress ring
                                 →   LogService.logInfo()                →  Log each sent email
                                 →   lastActionLabel.update()            →  Update "Last: Sent #X"

EmailSenderService.allEmailsSent →   confirmSendButton.restore()         →  Restore button from progress
                                 →   ToastService.success()              →  Show "X emails sent ✓" toast
                                 →   AppState.recordSendBatch()          →  Save to history
                                 →   LogService.logInfo()                →  Log completion

EmailSenderService.sendError     →   ReviewTableView.updateRowStatus()   →  Mark row as "Error ✖"
                                 →   ToastService.error()                →  Show error toast
                                 →   LogService.logError()               →  Write to activity log
                                 →   MainWindow.showErrorDetails()       →  Show error dialog with retry
```

### 2.5 UI State & Settings

```
Signals                              Slots                                   Effects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
themeToggleButton.toggled(bool)  →   ThemeManager.setTheme(dark)         →  Switch theme light/dark
                                 →   AppState.setDarkMode(dark)          →  Persist preference
                                 →   MainWindow.updateAllWidgets()       →  Re-apply styles

settingsButton.clicked()         →   SettingsDialog.exec()               →  Show settings modal

safeModeCard.switchToggled(bool) →   AppState.setSafeMode(bool)          →  Persist setting
                                 →   confirmSendButton.setDisabled(true) →  Disable sending if safe mode
                                 →   ToastService.info()                 →  Show "Safe mode enabled" toast

clearDataButton.clicked()        →   DataManager.clearLocalData()        →  Show confirmation dialog
                                 →   AppState.reset()                    →  Clear all stored data
                                 →   MainWindow.resetUI()                →  Reset all widgets to defaults
                                 →   ToastService.info()                 →  Show "Data cleared" toast

AppState.dataChanged(field)      →   PersistenceService.save()           →  Auto-save to JSON (debounced)
                                 →   LogService.logDebug()               →  Log state change (debug level)
```

### 2.6 Keyboard Shortcuts

```
Shortcut               Signal                           Slot/Effect
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ctrl+Shift+A       →   authenticateButton.clicked()  →  Trigger MS auth
Ctrl+T             →   fsTestButton.clicked()        →  Test Freshservice
Ctrl+G             →   generateDraftAction.clicked() →  Generate drafts
Ctrl+P             →   previewAction.clicked()       →  Generate preview
Ctrl+K             →   verifyButton.clicked()        →  Run preflight checks
Ctrl+Enter         →   confirmSendButton.clicked()   →  Confirm send (if enabled)
F1                 →   helpButton.clicked()          →  Show help/docs
F12                →   viewLogsButton.clicked()      →  Open log viewer
Ctrl+Q             →   MainWindow.close()            →  Quit application
Ctrl+,             →   settingsButton.clicked()      →  Open settings
Ctrl+W             →   (current modal).close()       →  Close active dialog
Escape             →   (current sheet/modal).close() →  Close active overlay
```

---

## 3. JSON APPSTATE SCHEMA

### 3.1 Schema Definition (JSON Schema Draft 7)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IT Ticket Email Generator - Application State",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "App version for migration compatibility"
    },
    "lastModified": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of last state save"
    },
    "ui": {
      "type": "object",
      "properties": {
        "theme": {
          "type": "string",
          "enum": ["auto", "light", "dark"],
          "default": "auto"
        },
        "windowGeometry": {
          "type": "object",
          "properties": {
            "x": { "type": "integer" },
            "y": { "type": "integer" },
            "width": { "type": "integer", "minimum": 1280 },
            "height": { "type": "integer", "minimum": 720 }
          }
        },
        "leftDockWidth": { "type": "integer", "minimum": 200 },
        "rightRailWidth": { "type": "integer", "minimum": 200 },
        "activityLogCollapsed": { "type": "boolean", "default": false }
      },
      "required": ["theme"]
    },
    "connections": {
      "type": "object",
      "properties": {
        "microsoft": {
          "type": "object",
          "properties": {
            "clientId": { "type": "string", "minLength": 36 },
            "tenantId": { "type": "string", "minLength": 36 },
            "senderEmail": { "type": "string", "format": "email" },
            "recipientEmail": { "type": "string", "format": "email" },
            "tokenExpiry": { "type": "string", "format": "date-time" },
            "isAuthenticated": { "type": "boolean", "default": false }
          },
          "required": ["clientId", "tenantId", "senderEmail", "recipientEmail"]
        },
        "claude": {
          "type": "object",
          "properties": {
            "apiKeyLastFour": { "type": "string", "pattern": "^[A-Za-z0-9]{4}$" },
            "isConfigured": { "type": "boolean", "default": false }
          }
        },
        "freshservice": {
          "type": "object",
          "properties": {
            "domain": { "type": "string", "pattern": "^[a-z0-9-]+\\.freshservice\\.com$" },
            "apiKeyLastFour": { "type": "string", "pattern": "^[A-Za-z0-9]{4}$" },
            "isConnected": { "type": "boolean", "default": false },
            "lastTestTime": { "type": "string", "format": "date-time" }
          }
        }
      },
      "required": ["microsoft", "freshservice"]
    },
    "generation": {
      "type": "object",
      "properties": {
        "emailCount": { "type": "integer", "minimum": 1, "maximum": 1000, "default": 5 },
        "quality": { "type": "string", "enum": ["basic", "realistic", "polished"], "default": "realistic" },
        "waitTimeMs": { "type": "integer", "minimum": 0, "maximum": 5000, "default": 10 },
        "mode": { "type": "string", "enum": ["guided", "custom"], "default": "guided" },
        "customPrompt": { "type": "string", "maxLength": 5000 },
        "nextTicketNumber": { "type": "integer", "minimum": 1, "default": 1 }
      },
      "required": ["emailCount", "quality", "mode"]
    },
    "drafts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "type": { "type": "string", "enum": ["Incident", "Service Request"] },
          "priority": { "type": "string", "enum": ["Priority 1", "Priority 2", "Priority 3", "Priority 4"] },
          "category": { "type": "string" },
          "subcategory": { "type": "string" },
          "item": { "type": "string" },
          "subject": { "type": "string" },
          "body": { "type": "string" },
          "recipient": { "type": "string", "format": "email" },
          "status": { "type": "string", "enum": ["draft", "ready", "sent", "error"] },
          "errorMessage": { "type": "string" },
          "sentTimestamp": { "type": "string", "format": "date-time" }
        },
        "required": ["id", "type", "priority", "subject", "body", "recipient", "status"]
      }
    },
    "preflight": {
      "type": "object",
      "properties": {
        "authChecked": { "type": "boolean", "default": false },
        "fsChecked": { "type": "boolean", "default": false },
        "draftsChecked": { "type": "boolean", "default": false },
        "dryRunChecked": { "type": "boolean", "default": false },
        "rateLimitChecked": { "type": "boolean", "default": false },
        "allPassed": { "type": "boolean", "default": false }
      }
    },
    "settings": {
      "type": "object",
      "properties": {
        "general": {
          "type": "object",
          "properties": {
            "launchOnStartup": { "type": "boolean", "default": false },
            "language": { "type": "string", "default": "en-US" }
          }
        },
        "network": {
          "type": "object",
          "properties": {
            "proxyEnabled": { "type": "boolean", "default": false },
            "proxyUrl": { "type": "string", "format": "uri" },
            "requestTimeoutMs": { "type": "integer", "minimum": 1000, "default": 30000 },
            "retryAttempts": { "type": "integer", "minimum": 0, "maximum": 5, "default": 3 }
          }
        },
        "privacy": {
          "type": "object",
          "properties": {
            "safeMode": { "type": "boolean", "default": false },
            "telemetryEnabled": { "type": "boolean", "default": false }
          }
        }
      }
    },
    "history": {
      "type": "array",
      "maxItems": 100,
      "items": {
        "type": "object",
        "properties": {
          "batchId": { "type": "string", "format": "uuid" },
          "timestamp": { "type": "string", "format": "date-time" },
          "emailsSent": { "type": "integer" },
          "emailsSucceeded": { "type": "integer" },
          "emailsFailed": { "type": "integer" },
          "recipient": { "type": "string", "format": "email" }
        }
      }
    }
  },
  "required": ["version", "lastModified", "ui", "connections", "generation"]
}
```

### 3.2 Example AppState JSON File

```json
{
  "version": "2.0.0",
  "lastModified": "2025-01-15T14:32:18.642Z",
  "ui": {
    "theme": "dark",
    "windowGeometry": {
      "x": 100,
      "y": 100,
      "width": 1600,
      "height": 900
    },
    "leftDockWidth": 280,
    "rightRailWidth": 320,
    "activityLogCollapsed": false
  },
  "connections": {
    "microsoft": {
      "clientId": "b060dd17-ce88-46ff-a238-25defdf28f4a",
      "tenantId": "f8ccc56f-b2b2-4afa-8a89-c6ccbcb6f6a3",
      "senderEmail": "mohammed.el-cheikh@dahlsens.com.au",
      "recipientEmail": "itsupport@dahlsens.com.au",
      "tokenExpiry": "2025-01-15T15:32:00.000Z",
      "isAuthenticated": true
    },
    "claude": {
      "apiKeyLastFour": "7kQ9",
      "isConfigured": true
    },
    "freshservice": {
      "domain": "dahlsens-servicedesk.freshservice.com",
      "apiKeyLastFour": "xY2p",
      "isConnected": true,
      "lastTestTime": "2025-01-15T14:30:45.123Z"
    }
  },
  "generation": {
    "emailCount": 10,
    "quality": "realistic",
    "waitTimeMs": 10,
    "mode": "guided",
    "customPrompt": "",
    "nextTicketNumber": 42
  },
  "drafts": [
    {
      "id": 1,
      "type": "Incident",
      "priority": "Priority 3",
      "category": "Hardware",
      "subcategory": "Desktop",
      "item": "Mouse",
      "subject": "Mouse not working on workstation",
      "body": "Hi, my mouse stopped working this morning. I tried unplugging and re-plugging but no luck. Can someone help? Thanks.",
      "recipient": "itsupport@dahlsens.com.au",
      "status": "ready",
      "errorMessage": null,
      "sentTimestamp": null
    },
    {
      "id": 2,
      "type": "Service Request",
      "priority": "Priority 4",
      "category": "Software",
      "subcategory": "Applications",
      "item": "Adobe Acrobat",
      "subject": "Need Adobe Acrobat license for new hire",
      "body": "Hello, we have a new employee starting Monday who needs Adobe Acrobat Pro. Please set up access. Employee ID: E12345.",
      "recipient": "itsupport@dahlsens.com.au",
      "status": "draft",
      "errorMessage": null,
      "sentTimestamp": null
    }
  ],
  "preflight": {
    "authChecked": true,
    "fsChecked": true,
    "draftsChecked": true,
    "dryRunChecked": false,
    "rateLimitChecked": true,
    "allPassed": false
  },
  "settings": {
    "general": {
      "launchOnStartup": false,
      "language": "en-US"
    },
    "network": {
      "proxyEnabled": false,
      "proxyUrl": "",
      "requestTimeoutMs": 30000,
      "retryAttempts": 3
    },
    "privacy": {
      "safeMode": false,
      "telemetryEnabled": false
    }
  },
  "history": [
    {
      "batchId": "a7f3c8e2-4d91-4b5a-9c1f-8e2b3d4c5a6b",
      "timestamp": "2025-01-15T10:15:30.000Z",
      "emailsSent": 25,
      "emailsSucceeded": 24,
      "emailsFailed": 1,
      "recipient": "itsupport@dahlsens.com.au"
    }
  ]
}
```

---

## 4. FINAL UI SPECIFICATION WITH MEASUREMENTS

### 4.1 Layout Grid & Breakpoints

**Base Grid:** 12-column responsive grid with 16px gutter

**Breakpoints:**
- **Small (1280-1439px):** 3-6-3 layout (left 3 cols, center 6 cols, right 3 cols)
- **Medium (1440-1919px):** 3-6-3 layout with increased padding
- **Large (1920px+):** 3-6-3 layout with max content width of 2000px, centered

**Responsive Behavior:**
- Below 1280px: Stack vertically (left → center → right)
- Center cards stack vertically on all breakpoints
- Right rail collapses into a slide-out panel on small screens (future)

### 4.2 Spacing Tokens

```
Base Unit: 8px

Compact:    4px  (0.5× base)
Default:    8px  (1× base)
Comfortable: 16px (2× base)
Spacious:   24px (3× base)
Section:    32px (4× base)
Major:      48px (6× base)

Card Padding:
  - Header: 16px horizontal, 12px vertical
  - Body: 16px all sides
  - Footer: 16px horizontal, 12px vertical

Input Spacing:
  - Between label & input: 4px vertical
  - Between input rows: 12px vertical
  - Between sections: 24px vertical

Button Spacing:
  - Inline buttons: 8px gap
  - Stacked buttons: 8px gap
  - Between button groups: 16px gap
```

### 4.3 Typography Scale (Segoe UI Variable)

```
Display:      32px / 40px line-height / Semi-Bold (unused in this app)
Title:        24px / 32px / Semi-Bold (modal headers)
Subtitle:     20px / 28px / Semi-Bold (card headers)
Body:         14px / 20px / Regular (primary text)
Body Strong:  14px / 20px / Semi-Bold (emphasized body)
Caption:      12px / 16px / Regular (labels, hints)
Caption Bold: 12px / 16px / Semi-Bold (status text)

Color Tokens (Light Theme):
  - Text Primary: rgba(0,0,0,0.9)
  - Text Secondary: rgba(0,0,0,0.6)
  - Text Tertiary: rgba(0,0,0,0.45)
  - Text Disabled: rgba(0,0,0,0.25)

Color Tokens (Dark Theme):
  - Text Primary: rgba(255,255,255,0.9)
  - Text Secondary: rgba(255,255,255,0.7)
  - Text Tertiary: rgba(255,255,255,0.55)
  - Text Disabled: rgba(255,255,255,0.35)
```

### 4.4 Card Specifications

**ElevatedCardWidget:**
- Border Radius: 12px
- Elevation: 2 (4px blur, 2px offset, rgba(0,0,0,0.14))
- Background: Card fill color (system surface)
- Border: 1px solid (divider color)
- Padding: 16px (adjustable per card)
- Min Height: 120px
- Hover: Lift to elevation 4 (8px blur, 4px offset)
- Transition: 200ms cubic-bezier(0.4, 0, 0.2, 1)

**SimpleCardWidget:**
- Border Radius: 8px
- Elevation: 0
- Background: Subtle fill (background + 5% alpha)
- Border: 1px solid (divider color)
- Padding: 12px
- Used for nested content (e.g., inside detail sheet)

### 4.5 Component Dimensions

**Left Dock (Connections Panel):**
- Width: 280px (min 240px, max 360px)
- Card Header Height: 40px
- Input Field Height: 32px
- Button Height: 32px
- Vertical spacing between cards: 16px

**Center Workspace:**
- Min Width: 600px
- Generation Card:
  - Min Height: 320px
  - SpinBox Width: 80px
  - RadioButton Spacing: 8px horizontal
  - TextEdit (custom prompt): Min 3 lines, max 8 lines, expanding
- Review Card:
  - Min Height: 400px
  - Table row height: 40px
  - Table column widths:
    - ID: 60px
    - Type: 120px
    - Priority: 100px
    - Category: 150px
    - Subject: flex (remaining width)
    - Status: 100px
    - Recipient: 200px

**Right Rail:**
- Width: 320px (min 280px, max 400px)
- Actions Card:
  - Button Height: 36px
  - Button Width: 100% (fill horizontal)
  - Spacing between buttons: 8px
- Preflight Card:
  - Checkbox Height: 28px
  - Checkbox Spacing: 6px vertical
- Activity Log Card:
  - Min Height: 300px
  - Max Height: 50vh (resizable)
  - Log line height: 20px
  - Font: Consolas 11px monospace

**Sticky Footer:**
- Height: 56px
- Elevation: 8 (shadow above, not below)
- Padding: 16px horizontal
- Button (Confirm & Send): Height 36px, min width 160px
- Status labels: Caption size (12px)

**Modals & Dialogs:**
- Settings Dialog:
  - Width: 800px
  - Height: 600px
  - Nav Rail Width: 200px
- Review Detail Sheet:
  - Width: 480px (slides from right)
  - Full height
  - Header Height: 56px
  - Footer Height: 56px
- Confirm Send Dialog:
  - Width: 440px
  - Height: 280px (auto-fit)
- Log Viewer Dialog:
  - Width: 1000px
  - Height: 700px
  - Min Width: 800px, Min Height: 500px (resizable)

### 4.6 Color Palette (Fluent System)

**Semantic Colors (Auto from qfluentwidgets):**
```
Primary:   System Accent (user's Windows accent color)
Success:   #107C10 (light) / #6CCB5F (dark)
Warning:   #CA5010 (light) / #FCE100 (dark)
Error:     #D13438 (light) / #FF99A4 (dark)
Info:      #0078D4 (light) / #60CDFF (dark)
```

**Surface Colors:**
```
Background (Light):      #F3F3F3 (mica base)
Surface (Light):         #FFFFFF
Card Fill (Light):       #FCFCFC
Divider (Light):         rgba(0,0,0,0.08)

Background (Dark):       #202020 (mica base)
Surface (Dark):          #2C2C2C
Card Fill (Dark):        #282828
Divider (Dark):          rgba(255,255,255,0.08)
```

**State Colors:**
```
Hover:     +5% alpha overlay
Pressed:   +10% alpha overlay
Disabled:  50% opacity
Focus:     2px accent color outline, 4px offset
```

### 4.7 Animation & Transitions

**Durations:**
```
Fast:     100ms - Hover states, ripples
Default:  200ms - Card elevation, color changes
Slow:     300ms - Slide-in/out sheets, modal fade
Very Slow: 500ms - Progress animations
```

**Easing Functions:**
```
Standard:     cubic-bezier(0.4, 0, 0.2, 1) - Most UI transitions
Decelerate:   cubic-bezier(0.0, 0, 0.2, 1) - Enter animations
Accelerate:   cubic-bezier(0.4, 0, 1, 1)   - Exit animations
Sharp:        cubic-bezier(0.4, 0, 0.6, 1) - Interactive feedback
```

**Key Animations:**
- Toast appear: Slide up 20px + fade in (200ms decelerate)
- Toast dismiss: Slide right 40px + fade out (150ms accelerate)
- Sheet slide-in: Translate X from 480px → 0 (300ms decelerate)
- Sheet slide-out: Translate X from 0 → 480px (250ms accelerate)
- Progress ring: Rotate 360deg infinite (1200ms linear)
- Ripple: Scale 0 → 1, opacity 0.2 → 0 (300ms standard)

---

## 5. MIGRATION STRATEGY FROM TKINTER

### 5.1 Feature Parity Checklist

**Core Features (Must Have):**
- [x] Microsoft OAuth authentication (preserve existing flow)
- [x] Freshservice API connection testing
- [x] Claude API key configuration
- [x] Email count, quality, wait time settings
- [x] Custom prompt mode
- [x] Preview generation (3 samples)
- [x] Batch draft generation (1-1000 emails)
- [x] Draft review table with status
- [x] Preflight checks before send
- [x] Confirm & Send with safety dialog
- [x] Activity log with levels
- [x] Ticket counter persistence
- [x] Export drafts to CSV

**New Features (Added):**
- [x] Hold-to-confirm button (3s hold for mass sends)
- [x] Dry-run requirement before enabling send
- [x] Detailed draft preview side sheet
- [x] Real-time validation feedback
- [x] Token expiry countdown
- [x] Send progress with cancel/abort
- [x] Toast notifications (non-blocking)
- [x] Structured log viewer with filters
- [x] Settings dialog (theme, network, shortcuts, privacy)
- [x] Safe Mode (preview-only, no send)
- [x] Send history tracking
- [x] Keyboard shortcuts for all actions

**Removed Features (Intentional):**
- [ ] ~~None~~ - All existing features preserved or enhanced

### 5.2 Data Migration

**From Tkinter App:**
- `.env` file: Read and migrate to new AppState JSON (one-time)
- `ticket_counter.json`: Merge `nextTicketNumber` into AppState
- Existing logs: Preserve in same directory, new logs follow new format

**Migration Script (run on first launch):**
```python
# Pseudo-code for migration function
def migrate_from_tkinter():
    if os.path.exists('.env') and not os.path.exists(appstate_path):
        env_vars = load_env_file('.env')
        appstate = {
            "version": "2.0.0",
            "connections": {
                "microsoft": {
                    "clientId": env_vars.get('CLIENT_ID', ''),
                    "tenantId": env_vars.get('TENANT_ID', ''),
                    "senderEmail": env_vars.get('SENDER_EMAIL', ''),
                    "recipientEmail": env_vars.get('RECIPIENT_EMAIL', '')
                },
                "freshservice": {
                    "domain": env_vars.get('FRESHSERVICE_DOMAIN', ''),
                }
            },
            "generation": {
                "emailCount": int(env_vars.get('NUM_EMAILS', 5)),
                "waitTimeMs": int(env_vars.get('WAIT_TIME_MS', 10))
            }
        }
        # Merge ticket counter
        if os.path.exists('ticket_counter.json'):
            with open('ticket_counter.json', 'r') as f:
                counter_data = json.load(f)
                appstate["generation"]["nextTicketNumber"] = counter_data.get('counter', 1)

        save_appstate(appstate)
        print("[Migration] Successfully migrated from tkinter app")
```

### 5.3 Code Module Mapping

**Preserve & Refactor:**
- `auth.py` → `services/graph.py` (minimal changes, keep OAuth flow)
- `freshservice_client.py` → `services/freshservice.py` (add async wrapper)
- `content_generator.py` → `services/generator.py` (add progress signals)
- `email_sender.py` → `services/sender.py` (add async + progress signals)
- `ticket_verifier.py` → `services/verifier.py` (add async wrapper)
- `ticket_counter.py` → merge into `state/models.py` (AppState.nextTicketNumber)
- `utils.py` → `utils/validators.py` (keep file readers, add email/domain validators)
- `logger.py` → `utils/logging.py` (refactor to structured logger with levels)

**New Modules:**
- `app.py` - Bootstrap, QApplication setup, exception handler
- `widgets/cards.py` - Custom card widgets
- `widgets/dialogs.py` - Custom dialogs (Confirm Send, Log Viewer)
- `widgets/sheets.py` - Slide-in sheets (Review Detail)
- `state/store.py` - AppState management + persistence
- `utils/async.py` - QRunnable wrappers for async tasks
- `utils/theme.py` - Theme manager (light/dark switching)

### 5.4 Testing Strategy

**Unit Tests:**
- `tests/test_validators.py` - Email, domain, prompt validators
- `tests/test_appstate.py` - State serialization, migration
- `tests/test_services.py` - Graph, Freshservice, Generator (mocked HTTP)

**Integration Tests:**
- `tests/test_generation_flow.py` - End-to-end generation → review → send
- `tests/test_auth_flow.py` - OAuth flow with mock token endpoint

**UI Tests (Smoke):**
- `tests/test_ui_smoke.py` - Launch app, verify all widgets present, close
- `tests/test_ui_interactions.py` - Click buttons, verify signal emissions

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1)
- [ ] Set up PySide6 + qfluentwidgets project structure
- [ ] Implement AppState model + JSON persistence
- [ ] Create frameless main window with title bar
- [ ] Build left dock (Connections Panel) with Microsoft & Freshservice cards
- [ ] Port `auth.py` and `freshservice_client.py` to services with async wrappers
- [ ] Implement theme manager (light/dark toggle)

### Phase 2: Generation & Review (Week 2)
- [ ] Build center workspace (Generation Card + Review Card)
- [ ] Port `content_generator.py` to services with progress signals
- [ ] Implement draft table with row selection
- [ ] Build Review Detail Sheet (slide-in)
- [ ] Add export to CSV functionality
- [ ] Implement custom prompt mode with lint heuristic

### Phase 3: Actions & Preflight (Week 3)
- [ ] Build right rail (Actions Card, Preflight Card, Activity Log Card)
- [ ] Implement PreflightChecker service
- [ ] Create Confirm Send Dialog with hold-to-confirm button
- [ ] Port `email_sender.py` with async + progress signals
- [ ] Build sticky footer with live status
- [ ] Implement send flow with cancel/abort

### Phase 4: Settings & Polish (Week 4)
- [ ] Build Settings Dialog with all tabs
- [ ] Implement keyboard shortcuts
- [ ] Add all toast notifications
- [ ] Build Log Viewer Dialog with filters
- [ ] Implement Safe Mode
- [ ] Add send history tracking
- [ ] Write migration script from tkinter

### Phase 5: Testing & Packaging (Week 5)
- [ ] Write all unit tests (validators, state, services)
- [ ] Write integration tests (flows)
- [ ] Write UI smoke tests
- [ ] Create PyInstaller spec with version stamping
- [ ] Test on multiple Windows versions (10/11)
- [ ] Test with 125%/150% display scaling
- [ ] Generate installer (MSI or NSIS)

### Phase 6: Documentation & Deployment
- [ ] Write user manual (markdown + PDF)
- [ ] Create video walkthrough (5-10 min)
- [ ] Document keyboard shortcuts in-app
- [ ] Set up crash reporter
- [ ] Final QA pass
- [ ] Release v2.0.0

---

## 7. OPEN QUESTIONS & DECISIONS NEEDED

**Q1:** Should secrets (API keys, tokens) be stored in Windows Credential Manager instead of JSON?
**A:** Recommend using `keyring` library (cross-platform) for production. For MVP, masked JSON with file permissions is acceptable.

**Q2:** Should we support multiple profiles (different MS tenants / FS domains)?
**A:** Not in v2.0. Add in v2.1 if requested.

**Q3:** Telemetry/analytics - should we track usage (anonymized)?
**A:** Off by default, opt-in via Settings → Data/Privacy. Only if legal/compliance allows.

**Q4:** Localization - support other languages?
**A:** Not in v2.0. Architecture should support i18n via Qt's translation system for future.

**Q5:** Auto-update mechanism?
**A:** Not in v2.0. Manual download for now. Add auto-update in v2.2 with Sparkle/WinSparkle.

---

## 8. DELIVERABLE SUMMARY

**Completed Artifacts:**
1. ✅ Full component tree with Qt object names
2. ✅ Signal/slot interaction map for all flows
3. ✅ JSON AppState schema (JSON Schema Draft 7) + example file
4. ✅ UI specification with measurements, spacing, typography, colors
5. ✅ Migration strategy from tkinter app
6. ✅ Implementation roadmap with 6 phases

**Ready for Approval:**
- Architecture review by senior dev
- UX review by stakeholders
- Security review for secrets storage

**Next Steps After Approval:**
- Generate PySide6 code for Phase 1 modules:
  - `app.py`
  - `state/models.py` + `state/store.py`
  - `widgets/main_window.py` (with title bar + grid layout)
  - `widgets/connection_cards.py`
  - `services/graph.py` (async wrapper)
  - `services/freshservice.py` (async wrapper)
  - `utils/theme.py`

---

**End of Specification Document**

*This document serves as the definitive blueprint for implementing the PySide6 redesign. All design decisions, component hierarchies, interactions, and data structures are finalized. Code generation can proceed module-by-module following the roadmap.*
