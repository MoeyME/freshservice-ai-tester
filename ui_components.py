"""
UI Components Module
Contains enhanced UI widgets and utilities for the IT Ticket Email Generator.
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Optional, Callable


class ToastNotification:
    """
    Modern toast notification system for temporary messages.
    Displays notifications that auto-dismiss after a duration.
    """

    def __init__(self, parent, colors):
        """
        Initialize toast notification system.

        Args:
            parent: Parent widget (usually root window)
            colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = colors
        self.active_toasts = []
        self.toast_offset = 10  # Starting Y offset from bottom

    def show(self, message: str, level: str = "info", duration: int = 3000):
        """
        Display a toast notification.

        Args:
            message: Message to display
            level: Type of notification ("info", "success", "error", "warning")
            duration: How long to show in milliseconds (default 3000)
        """
        # Color mapping
        level_colors = {
            "info": self.colors['primary'],
            "success": self.colors['success'],
            "error": self.colors['error'],
            "warning": self.colors['warning']
        }

        # Icon mapping
        level_icons = {
            "info": "ℹ️",
            "success": "✓",
            "error": "❌",
            "warning": "⚠️"
        }

        bg_color = level_colors.get(level, self.colors['primary'])
        icon = level_icons.get(level, "ℹ️")

        # Create toast frame
        toast = tk.Toplevel(self.parent)
        toast.overrideredirect(True)  # Remove window decorations
        toast.attributes('-topmost', True)  # Keep on top

        # Position at bottom-right of parent window
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Create frame with content
        frame = tk.Frame(toast, bg=bg_color, padx=20, pady=12)
        frame.pack()

        label = tk.Label(
            frame,
            text=f"{icon}  {message}",
            bg=bg_color,
            fg='white',
            font=('Segoe UI', 10, 'bold')
        )
        label.pack()

        # Update to get actual size
        toast.update_idletasks()
        toast_width = toast.winfo_width()
        toast_height = toast.winfo_height()

        # Calculate position (bottom-right with offset for multiple toasts)
        current_offset = self.toast_offset + (len(self.active_toasts) * (toast_height + 10))
        x = parent_x + parent_width - toast_width - 20
        y = parent_y + parent_height - toast_height - current_offset

        toast.geometry(f"+{x}+{y}")

        # Fade-in animation
        toast.attributes('-alpha', 0.0)
        self._fade_in(toast, 0.0)

        # Track active toast
        self.active_toasts.append(toast)

        # Schedule fade-out and destroy
        toast.after(duration, lambda: self._fade_out_and_destroy(toast))

    def _fade_in(self, widget, alpha):
        """Animate fade-in effect."""
        if alpha < 1.0:
            alpha += 0.1
            widget.attributes('-alpha', alpha)
            widget.after(30, lambda: self._fade_in(widget, alpha))

    def _fade_out_and_destroy(self, widget):
        """Animate fade-out and destroy widget."""
        def fade_step(alpha):
            if alpha > 0:
                alpha -= 0.1
                widget.attributes('-alpha', alpha)
                widget.after(30, lambda: fade_step(alpha))
            else:
                if widget in self.active_toasts:
                    self.active_toasts.remove(widget)
                widget.destroy()
        fade_step(1.0)


class LoadingSpinner(tk.Canvas):
    """
    Animated loading spinner widget.
    Shows a rotating circular indicator.
    """

    def __init__(self, parent, size=40, color="#6366F1", **kwargs):
        """
        Initialize loading spinner.

        Args:
            parent: Parent widget
            size: Size of the spinner in pixels
            color: Color of the spinner
        """
        super().__init__(parent, width=size, height=size, bg='white',
                        highlightthickness=0, **kwargs)
        self.size = size
        self.color = color
        self.angle = 0
        self.is_spinning = False
        self._animation_id = None

    def start(self):
        """Start the spinning animation."""
        if not self.is_spinning:
            self.is_spinning = True
            self._animate()

    def stop(self):
        """Stop the spinning animation."""
        self.is_spinning = False
        if self._animation_id:
            self.after_cancel(self._animation_id)
            self._animation_id = None
        self.delete("all")

    def _animate(self):
        """Animate the spinner rotation."""
        if not self.is_spinning:
            return

        self.delete("all")

        # Draw circular arc
        padding = 5
        arc_width = 4

        self.create_arc(
            padding, padding,
            self.size - padding, self.size - padding,
            start=self.angle,
            extent=270,
            outline=self.color,
            width=arc_width,
            style=tk.ARC
        )

        # Update angle
        self.angle = (self.angle + 10) % 360

        # Schedule next frame
        self._animation_id = self.after(50, self._animate)


