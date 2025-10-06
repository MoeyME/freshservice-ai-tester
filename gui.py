#!/usr/bin/env python3
"""
IT Ticket Email Generator - GUI Version
Graphical interface for generating and sending realistic IT support ticket emails.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from datetime import datetime, timedelta
import os
from typing import Optional

from auth import GraphAuthenticator, validate_credentials
from content_generator import ContentGenerator, validate_api_key
from email_sender import EmailSender
from logger import TicketLogger
from ticket_counter import TicketCounter
from config import load_env_file, get_config, get_optional_config
from utils import (
    read_categories,
    read_priorities_and_types,
    generate_distribution,
    calculate_distribution_stats
)
from freshservice_client import FreshserviceClient, validate_freshservice_credentials
from ticket_verifier import TicketVerifier
from verification_logger import VerificationLogger


class TicketGeneratorGUI:
    # Modern color scheme with gradients
    COLORS = {
        'primary': '#6366F1',      # Modern Indigo
        'primary_dark': '#4F46E5',
        'primary_light': '#818CF8',
        'success': '#10B981',      # Modern Green
        'success_light': '#34D399',
        'error': '#EF4444',        # Modern Red
        'warning': '#F59E0B',      # Modern Amber
        'background': '#F3F4F6',   # Light gray background
        'surface': '#FFFFFF',      # White
        'text_primary': '#111827',
        'text_secondary': '#6B7280',
        'border': '#E5E7EB',
        'shadow_light': '#E8E8E8',  # Light shadow
        'shadow_medium': '#D1D5DB',  # Medium shadow
        'accent': '#8B5CF6',       # Purple accent
        'gradient_start': '#6366F1',
        'gradient_end': '#8B5CF6'
    }

    def __init__(self, root):
        self.root = root
        self.root.title("IT Ticket Email Generator • Modern Interface")
        self.root.geometry("1250x920")

        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1250
        window_height = 920
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure modern styling
        self.configure_styles()

        # Variables
        self.client_id = tk.StringVar()
        self.tenant_id = tk.StringVar()
        self.sender_email = tk.StringVar()
        self.recipient_email = tk.StringVar()
        self.claude_api_key = tk.StringVar()
        self.num_emails = tk.IntVar(value=5)
        self.writing_quality = tk.StringVar(value="basic")

        # Freshservice variables
        self.fs_domain = tk.StringVar()
        self.fs_api_key = tk.StringVar()
        self.fs_expected_group = tk.StringVar(value="IT Support Team")
        self.fs_wait_time = tk.IntVar(value=10)

        # State variables
        self.authenticated = False
        self.access_token = None
        self.categories = []
        self.priorities = []
        self.types = []
        self.content_gen = None
        self.email_sender = None
        self.ticket_counter = TicketCounter()
        self.fs_client = None
        self.fs_connected = False

        # Session file path
        self.session_file = os.path.join(os.getcwd(), ".session_cache.json")

        # Last batch data for verification
        self.last_batch_emails = []
        self.last_batch_start_time = None
        self.last_batch_log_file = None

        # Create GUI
        self.create_widgets()
        self.load_configuration()

        # Try to restore previous session (after widgets are created)
        self.root.after(100, self.restore_session)

    def configure_styles(self):
        """Configure modern ttk styles with shadows and improved design."""
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base

        # Configure background
        self.root.configure(bg=self.COLORS['background'])

        # Frame styles with shadow effect
        style.configure('Card.TFrame',
                       background=self.COLORS['surface'],
                       relief='flat',
                       borderwidth=0)
        style.configure('Main.TFrame', background=self.COLORS['background'])

        # Label styles - modern and elegant
        style.configure('Title.TLabel',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['primary'],
                       font=('Segoe UI', 24, 'bold'))
        style.configure('SectionTitle.TLabel',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 13, 'bold'))
        style.configure('Card.TLabel',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Info.TLabel',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_secondary'],
                       font=('Segoe UI', 9, 'italic'))

        # Button styles - modern with shadow effect
        style.configure('Primary.TButton',
                       background=self.COLORS['primary'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       focuscolor='none',
                       padding=(24, 14))
        style.map('Primary.TButton',
                 background=[('active', self.COLORS['primary_dark']),
                           ('disabled', '#D1D5DB')],
                 foreground=[('active', 'white'), ('disabled', '#9CA3AF')])

        style.configure('Success.TButton',
                       background=self.COLORS['success'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       focuscolor='none',
                       padding=(24, 14))
        style.map('Success.TButton',
                 background=[('active', self.COLORS['success_light']),
                           ('disabled', '#D1D5DB')],
                 foreground=[('active', 'white'), ('disabled', '#9CA3AF')])

        style.configure('Accent.TButton',
                       background=self.COLORS['accent'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       focuscolor='none',
                       padding=(20, 10))
        style.map('Accent.TButton',
                 background=[('active', '#7C3AED')],
                 foreground=[('active', 'white')])

        # Entry style - modern with subtle border
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='flat',
                       bordercolor=self.COLORS['border'],
                       padding=10)

        # Radiobutton style
        style.configure('Card.TRadiobutton',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_primary'],
                       font=('Segoe UI', 10))

        # Labelframe style - modern flat design
        style.configure('Card.TLabelframe',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       bordercolor=self.COLORS['border'])
        style.configure('Card.TLabelframe.Label',
                       background=self.COLORS['surface'],
                       foreground=self.COLORS['primary'],
                       font=('Segoe UI', 11, 'bold'))

        # Progressbar style - modern gradient-like
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.COLORS['primary'],
                       troughcolor='#E0E7FF',
                       borderwidth=0,
                       thickness=24)

    def create_card_with_shadow(self, parent, **kwargs):
        """Create a card frame with shadow effect."""
        # Shadow frame (slightly larger and offset)
        shadow_frame = tk.Frame(parent, bg=self.COLORS['shadow_medium'])

        # Actual card frame
        card_frame = ttk.Frame(shadow_frame, style='Card.TFrame', **kwargs)
        card_frame.pack(padx=(0, 3), pady=(0, 3), fill=tk.BOTH, expand=True)

        return shadow_frame, card_frame

    def create_widgets(self):
        # Create canvas with scrollbar for main content
        canvas_container = ttk.Frame(self.root, style='Main.TFrame')
        canvas_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        canvas_container.columnconfigure(0, weight=1)
        canvas_container.rowconfigure(0, weight=1)

        # Create canvas and scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)

        # Main container with padding
        main_frame = ttk.Frame(canvas, style='Main.TFrame', padding="35")

        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Update scroll region when content changes
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main_frame.bind("<Configure>", configure_scroll_region)

        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Update canvas window width when canvas is resized
        def on_canvas_configure(event):
            try:
                canvas.itemconfig(canvas_window, width=event.width)
            except:
                pass

        canvas.bind("<Configure>", on_canvas_configure)

        # Enable mousewheel scrolling anywhere in the window
        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass

        # Bind mousewheel to the root window so it works anywhere
        self.root.bind("<MouseWheel>", on_mousewheel)

        # Also bind to canvas for redundancy
        canvas.bind("<MouseWheel>", on_mousewheel)

        # Bind to main_frame and all its children recursively
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        # Store canvas reference for later use
        self.main_canvas = canvas

        # Initial binding to all existing widgets
        bind_mousewheel(main_frame)

        main_frame.columnconfigure(0, weight=1)

        row = 0

        # Header Card with gradient background effect
        header_shadow = tk.Frame(main_frame, bg=self.COLORS['shadow_medium'])
        header_shadow.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 25))

        # Gradient-like header (using primary color)
        header_card = tk.Frame(header_shadow, bg=self.COLORS['primary'], padx=0, pady=0)
        header_card.pack(padx=(0, 3), pady=(0, 3), fill=tk.BOTH, expand=True)
        header_card.columnconfigure(0, weight=1)

        # Content area within header
        header_content = ttk.Frame(header_card, style='Card.TFrame', padding="30")
        header_content.pack(fill=tk.BOTH, expand=True)
        header_content.columnconfigure(0, weight=1)

        # Title with icon and refresh button
        title_frame = ttk.Frame(header_content, style='Card.TFrame')
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(title_frame, text="📧 IT Ticket Email Generator",
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        # Refresh button on the right
        refresh_button = ttk.Button(title_frame, text="🔄 Reload Config",
                                   command=self.reload_modules,
                                   style='Primary.TButton')
        refresh_button.pack(side=tk.RIGHT, padx=(10, 0))

        subtitle_label = ttk.Label(header_content,
                                   text="Generate realistic test emails for IT support systems",
                                   style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        row += 1

        # Configuration Card with shadow
        config_shadow, config_card = self.create_card_with_shadow(main_frame, padding="25")
        config_shadow.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        config_card.columnconfigure(1, weight=1)

        config_row = 0

        # Section title
        ttk.Label(config_card, text="🔐 Configuration",
                 style='SectionTitle.TLabel').grid(row=config_row, column=0, columnspan=2,
                                                   sticky=tk.W, pady=(0, 15))
        config_row += 1

        # Azure subsection
        ttk.Label(config_card, text="Microsoft Azure", style='Card.TLabel',
                 font=('Segoe UI', 10, 'bold')).grid(row=config_row, column=0, columnspan=2,
                                                     sticky=tk.W, pady=(5, 10))
        config_row += 1

        ttk.Label(config_card, text="Client ID:", style='Card.TLabel').grid(row=config_row, column=0,
                                                                            sticky=tk.W, pady=8, padx=(0, 15))
        client_entry = ttk.Entry(config_card, textvariable=self.client_id, font=('Segoe UI', 10))
        client_entry.grid(row=config_row, column=1, sticky=(tk.W, tk.E), pady=8)
        config_row += 1

        ttk.Label(config_card, text="Tenant ID:", style='Card.TLabel').grid(row=config_row, column=0,
                                                                            sticky=tk.W, pady=8, padx=(0, 15))
        tenant_entry = ttk.Entry(config_card, textvariable=self.tenant_id, font=('Segoe UI', 10))
        tenant_entry.grid(row=config_row, column=1, sticky=(tk.W, tk.E), pady=8)
        config_row += 1

        ttk.Label(config_card, text="Sender Email:", style='Card.TLabel').grid(row=config_row, column=0,
                                                                               sticky=tk.W, pady=8, padx=(0, 15))
        sender_entry = ttk.Entry(config_card, textvariable=self.sender_email, font=('Segoe UI', 10))
        sender_entry.grid(row=config_row, column=1, sticky=(tk.W, tk.E), pady=8)
        config_row += 1

        ttk.Label(config_card, text="Recipient Email:", style='Card.TLabel').grid(row=config_row, column=0,
                                                                                  sticky=tk.W, pady=8, padx=(0, 15))
        recipient_entry = ttk.Entry(config_card, textvariable=self.recipient_email, font=('Segoe UI', 10))
        recipient_entry.grid(row=config_row, column=1, sticky=(tk.W, tk.E), pady=8)
        config_row += 1

        # Claude API subsection
        ttk.Label(config_card, text="Claude API", style='Card.TLabel',
                 font=('Segoe UI', 10, 'bold')).grid(row=config_row, column=0, columnspan=2,
                                                     sticky=tk.W, pady=(15, 10))
        config_row += 1

        ttk.Label(config_card, text="API Key:", style='Card.TLabel').grid(row=config_row, column=0,
                                                                          sticky=tk.W, pady=8, padx=(0, 15))
        api_entry = ttk.Entry(config_card, textvariable=self.claude_api_key, show="•", font=('Segoe UI', 10))
        api_entry.grid(row=config_row, column=1, sticky=(tk.W, tk.E), pady=8)
        config_row += 1

        # Authentication section
        auth_frame = ttk.Frame(config_card, style='Card.TFrame')
        auth_frame.grid(row=config_row, column=0, columnspan=2, pady=(15, 0))

        self.auth_button = ttk.Button(auth_frame, text="🔑 Authenticate", command=self.authenticate,
                                      style='Primary.TButton')
        self.auth_button.pack(side=tk.LEFT, padx=(0, 15))

        status_frame = tk.Frame(auth_frame, bg=self.COLORS['surface'],
                               highlightthickness=1, highlightbackground=self.COLORS['border'],
                               padx=12, pady=6)
        status_frame.pack(side=tk.LEFT)

        self.auth_status_icon = ttk.Label(status_frame, text="●", style='Card.TLabel',
                                          foreground=self.COLORS['error'], font=('Segoe UI', 16))
        self.auth_status_icon.pack(side=tk.LEFT, padx=(0, 8))

        self.auth_status = ttk.Label(status_frame, text="Not Authenticated", style='Card.TLabel',
                                     foreground=self.COLORS['error'], font=('Segoe UI', 10, 'bold'))
        self.auth_status.pack(side=tk.LEFT)

        row += 1

        # Freshservice Configuration Card with shadow
        fs_shadow, fs_card = self.create_card_with_shadow(main_frame, padding="25")
        fs_shadow.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        fs_card.columnconfigure(1, weight=1)

        fs_row = 0

        # Section title
        ttk.Label(fs_card, text="🔍 Freshservice Verification (Optional)",
                 style='SectionTitle.TLabel').grid(row=fs_row, column=0, columnspan=2,
                                                   sticky=tk.W, pady=(0, 10))
        fs_row += 1

        # Info label
        ttk.Label(fs_card, text="Configure Freshservice to verify ticket categorization after emails are sent",
                 style='Info.TLabel').grid(row=fs_row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        fs_row += 1

        # Freshservice Domain
        ttk.Label(fs_card, text="Freshservice Domain:", style='Card.TLabel').grid(row=fs_row, column=0,
                                                                                  sticky=tk.W, pady=8, padx=(0, 15))
        domain_entry = ttk.Entry(fs_card, textvariable=self.fs_domain, font=('Segoe UI', 10))
        domain_entry.grid(row=fs_row, column=1, sticky=(tk.W, tk.E), pady=8)
        fs_row += 1

        # API Key
        ttk.Label(fs_card, text="API Key:", style='Card.TLabel').grid(row=fs_row, column=0,
                                                                      sticky=tk.W, pady=8, padx=(0, 15))
        fs_api_entry = ttk.Entry(fs_card, textvariable=self.fs_api_key, show="•", font=('Segoe UI', 10))
        fs_api_entry.grid(row=fs_row, column=1, sticky=(tk.W, tk.E), pady=8)
        fs_row += 1

        # Info about group assignment
        info_label = ttk.Label(fs_card,
                              text="Note: Group assignment is tracked for AI learning (not pass/fail)",
                              style='Info.TLabel')
        info_label.grid(row=fs_row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        fs_row += 1

        # Wait Time
        ttk.Label(fs_card, text="Verification Wait Time:", style='Card.TLabel').grid(row=fs_row, column=0,
                                                                                     sticky=tk.W, pady=8, padx=(0, 15))
        wait_frame = ttk.Frame(fs_card, style='Card.TFrame')
        wait_frame.grid(row=fs_row, column=1, sticky=tk.W, pady=8)

        wait_spinbox = ttk.Spinbox(wait_frame, from_=1, to=30, textvariable=self.fs_wait_time,
                                   width=5, font=('Segoe UI', 10))
        wait_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(wait_frame, text="minutes", style='Info.TLabel').pack(side=tk.LEFT)
        fs_row += 1

        # Test Connection Button
        fs_button_frame = ttk.Frame(fs_card, style='Card.TFrame')
        fs_button_frame.grid(row=fs_row, column=0, columnspan=2, pady=(15, 0))

        self.fs_test_button = ttk.Button(fs_button_frame, text="🔗 Test Connection",
                                        command=self.test_freshservice_connection,
                                        style='Primary.TButton')
        self.fs_test_button.pack(side=tk.LEFT, padx=(0, 15))

        fs_status_frame = tk.Frame(fs_button_frame, bg=self.COLORS['surface'],
                                  highlightthickness=1, highlightbackground=self.COLORS['border'],
                                  padx=12, pady=6)
        fs_status_frame.pack(side=tk.LEFT)

        self.fs_status_icon = ttk.Label(fs_status_frame, text="●", style='Card.TLabel',
                                        foreground=self.COLORS['text_secondary'], font=('Segoe UI', 16))
        self.fs_status_icon.pack(side=tk.LEFT, padx=(0, 8))

        self.fs_status = ttk.Label(fs_status_frame, text="Not Configured", style='Card.TLabel',
                                   foreground=self.COLORS['text_secondary'], font=('Segoe UI', 10, 'bold'))
        self.fs_status.pack(side=tk.LEFT)

        row += 1

        # Generation Settings Card with shadow
        gen_shadow, gen_card = self.create_card_with_shadow(main_frame, padding="25")
        gen_shadow.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        gen_card.columnconfigure(1, weight=1)

        gen_row = 0

        # Section title
        ttk.Label(gen_card, text="⚙️ Generation Settings",
                 style='SectionTitle.TLabel').grid(row=gen_row, column=0, columnspan=2,
                                                   sticky=tk.W, pady=(0, 15))
        gen_row += 1

        # Number of emails
        ttk.Label(gen_card, text="Number of Emails:", style='Card.TLabel').grid(row=gen_row, column=0,
                                                                                sticky=tk.W, pady=8, padx=(0, 15))
        email_frame = ttk.Frame(gen_card, style='Card.TFrame')
        email_frame.grid(row=gen_row, column=1, sticky=tk.W, pady=8)

        spinbox = ttk.Spinbox(email_frame, from_=1, to=1000, textvariable=self.num_emails,
                             width=10, font=('Segoe UI', 10))
        spinbox.pack(side=tk.LEFT, padx=(0, 10))

        self.next_ticket_label = ttk.Label(email_frame,
                                          text=f"Next ticket: #{self.ticket_counter.get_current()}",
                                          style='Info.TLabel')
        self.next_ticket_label.pack(side=tk.LEFT)
        gen_row += 1

        # Writing quality
        ttk.Label(gen_card, text="Writing Quality:", style='Card.TLabel').grid(row=gen_row, column=0,
                                                                               sticky=tk.W, pady=12, padx=(0, 15))
        quality_frame = ttk.Frame(gen_card, style='Card.TFrame')
        quality_frame.grid(row=gen_row, column=1, sticky=tk.W, pady=12)

        ttk.Radiobutton(quality_frame, text="📝 Basic (7th grade)", variable=self.writing_quality,
                       value="basic", style='Card.TRadiobutton').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(quality_frame, text="📄 Realistic (10th grade)", variable=self.writing_quality,
                       value="realistic", style='Card.TRadiobutton').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(quality_frame, text="✨ Polished", variable=self.writing_quality,
                       value="polished", style='Card.TRadiobutton').pack(side=tk.LEFT)
        gen_row += 1

        # Generate Button
        button_frame = ttk.Frame(gen_card, style='Card.TFrame')
        button_frame.grid(row=gen_row, column=0, columnspan=2, pady=(15, 0))

        self.generate_button = ttk.Button(button_frame, text="🚀 Generate & Send Emails",
                                         command=self.generate_emails, state=tk.DISABLED,
                                         style='Success.TButton')
        self.generate_button.pack()

        row += 1

        # Progress Card with shadow
        progress_shadow, progress_card = self.create_card_with_shadow(main_frame, padding="25")
        progress_shadow.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 25))
        progress_card.columnconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)

        prog_row = 0

        # Section title
        ttk.Label(progress_card, text="📊 Progress & Logs",
                 style='SectionTitle.TLabel').grid(row=prog_row, column=0, sticky=tk.W, pady=(0, 15))
        prog_row += 1

        # Status label
        self.status_label = ttk.Label(progress_card, text="Ready to start", style='Card.TLabel')
        self.status_label.grid(row=prog_row, column=0, sticky=tk.W, pady=(0, 10))
        prog_row += 1

        # Progress bar
        self.progress = ttk.Progressbar(progress_card, mode='determinate',
                                       style='Custom.Horizontal.TProgressbar')
        self.progress.grid(row=prog_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        prog_row += 1

        # Log output
        log_container = ttk.LabelFrame(progress_card, text="Activity Log", style='Card.TLabelframe',
                                      padding="10")
        log_container.grid(row=prog_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        progress_card.rowconfigure(prog_row, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_container, height=12, wrap=tk.WORD,
                                                  font=('Consolas', 9),
                                                  bg='#F9FAFB',
                                                  relief='flat',
                                                  borderwidth=1,
                                                  highlightthickness=1,
                                                  highlightbackground=self.COLORS['border'],
                                                  highlightcolor=self.COLORS['primary_light'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        prog_row += 1

        # Buttons
        button_container = ttk.Frame(progress_card, style='Card.TFrame')
        button_container.grid(row=prog_row, column=0, pady=(0, 0))

        self.view_logs_button = ttk.Button(button_container, text="📁 View Log Files",
                                          command=self.view_logs, style='Primary.TButton')
        self.view_logs_button.pack(side=tk.LEFT, padx=(0, 10))

        self.verify_button = ttk.Button(button_container, text="🔍 Verify Tickets",
                                       command=self.verify_tickets, state=tk.DISABLED,
                                       style='Success.TButton')
        self.verify_button.pack(side=tk.LEFT)

        prog_row += 1

        # Verification status (hidden initially)
        self.verify_status_frame = ttk.Frame(progress_card, style='Card.TFrame')
        self.verify_status_frame.grid(row=prog_row, column=0, pady=(10, 0))
        self.verify_status_frame.grid_remove()  # Hidden initially

        self.verify_status_label = ttk.Label(self.verify_status_frame, text="",
                                            style='Card.TLabel')
        self.verify_status_label.pack()

    def load_configuration(self):
        """Load configuration from environment files."""
        try:
            env_vars = load_env_file()

            # Set variables if found
            if "AZURE_CLIENT_ID" in env_vars:
                self.client_id.set(env_vars["AZURE_CLIENT_ID"])
            if "AZURE_TENANT_ID" in env_vars:
                self.tenant_id.set(env_vars["AZURE_TENANT_ID"])
            if "SENDER_EMAIL" in env_vars:
                self.sender_email.set(env_vars["SENDER_EMAIL"])
            if "RECIPIENT_EMAIL" in env_vars:
                self.recipient_email.set(env_vars["RECIPIENT_EMAIL"])
            if "CLAUDE_API_KEY" in env_vars:
                self.claude_api_key.set(env_vars["CLAUDE_API_KEY"])

            # Load Freshservice configuration (optional)
            if "FRESHSERVICE_DOMAIN" in env_vars:
                self.fs_domain.set(env_vars["FRESHSERVICE_DOMAIN"])
            if "FRESHSERVICE_API_KEY" in env_vars:
                self.fs_api_key.set(env_vars["FRESHSERVICE_API_KEY"])
            if "FRESHSERVICE_EXPECTED_GROUP" in env_vars:
                self.fs_expected_group.set(env_vars["FRESHSERVICE_EXPECTED_GROUP"])
            if "FRESHSERVICE_VERIFY_WAIT_MINUTES" in env_vars:
                try:
                    wait_time = int(env_vars["FRESHSERVICE_VERIFY_WAIT_MINUTES"])
                    self.fs_wait_time.set(wait_time)
                except ValueError:
                    pass

            self.log("Configuration loaded from .env file")

            # Load data files
            self.categories = read_categories()
            priorities_data = read_priorities_and_types()
            self.priorities = priorities_data['priorities']
            self.types = priorities_data['types']

            self.log(f"Loaded {len(self.categories)} categories, {len(self.priorities)} priorities, {len(self.types)} types")

        except Exception as e:
            self.log(f"Error loading configuration: {str(e)}", "error")

    def log(self, message, level="info"):
        """Add message to log output with color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Configure tags for colored text
        self.log_text.tag_config("timestamp", foreground=self.COLORS['text_secondary'])
        self.log_text.tag_config("info", foreground=self.COLORS['primary'])
        self.log_text.tag_config("error", foreground=self.COLORS['error'])
        self.log_text.tag_config("ok", foreground=self.COLORS['success'])
        self.log_text.tag_config("warning", foreground=self.COLORS['warning'])

        # Determine icon and tag based on level
        if level == "error":
            icon = "❌"
            tag = "error"
        elif level == "ok":
            icon = "✓"
            tag = "ok"
        elif level == "warning":
            icon = "⚠️"
            tag = "warning"
        else:
            icon = "ℹ️"
            tag = "info"

        # Insert timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        # Insert icon and message
        self.log_text.insert(tk.END, f"{icon} {message}\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def authenticate(self):
        """Authenticate with Microsoft Graph API."""
        # Validate inputs
        if not validate_credentials(self.client_id.get(), self.tenant_id.get()):
            messagebox.showerror("Error", "Invalid Azure credentials format")
            return

        if '@' not in self.sender_email.get() or '@' not in self.recipient_email.get():
            messagebox.showerror("Error", "Invalid email format")
            return

        if not validate_api_key(self.claude_api_key.get()):
            messagebox.showerror("Error", "Invalid Claude API key format")
            return

        # Disable button during auth
        self.auth_button.config(state=tk.DISABLED)
        self.status_label.config(text="Authenticating... (check terminal for instructions)")

        def auth_thread():
            try:
                self.log("Starting authentication...")
                self.log("IMPORTANT: Do NOT close this window or press Ctrl+C in the terminal!", "info")
                self.log("Follow the authentication instructions in the terminal...", "info")
                authenticator = GraphAuthenticator(self.client_id.get(), self.tenant_id.get())
                self.access_token = authenticator.authenticate_device_flow()

                # Initialize components
                self.email_sender = EmailSender(self.access_token, self.sender_email.get())
                self.content_gen = ContentGenerator(
                    self.claude_api_key.get(),
                    writing_quality=self.writing_quality.get()
                )

                # Test connection
                self.log("Testing Microsoft Graph API connection...")
                if self.email_sender.test_connection():
                    self.authenticated = True
                    self.root.after(0, lambda: self.auth_status_icon.config(foreground=self.COLORS['success']))
                    self.root.after(0, lambda: self.auth_status.config(
                        text="Authenticated ✓",
                        foreground=self.COLORS['success']))
                    self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.status_label.config(text="Ready to generate emails"))
                    self.log("Authentication successful", "ok")

                    # Save session for next time
                    self.save_session()
                else:
                    raise Exception("Failed to connect to Microsoft Graph API")

            except KeyboardInterrupt:
                self.log("Authentication cancelled by user", "error")
                self.root.after(0, lambda: self.status_label.config(text="Authentication cancelled"))
            except Exception as e:
                error_msg = str(e)
                self.log(f"Authentication failed: {error_msg}", "error")
                self.root.after(0, lambda: messagebox.showerror("Authentication Error", error_msg))
            finally:
                self.root.after(0, lambda: self.auth_button.config(state=tk.NORMAL))

        # Run in separate thread to avoid blocking GUI
        # Use daemon=False to ensure authentication completes even if window is closed
        auth_t = threading.Thread(target=auth_thread, daemon=False)
        auth_t.start()

    def generate_emails(self):
        """Generate and send emails."""
        if not self.authenticated:
            messagebox.showerror("Error", "Please authenticate first")
            return

        num_emails = self.num_emails.get()
        if num_emails < 1 or num_emails > 1000:
            messagebox.showerror("Error", "Number of emails must be between 1 and 1000")
            return

        # Confirm
        if not messagebox.askyesno("Confirm",
                                   f"Generate and send {num_emails} emails?\n\n"
                                   f"From: {self.sender_email.get()}\n"
                                   f"To: {self.recipient_email.get()}\n"
                                   f"Writing Quality: {self.writing_quality.get()}"):
            return

        # Disable button during generation
        self.generate_button.config(state=tk.DISABLED)
        self.progress['value'] = 0

        def generate_thread():
            try:
                # Save batch start time for verification
                self.last_batch_start_time = datetime.now()
                self.last_batch_emails = []
                self.last_batch_log_file = None

                # Update content generator with current writing quality
                self.content_gen.writing_quality = self.writing_quality.get()

                # Get ticket number range
                start_ticket, end_ticket = self.ticket_counter.get_range(num_emails)

                # Generate distribution
                distribution = generate_distribution(num_emails, self.categories,
                                                    self.priorities, self.types)
                priority_counts, type_counts = calculate_distribution_stats(distribution)

                # Create logger
                logger = TicketLogger()
                log_file = logger.start_log(
                    self.client_id.get(), self.tenant_id.get(),
                    self.sender_email.get(), self.recipient_email.get(),
                    self.claude_api_key.get(), num_emails
                )
                self.last_batch_log_file = log_file

                self.log(f"Log file created: {log_file}", "ok")
                self.log(f"Generating {num_emails} emails (Tickets #{start_ticket} to #{end_ticket})...", "info")

                # Generation phase
                emails_to_send = []
                generation_errors = 0

                for i, ticket in enumerate(distribution, 1):
                    ticket_number = start_ticket + i - 1
                    try:
                        self.root.after(0, lambda i=i: self.status_label.config(
                            text=f"Generating email {i} of {num_emails}..."))

                        subject, description = self.content_gen.generate_email_content(
                            category=ticket['category'],
                            subcategory=ticket['subcategory'],
                            item=ticket['item'],
                            priority=ticket['priority'],
                            ticket_type=ticket['type'],
                            ticket_number=ticket_number
                        )

                        # Build full category name
                        category_full = ticket['category']
                        if ticket['subcategory']:
                            category_full += f" > {ticket['subcategory']}"
                        if ticket['item']:
                            category_full += f" > {ticket['item']}"

                        emails_to_send.append({
                            'number': ticket_number,
                            'category': category_full,
                            'priority': ticket['priority'],
                            'type': ticket['type'],
                            'subject': subject,
                            'description': description
                        })

                        self.log(f"Generated ticket #{ticket_number}: {subject[:50]}...", "ok")

                        # Update progress
                        progress_val = (i / num_emails) * 50  # First 50% for generation
                        self.root.after(0, lambda v=progress_val: self.progress.config(value=v))

                    except Exception as e:
                        self.log(f"Failed to generate email {i}: {str(e)}", "error")
                        generation_errors += 1

                        # Build full category name
                        category_full = ticket['category']
                        if ticket['subcategory']:
                            category_full += f" > {ticket['subcategory']}"
                        if ticket['item']:
                            category_full += f" > {ticket['item']}"

                        logger.log_email(
                            email_number=i,
                            category=category_full,
                            ticket_type=ticket['type'],
                            priority=ticket['priority'],
                            subject="[GENERATION FAILED]",
                            description=f"Error: {str(e)}",
                            success=False,
                            error=str(e)
                        )

                # Sending phase
                self.log(f"\nSending {len(emails_to_send)} emails...")
                success_count = 0
                failure_count = 0

                for i, email in enumerate(emails_to_send):
                    try:
                        self.root.after(0, lambda e=email: self.status_label.config(
                            text=f"Sending email {e['number']} of {num_emails}..."))

                        # Send email with delay for subsequent emails
                        if i > 0:
                            result = self.email_sender.send_email_with_delay(
                                to_email=self.recipient_email.get(),
                                subject=email['subject'],
                                body=email['description'],
                                delay_seconds=10,
                                show_countdown=False
                            )
                        else:
                            result = self.email_sender.send_email(
                                to_email=self.recipient_email.get(),
                                subject=email['subject'],
                                body=email['description']
                            )

                        if result['success']:
                            self.log(f"Sent ticket #{email['number']}: {email['subject'][:50]}...", "ok")
                            success_count += 1
                            logger.log_email(
                                email_number=email['number'],
                                category=email['category'],
                                ticket_type=email['type'],
                                priority=email['priority'],
                                subject=email['subject'],
                                description=email['description'],
                                success=True
                            )
                        else:
                            self.log(f"Failed to send email {email['number']}: {result['error']}", "error")
                            failure_count += 1
                            logger.log_email(
                                email_number=email['number'],
                                category=email['category'],
                                ticket_type=email['type'],
                                priority=email['priority'],
                                subject=email['subject'],
                                description=email['description'],
                                success=False,
                                error=result['error']
                            )

                        # Update progress (50-100%)
                        progress_val = 50 + ((i + 1) / len(emails_to_send)) * 50
                        self.root.after(0, lambda v=progress_val: self.progress.config(value=v))

                    except Exception as e:
                        self.log(f"Error sending email {email['number']}: {str(e)}", "error")
                        failure_count += 1
                        logger.log_email(
                            email_number=email['number'],
                            category=email['category'],
                            ticket_type=email['type'],
                            priority=email['priority'],
                            subject=email['subject'],
                            description=email['description'],
                            success=False,
                            error=str(e)
                        )

                # Finalize log
                token_stats = self.content_gen.get_token_stats()
                estimated_cost = self.content_gen.get_estimated_cost()

                logger.finalize_log(
                    total_sent=len(emails_to_send),
                    success_count=success_count,
                    failure_count=failure_count,
                    distribution=priority_counts,
                    type_distribution=type_counts,
                    estimated_cost=estimated_cost,
                    token_stats=token_stats
                )

                # Summary
                self.log(f"\n{'─'*50}", "info")
                self.log(f"BATCH COMPLETE - SUMMARY", "ok")
                self.log(f"{'─'*50}", "info")
                self.log(f"Total Generated: {len(emails_to_send)}", "info")
                self.log(f"Successfully Sent: {success_count}", "ok" if success_count > 0 else "info")
                if failure_count > 0:
                    self.log(f"Failed: {failure_count}", "error")
                self.log(f"Total Tokens: {token_stats['total_tokens']:,}", "info")
                self.log(f"Estimated Cost: ${estimated_cost:.4f}", "info")
                self.log(f"Log file: {log_file}", "info")

                # Save batch data for verification
                self.last_batch_emails = emails_to_send.copy()

                # Save ticket counter
                self.ticket_counter.finalize()
                self.root.after(0, lambda: self.next_ticket_label.config(
                    text=f"(Next ticket: #{self.ticket_counter.get_current()})"))

                # Remind about verification if Freshservice is configured
                if self.fs_connected and success_count > 0:
                    wait_time = self.fs_wait_time.get()
                    self.log(f"\n🔍 Verification available - wait {wait_time} min for best results, then click 'Verify Tickets'", "info")

                self.root.after(0, lambda: self.status_label.config(text="✓ Batch completed successfully!"))
                self.root.after(0, lambda: messagebox.showinfo("✓ Batch Complete",
                    f"Successfully completed email generation!\n\n"
                    f"📊 Statistics:\n"
                    f"  • Tickets: #{start_ticket} to #{end_ticket}\n"
                    f"  • Generated: {len(emails_to_send)}\n"
                    f"  • Sent: {success_count}\n" +
                    (f"  • Failed: {failure_count}\n" if failure_count > 0 else "") +
                    f"\n💰 Cost: ${estimated_cost:.4f}\n"
                    f"\n📁 Log: {os.path.basename(log_file)}" +
                    (f"\n\n🔍 Verify button enabled! Wait {self.fs_wait_time.get()} min for best results." if self.fs_connected and success_count > 0 else "")))

            except Exception as e:
                self.log(f"Error: {str(e)}", "error")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.progress.config(value=0))

        # Run in separate thread
        threading.Thread(target=generate_thread, daemon=True).start()

    def test_freshservice_connection(self):
        """Test Freshservice API connection."""
        domain = self.fs_domain.get().strip()
        api_key = self.fs_api_key.get().strip()

        if not domain or not api_key:
            messagebox.showerror("Error", "Please enter Freshservice domain and API key")
            return

        if not validate_freshservice_credentials(domain, api_key):
            messagebox.showerror("Error", "Invalid Freshservice credentials format")
            return

        # Test connection
        self.fs_test_button.config(state=tk.DISABLED)
        self.fs_status.config(text="Testing...")

        def test_thread():
            try:
                client = FreshserviceClient(domain, api_key)
                if client.test_connection():
                    self.fs_client = client
                    self.fs_connected = True

                    # Update UI elements
                    def update_ui():
                        self.fs_status_icon.config(foreground=self.COLORS['success'])
                        self.fs_status.config(text="Connected ✓", foreground=self.COLORS['success'])
                        self.verify_button.config(state=tk.NORMAL)

                    self.root.after(0, update_ui)
                    self.log("Freshservice connection successful", "ok")
                    self.log("🔍 Verify button enabled - you can verify any of your last 10 tickets!", "ok")

                    # Save session for next time
                    self.save_session()
                else:
                    raise Exception("Connection test failed")

            except Exception as e:
                self.fs_connected = False
                self.log(f"Freshservice connection failed: {str(e)}", "error")
                self.root.after(0, lambda: self.fs_status_icon.config(foreground=self.COLORS['error']))
                self.root.after(0, lambda: self.fs_status.config(
                    text="Connection Failed",
                    foreground=self.COLORS['error']))
                self.root.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
            finally:
                self.root.after(0, lambda: self.fs_test_button.config(state=tk.NORMAL))

        threading.Thread(target=test_thread, daemon=True).start()

    def show_ticket_selection_dialog(self, current_ticket):
        """
        Show a dialog to select which tickets to verify.

        Args:
            current_ticket: The most recent ticket number

        Returns:
            List of ticket numbers to verify, or None if cancelled
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Tickets to Verify")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.COLORS['background'])

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")

        result = {'selected': None}

        # Main container with padding
        container = ttk.Frame(dialog, style='Main.TFrame', padding="25")
        container.pack(fill=tk.BOTH, expand=True)

        # Header card with shadow
        header_shadow = tk.Frame(container, bg=self.COLORS['shadow_medium'])
        header_shadow.pack(fill=tk.X, pady=(0, 20))

        header_card = tk.Frame(header_shadow, bg=self.COLORS['primary'], padx=0, pady=0)
        header_card.pack(padx=(0, 3), pady=(0, 3), fill=tk.BOTH)

        header_content = ttk.Frame(header_card, style='Card.TFrame', padding="25")
        header_content.pack(fill=tk.BOTH)

        # Title with icon
        title_label = ttk.Label(header_content, text="🔍 Select Tickets to Verify",
                                font=('Segoe UI', 18, 'bold'),
                                foreground=self.COLORS['primary'],
                                background=self.COLORS['surface'])
        title_label.pack(pady=(0, 10))

        # Info
        last_10_start = max(1, current_ticket - 9)
        info_text = f"Most recent ticket: #{current_ticket}\nLast 10 tickets: #{last_10_start} to #{current_ticket}"
        info_label = ttk.Label(header_content, text=info_text,
                              font=('Segoe UI', 10),
                              foreground=self.COLORS['text_secondary'],
                              background=self.COLORS['surface'],
                              justify=tk.CENTER)
        info_label.pack()

        # Quick selection card
        quick_shadow, quick_card = self.create_card_with_shadow(container, padding="20")
        quick_shadow.pack(fill=tk.X, pady=(0, 20))

        quick_title = ttk.Label(quick_card, text="⚡ Quick Select",
                               font=('Segoe UI', 12, 'bold'),
                               foreground=self.COLORS['text_primary'],
                               background=self.COLORS['surface'])
        quick_title.pack(anchor=tk.W, pady=(0, 15))

        def select_all_10():
            tickets = list(range(last_10_start, current_ticket + 1))
            result['selected'] = tickets
            dialog.destroy()

        def select_last_5():
            last_5_start = max(1, current_ticket - 4)
            tickets = list(range(last_5_start, current_ticket + 1))
            result['selected'] = tickets
            dialog.destroy()

        # Quick selection buttons
        all_10_btn = ttk.Button(quick_card,
                                text=f"Check All 10 Tickets (#{last_10_start} - #{current_ticket})",
                                command=select_all_10,
                                style='Primary.TButton')
        all_10_btn.pack(fill=tk.X, pady=(0, 10))

        last_5_start = max(1, current_ticket - 4)
        last_5_btn = ttk.Button(quick_card,
                               text=f"Check Last 5 Tickets (#{last_5_start} - #{current_ticket})",
                               command=select_last_5,
                               style='Accent.TButton')
        last_5_btn.pack(fill=tk.X)

        # Custom selection card
        custom_shadow, custom_card = self.create_card_with_shadow(container, padding="20")
        custom_shadow.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        custom_title = ttk.Label(custom_card, text="📋 Custom Selection",
                                font=('Segoe UI', 12, 'bold'),
                                foreground=self.COLORS['text_primary'],
                                background=self.COLORS['surface'])
        custom_title.pack(anchor=tk.W, pady=(0, 10))

        custom_info = ttk.Label(custom_card,
                               text="Select specific tickets to verify:",
                               font=('Segoe UI', 9),
                               foreground=self.COLORS['text_secondary'],
                               background=self.COLORS['surface'])
        custom_info.pack(anchor=tk.W, pady=(0, 15))

        # Checkboxes container with styled border
        checkbox_container = tk.Frame(custom_card,
                                     bg='#F9FAFB',
                                     highlightthickness=1,
                                     highlightbackground=self.COLORS['border'])
        checkbox_container.pack(fill=tk.BOTH, expand=True)

        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(checkbox_container,
                          bg='#F9FAFB',
                          highlightthickness=0,
                          height=200)
        scrollbar = ttk.Scrollbar(checkbox_container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='#F9FAFB')

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 5))

        # Create checkboxes with improved styling
        checkbox_vars = {}
        for i in range(last_10_start, current_ticket + 1):
            var = tk.BooleanVar(value=False)
            checkbox_vars[i] = var

            # Create a frame for each checkbox row
            cb_frame = tk.Frame(scrollable, bg='#F9FAFB')
            cb_frame.pack(fill=tk.X, pady=3)

            cb = ttk.Checkbutton(cb_frame,
                                text=f"Ticket #{i}",
                                variable=var,
                                style='Card.TRadiobutton')
            cb.pack(anchor=tk.W, padx=5)

        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)

        # Bottom action buttons
        bottom_shadow, bottom_card = self.create_card_with_shadow(container, padding="15")
        bottom_shadow.pack(fill=tk.X)

        button_container = ttk.Frame(bottom_card, style='Card.TFrame')
        button_container.pack()

        def verify_selected():
            selected = [num for num, var in checkbox_vars.items() if var.get()]
            if not selected:
                messagebox.showwarning("No Selection",
                                      "Please select at least one ticket to verify.",
                                      parent=dialog)
                return
            result['selected'] = sorted(selected)
            dialog.destroy()

        def cancel():
            dialog.destroy()

        verify_btn = ttk.Button(button_container,
                               text="✓ Verify Selected Tickets",
                               command=verify_selected,
                               style='Success.TButton')
        verify_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = ttk.Button(button_container,
                               text="Cancel",
                               command=cancel,
                               style='Primary.TButton')
        cancel_btn.pack(side=tk.LEFT)

        # Wait for dialog to close
        self.root.wait_window(dialog)

        return result['selected']

    def verify_tickets(self):
        """Verify tickets in Freshservice."""
        if not self.fs_connected or not self.fs_client:
            messagebox.showerror("Error", "Please test Freshservice connection first")
            return

        # Get the last 10 tickets from ticket counter
        # get_current() returns the NEXT ticket number, so we need to subtract 1 to get the last generated
        current_ticket = self.ticket_counter.get_current() - 1

        if current_ticket <= 0:
            messagebox.showinfo("No Tickets", "No tickets have been generated yet.")
            return

        # Show ticket selection dialog
        selected_tickets = self.show_ticket_selection_dialog(current_ticket)

        if not selected_tickets:
            return  # User cancelled

        # Try to load email data from log files for selected tickets
        self.log(f"Loading email data for {len(selected_tickets)} ticket(s)...", "info")
        batch_emails = self.load_email_data_from_logs(selected_tickets)

        if batch_emails:
            self.last_batch_emails = batch_emails
            self.log(f"Loaded full email data for {len(batch_emails)} ticket(s)", "ok")
        else:
            # Fallback: create minimal batch data (discovery mode)
            self.last_batch_emails = [{'number': num, 'subject': f'[TEST-TKT-{num}]'} for num in selected_tickets]
            self.log(f"No log files found - using discovery mode", "info")

        self.last_batch_start_time = datetime.now() - timedelta(hours=24)  # Search last 24 hours
        self.log(f"Verifying {len(selected_tickets)} ticket(s): {selected_tickets}", "info")

        # Run verification
        self.verify_button.config(state=tk.DISABLED)
        self.verify_status_frame.grid()
        self.verify_status_label.config(text="⏳ Verifying tickets in Freshservice...")

        def verify_thread():
            try:
                self.log("Starting ticket verification...", "info")

                # Create verifier
                verifier = TicketVerifier(self.fs_client)

                # Run verification (group is tracked but not used for pass/fail)
                verification_data = verifier.verify_batch(
                    self.last_batch_emails,
                    self.recipient_email.get(),
                    self.last_batch_start_time,
                    None,  # No expected group - AI is learning
                    self.sender_email.get()  # Sender becomes the Freshservice requester
                )

                # Create verification report
                v_logger = VerificationLogger()
                report_file = v_logger.create_verification_report(
                    verification_data,
                    self.recipient_email.get(),
                    self.fs_domain.get()
                )

                # Update UI with results
                summary = verification_data['summary']
                self.root.after(0, lambda: self.verify_status_label.config(
                    text=f"✓ Verification Complete: {summary['passed']}/{verification_data['total_found']} "
                         f"passed ({summary['pass_rate']:.1f}%)"))

                # Log summary
                self.log(f"\n{'─'*50}", "info")
                self.log(f"VERIFICATION RESULTS", "ok")
                self.log(f"{'─'*50}", "info")
                self.log(f"Found: {verification_data['total_found']}/{verification_data['total_sent']}", "info")
                self.log(f"Passed: {summary['passed']}", "ok" if summary['passed'] > 0 else "info")
                self.log(f"Failed: {summary['failed']}", "error" if summary['failed'] > 0 else "info")
                self.log(f"Success Rate: {summary['pass_rate']:.1f}%", "ok" if summary['pass_rate'] >= 80 else "warning")
                self.log(f"Report saved: {report_file}", "ok")

                # Show detailed results dialog
                self.root.after(0, lambda: self._show_verification_results(verification_data, report_file))

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.log(f"Verification error: {str(e)}", "error")
                self.log(f"Error details: {error_details}", "error")
                self.root.after(0, lambda: self.verify_status_label.config(text=f"✗ Verification Failed"))
                self.root.after(0, lambda: messagebox.showerror("Verification Error", f"{str(e)}\n\nSee console for details"))
            finally:
                self.root.after(0, lambda: self.verify_button.config(state=tk.NORMAL))

        threading.Thread(target=verify_thread, daemon=True).start()

    def _show_verification_results(self, verification_data: dict, report_file: str):
        """Show verification results in a detailed window."""
        summary = verification_data['summary']
        results = verification_data['results']

        # Create new window for results
        results_window = tk.Toplevel(self.root)
        results_window.title("Freshservice Verification Results")
        results_window.geometry("1200x800")
        results_window.configure(bg=self.COLORS['background'])

        # Main container with scrollbar
        container = ttk.Frame(results_window, style='Card.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Canvas for scrolling
        canvas = tk.Canvas(container, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="✓ Freshservice Verification Complete",
            font=("Segoe UI", 18, "bold"),
            foreground=self.COLORS['success'],
            background=self.COLORS['surface']
        )
        title_label.pack()

        # Summary Statistics Card
        summary_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="15")
        summary_card.pack(fill=tk.X, pady=(0, 15))

        summary_title = ttk.Label(
            summary_card,
            text="📊 Summary Statistics",
            font=("Segoe UI", 12, "bold"),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface']
        )
        summary_title.pack(anchor=tk.W, pady=(0, 10))

        summary_text = f"""Total Emails Sent: {verification_data['total_sent']}
