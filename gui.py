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


class NtropyGUI:
    """Main GUI for the Ntropy application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ntropy")
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
        data_menu.add_command(label="Ver Objetivos", command=self._show_objectives)
        data_menu.add_separator()
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

        # Check if both regions are configured for this game
        game_config = self.storage.get_game_config(self.current_game_id)
        region_conv = game_config.get("region_converted") if game_config else None
        region_int = game_config.get("region_integer") if game_config else None

        if not region_conv or not region_int:
            missing = []
            if not region_conv:
                missing.append("Valores Convertidos")
            if not region_int:
                missing.append("Valores Inteiros")

            response = messagebox.askyesno(
                "Regiões não configuradas",
                f"As seguintes regiões precisam ser configuradas para {game_config.get('name', 'este jogo')}:\n"
                f"• {' e '.join(missing)}\n\n"
                "Deseja configurar agora?"
            )
            if response:
                # TODO: Open region selector for this specific game
                messagebox.showinfo("Em desenvolvimento", "Configuração de regiões por jogo em breve!")
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
            region_converted = game_config.get("region_converted")
            region_integer = game_config.get("region_integer")

            if not region_converted or not region_integer:
                self.root.after(0, lambda: self._capture_failed("Regiões não configuradas. Configure ambas as regiões."))
                return

            # Get conversion ratio
            ratio = self.storage.get_conversion_ratio()

            # === CAPTURE CONVERTED VALUES ===
            image_conv = self.screen_capture.capture_region(
                region_converted["x"],
                region_converted["y"],
                region_converted["width"],
                region_converted["height"]
            )

            if image_conv is None:
                self.root.after(0, lambda: self._capture_failed("Falha ao capturar valores convertidos"))
                return

            image_conv = self.screen_capture.preprocess_for_ocr(image_conv)
            value_converted = self.ocr.extract_number(image_conv, debug=True)

            if value_converted is None:
                value_converted = 0  # Se não conseguir ler, assume 0

            # === CAPTURE INTEGER VALUES ===
            image_int = self.screen_capture.capture_region(
                region_integer["x"],
                region_integer["y"],
                region_integer["width"],
                region_integer["height"]
            )

            if image_int is None:
                self.root.after(0, lambda: self._capture_failed("Falha ao capturar valores inteiros"))
                return

            image_int = self.screen_capture.preprocess_for_ocr(image_int)
            value_integer = self.ocr.extract_number(image_int, debug=True)

            if value_integer is None:
                value_integer = 0  # Se não conseguir ler, assume 0

            # === CALCULATE TOTAL ===
            # Formula: Total = Converted + (Integer / 160)
            total_value = value_converted + (value_integer / ratio)

            print(f"Convertidos: {value_converted}")
            print(f"Inteiros: {value_integer}")
            print(f"Cálculo: {value_converted} + ({value_integer} / {ratio}) = {total_value}")

            # Save to storage with game_id
            capture_id = self.storage.save_capture(total_value, game_id=self.current_game_id)

            # Update UI in main thread
            self.root.after(0, lambda: self._capture_success(total_value))

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
            initialfile=f"ntropy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
            "Sobre Ntropy",
            "Ntropy v2.0 - Multi-Jogos\n\n"
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

    def _show_objectives(self):
        """Show objectives window."""
        ObjectivesWindow(self.root, self.storage)

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
                "Bem-vindo ao Ntropy Multi-Jogos!",
                "Bem-vindo ao Ntropy!\n\n"
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


class ObjectivesWindow:
    """Window to view and manage objectives across all games."""

    def __init__(self, parent, storage: Storage):
        self.storage = storage
        self.window = tk.Toplevel(parent)
        self.window.title("Objetivos - Gacha Tracker")
        self.window.geometry("950x650")
        self.window.transient(parent)

        # Game colors
        self.game_colors = {
            1: "#4CAF50",  # Green - Genshin Impact
            2: "#2196F3",  # Blue - Honkai Star Rail
            3: "#FF9800",  # Orange - Zenless Zone Zero
            4: "#9C27B0"   # Purple - Wuthering Waves
        }

        # Temporary injected values (game_id -> pulls)
        self.injected_values = {}

        self._setup_ui()
        self._load_objectives()

    def _setup_ui(self):
        """Setup the objectives window UI."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🎯 Objetivos por Jogo",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Simulation frame
        sim_frame = ttk.LabelFrame(main_frame, text="🧪 Simulação de Pulls (temporário)", padding="10")
        sim_frame.pack(fill=tk.X, pady=(0, 10))

        sim_info = ttk.Frame(sim_frame)
        sim_info.pack(fill=tk.X)

        ttk.Label(
            sim_info,
            text="Jogo:",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.sim_game_var = tk.StringVar()
        sim_game_combo = ttk.Combobox(
            sim_info,
            textvariable=self.sim_game_var,
            state="readonly",
            width=20,
            font=("Arial", 9)
        )
        games = self.storage.get_all_games()
        game_options = [f"{game_id}: {config['name']}" for game_id, config in games.items()]
        sim_game_combo['values'] = game_options
        if game_options:
            sim_game_combo.current(0)
        sim_game_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(
            sim_info,
            text="Pulls:",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.sim_pulls_entry = ttk.Entry(sim_info, width=10, font=("Arial", 9))
        self.sim_pulls_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.sim_pulls_entry.insert(0, "0")

        apply_btn = tk.Button(
            sim_info,
            text="✓ Aplicar",
            command=self._apply_simulation,
            font=("Arial", 9, "bold"),
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = tk.Button(
            sim_info,
            text="✗ Limpar",
            command=self._clear_simulation,
            font=("Arial", 9),
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT)

        # Status label for simulation
        self.sim_status_label = tk.Label(
            sim_frame,
            text="Use valores temporários para simular probabilidades sem capturar da tela",
            font=("Arial", 8),
            fg="gray"
        )
        self.sim_status_label.pack(pady=(5, 0))

        # Scrollable frame for objectives
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.objectives_container = scrollable_frame

        # Bottom buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        add_btn = tk.Button(
            button_frame,
            text="➕ Adicionar Objetivo",
            command=self._add_objective,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Atualizar",
            command=self._load_objectives,
            font=("Arial", 12),
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

    def _apply_simulation(self):
        """Apply simulated pulls value for a game."""
        game_str = self.sim_game_var.get()
        if not game_str:
            messagebox.showerror("Erro", "Selecione um jogo")
            return

        game_id = int(game_str.split(":")[0])

        try:
            pulls = float(self.sim_pulls_entry.get().strip())
            if pulls < 0:
                messagebox.showerror("Erro", "Digite um valor positivo")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido")
            return

        # Store injected value
        self.injected_values[game_id] = pulls

        # Update status
        game_name = self.storage.get_game_config(game_id)["name"]
        self.sim_status_label.config(
            text=f"✓ Simulando {pulls:.1f} pulls para {game_name}",
            fg="green"
        )

        # Reload objectives to show updated probabilities
        self._load_objectives()

    def _clear_simulation(self):
        """Clear all simulated values and return to real captured values."""
        if not self.injected_values:
            messagebox.showinfo("Info", "Nenhuma simulação ativa")
            return

        self.injected_values.clear()
        self.sim_pulls_entry.delete(0, tk.END)
        self.sim_pulls_entry.insert(0, "0")

        self.sim_status_label.config(
            text="Simulação limpa. Usando valores reais capturados.",
            fg="blue"
        )

        # Reload objectives
        self._load_objectives()

    def _get_current_pulls(self, game_id: int) -> float:
        """Get current pulls for a game, considering injected values."""
        # Check if there's an injected value
        if game_id in self.injected_values:
            return self.injected_values[game_id]

        # Otherwise, use real captured value
        last_capture = self.storage.get_last_capture(game_id=game_id)
        return last_capture.get("value", 0) if last_capture else 0

    def _calculate_objective_progress(self, objective: dict, current_pulls: float) -> dict:
        """Calculate progress for an objective with given pulls amount."""
        pulls_needed = objective.get("pulls_needed", 180)
        current_pity = objective.get("current_pity", 0)
        guaranteed = objective.get("guaranteed", False)

        # Calculate basic progress
        progress_percent = (current_pulls / pulls_needed * 100) if pulls_needed > 0 else 0
        progress_percent = min(progress_percent, 100)

        remaining = max(pulls_needed - current_pulls, 0)

        # Calculate real probability using gacha calculator
        try:
            from gacha_probability import get_calculator
            calc = get_calculator()
            prob_info = calc.get_probability_explanation(
                int(current_pulls),
                current_pity,
                guaranteed
            )

            real_probability = prob_info["percentage"]
            probability_explanation = prob_info["explanation"]
        except Exception:
            real_probability = progress_percent
            probability_explanation = "Cálculo simples (pulls / total)"

        return {
            "objective": objective,
            "current_pulls": current_pulls,
            "progress_percent": progress_percent,
            "real_probability": real_probability,
            "probability_explanation": probability_explanation,
            "remaining": remaining,
            "is_complete": real_probability >= 99.0
        }

    def _load_objectives(self):
        """Load and display all objectives with progress."""
        # Clear existing widgets
        for widget in self.objectives_container.winfo_children():
            widget.destroy()

        # Get all objectives
        all_objectives = self.storage.get_all_objectives()

        if not all_objectives:
            # No objectives yet
            no_obj_label = tk.Label(
                self.objectives_container,
                text="Nenhum objetivo cadastrado ainda.\n\nClique em 'Adicionar Objetivo' para criar um!",
                font=("Arial", 12),
                fg="gray"
            )
            no_obj_label.pack(pady=50)
            return

        # Display objectives grouped by game
        for game_id in range(1, 5):
            if game_id not in all_objectives:
                continue

            game_config = self.storage.get_game_config(game_id)
            game_name = game_config.get("name", f"Jogo {game_id}")
            game_color = self.game_colors[game_id]

            # Game section
            game_frame = ttk.LabelFrame(
                self.objectives_container,
                text=f"⭐ {game_name}",
                padding="10"
            )
            game_frame.pack(fill=tk.X, pady=(0, 10))

            # Get current pulls for this game (real or injected)
            current_pulls = self._get_current_pulls(game_id)

            # Show if using simulated value
            if game_id in self.injected_values:
                sim_indicator = tk.Label(
                    game_frame,
                    text=f"🧪 SIMULAÇÃO: {current_pulls:.1f} pulls (valor temporário)",
                    font=("Arial", 9, "bold"),
                    fg="orange",
                    bg="#fff3cd",
                    padx=5,
                    pady=3
                )
                sim_indicator.pack(fill=tk.X, pady=(0, 5))

            # Objectives for this game
            for obj in all_objectives[game_id]:
                # Calculate progress with current pulls (real or injected)
                progress_data = self._calculate_objective_progress(obj, current_pulls)
                obj = progress_data["objective"]
                current = progress_data["current_pulls"]
                percent = progress_data["progress_percent"]
                real_prob = progress_data.get("real_probability", percent)
                prob_explanation = progress_data.get("probability_explanation", "")
                remaining = progress_data["remaining"]
                is_complete = progress_data["is_complete"]

                # Objective row
                obj_frame = ttk.Frame(game_frame)
                obj_frame.pack(fill=tk.X, pady=5)

                # Left side: Name and progress bar
                left_frame = ttk.Frame(obj_frame)
                left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

                # Objective name with state
                pity = obj.get("current_pity", 0)
                guaranteed = obj.get("guaranteed", False)
                state_text = " 🎯" if guaranteed else " 🎲"
                state_tooltip = "GARANTIDO" if guaranteed else "50/50"

                name_label = tk.Label(
                    left_frame,
                    text=f"{obj['name']}{state_text}",
                    font=("Arial", 12, "bold"),
                    fg=game_color,
                    anchor="w"
                )
                name_label.pack(anchor="w")

                # State and pity info
                state_info_label = tk.Label(
                    left_frame,
                    text=f"Estado: {state_tooltip}  •  Pity: {pity}/90",
                    font=("Arial", 9),
                    fg="#666",
                    anchor="w"
                )
                state_info_label.pack(anchor="w")

                # Progress info with REAL PROBABILITY
                progress_text = f"{current:.1f} pulls guardados  •  Probabilidade Real: {real_prob:.1f}%"
                if is_complete:
                    progress_text += "  ✓ PRATICAMENTE GARANTIDO"

                progress_label = tk.Label(
                    left_frame,
                    text=progress_text,
                    font=("Arial", 10, "bold"),
                    fg="green" if is_complete else game_color,
                    anchor="w"
                )
                progress_label.pack(anchor="w")

                # Progress bar (usando probabilidade real)
                progress_bar_frame = ttk.Frame(left_frame)
                progress_bar_frame.pack(fill=tk.X, pady=(2, 0))

                canvas_progress = tk.Canvas(
                    progress_bar_frame,
                    height=20,
                    bg="white",
                    highlightthickness=1,
                    highlightbackground="gray"
                )
                canvas_progress.pack(fill=tk.X)

                # Draw progress bar using REAL PROBABILITY
                bar_width = int((real_prob / 100) * canvas_progress.winfo_reqwidth() or 200)
                bar_color = "green" if is_complete else game_color

                canvas_progress.create_rectangle(
                    0, 0, bar_width, 20,
                    fill=bar_color,
                    outline=""
                )

                # Explanation text
                if not is_complete:
                    explanation_parts = prob_explanation.split("\n")
                    main_explanation = explanation_parts[0] if explanation_parts else prob_explanation

                    explanation_label = tk.Label(
                        left_frame,
                        text=f"📊 {main_explanation}",
                        font=("Arial", 9),
                        fg="#666"
                    )
                    explanation_label.pack(anchor="w")

                # Right side: Delete button
                delete_btn = tk.Button(
                    obj_frame,
                    text="🗑️",
                    command=lambda gid=game_id, oid=obj["id"]: self._delete_objective(gid, oid),
                    fg="red",
                    cursor="hand2",
                    width=3
                )
                delete_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def _add_objective(self):
        """Show dialog to add a new objective."""
        AddObjectiveDialog(self.window, self.storage, self._load_objectives)

    def _delete_objective(self, game_id: int, objective_id: str):
        """Delete an objective."""
        obj = None
        for o in self.storage.get_objectives(game_id):
            if o["id"] == objective_id:
                obj = o
                break

        if not obj:
            return

        response = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar o objetivo:\n\n'{obj['name']}'?"
        )

        if response:
            self.storage.remove_objective(game_id, objective_id)
            self._load_objectives()


class AddObjectiveDialog:
    """Dialog to add a new objective."""

    def __init__(self, parent, storage: Storage, callback):
        self.storage = storage
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Objetivo")
        self.dialog.geometry("450x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the add objective dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="➕ Novo Objetivo",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Game selection
        ttk.Label(main_frame, text="Jogo:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.game_var = tk.StringVar()
        game_combo = ttk.Combobox(
            main_frame,
            textvariable=self.game_var,
            state="readonly",
            font=("Arial", 10)
        )

        games = self.storage.get_all_games()
        game_options = [f"{game_id}: {config['name']}" for game_id, config in games.items()]
        game_combo['values'] = game_options
        if game_options:
            game_combo.current(0)
        game_combo.pack(fill=tk.X, pady=(0, 10))

        # Objective name
        ttk.Label(main_frame, text="Nome do Objetivo:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.name_entry = ttk.Entry(main_frame, font=("Arial", 10))
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        self.name_entry.insert(0, "Ex: Klee R1")

        # Pulls needed
        ttk.Label(main_frame, text="Pulls Necessários (máximo):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.pulls_entry = ttk.Entry(main_frame, font=("Arial", 10))
        self.pulls_entry.pack(fill=tk.X, pady=(0, 10))
        self.pulls_entry.insert(0, "180")

        # Current pity
        ttk.Label(main_frame, text="Pity Atual (0-89):", font=("Arial", 10, "bold")).pack(anchor="w")
        pity_frame = ttk.Frame(main_frame)
        pity_frame.pack(fill=tk.X, pady=(0, 10))

        self.pity_entry = ttk.Entry(pity_frame, font=("Arial", 10), width=10)
        self.pity_entry.pack(side=tk.LEFT)
        self.pity_entry.insert(0, "0")

        ttk.Label(
            pity_frame,
            text="  (quantos pulls desde o último 5★)",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.LEFT)

        # Guaranteed checkbox
        self.guaranteed_var = tk.BooleanVar(value=False)
        guaranteed_check = ttk.Checkbutton(
            main_frame,
            text="✓ Próximo 5★ é GARANTIDO (perdeu o 50/50 antes)",
            variable=self.guaranteed_var,
            style="TCheckbutton"
        )
        guaranteed_check.pack(anchor="w", pady=(0, 20))

        # Info label
        info_label = tk.Label(
            main_frame,
            text="💡 O Ntropy calculará a probabilidade real considerando\npity e 50/50 automaticamente!",
            font=("Arial", 9),
            fg="#666",
            justify=tk.LEFT,
            bg="#f0f0f0",
            padx=10,
            pady=5
        )
        info_label.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        save_btn = tk.Button(
            button_frame,
            text="✓ Salvar",
            command=self._save,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = tk.Button(
            button_frame,
            text="✗ Cancelar",
            command=self.dialog.destroy,
            font=("Arial", 11),
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT)

    def _save(self):
        """Save the new objective."""
        # Get selected game ID
        game_str = self.game_var.get()
        if not game_str:
            messagebox.showerror("Erro", "Selecione um jogo")
            return

        game_id = int(game_str.split(":")[0])

        # Get objective name
        name = self.name_entry.get().strip()
        if not name or name == "Ex: Klee R1":
            messagebox.showerror("Erro", "Digite um nome para o objetivo")
            return

        # Get pulls needed
        try:
            pulls_needed = int(self.pulls_entry.get().strip())
            if pulls_needed <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido de pulls (maior que 0)")
            return

        # Get current pity
        try:
            current_pity = int(self.pity_entry.get().strip())
            if current_pity < 0 or current_pity > 89:
                messagebox.showerror("Erro", "Pity deve estar entre 0 e 89")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido para o pity")
            return

        # Get guaranteed status
        guaranteed = self.guaranteed_var.get()

        # Save objective with all parameters
        self.storage.add_objective(game_id, name, pulls_needed, current_pity, guaranteed)

        # Close dialog and refresh parent
        self.dialog.destroy()
        if self.callback:
            self.callback()

        messagebox.showinfo("Sucesso", f"Objetivo '{name}' adicionado com sucesso!")