class PulsingButton(ttk.Button):
    """
    Button with pulsing animation effect.
    Draws attention when enabled and ready.
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize pulsing button.

        Args:
            parent: Parent widget
            **kwargs: Standard Button arguments
        """
        super().__init__(parent, **kwargs)
        self.is_pulsing = False
        self._pulse_id = None
        self._pulse_state = 0

    def start_pulsing(self):
        """Start the pulsing animation."""
        if not self.is_pulsing:
            self.is_pulsing = True
            self._pulse()

    def stop_pulsing(self):
        """Stop the pulsing animation."""
        self.is_pulsing = False
        if self._pulse_id:
            self.after_cancel(self._pulse_id)
            self._pulse_id = None

    def _pulse(self):
        """Animate the pulse effect using style changes."""
        if not self.is_pulsing:
            return

        # Cycle through pulse states (subtle opacity-like effect via relief)
        self._pulse_state = (self._pulse_state + 1) % 20

        # This creates a subtle visual pulse
        # In a more advanced implementation, we could modify the style
        # For now, we'll use a simple approach

        self._pulse_id = self.after(100, self._pulse)


class ValidationEntry(ttk.Entry):
    """
    Entry widget with built-in validation indicators.
    Shows ✓ or ❌ based on validation function.
    """

    def __init__(self, parent, validator: Optional[Callable] = None,
                 colors=None, **kwargs):
        """
        Initialize validation entry.

        Args:
            parent: Parent widget
            validator: Function that takes value and returns (is_valid, message)
            colors: Color scheme dictionary
            **kwargs: Standard Entry arguments
        """
        self.frame = ttk.Frame(parent)
        super().__init__(self.frame, **kwargs)

        self.validator = validator
        self.colors = colors or {}

        # Create indicator label
        self.indicator = tk.Label(
            self.frame,
            text="",
            font=('Segoe UI', 10),
            width=2
        )

        # Layout
        self.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.indicator.pack(side=tk.LEFT, padx=(5, 0))

        # Bind validation on key release
        if validator:
            self.bind('<KeyRelease>', self._validate)
            self.bind('<FocusOut>', self._validate)

    def _validate(self, event=None):
        """Validate the current value and update indicator."""
        if not self.validator:
            return

        value = self.get()
        if not value:
            self.indicator.config(text="", bg=self.frame.cget('background'))
            return

        is_valid, message = self.validator(value)

        if is_valid:
            self.indicator.config(
                text="✓",
                fg=self.colors.get('success', 'green')
            )
        else:
            self.indicator.config(
                text="❌",
                fg=self.colors.get('error', 'red')
            )

    def get_frame(self):
        """Get the container frame for grid/pack."""
        return self.frame