Tickets Found: {verification_data['total_found']}
Tickets Not Found: {verification_data['total_not_found']}

✓ Passed: {summary['passed']}
✗ Failed: {summary['failed']}
Success Rate: {summary['pass_rate']:.1f}%"""

        summary_label = ttk.Label(
            summary_card,
            text=summary_text,
            font=("Consolas", 10),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface'],
            justify=tk.LEFT
        )
        summary_label.pack(anchor=tk.W)

        # Field Accuracy Card
        accuracy_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="15")
        accuracy_card.pack(fill=tk.X, pady=(0, 15))

        accuracy_title = ttk.Label(
            accuracy_card,
            text="📋 Field Accuracy",
            font=("Segoe UI", 12, "bold"),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface']
        )
        accuracy_title.pack(anchor=tk.W, pady=(0, 10))

        accuracy_text = ""
        for field, stats in summary['field_stats'].items():
            if field == 'group_assignments':
                continue
            # Make sure stats is a dict with the expected keys
            if isinstance(stats, dict) and 'total' in stats and 'correct' in stats and 'percentage' in stats:
                if stats['total'] > 0:
                    field_name = field.replace('_', ' ').title()
                    accuracy_text += f"{field_name:<20} {stats['correct']}/{stats['total']} ({stats['percentage']:.1f}%)\n"

        accuracy_label = ttk.Label(
            accuracy_card,
            text=accuracy_text,
            font=("Consolas", 10),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface'],
            justify=tk.LEFT
        )
        accuracy_label.pack(anchor=tk.W)

        # Group Assignments Card (Informational)
        if 'group_assignments' in summary['field_stats']:
            group_data = summary['field_stats']['group_assignments']
            if isinstance(group_data, dict) and group_data:
                group_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="15")
                group_card.pack(fill=tk.X, pady=(0, 15))

                group_title = ttk.Label(
                    group_card,
                    text="ℹ Group Assignment Distribution (AI Learning)",
                    font=("Segoe UI", 12, "bold"),
                    foreground=self.COLORS['text_primary'],
                    background=self.COLORS['surface']
                )
                group_title.pack(anchor=tk.W, pady=(0, 10))

                group_text = ""
                try:
                    for group_name, count in sorted(group_data.items()):
                        group_text += f"{group_name:<40} {count} tickets\n"
                except Exception as e:
                    group_text = f"Error displaying group assignments: {str(e)}\n"

                group_label = ttk.Label(
                    group_card,
                    text=group_text,
                    font=("Consolas", 10),
                    foreground=self.COLORS['text_primary'],
                    background=self.COLORS['surface'],
                    justify=tk.LEFT
                )
                group_label.pack(anchor=tk.W)

        # Detailed Ticket Results
        details_title = ttk.Label(
            scrollable_frame,
            text="📝 Detailed Ticket Verification",
            font=("Segoe UI", 14, "bold"),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface'],
            padding=(0, 10)
        )
        details_title.pack(anchor=tk.W)

        # Each ticket result
        for result in results:
            ticket_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="15")
            ticket_card.pack(fill=tk.X, pady=(0, 10))

            # Ticket header
            status = result['status']
            overall = result['overall_result']

            if status == 'NOT_FOUND':
                status_icon = "⚠"
                status_text = "NOT FOUND"
                status_color = self.COLORS['warning']
            elif overall == 'PASS':
                status_icon = "✓"
                status_text = "PASS"
                status_color = self.COLORS['success']
            else:
                status_icon = "✗"
                status_text = f"FAIL ({result['mismatch_count']} mismatches)"
                status_color = self.COLORS['error']

            ticket_header = ttk.Label(
                ticket_card,
                text=f"TICKET #{result['ticket_number']} - {status_icon} {status_text}",
                font=("Segoe UI", 11, "bold"),
                foreground=status_color,
                background=self.COLORS['surface']
            )
            ticket_header.pack(anchor=tk.W, pady=(0, 5))

            # Subject
            subject = result['subject']
            if len(subject) > 80:
                subject = subject[:77] + "..."

            subject_label = ttk.Label(
                ticket_card,
                text=f"Subject: {subject}",
                font=("Segoe UI", 9),
                foreground=self.COLORS['text_primary'],
                background=self.COLORS['surface']
            )
            subject_label.pack(anchor=tk.W, pady=(0, 5))

            if status == 'FOUND':
                # Freshservice ID
                fs_id_label = ttk.Label(
                    ticket_card,
                    text=f"Freshservice ID: {result['freshservice_id']}",
                    font=("Segoe UI", 9),
                    foreground=self.COLORS['text_primary'],
                    background=self.COLORS['surface']
                )
                fs_id_label.pack(anchor=tk.W, pady=(0, 10))

                # Comparison table
                comparison_text = f"{'Field':<20} {'Expected':<25} {'Actual':<25} {'Status':<10}\n"
                comparison_text += "-" * 80 + "\n"

                for field_name, comparison in result['comparisons'].items():
                    field_label = field_name.replace('_', ' ').title()
                    expected = str(comparison['expected'])[:24]
                    actual = str(comparison['actual'])[:24]

                    if comparison.get('informational'):
                        match_icon = "ℹ INFO"
                    elif comparison['match']:
                        match_icon = "✓ MATCH"
                    else:
                        match_icon = "✗ MISMATCH"

                    comparison_text += f"{field_label:<20} {expected:<25} {actual:<25} {match_icon:<10}\n"

                comparison_label = ttk.Label(
                    ticket_card,
                    text=comparison_text,
                    font=("Consolas", 9),
                    foreground=self.COLORS['text_primary'],
                    background=self.COLORS['surface'],
                    justify=tk.LEFT
                )
                comparison_label.pack(anchor=tk.W)

        # Footer with report file
        footer_frame = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="15")
        footer_frame.pack(fill=tk.X, pady=(15, 0))

        report_label = ttk.Label(
            footer_frame,
            text=f"📁 Detailed report saved: {os.path.basename(report_file)}",
            font=("Segoe UI", 10),
            foreground=self.COLORS['text_primary'],
            background=self.COLORS['surface']
        )
        report_label.pack(anchor=tk.W)

        # Close button
        close_button = ttk.Button(
            footer_frame,
            text="Close",
            command=results_window.destroy,
            style='Accent.TButton'
        )
        close_button.pack(pady=(10, 0))

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mousewheel scrolling (bind to canvas only)
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)

    def reload_modules(self):
        """Reload Python modules without restarting the app."""
        try:
            import importlib
            import sys

            # List of modules to reload
            modules_to_reload = [
                'content_generator',
                'freshservice_client',
                'ticket_verifier',
                'verification_logger',
                'email_sender',
                'file_readers',
                'logger'
            ]

            self.log("🔄 Reloading modules...", "info")

            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    self.log(f"  ✓ Reloaded {module_name}", "ok")

            # Reinitialize components if they exist
            if self.access_token and self.email_sender:
                from email_sender import EmailSender
                self.email_sender = EmailSender(self.access_token, self.sender_email.get())
                self.log("  ✓ Reinitialized email sender", "ok")

            if self.claude_api_key.get():
                from content_generator import ContentGenerator
                self.content_gen = ContentGenerator(
                    self.claude_api_key.get(),
                    writing_quality=self.writing_quality.get()
                )
                self.log("  ✓ Reinitialized content generator", "ok")

            if self.fs_connected and self.fs_client:
                from freshservice_client import FreshserviceClient
                self.fs_client = FreshserviceClient(
                    self.fs_domain.get(),
                    self.fs_api_key.get()
                )
                self.log("  ✓ Reinitialized Freshservice client", "ok")

            self.log("✓ All modules reloaded successfully!", "ok")
            messagebox.showinfo("✓ Reload Complete", "All modules have been reloaded!\n\nYour authentication and configuration are preserved.")

        except Exception as e:
            self.log(f"✗ Reload failed: {str(e)}", "error")
            messagebox.showerror("Reload Error", f"Failed to reload modules:\n{str(e)}")

    def load_email_data_from_logs(self, ticket_numbers):
        """
        Load email data from log files for specific ticket numbers.

        Args:
            ticket_numbers: List of ticket numbers to load

        Returns:
            List of email dictionaries with full data, or empty list if not found
        """
        import re

        logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_dir):
            return []

        # Get all log files, sorted by modification time (newest first)
        log_files = [f for f in os.listdir(logs_dir) if f.startswith("email_test_log_") and f.endswith(".txt")]
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)

        email_data = {}

        # Search through log files for the ticket numbers
        for log_file in log_files:
            log_path = os.path.join(logs_dir, log_file)
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Parse each ticket from the log
                    for ticket_num in ticket_numbers:
                        if ticket_num in email_data:
                            continue  # Already found this ticket

                        # Look for the ticket block
                        pattern = rf"Ticket Number:\s+{ticket_num}\s*\n.*?Category:\s+([^\n]+)\s*\nType:\s+([^\n]+)\s*\nPriority:\s+([^\n]+)\s*\nSubject:\s+\[TEST-TKT-{ticket_num}\]([^\n]*)"
                        match = re.search(pattern, content, re.DOTALL)

                        if match:
                            category = match.group(1).strip()
                            ticket_type = match.group(2).strip()
                            priority = match.group(3).strip()
                            subject_rest = match.group(4).strip()

                            email_data[ticket_num] = {
                                'number': ticket_num,
                                'category': category,
                                'type': ticket_type,
                                'priority': priority,
                                'subject': f'[TEST-TKT-{ticket_num}] {subject_rest}'
                            }

                # If we found all tickets, stop searching
                if len(email_data) == len(ticket_numbers):
                    break

            except Exception as e:
                print(f"Error reading log file {log_file}: {e}")
                continue

        # Return list of email data in the same order as ticket_numbers
        return [email_data[num] for num in ticket_numbers if num in email_data]

    def view_logs(self):
        """Open logs directory."""
        logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            messagebox.showinfo("Info", "Logs directory created but no log files exist yet")
            return

        # Open directory in file explorer
        if os.name == 'nt':  # Windows
            os.startfile(logs_dir)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open "{logs_dir}"')

    def save_session(self):
        """Save current session data to file."""
        try:
            import json
            from datetime import datetime

            session_data = {
                'access_token': self.access_token,
                'authenticated': self.authenticated,
                'sender_email': self.sender_email.get(),
                'fs_connected': self.fs_connected,
                'fs_domain': self.fs_domain.get(),
                'timestamp': datetime.now().isoformat()
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save session: {e}")

    def restore_session(self):
        """Restore previous session if available."""
        try:
            import json
            from datetime import datetime, timedelta

            if not os.path.exists(self.session_file):
                return

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            # Check if session is less than 24 hours old
            saved_time = datetime.fromisoformat(session_data['timestamp'])
            if datetime.now() - saved_time > timedelta(hours=24):
                self.log("Previous session expired (>24h)", "info")
                try:
                    os.remove(self.session_file)
                except:
                    pass
                return

            # Restore Microsoft authentication
            if session_data.get('access_token') and session_data.get('authenticated'):
                self.access_token = session_data['access_token']
                sender_email = session_data.get('sender_email', self.sender_email.get())

                # Test if token still works
                self.log("Restoring previous Microsoft authentication...", "info")
                try:
                    from email_sender import EmailSender
                    self.email_sender = EmailSender(self.access_token, sender_email)

                    if self.email_sender.test_connection():
                        self.authenticated = True
                        self.auth_status_icon.config(foreground=self.COLORS['success'])
                        self.auth_status.config(text="Authenticated ✓", foreground=self.COLORS['success'])
                        self.generate_button.config(state=tk.NORMAL)
                        self.log("✓ Microsoft authentication restored!", "ok")

                        # Initialize content generator if Claude key is available
                        if self.claude_api_key.get():
                            from content_generator import ContentGenerator
                            self.content_gen = ContentGenerator(
                                self.claude_api_key.get(),
                                writing_quality=self.writing_quality.get()
                            )
                    else:
                        raise Exception("Token expired")

                except Exception as e:
                    self.log(f"Could not restore authentication: {str(e)}", "warning")
                    self.log("Please click 'Authenticate' to login again", "info")
                    try:
                        os.remove(self.session_file)
                    except:
                        pass

            # Restore Freshservice connection
            if session_data.get('fs_connected') and self.fs_domain.get() and self.fs_api_key.get():
                self.log("Restoring Freshservice connection...", "info")
                try:
                    from freshservice_client import FreshserviceClient
                    self.fs_client = FreshserviceClient(
                        self.fs_domain.get(),
                        self.fs_api_key.get()
                    )

                    if self.fs_client.test_connection():
                        self.fs_connected = True
                        self.fs_status_icon.config(foreground=self.COLORS['success'])
                        self.fs_status.config(text="Connected ✓", foreground=self.COLORS['success'])
                        self.verify_button.config(state=tk.NORMAL)  # Enable verify button
                        self.log("✓ Freshservice connection restored!", "ok")
                        self.log("🔍 Verify button enabled - you can verify any of your last 10 tickets!", "ok")
                    else:
                        raise Exception("Connection failed")

                except Exception as e:
                    self.log(f"Could not restore Freshservice: {str(e)}", "warning")
                    self.log("Please click 'Test Connection' in Freshservice section", "info")

        except Exception as e:
            # Don't let session restore errors break the app
            print(f"Warning: Could not restore session: {e}")
            self.log("Starting fresh session", "info")
            try:
                if os.path.exists(self.session_file):
                    os.remove(self.session_file)
            except:
                pass


def main():
    try:
        root = tk.Tk()
        app = TicketGeneratorGUI(root)

        # Handle window close properly
        def on_closing():
            try:
                root.quit()
                root.destroy()
            except:
                pass

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
