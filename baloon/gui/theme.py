"""
Налаштування теми для GUI
"""

import tkinter as tk
from tkinter import ttk


def setup_dark_theme(root: tk.Tk):
    """Налаштування темної теми"""
    # Базова сучасна палітра
    style = ttk.Style()
    style.theme_use('clam')
    
    # Кольори для темної теми
    bg_color = "#2b2b2b"
    fg_color = "#ffffff"
    entry_bg = "#1e1e1e"
    select_bg = "#404040"
    accent = "#4a90e2"
    card_bg = "#303030"
    
    # Налаштування стилів
    default_font = ("Segoe UI", 10)
    root.option_add("*Font", default_font)
    
    style.configure('TFrame', background=bg_color)
    style.configure('Card.TFrame', background=card_bg, relief="ridge")
    style.configure('TLabel', background=bg_color, foreground=fg_color)
    style.configure('Heading.TLabel', background=bg_color, foreground=fg_color, font=("Segoe UI Semibold", 12))
    style.configure('Subheading.TLabel', background=bg_color, foreground=fg_color, font=("Segoe UI Semibold", 11))
    
    style.configure('TButton', background="#3a3a3a", foreground=fg_color, padding=6)
    style.map('TButton',
              background=[('active', '#4b4b4b'), ('pressed', '#2f2f2f')])
    
    style.configure('Accent.TButton', background=accent, foreground="#ffffff", padding=7)
    style.map('Accent.TButton',
              background=[('active', '#5aa1f3'), ('pressed', '#3b7ccc')])
    
    style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color,
                   bordercolor="#555555", insertcolor=fg_color, padding=4)
    style.configure('TCombobox', fieldbackground=entry_bg, foreground=fg_color,
                   bordercolor="#555555", arrowcolor=fg_color, padding=4)
    style.map('TCombobox',
              fieldbackground=[('readonly', entry_bg), ('!disabled', entry_bg)],
              foreground=[('readonly', fg_color), ('!disabled', fg_color)],
              selectbackground=[('readonly', entry_bg)],
              selectforeground=[('readonly', fg_color)],
              background=[('readonly', entry_bg)])
    style.configure('TRadiobutton', background=bg_color, foreground=fg_color,
                   selectcolor=select_bg)
    style.configure('TSeparator', background="#555555")
    style.configure('TNotebook', background=bg_color, borderwidth=0)
    style.configure('TNotebook.Tab', background="#404040", foreground=fg_color,
                   padding=[10, 5])
    style.map('TNotebook.Tab',
              background=[('selected', bg_color)],
              expand=[('selected', [1, 1, 1, 0])])
    
    # Налаштування фону головного вікна
    root.configure(bg=bg_color)