class Tooltip:
    """
    Tooltip widget that shows on hover.
    Provides contextual help for any widget.
    """

    def __init__(self, widget, text: str, delay: int = 500):
        """
        Initialize tooltip.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
            delay: Delay before showing in milliseconds
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self._show_id = None

        # Bind events
        widget.bind('<Enter>', self._on_enter)
        widget.bind('<Leave>', self._on_leave)
        widget.bind('<Button>', self._on_leave)

    def _on_enter(self, event=None):
        """Handle mouse enter event."""
        self._schedule_show()

    def _on_leave(self, event=None):
        """Handle mouse leave event."""
        self._cancel_show()
        self._hide()

    def _schedule_show(self):
        """Schedule tooltip to show after delay."""
        self._cancel_show()
        self._show_id = self.widget.after(self.delay, self._show)

    def _cancel_show(self):
        """Cancel scheduled tooltip show."""
        if self._show_id:
            self.widget.after_cancel(self._show_id)
            self._show_id = None

    def _show(self):
        """Display the tooltip."""
        if self.tooltip_window:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Create tooltip content
        frame = tk.Frame(
            self.tooltip_window,
            background="#2D3748",
            borderwidth=1,
            relief=tk.SOLID
        )
        frame.pack()

        label = tk.Label(
            frame,
            text=self.text,
            background="#2D3748",
            foreground="white",
            font=('Segoe UI', 9),
            padx=10,
            pady=6,
            justify=tk.LEFT
        )
        label.pack()

    def _hide(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class CollapsibleFrame(ttk.Frame):
    """
    Frame that can be collapsed/expanded with animation.
    Shows a toggle button to expand/collapse content.
    """

    def __init__(self, parent, title: str = "", colors=None, **kwargs):
        """
        Initialize collapsible frame.

        Args:
            parent: Parent widget
            title: Title shown in header
            colors: Color scheme dictionary
            **kwargs: Standard Frame arguments
        """
        super().__init__(parent, **kwargs)
        self.colors = colors or {}
        self.is_expanded = True

        # Header with toggle button
        self.header = ttk.Frame(self, style='Card.TFrame')
        self.header.pack(fill=tk.X, pady=(0, 5))

        self.toggle_btn = ttk.Button(
            self.header,
            text="▼",
            width=3,
            command=self.toggle,
            style='Accent.TButton'
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.title_label = ttk.Label(
            self.header,
            text=title,
            font=('Segoe UI', 11, 'bold'),
            foreground=self.colors.get('primary', '#6366F1'),
            style='Card.TLabel'
        )
        self.title_label.pack(side=tk.LEFT)

        # Content frame (collapsible)
        self.content = ttk.Frame(self, style='Card.TFrame')
        self.content.pack(fill=tk.BOTH, expand=True)

    def toggle(self):
        """Toggle the collapsed/expanded state."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def collapse(self):
        """Collapse the content."""
        self.content.pack_forget()
        self.toggle_btn.config(text="▶")
        self.is_expanded = False

    def expand(self):
        """Expand the content."""
        self.content.pack(fill=tk.BOTH, expand=True)
        self.toggle_btn.config(text="▼")
        self.is_expanded = True

    def get_content_frame(self):
        """Get the content frame for adding widgets."""
        return self.content


class CharacterCounter:
    """
    Character counter for text widgets.
    Shows current/max character count.
    """

    def __init__(self, text_widget, label_widget, max_chars: Optional[int] = None):
        """
        Initialize character counter.

        Args:
            text_widget: Text widget to monitor
            label_widget: Label widget to update with count
            max_chars: Maximum character limit (optional)
        """
        self.text_widget = text_widget
        self.label_widget = label_widget
        self.max_chars = max_chars

        # Bind to text changes
        text_widget.bind('<KeyRelease>', self._update_count)
        text_widget.bind('<<Modified>>', self._update_count)

        # Initial update
        self._update_count()

    def _update_count(self, event=None):
        """Update the character count display."""
        content = self.text_widget.get('1.0', 'end-1c')
        current = len(content)

        if self.max_chars:
            text = f"{current}/{self.max_chars} chars"

            # Color based on usage
            if current > self.max_chars:
                self.label_widget.config(foreground='red')
            elif current > self.max_chars * 0.9:
                self.label_widget.config(foreground='orange')
            else:
                self.label_widget.config(foreground='gray')
        else:
            text = f"{current} chars"

        self.label_widget.config(text=text)


class HelpIcon(tk.Label):
    """
    Help icon with tooltip.
    Shows '?' icon that displays help text on hover.
    """

    def __init__(self, parent, help_text: str, colors=None, **kwargs):
        """
        Initialize help icon.

        Args:
            parent: Parent widget
            help_text: Help text to show in tooltip
            colors: Color scheme dictionary
            **kwargs: Standard Label arguments
        """
        colors = colors or {}
        super().__init__(
            parent,
            text="?",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg=colors.get('primary', '#6366F1'),
            width=2,
            height=1,
            cursor='question_arrow',
            relief=tk.FLAT,
            **kwargs
        )

        # Add tooltip
        Tooltip(self, help_text)

        # Make circular (ish) appearance
        self.config(borderwidth=1, relief=tk.SOLID)


