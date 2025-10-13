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
    # Light theme color scheme
    COLORS_LIGHT = {
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

    # Dark theme color scheme
    COLORS_DARK = {
        'primary': '#818CF8',      # Lighter Indigo for dark mode
        'primary_dark': '#6366F1',
        'primary_light': '#A5B4FC',
        'success': '#34D399',      # Lighter Green
        'success_light': '#6EE7B7',
        'error': '#F87171',        # Lighter Red
        'warning': '#FBBF24',      # Lighter Amber
        'background': '#1F2937',   # Dark gray background
        'surface': '#111827',      # Darker surface
        'text_primary': '#F9FAFB',
        'text_secondary': '#D1D5DB',
        'border': '#374151',
        'shadow_light': '#0F172A',  # Dark shadow
        'shadow_medium': '#1E293B',  # Medium dark shadow
        'accent': '#A78BFA',       # Lighter Purple accent
        'gradient_start': '#818CF8',
        'gradient_end': '#A78BFA'
    }

    COLORS = COLORS_LIGHT.copy()  # Default to light mode

    def __init__(self, root):
        self.root = root

        # Wrap root.quit() to track when it's called
        original_quit = self.root.quit
        def tracked_quit():
            import traceback
            print("[DEBUG] root.quit() called! Stack trace:")
            traceback.print_stack()
            original_quit()
        self.root.quit = tracked_quit

        self.root.title("IT Ticket Email Generator • Dashboard")
        self.root.geometry("1400x900")

        # Dark mode state
        self.dark_mode = tk.BooleanVar(value=False)

        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1400
        window_height = 900
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
        self.custom_instructions = tk.StringVar()
        self.use_custom_instructions = tk.BooleanVar(value=False)

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
        self.is_shutting_down = False  # Flag to prevent thread errors during shutdown

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

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.dark_mode.set(not self.dark_mode.get())

        # Update COLORS dictionary
        if self.dark_mode.get():
            self.COLORS = self.COLORS_DARK.copy()
            self.theme_button.config(text="☀️ Light Mode")
        else:
            self.COLORS = self.COLORS_LIGHT.copy()
            self.theme_button.config(text="🌙 Dark Mode")

        # Reconfigure all styles
        self.configure_styles()

        # Force update all widgets recursively
        self._update_widget_colors(self.root)

        # Update main canvas background
        if hasattr(self, 'main_canvas'):
            self.main_canvas.configure(bg=self.COLORS['background'])

    def _update_widget_colors(self, widget):
        """Recursively update widget colors for theme change."""
        try:
            widget_class = widget.winfo_class()

            # Update Frame backgrounds
            if widget_class == 'Frame':
                current_bg = widget.cget('bg')
                # Update if it's a themed color
                if current_bg in self.COLORS_LIGHT.values() or current_bg in self.COLORS_DARK.values():
                    # Map old color to new color key
                    for key, value in (self.COLORS_DARK if not self.dark_mode.get() else self.COLORS_LIGHT).items():
                        if current_bg == value:
                            widget.configure(bg=self.COLORS[key])
                            break

            # Update Text and ScrolledText widgets
            elif widget_class in ['Text', 'ScrolledText']:
                widget.configure(
                    bg=self.COLORS['surface'] if str(widget.cget('bg')) in ['white', '#FFFFFF', '#111827'] else '#F9FAFB' if not self.dark_mode.get() else '#1E293B',
                    fg=self.COLORS['text_primary']
                )

            # Update Listbox widgets
            elif widget_class == 'Listbox':
                widget.configure(
                    bg='white' if not self.dark_mode.get() else '#1E293B',
                    fg=self.COLORS['text_primary']
                )

            # Update Canvas widgets
            elif widget_class == 'Canvas':
                widget.configure(bg=self.COLORS['background'])

            # Update Label widgets
            elif widget_class == 'Label':
                current_bg = widget.cget('bg')
                current_fg = widget.cget('fg')

                # Update backgrounds
                if current_bg in self.COLORS_LIGHT.values() or current_bg in self.COLORS_DARK.values():
                    for key, value in (self.COLORS_DARK if not self.dark_mode.get() else self.COLORS_LIGHT).items():
                        if current_bg == value:
                            widget.configure(bg=self.COLORS[key])
                            break

                # Update foregrounds
                if current_fg in self.COLORS_LIGHT.values() or current_fg in self.COLORS_DARK.values():
                    for key, value in (self.COLORS_DARK if not self.dark_mode.get() else self.COLORS_LIGHT).items():
                        if current_fg == value:
                            widget.configure(fg=self.COLORS[key])
                            break

            # Recursively update children
            for child in widget.winfo_children():
                self._update_widget_colors(child)

        except Exception:
            pass  # Skip widgets that don't support these options

    def create_card_with_shadow(self, parent, **kwargs):
        """Create a card frame with shadow effect."""
        # Shadow frame (slightly larger and offset)
        shadow_frame = tk.Frame(parent, bg=self.COLORS['shadow_medium'])

        # Actual card frame
        card_frame = ttk.Frame(shadow_frame, style='Card.TFrame', **kwargs)
        card_frame.pack(padx=(0, 3), pady=(0, 3), fill=tk.BOTH, expand=True)

        return shadow_frame, card_frame

    def create_widgets(self):
        # Main container - no scrolling, fixed dashboard layout
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 3-column grid layout
        main_frame.columnconfigure(0, weight=1)  # Left column
        main_frame.columnconfigure(1, weight=1)  # Middle column
        main_frame.columnconfigure(2, weight=1)  # Right column

        # 3 rows
        main_frame.rowconfigure(0, weight=0)  # Header (fixed height)
        main_frame.rowconfigure(1, weight=1)  # Middle row (expandable)
        main_frame.rowconfigure(2, weight=1)  # Bottom row (expandable)

        # ===== ROW 0: HEADER (spans all 3 columns) =====
        header_shadow = tk.Frame(main_frame, bg=self.COLORS['shadow_medium'])
        header_shadow.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10), padx=5)

        # Compact header
        header_card = tk.Frame(header_shadow, bg=self.COLORS['primary'], padx=0, pady=0)
        header_card.pack(padx=(0, 2), pady=(0, 2), fill=tk.BOTH)

        header_content = ttk.Frame(header_card, style='Card.TFrame', padding="15")
        header_content.pack(fill=tk.BOTH)
        header_content.columnconfigure(0, weight=1)

        title_frame = ttk.Frame(header_content, style='Card.TFrame')
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="📧 IT Ticket Email Generator",
                 font=('Segoe UI', 16, 'bold'), foreground=self.COLORS['primary'],
                 background=self.COLORS['surface']).pack(side=tk.LEFT)

        self.theme_button = ttk.Button(title_frame, text="🌙", command=self.toggle_theme,
                                      style='Primary.TButton', width=3)
        self.theme_button.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(title_frame, text="🔄", command=self.reload_modules,
                  style='Primary.TButton', width=3).pack(side=tk.RIGHT, padx=(5, 0))

        # ===== CARD 1: Configuration (Row 1, Col 0) =====
        config_shadow, config_card = self.create_card_with_shadow(main_frame, padding="12")
        config_shadow.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        ttk.Label(config_card, text="🔐 Configuration", font=('Segoe UI', 11, 'bold'),
                 foreground=self.COLORS['primary'], background=self.COLORS['surface']).pack(anchor=tk.W, pady=(0, 8))

        form_frame = ttk.Frame(config_card, style='Card.TFrame')
        form_frame.pack(fill=tk.BOTH)

        ttk.Label(form_frame, text="Client ID:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(form_frame, textvariable=self.client_id, font=('Segoe UI', 8), width=25).grid(row=0, column=1, sticky=tk.W, pady=3)

        ttk.Label(form_frame, text="Tenant ID:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Entry(form_frame, textvariable=self.tenant_id, font=('Segoe UI', 8), width=25).grid(row=1, column=1, sticky=tk.W, pady=3)

        ttk.Label(form_frame, text="Sender:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(form_frame, textvariable=self.sender_email, font=('Segoe UI', 8), width=25).grid(row=2, column=1, sticky=tk.W, pady=3)

        ttk.Label(form_frame, text="Recipient:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=3, column=0, sticky=tk.W, pady=3)
        ttk.Entry(form_frame, textvariable=self.recipient_email, font=('Segoe UI', 8), width=25).grid(row=3, column=1, sticky=tk.W, pady=3)

        ttk.Label(form_frame, text="Claude Key:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=4, column=0, sticky=tk.W, pady=3)
        ttk.Entry(form_frame, textvariable=self.claude_api_key, show="•", font=('Segoe UI', 8), width=25).grid(row=4, column=1, sticky=tk.W, pady=3)

        auth_frame = ttk.Frame(config_card, style='Card.TFrame')
        auth_frame.pack(fill=tk.X, pady=(8, 0))

        self.auth_button = ttk.Button(auth_frame, text="🔑 Authenticate", command=self.authenticate,
                                      style='Primary.TButton')
        self.auth_button.pack(side=tk.LEFT, padx=(0, 5))

        status_frame = tk.Frame(auth_frame, bg=self.COLORS['surface'],
                               highlightthickness=1, highlightbackground=self.COLORS['border'],
                               padx=8, pady=4)
        status_frame.pack(side=tk.LEFT)

        self.auth_status_icon = ttk.Label(status_frame, text="●", style='Card.TLabel',
                                          foreground=self.COLORS['error'], font=('Segoe UI', 12))
        self.auth_status_icon.pack(side=tk.LEFT, padx=(0, 5))

        self.auth_status = ttk.Label(status_frame, text="Not Auth", style='Card.TLabel',
                                     foreground=self.COLORS['error'], font=('Segoe UI', 9, 'bold'))
        self.auth_status.pack(side=tk.LEFT)

        # ===== CARD 2: Freshservice (Row 1, Col 1) =====
        fs_shadow, fs_card = self.create_card_with_shadow(main_frame, padding="12")
        fs_shadow.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        ttk.Label(fs_card, text="🔍 Freshservice", font=('Segoe UI', 11, 'bold'),
                 foreground=self.COLORS['primary'], background=self.COLORS['surface']).pack(anchor=tk.W, pady=(0, 8))

        fs_form = ttk.Frame(fs_card, style='Card.TFrame')
        fs_form.pack(fill=tk.BOTH)

        ttk.Label(fs_form, text="Domain:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Entry(fs_form, textvariable=self.fs_domain, font=('Segoe UI', 8), width=25).grid(row=0, column=1, sticky=tk.W, pady=3)

        ttk.Label(fs_form, text="API Key:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Entry(fs_form, textvariable=self.fs_api_key, show="•", font=('Segoe UI', 8), width=25).grid(row=1, column=1, sticky=tk.W, pady=3)

        ttk.Label(fs_form, text="Wait (min):", font=('Segoe UI', 8), style='Card.TLabel').grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(fs_form, from_=1, to=30, textvariable=self.fs_wait_time, width=8, font=('Segoe UI', 8)).grid(row=2, column=1, sticky=tk.W, pady=3)

        fs_btn_frame = ttk.Frame(fs_card, style='Card.TFrame')
        fs_btn_frame.pack(fill=tk.X, pady=(8, 0))

        self.fs_test_button = ttk.Button(fs_btn_frame, text="🔗 Test", command=self.test_freshservice_connection,
                                        style='Primary.TButton')
        self.fs_test_button.pack(side=tk.LEFT, padx=(0, 5))

        fs_status_frame = tk.Frame(fs_btn_frame, bg=self.COLORS['surface'],
                                  highlightthickness=1, highlightbackground=self.COLORS['border'],
                                  padx=8, pady=4)
        fs_status_frame.pack(side=tk.LEFT)

        self.fs_status_icon = ttk.Label(fs_status_frame, text="●", style='Card.TLabel',
                                        foreground=self.COLORS['text_secondary'], font=('Segoe UI', 12))
        self.fs_status_icon.pack(side=tk.LEFT, padx=(0, 5))

        self.fs_status = ttk.Label(fs_status_frame, text="Not Configured", style='Card.TLabel',
                                   foreground=self.COLORS['text_secondary'], font=('Segoe UI', 9, 'bold'))
        self.fs_status.pack(side=tk.LEFT)

        # ===== CARD 3: Generation Settings (Row 1, Col 2) =====
        gen_shadow, gen_card = self.create_card_with_shadow(main_frame, padding="12")
        gen_shadow.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        ttk.Label(gen_card, text="⚙️ Generation", font=('Segoe UI', 11, 'bold'),
                 foreground=self.COLORS['primary'], background=self.COLORS['surface']).pack(anchor=tk.W, pady=(0, 8))

        gen_form = ttk.Frame(gen_card, style='Card.TFrame')
        gen_form.pack(fill=tk.BOTH)

        ttk.Label(gen_form, text="Emails:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=3)
        email_spin_frame = ttk.Frame(gen_form, style='Card.TFrame')
        email_spin_frame.grid(row=0, column=1, sticky=tk.W, pady=3)
        ttk.Spinbox(email_spin_frame, from_=1, to=1000, textvariable=self.num_emails, width=8, font=('Segoe UI', 8)).pack(side=tk.LEFT)
        self.next_ticket_label = ttk.Label(email_spin_frame, text=f"(#{self.ticket_counter.get_current()})",
                                          font=('Segoe UI', 7), foreground=self.COLORS['text_secondary'],
                                          background=self.COLORS['surface'])
        self.next_ticket_label.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(gen_form, text="Quality:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=1, column=0, sticky=tk.W, pady=3)
        quality_frame = ttk.Frame(gen_form, style='Card.TFrame')
        quality_frame.grid(row=1, column=1, sticky=tk.W, pady=3)
        ttk.Radiobutton(quality_frame, text="Basic", variable=self.writing_quality, value="basic",
                       style='Card.TRadiobutton').pack(side=tk.LEFT, padx=(0, 3))
        ttk.Radiobutton(quality_frame, text="Realistic", variable=self.writing_quality, value="realistic",
                       style='Card.TRadiobutton').pack(side=tk.LEFT, padx=(0, 3))
        ttk.Radiobutton(quality_frame, text="Polished", variable=self.writing_quality, value="polished",
                       style='Card.TRadiobutton').pack(side=tk.LEFT)

        ttk.Label(gen_form, text="Custom:", font=('Segoe UI', 8), style='Card.TLabel').grid(row=2, column=0, sticky=(tk.W, tk.N), pady=3)
        custom_frame = ttk.Frame(gen_form, style='Card.TFrame')
        custom_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=3)

        self.custom_checkbox = ttk.Checkbutton(custom_frame, text="Override with custom",
                                              variable=self.use_custom_instructions, style='Card.TRadiobutton')
        self.custom_checkbox.pack(anchor=tk.W)

        custom_text_container = tk.Frame(custom_frame, bg='#F9FAFB', highlightthickness=1,
                                        highlightbackground=self.COLORS['border'])
        custom_text_container.pack(fill=tk.BOTH, expand=True)

        self.custom_text = scrolledtext.ScrolledText(custom_text_container, height=3, wrap=tk.WORD,
                                                     font=('Segoe UI', 8), bg='#F9FAFB', relief='flat', borderwidth=0)
        self.custom_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.custom_text.insert('1.0', 'Example: Generate tickets about printer issues...')
        self.custom_text.bind('<FocusIn>', lambda e: self.custom_text.delete('1.0', tk.END) if self.custom_text.get('1.0', tk.END).strip().startswith('Example:') else None)

        self.generate_button = ttk.Button(gen_card, text="🚀 Generate & Send",
                                         command=self.generate_emails, state=tk.DISABLED, style='Success.TButton')
        self.generate_button.pack(fill=tk.X, pady=(8, 0))

        # ===== CARD 4: Progress & Activity (Row 2, Col 0-1 span) =====
        progress_shadow, progress_card = self.create_card_with_shadow(main_frame, padding="12")
        progress_shadow.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        ttk.Label(progress_card, text="📊 Progress & Activity", font=('Segoe UI', 11, 'bold'),
                 foreground=self.COLORS['primary'], background=self.COLORS['surface']).pack(anchor=tk.W, pady=(0, 8))

        self.status_label = ttk.Label(progress_card, text="Ready to start", font=('Segoe UI', 9), style='Card.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        self.progress = ttk.Progressbar(progress_card, mode='determinate', style='Custom.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 8))

        log_container = ttk.LabelFrame(progress_card, text="Activity Log", style='Card.TLabelframe', padding="8")
        log_container.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_container, height=8, wrap=tk.WORD, font=('Consolas', 8),
                                                  bg='#F9FAFB', relief='flat', borderwidth=1,
                                                  highlightthickness=1, highlightbackground=self.COLORS['border'])
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ===== CARD 5: Actions (Row 2, Col 2) =====
        actions_shadow, actions_card = self.create_card_with_shadow(main_frame, padding="12")
        actions_shadow.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        ttk.Label(actions_card, text="🎯 Actions", font=('Segoe UI', 11, 'bold'),
                 foreground=self.COLORS['primary'], background=self.COLORS['surface']).pack(anchor=tk.W, pady=(0, 8))

        self.view_logs_button = ttk.Button(actions_card, text="📁 View Logs", command=self.view_logs,
                                          style='Primary.TButton')
        self.view_logs_button.pack(fill=tk.X, pady=(0, 5))

        self.verify_button = ttk.Button(actions_card, text="🔍 Verify Tickets", command=self.verify_tickets,
                                       state=tk.DISABLED, style='Success.TButton')
        self.verify_button.pack(fill=tk.X, pady=(0, 5))

        self.verify_status_frame = ttk.Frame(actions_card, style='Card.TFrame')
        self.verify_status_frame.pack(fill=tk.X, pady=(8, 0))
        self.verify_status_frame.pack_forget()

        self.verify_status_label = ttk.Label(self.verify_status_frame, text="", font=('Segoe UI', 8), style='Card.TLabel')
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
        """
        Add message to log output with color coding.
        Thread-safe: schedules GUI updates on main thread via root.after().
        """
        def _log_internal():
            try:
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
            except RuntimeError:
                # Main loop is not running, silently ignore
                pass

        # Schedule on main thread to ensure thread safety
        try:
            self.root.after(0, _log_internal)
        except RuntimeError:
            # Main loop is not running, silently ignore
            pass

    def generate_custom_distribution(self, num_emails: int) -> list:
        """
        Generate distribution for custom instructions mode.
        Uses unique categories (no repeats until all used) and alternates ticket types.

        Args:
            num_emails: Number of tickets to generate

        Returns:
            List of ticket distribution dictionaries
        """
        import random

        distribution = []

        # Create a shuffled list of unique categories
        available_categories = self.categories.copy()
        random.shuffle(available_categories)

        # Alternate between Service Request and Incident
        # Start with Service Request
        ticket_types = ["Service Request", "Incident"]

        for i in range(num_emails):
            # Get next unique category (reshuffle if we run out)
            if not available_categories:
                available_categories = self.categories.copy()
                random.shuffle(available_categories)

            category_info = available_categories.pop(0)

            # Alternate ticket type: SR, Inc, SR, Inc, SR, Inc...
            ticket_type = ticket_types[i % 2]

            # Use a default priority (can be random or default to Priority 3)
            priority = random.choice(self.priorities) if self.priorities else "Priority 3"

            distribution.append({
                "category": category_info['category'],
                "subcategory": category_info['subcategory'],
                "item": category_info['item'],
                "priority": priority,
                "type": ticket_type
            })

        return distribution

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
                # Capture values from StringVars early before any potential interruption
                try:
                    client_id = self.client_id.get()
                    tenant_id = self.tenant_id.get()
                    sender_email = self.sender_email.get()
                    claude_key = self.claude_api_key.get()
                    writing_qual = self.writing_quality.get()
                except RuntimeError:
                    # Window is closing, exit silently
                    return

                self.log("Starting authentication...")
                self.log("IMPORTANT: Do NOT close this window or press Ctrl+C in the terminal!", "info")
                self.log("Follow the authentication instructions in the terminal...", "info")
                authenticator = GraphAuthenticator(client_id, tenant_id)
                self.access_token = authenticator.authenticate_device_flow()

                # Check if shutting down before continuing
                if self.is_shutting_down:
                    return

                # Initialize components
                self.email_sender = EmailSender(self.access_token, sender_email)
                self.content_gen = ContentGenerator(
                    claude_key,
                    writing_quality=writing_qual
                )

                # Test connection
                self.log("Testing Microsoft Graph API connection...")
                if self.email_sender.test_connection():
                    self.authenticated = True
                    if not self.is_shutting_down:
                        try:
                            self.root.after(0, lambda: self.auth_status_icon.config(foreground=self.COLORS['success']))
                            self.root.after(0, lambda: self.auth_status.config(
                                text="Authenticated ✓",
                                foreground=self.COLORS['success']))
                            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
                            self.root.after(0, lambda: self.status_label.config(text="Ready to generate emails"))
                        except RuntimeError:
                            # Main loop stopped, ignore GUI updates
                            pass
                    self.log("Authentication successful", "ok")

                    # Save session for next time
                    if not self.is_shutting_down:
                        self.save_session()
                else:
                    raise Exception("Failed to connect to Microsoft Graph API")

            except KeyboardInterrupt:
                if not self.is_shutting_down:
                    self.log("Authentication cancelled by user", "error")
                    try:
                        self.root.after(0, lambda: self.status_label.config(text="Authentication cancelled"))
                    except RuntimeError:
                        pass
            except Exception as e:
                if not self.is_shutting_down:
                    error_msg = str(e)
                    self.log(f"Authentication failed: {error_msg}", "error")
                    try:
                        self.root.after(0, lambda: messagebox.showerror("Authentication Error", error_msg))
                    except RuntimeError:
                        pass
            finally:
                if not self.is_shutting_down:
                    try:
                        self.root.after(0, lambda: self.auth_button.config(state=tk.NORMAL))
                    except RuntimeError:
                        pass

        # Run in separate thread to avoid blocking GUI
        # Use daemon=True to prevent thread from outliving the main program
        # The is_shutting_down flag prevents auth from continuing if window closes
        auth_t = threading.Thread(target=auth_thread, daemon=True)
        print(f"[DEBUG] Starting authentication thread (daemon={auth_t.daemon})")
        auth_t.start()
        print(f"[DEBUG] Authentication thread started, main thread continuing...")

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

                # Generate distribution based on whether custom instructions are enabled
                custom_instructions_enabled = self.use_custom_instructions.get()
                custom_instructions_text = self.custom_text.get('1.0', tk.END).strip()

                if custom_instructions_enabled and custom_instructions_text and not custom_instructions_text.startswith('Example:'):
                    # For custom instructions: use unique categories and alternate ticket types
                    distribution = self.generate_custom_distribution(num_emails)
                    self.log(f"Using custom distribution: unique categories, alternating types (SR/Inc/SR/Inc...)", "info")
                else:
                    # Standard weighted distribution
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

                # Get custom instructions if enabled
                custom_instructions = None
                if self.use_custom_instructions.get():
                    custom_instructions = self.custom_text.get('1.0', tk.END).strip()
                    if custom_instructions and not custom_instructions.startswith('Example:'):
                        self.log(f"Using custom AI instructions for generation", "info")
                    else:
                        custom_instructions = None
                        self.log("Custom instructions enabled but empty - using category-based generation", "warning")

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
                            ticket_number=ticket_number,
                            custom_instructions=custom_instructions,
                            ticket_index=i,
                            total_tickets=num_emails
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
                comparison_text = f"{'Field':<30} {'Actual':<50}\n"
                comparison_text += "-" * 80 + "\n"

                for field_name, comparison in result['comparisons'].items():
                    field_label = field_name.replace('_', ' ').title()
                    actual = str(comparison['actual'])[:48]

                    comparison_text += f"{field_label:<30} {actual:<50}\n"

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
        """Show log file selection dialog and viewer."""
        logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            messagebox.showinfo("Info", "Logs directory created but no log files exist yet")
            return

        # Get all log files
        log_files = []
        for filename in os.listdir(logs_dir):
            if filename.startswith("email_test_log_") and filename.endswith(".txt"):
                filepath = os.path.join(logs_dir, filename)
                log_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'modified': os.path.getmtime(filepath)
                })

        if not log_files:
            messagebox.showinfo("Info", "No log files found")
            return

        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x['modified'], reverse=True)

        # Show log selection dialog
        self.show_log_selection_dialog(log_files)

    def show_log_selection_dialog(self, log_files):
        """Show dialog to select which log file to view."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Log File to View")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 700) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"700x500+{x}+{y}")

        # Header
        header_frame = tk.Frame(dialog, bg=self.COLORS['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="📋 Select Log File",
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.COLORS['primary'], fg='white')
        title_label.pack(pady=15)

        # Info label
        info_frame = tk.Frame(dialog, bg=self.COLORS['background'])
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        info_label = tk.Label(info_frame,
                             text=f"Found {len(log_files)} log file(s). Select one to view:",
                             font=('Segoe UI', 10),
                             bg=self.COLORS['background'],
                             fg=self.COLORS['text_primary'])
        info_label.pack(anchor=tk.W)

        # Listbox frame with scrollbar
        list_frame = tk.Frame(dialog, bg=self.COLORS['background'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame,
                            font=('Consolas', 10),
                            bg='white',
                            fg=self.COLORS['text_primary'],
                            selectmode=tk.SINGLE,
                            yscrollcommand=scrollbar.set,
                            highlightthickness=1,
                            highlightbackground=self.COLORS['border'],
                            activestyle='none',
                            selectbackground=self.COLORS['primary_light'],
                            selectforeground='white')
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox with log files
        from datetime import datetime
        for log_file in log_files:
            mod_time = datetime.fromtimestamp(log_file['modified'])
            display_text = f"{log_file['filename']} • {mod_time.strftime('%Y-%m-%d %I:%M:%S %p')}"
            listbox.insert(tk.END, display_text)

        # Button frame
        button_frame = tk.Frame(dialog, bg=self.COLORS['background'])
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def on_view():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a log file to view")
                return

            selected_log = log_files[selection[0]]
            dialog.destroy()
            self.show_log_viewer(selected_log['filepath'], selected_log['filename'])

        def on_cancel():
            dialog.destroy()

        # Double-click to view
        listbox.bind('<Double-Button-1>', lambda e: on_view())

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        view_btn = ttk.Button(button_frame, text="📖 View Log", command=on_view, style='Success.TButton')
        view_btn.pack(side=tk.RIGHT)

        # Select first item by default
        if log_files:
            listbox.selection_set(0)
            listbox.focus_set()

    def show_log_viewer(self, filepath, filename):
        """Show log file viewer window."""
        viewer = tk.Toplevel(self.root)
        viewer.title(f"Log Viewer - {filename}")
        viewer.geometry("1000x700")
        viewer.transient(self.root)

        # Center viewer
        viewer.update_idletasks()
        x = (viewer.winfo_screenwidth() - 1000) // 2
        y = (viewer.winfo_screenheight() - 700) // 2
        viewer.geometry(f"1000x700+{x}+{y}")

        # Header
        header_frame = tk.Frame(viewer, bg=self.COLORS['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=f"📋 {filename}",
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.COLORS['primary'], fg='white')
        title_label.pack(pady=15)

        # Main content frame
        content_frame = tk.Frame(viewer, bg=self.COLORS['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Text widget with scrollbar
        text_container = tk.Frame(content_frame, bg='white',
                                 highlightthickness=1,
                                 highlightbackground=self.COLORS['border'])
        text_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_container,
                             font=('Consolas', 9),
                             bg='white',
                             fg=self.COLORS['text_primary'],
                             wrap=tk.WORD,
                             yscrollcommand=scrollbar.set,
                             relief='flat',
                             padx=15,
                             pady=15)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        # Read and display log file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Configure text tags for syntax highlighting
            text_widget.tag_config('header', font=('Consolas', 10, 'bold'),
                                  foreground=self.COLORS['primary'])
            text_widget.tag_config('section', font=('Consolas', 9, 'bold'),
                                  foreground=self.COLORS['accent'])
            text_widget.tag_config('success', foreground=self.COLORS['success'])
            text_widget.tag_config('error', foreground=self.COLORS['error'])
            text_widget.tag_config('key', foreground=self.COLORS['text_secondary'])
            text_widget.tag_config('separator', foreground=self.COLORS['border'])

            # Insert content with formatting
            lines = content.split('\n')
            for line in lines:
                if line.startswith('='*50) or line.startswith('-'*50):
                    text_widget.insert(tk.END, line + '\n', 'separator')
                elif 'CONFIGURATION' in line or 'GENERATION LOG' in line or 'SENDING LOG' in line or 'SUMMARY' in line:
                    text_widget.insert(tk.END, line + '\n', 'header')
                elif line.startswith('Ticket #') or line.startswith('['):
                    text_widget.insert(tk.END, line + '\n', 'section')
                elif 'SUCCESS' in line or 'Sent successfully' in line:
                    text_widget.insert(tk.END, line + '\n', 'success')
                elif 'FAILED' in line or 'Error' in line:
                    text_widget.insert(tk.END, line + '\n', 'error')
                elif ':' in line and not line.startswith(' '):
                    # Key-value pairs
                    parts = line.split(':', 1)
                    text_widget.insert(tk.END, parts[0] + ':', 'key')
                    if len(parts) > 1:
                        text_widget.insert(tk.END, parts[1] + '\n')
                    else:
                        text_widget.insert(tk.END, '\n')
                else:
                    text_widget.insert(tk.END, line + '\n')

            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            text_widget.insert(tk.END, f"Error reading log file: {str(e)}", 'error')
            text_widget.config(state=tk.DISABLED)

        # Button frame
        button_frame = tk.Frame(viewer, bg=self.COLORS['background'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        def open_in_folder():
            """Open the log file location in file explorer."""
            logs_dir = os.path.dirname(filepath)
            if os.name == 'nt':  # Windows
                os.startfile(logs_dir)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{logs_dir}"')

        close_btn = ttk.Button(button_frame, text="Close", command=viewer.destroy)
        close_btn.pack(side=tk.RIGHT, padx=(5, 0))

        folder_btn = ttk.Button(button_frame, text="📁 Open in Folder", command=open_in_folder)
        folder_btn.pack(side=tk.RIGHT)

    def save_session(self):
        """Save current session data to file."""
        # Try to get StringVar values, skip if main loop stopped
        try:
            sender_email = self.sender_email.get()
            fs_domain = self.fs_domain.get()
        except RuntimeError:
            # Main loop not running, skip session save silently
            return

        try:
            import json
            from datetime import datetime

            session_data = {
                'access_token': self.access_token,
                'authenticated': self.authenticated,
                'sender_email': sender_email,
                'fs_connected': self.fs_connected,
                'fs_domain': fs_domain,
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
            print("[DEBUG] on_closing() called - user closed window")
            app.is_shutting_down = True
            try:
                root.quit()
                root.destroy()
            except:
                pass

        root.protocol("WM_DELETE_WINDOW", on_closing)
        print("[DEBUG] Starting mainloop...")
        root.mainloop()
        print("[DEBUG] Mainloop exited")
    except KeyboardInterrupt:
        # Suppress the message if we're shutting down normally
        print("[DEBUG] KeyboardInterrupt caught in main()")
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
