import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional
import threading

from storage import Storage
from capture import ScreenCapture
from ocr_processor import OCRProcessor
from region_selector import select_region_simple
from game_detector import GameDetector


class CashTrackerGUI:
    """Main GUI for the Cash Tracker application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cash Tracker")
        self.root.geometry("600x700")

        # Initialize components
        self.storage = Storage()
        self.screen_capture = ScreenCapture()
        self.ocr = OCRProcessor()

        # Initialize game detector
        games_config = self.storage.get_all_games()
        self.game_detector = GameDetector(games_config)
        self.current_game_id = None

        # Game colors for UI
        self.game_colors = {
            1: "#4CAF50",  # Green - Genshin Impact
            2: "#2196F3",  # Blue - Honkai Star Rail
            3: "#FF9800",  # Orange - Zenless Zone Zero
            4: "#9C27B0"   # Purple - Wuthering Waves
        }

        # Setup UI
        self._setup_ui()
        self._load_history()

        # Setup hotkey (will be implemented with pynput)
        self._setup_hotkey()

        # Start periodic game detection
        self._update_game_status()

        # Apply settings
        if self.storage.get_always_on_top():
            self.root.attributes('-topmost', True)

    def _setup_ui(self):
        """Setup the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=settings_menu)
        settings_menu.add_command(label="Configurar Jogos", command=self._configure_games)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(
            label="Sempre no Topo",
            command=self._toggle_always_on_top
        )
        settings_menu.add_separator()
        settings_menu.add_command(label="Testar OCR", command=self._test_ocr)

        # Data menu
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dados", menu=data_menu)
        data_menu.add_command(label="Exportar para CSV", command=self._export_csv)
        data_menu.add_command(label="Limpar Histórico", command=self._clear_history)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about)

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== Game Status Indicator =====
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(status_frame, text="Jogo Ativo:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.game_status_label = tk.Label(
            status_frame,
            text="Detectando...",
            font=("Arial", 10),
            fg="gray"
        )
        self.game_status_label.pack(side=tk.LEFT)

        # ===== 4-Game Comparison View =====
        comparison_frame = ttk.LabelFrame(main_frame, text="Comparação dos Jogos", padding="10")
        comparison_frame.pack(fill=tk.X, pady=(0, 10))

        # Create 4 columns for the games
        self.game_widgets = {}
        for game_id in range(1, 5):
            game_col = ttk.Frame(comparison_frame)
            game_col.grid(row=0, column=game_id-1, padx=5, sticky=tk.N+tk.S+tk.E+tk.W)
            comparison_frame.columnconfigure(game_id-1, weight=1)

            # Game name
            game_config = self.storage.get_game_config(game_id)
            game_name = game_config.get("name", f"Jogo {game_id}") if game_config else f"Jogo {game_id}"

            name_label = tk.Label(
                game_col,
                text=game_name,
                font=("Arial", 10, "bold"),
                fg=self.game_colors[game_id]
            )
            name_label.pack()

            # Last value
            value_label = tk.Label(
                game_col,
                text="---",
                font=("Arial", 20, "bold"),
                fg=self.game_colors[game_id]
            )
            value_label.pack()

            # Timestamp
            time_label = tk.Label(
                game_col,
                text="---",
                font=("Arial", 8),
                fg="gray"
            )
            time_label.pack()

            # Stats
            stats_frame = ttk.Frame(game_col)
            stats_frame.pack(pady=(5, 0))

            total_label = ttk.Label(stats_frame, text="Total: 0", font=("Arial", 8))
            total_label.pack()

            count_label = ttk.Label(stats_frame, text="Count: 0", font=("Arial", 8))
            count_label.pack()

            # Store widgets for later updates
            self.game_widgets[game_id] = {
                "name": name_label,
                "value": value_label,
                "time": time_label,
                "total": total_label,
                "count": count_label
            }

        # ===== Capture Button =====
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.capture_btn = tk.Button(
            button_frame,
            text="CAPTURAR (F9)",
            command=self._capture_value,
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2,
            cursor="hand2"
        )
        self.capture_btn.pack(fill=tk.X)

        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="",
            font=("Arial", 9),
            fg="blue"
        )
        self.status_label.pack(pady=(5, 0))

        # ===== History Table =====
        history_frame = ttk.LabelFrame(main_frame, text="Histórico de Capturas", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ("ID", "Jogo", "Valor", "Data/Hora")
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )

        # Configure columns
        self.history_tree.heading("ID", text="ID")
        self.history_tree.heading("Jogo", text="Jogo")
        self.history_tree.heading("Valor", text="Valor")
        self.history_tree.heading("Data/Hora", text="Data/Hora")

        self.history_tree.column("ID", width=50, anchor=tk.CENTER)
        self.history_tree.column("Jogo", width=120, anchor=tk.W)
        self.history_tree.column("Valor", width=120, anchor=tk.E)
        self.history_tree.column("Data/Hora", width=150, anchor=tk.CENTER)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)

        # Context menu for history
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Deletar", command=self._delete_selected)
        self.history_tree.bind("<Button-3>", self._show_context_menu)

    def _setup_hotkey(self):
        """Setup global hotkeys (F9 manual, F3/F4 auto-capture)."""
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    # F9 = Manual capture (immediate)
                    if key == keyboard.Key.f9:
                        self.root.after(0, self._capture_value)

                    # F3/F4 = Auto-capture with delay (for game screens)
                    elif key == keyboard.Key.f3 or key == keyboard.Key.f4:
                        # Check if current game uses this key
                        if self.current_game_id:
                            game_config = self.storage.get_game_config(self.current_game_id)
                            if game_config:
                                auto_key = game_config.get("auto_capture_key", "").lower()
                                key_name = key.name.lower()

                                if auto_key == key_name:
                                    delay = game_config.get("auto_capture_delay", 3) * 1000  # Convert to ms
                                    self.root.after(0, lambda: self._set_status(f"Auto-captura em {delay//1000}s..."))
                                    self.root.after(delay, self._capture_value)

                except AttributeError:
                    pass

            # Start listener in background thread
            listener = keyboard.Listener(on_press=on_press)
            listener.daemon = True
            listener.start()

        except ImportError:
            print("Warning: pynput not installed. Hotkey support disabled.")
        except Exception as e:
            print(f"Warning: Could not setup hotkey: {e}")

    def _update_game_status(self):
        """Update game status indicator periodically."""
        try:
            # Refresh game configs in case they changed
            games_config = self.storage.get_all_games()
            self.game_detector = GameDetector(games_config)

            # Detect active game
            active_game_id = self.game_detector.get_active_game()

            if active_game_id:
                self.current_game_id = active_game_id
                game_config = self.storage.get_game_config(active_game_id)
                game_name = game_config.get("name", f"Jogo {active_game_id}") if game_config else f"Jogo {active_game_id}"
                process_name = game_config.get("process_name", "?") if game_config else "?"

                self.game_status_label.config(
                    text=f"{game_name} ({process_name})",
                    fg=self.game_colors.get(active_game_id, "black")
                )
            else:
                self.current_game_id = None
                self.game_status_label.config(text="Nenhum jogo detectado", fg="gray")

        except Exception as e:
            print(f"Error updating game status: {e}")

        # Schedule next update (every 2 seconds)
        self.root.after(2000, self._update_game_status)

    def _configure_games(self):
        """Open game configuration dialog."""
        # Simple placeholder - just show message for now
        messagebox.showinfo(
            "Configuração de Jogos",
            "Funcionalidade em desenvolvimento.\n\n"
            "Os 4 jogos estão pré-configurados:\n"
            "1. Genshin Impact\n"
            "2. Honkai Star Rail\n"
            "3. Zenless Zone Zero\n"
            "4. Wuthering Waves\n\n"
            "Configure as regiões de captura através do menu quando cada jogo estiver aberto."
        )

    def _capture_value(self):
        """Capture value from configured region."""
        # Detect active game
        if not self.current_game_id:
            messagebox.showerror(
                "Nenhum Jogo Detectado",
                "Nenhum dos jogos configurados está rodando no momento.\n\n"
                "Certifique-se de que um dos seguintes jogos está aberto:\n"
                "- Genshin Impact\n"
                "- Honkai Star Rail\n"
                "- Zenless Zone Zero\n"
                "- Wuthering Waves"
            )
            return

        # Check if region is configured for this game
        game_config = self.storage.get_game_config(self.current_game_id)
        if not game_config or not game_config.get("region"):
            response = messagebox.askyesno(
                "Região não configurada",
                f"A região de captura para {game_config.get('name', 'este jogo')} ainda não foi configurada.\n\n"
                "Deseja configurar agora?"
            )
            if response:
                # TODO: Open region selector for this specific game
                messagebox.showinfo("Em desenvolvimento", "Configuração de região por jogo em breve!")
            return

        self._set_status("Capturando...")
        self.capture_btn.config(state=tk.DISABLED)

        # Perform capture in background thread
        thread = threading.Thread(target=self._do_capture, daemon=True)
        thread.start()

    def _do_capture(self):
        """Perform the actual capture (runs in background thread)."""
        try:
            # Get region coordinates for current game
            game_config = self.storage.get_game_config(self.current_game_id)
            region = game_config.get("region")

            if not region:
                self.root.after(0, lambda: self._capture_failed("Região não configurada"))
                return

            x = region["x"]
            y = region["y"]
            width = region["width"]
            height = region["height"]

            # Capture screen region
            image = self.screen_capture.capture_region(x, y, width, height)

            if image is None:
                self.root.after(0, lambda: self._capture_failed("Falha ao capturar tela"))
                return

            # Preprocess for better OCR
            image = self.screen_capture.preprocess_for_ocr(image)

            # Save debug image (optional)
            # self.screen_capture.save_debug_image(image, "last_capture.png")

            # Extract number using OCR
            value = self.ocr.extract_number(image, debug=True)

            if value is None:
                self.root.after(0, lambda: self._capture_failed("Não foi possível ler o número"))
                return

            # Save to storage with game_id
            capture_id = self.storage.save_capture(value, game_id=self.current_game_id)

            # Update UI in main thread
            self.root.after(0, lambda: self._capture_success(value))

        except Exception as e:
            self.root.after(0, lambda: self._capture_failed(f"Erro: {str(e)}"))

    def _capture_success(self, value: float):
        """Handle successful capture."""
        self._set_status(f"Capturado: {value:,.2f}")
        self.capture_btn.config(state=tk.NORMAL)
        self._load_history()

    def _capture_failed(self, message: str):
        """Handle failed capture."""
        self._set_status(message)
        self.capture_btn.config(state=tk.NORMAL)
        messagebox.showerror("Erro na Captura", message)

    def _load_history(self):
        """Load and display capture history."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Load history
        history = self.storage.load_history(limit=100)

        # Populate tree
        for capture in history:
            game_id = capture.get("game_id", 1)
            game_config = self.storage.get_game_config(game_id)
            game_name = game_config.get("name", f"Jogo {game_id}") if game_config else f"Jogo {game_id}"

            self.history_tree.insert(
                "",
                tk.END,
                values=(
                    capture["id"],
                    game_name,
                    f"{capture['value']:,.2f}",
                    capture["timestamp"]
                ),
                tags=(f"game_{game_id}",)
            )

        # Color rows by game
        for game_id in range(1, 5):
            self.history_tree.tag_configure(
                f"game_{game_id}",
                foreground=self.game_colors.get(game_id, "black")
            )

        # Update comparison view for all games
        self._update_comparison_view()

    def _update_comparison_view(self):
        """Update the 4-game comparison view."""
        all_stats = self.storage.get_stats_all_games()

        for game_id in range(1, 5):
            stats = all_stats.get(game_id, {})
            last_capture = self.storage.get_last_capture(game_id=game_id)

            widgets = self.game_widgets.get(game_id)
            if not widgets:
                continue

            # Update last value
            if last_capture:
                widgets["value"].config(text=f"{last_capture['value']:,.2f}")
                # Extract just time from timestamp
                timestamp = last_capture.get('timestamp', '')
                time_part = timestamp.split()[1] if len(timestamp.split()) > 1 else timestamp
                widgets["time"].config(text=time_part)
            else:
                widgets["value"].config(text="---")
                widgets["time"].config(text="---")

            # Update stats
            widgets["total"].config(text=f"Total: {stats.get('total', 0):,.0f}")
            widgets["count"].config(text=f"Capturas: {stats.get('count', 0)}")

    def _show_context_menu(self, event):
        """Show context menu for history items."""
        # Select item under cursor
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _delete_selected(self):
        """Delete selected history item."""
        selection = self.history_tree.selection()
        if not selection:
            return

        # Get capture ID
        item = selection[0]
        values = self.history_tree.item(item, "values")
        capture_id = int(values[0])

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deletar captura #{capture_id}?"
        )

        if response:
            self.storage.delete_capture(capture_id)
            self._load_history()
            self._set_status(f"Captura #{capture_id} deletada")

    def _toggle_always_on_top(self):
        """Toggle always-on-top setting."""
        current = self.storage.get_always_on_top()
        new_value = not current
        self.storage.update_config(always_on_top=new_value)
        self.root.attributes('-topmost', new_value)

    def _test_ocr(self):
        """Test OCR installation."""
        success, message = self.ocr.test_ocr()
        if success:
            messagebox.showinfo("Teste OCR", message)
        else:
            messagebox.showerror("Erro OCR", message)

    def _export_csv(self):
        """Export history to CSV file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"cash_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if filename:
            try:
                self.storage.export_to_csv(filename)
                messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar:\n{str(e)}")

    def _clear_history(self):
        """Clear all capture history."""
        response = messagebox.askyesno(
            "Confirmar",
            "Tem certeza que deseja limpar todo o histórico?\n\n"
            "Esta ação não pode ser desfeita!"
        )

        if response:
            self.storage.clear_history()
            self._load_history()
            self._set_status("Histórico limpo")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "Sobre Cash Tracker",
            "Cash Tracker v2.0 - Multi-Jogos\n\n"
            "Captura automática de valores para 4 jogos:\n"
            "• Genshin Impact\n"
            "• Honkai Star Rail\n"
            "• Zenless Zone Zero\n"
            "• Wuthering Waves\n\n"
            "Atalhos:\n"
            "F3 (Genshin/HSR/WuWa) - Auto-captura\n"
            "F4 (Zenless) - Auto-captura\n"
            "F9 - Captura manual\n\n"
            "Desenvolvido com Python + Tkinter + Tesseract OCR"
        )

    def _set_status(self, message: str):
        """Set status message."""
        self.status_label.config(text=message)

    def run(self):
        """Start the application."""
        # Welcome message on first run
        games = self.storage.get_all_games()
        any_configured = any(g.get("region") for g in games.values() if g)

        if not any_configured:
            messagebox.showinfo(
                "Bem-vindo ao Cash Tracker Multi-Jogos!",
                "Bem-vindo ao Cash Tracker!\n\n"
                "Este app detecta automaticamente qual dos 4 jogos está rodando:\n"
                "• Genshin Impact\n"
                "• Honkai Star Rail\n"
                "• Zenless Zone Zero\n"
                "• Wuthering Waves\n\n"
                "ATALHOS:\n"
                "• F3 (Genshin/HSR/WuWa) = Auto-captura após 3s\n"
                "• F4 (Zenless) = Auto-captura após 3s\n"
                "• F9 = Captura manual imediata\n\n"
                "Configure as regiões de captura quando cada jogo estiver aberto."
            )

        self.root.mainloop()