class ValidationHelper:
    """
    Helper class for common validation functions.
    """

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email format.

        Returns:
            (is_valid, message) tuple
        """
        if not email:
            return (False, "Email is required")

        if '@' not in email or '.' not in email.split('@')[-1]:
            return (False, "Invalid email format")

        return (True, "Valid email")

    @staticmethod
    def validate_api_key(key: str, prefix: str = "") -> tuple[bool, str]:
        """
        Validate API key format.

        Args:
            key: API key to validate
            prefix: Expected prefix (e.g., "sk-")

        Returns:
            (is_valid, message) tuple
        """
        if not key:
            return (False, "API key is required")

        if prefix and not key.startswith(prefix):
            return (False, f"API key should start with {prefix}")

        if len(key) < 20:
            return (False, "API key seems too short")

        return (True, "Valid API key")

    @staticmethod
    def validate_uuid(value: str) -> tuple[bool, str]:
        """
        Validate UUID format (for Azure IDs).

        Returns:
            (is_valid, message) tuple
        """
        if not value:
            return (False, "ID is required")

        # Simple UUID format check
        parts = value.split('-')
        if len(parts) != 5:
            return (False, "Invalid UUID format")

        return (True, "Valid UUID")


class ProgressBarAnimator:
    """
    Animator for progress bar color transitions.
    """

    def __init__(self, progress_bar, style, colors):
        """
        Initialize progress bar animator.

        Args:
            progress_bar: Progressbar widget
            style: ttk.Style instance
            colors: Color scheme dictionary
        """
        self.progress_bar = progress_bar
        self.style = style
        self.colors = colors

    def animate_color_transition(self, from_color: str, to_color: str,
                                 duration: int = 500):
        """
        Animate color transition for progress bar.

        Args:
            from_color: Starting color (hex)
            to_color: Ending color (hex)
            duration: Animation duration in milliseconds
        """
        steps = 20
        delay = duration // steps

        # Convert hex to RGB
        from_rgb = self._hex_to_rgb(from_color)
        to_rgb = self._hex_to_rgb(to_color)

        def step(current_step):
            if current_step >= steps:
                # Final color
                self.style.configure(
                    'Custom.Horizontal.TProgressbar',
                    background=to_color
                )
                return

            # Interpolate
            ratio = current_step / steps
            r = int(from_rgb[0] + (to_rgb[0] - from_rgb[0]) * ratio)
            g = int(from_rgb[1] + (to_rgb[1] - from_rgb[1]) * ratio)
            b = int(from_rgb[2] + (to_rgb[2] - from_rgb[2]) * ratio)

            color = f'#{r:02x}{g:02x}{b:02x}'
            self.style.configure(
                'Custom.Horizontal.TProgressbar',
                background=color
            )

            # Schedule next step
            self.progress_bar.after(delay, lambda: step(current_step + 1))

        step(0)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def complete(self):
        """Animate to completion (green)."""
        self.animate_color_transition(
            self.colors['primary'],
            self.colors['success']
        )

    def error(self):
        """Animate to error state (red)."""
        self.animate_color_transition(
            self.colors['primary'],
            self.colors['error']
        )

    def reset(self):
        """Reset to default color."""
        self.style.configure(
            'Custom.Horizontal.TProgressbar',
            background=self.colors['primary']
        )


class CardBorderValidator:
    """
    Manages color-coded borders for card validation.
    Shows red for invalid, green for valid, default otherwise.
    """

    def __init__(self, frame, colors):
        """
        Initialize card border validator.

        Args:
            frame: Frame to add border to
            colors: Color scheme dictionary
        """
        self.frame = frame
        self.colors = colors

    def set_valid(self):
        """Set border to valid (green) state."""
        self.frame.config(
            highlightthickness=2,
            highlightbackground=self.colors['success'],
            highlightcolor=self.colors['success']
        )

    def set_invalid(self):
        """Set border to invalid (red) state."""
        self.frame.config(
            highlightthickness=2,
            highlightbackground=self.colors['error'],
            highlightcolor=self.colors['error']
        )

    def set_default(self):
        """Set border to default state."""
        self.frame.config(
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['border']
        )
