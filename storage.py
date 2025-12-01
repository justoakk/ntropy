import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Storage:
    """Handles all data persistence for the Cash Tracker application."""

    def __init__(self, data_file="data.json", config_file="config.json"):
        self.data_file = data_file
        self.config_file = config_file
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Create data and config files if they don't exist."""
        if not os.path.exists(self.data_file):
            self._write_json(self.data_file, {"captures": []})

        if not os.path.exists(self.config_file):
            self._write_json(self.config_file, {
                "games": {
                    "1": {"name": "Genshin Impact", "process_name": "GenshinImpact.exe", "region": None, "auto_capture_key": "f3", "auto_capture_delay": 3},
                    "2": {"name": "Honkai Star Rail", "process_name": "StarRail.exe", "region": None, "auto_capture_key": "f3", "auto_capture_delay": 3},
                    "3": {"name": "Zenless Zone Zero", "process_name": "ZenlessZoneZero.exe", "region": None, "auto_capture_key": "f4", "auto_capture_delay": 3},
                    "4": {"name": "Wuthering Waves", "process_name": "Wuthering Waves.exe", "region": None, "auto_capture_key": "f3", "auto_capture_delay": 3}
                },
                "hotkey": "F9",
                "always_on_top": True
            })
        else:
            # Migrate old format if needed
            self.migrate_old_data()

    def _read_json(self, file_path: str) -> dict:
        """Read and parse JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_json(self, file_path: str, data: dict):
        """Write data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Configuration methods

    def get_config(self) -> dict:
        """Get current configuration."""
        return self._read_json(self.config_file)

    def get_region(self) -> Optional[Dict[str, int]]:
        """Get configured screen region coordinates."""
        config = self.get_config()
        return config.get("region")

    def save_region(self, x: int, y: int, width: int, height: int):
        """Save screen region coordinates."""
        config = self.get_config()
        config["region"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self._write_json(self.config_file, config)

    def get_hotkey(self) -> str:
        """Get configured hotkey."""
        config = self.get_config()
        return config.get("hotkey", "F9")

    def get_always_on_top(self) -> bool:
        """Get always-on-top setting."""
        config = self.get_config()
        return config.get("always_on_top", True)

    def update_config(self, **kwargs):
        """Update configuration with provided key-value pairs."""
        config = self.get_config()
        config.update(kwargs)
        self._write_json(self.config_file, config)

    # Game configuration methods

    def get_all_games(self) -> dict:
        """Get all game configurations."""
        config = self.get_config()
        return config.get("games", {})

    def get_game_config(self, game_id: int) -> Optional[dict]:
        """Get configuration for a specific game."""
        games = self.get_all_games()
        return games.get(str(game_id))

    def save_game_region(self, game_id: int, x: int, y: int, width: int, height: int):
        """Save screen region coordinates for a specific game."""
        config = self.get_config()
        if "games" not in config:
            config["games"] = {}
        if str(game_id) not in config["games"]:
            config["games"][str(game_id)] = {"name": f"Jogo {game_id}", "process_name": "", "region": None}

        config["games"][str(game_id)]["region"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self._write_json(self.config_file, config)

    def update_game(self, game_id: int, **kwargs):
        """Update game configuration with provided key-value pairs."""
        config = self.get_config()
        if "games" not in config:
            config["games"] = {}
        if str(game_id) not in config["games"]:
            config["games"][str(game_id)] = {"name": f"Jogo {game_id}", "process_name": "", "region": None}

        config["games"][str(game_id)].update(kwargs)
        self._write_json(self.config_file, config)

    def save_game_region_converted(self, game_id: int, x: int, y: int, width: int, height: int):
        """Save region coordinates for converted values."""
        config = self.get_config()
        if "games" not in config or str(game_id) not in config["games"]:
            return

        config["games"][str(game_id)]["region_converted"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self._write_json(self.config_file, config)

    def save_game_region_integer(self, game_id: int, x: int, y: int, width: int, height: int):
        """Save region coordinates for integer values."""
        config = self.get_config()
        if "games" not in config or str(game_id) not in config["games"]:
            return

        config["games"][str(game_id)]["region_integer"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self._write_json(self.config_file, config)

    def get_conversion_ratio(self) -> int:
        """Get the conversion ratio (integer / ratio = converted)."""
        config = self.get_config()
        return config.get("conversion_ratio", 160)

    def migrate_old_data(self):
        """Migrate old single-game format to new multi-game format."""
        try:
            config = self.get_config()

            # Check if old format (has 'region' key instead of 'games')
            if "region" in config and "games" not in config:
                print("Migrating old config format...")

                old_region = config.pop("region")

                # Create new games structure
                config["games"] = {
                    "1": {"name": "Genshin Impact", "process_name": "GenshinImpact.exe", "region": old_region, "auto_capture_key": "f3", "auto_capture_delay": 3},
                    "2": {"name": "Honkai Star Rail", "process_name": "StarRail.exe", "region": None, "auto_capture_key": "f3", "auto_capture_delay": 3},
                    "3": {"name": "Zenless Zone Zero", "process_name": "ZenlessZoneZero.exe", "region": None, "auto_capture_key": "f4", "auto_capture_delay": 3},
                    "4": {"name": "Wuthering Waves", "process_name": "Wuthering Waves.exe", "region": None, "auto_capture_key": "f3", "auto_capture_delay": 3}
                }

                self._write_json(self.config_file, config)
                print("Config migrated successfully")

                # Migrate data - add game_id=1 to all existing captures
                data = self._read_json(self.data_file)
                captures = data.get("captures", [])

                migrated_count = 0
                for capture in captures:
                    if "game_id" not in capture:
                        capture["game_id"] = 1
                        migrated_count += 1

                if migrated_count > 0:
                    data["captures"] = captures
                    self._write_json(self.data_file, data)
                    print(f"Migrated {migrated_count} captures to game_id=1")

        except Exception as e:
            print(f"Migration error: {e}")

    # Data capture methods

    def save_capture(self, value: float, game_id: int, notes: str = "") -> int:
        """Save a new captured value and return its ID."""
        data = self._read_json(self.data_file)
        captures = data.get("captures", [])

        # Generate new ID
        new_id = max([c.get("id", 0) for c in captures], default=0) + 1

        capture = {
            "id": new_id,
            "value": value,
            "game_id": game_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": notes
        }

        captures.append(capture)
        data["captures"] = captures
        self._write_json(self.data_file, data)

        return new_id

    def load_history(self, game_id: Optional[int] = None, limit: Optional[int] = None) -> List[dict]:
        """Load capture history, optionally filtered by game_id and limited to most recent N entries."""
        data = self._read_json(self.data_file)
        captures = data.get("captures", [])

        # Filter by game_id if specified
        if game_id is not None:
            captures = [c for c in captures if c.get("game_id") == game_id]

        # Sort by timestamp (most recent first)
        captures.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        if limit:
            return captures[:limit]
        return captures

    def get_last_capture(self, game_id: Optional[int] = None) -> Optional[dict]:
        """Get the most recent capture, optionally filtered by game_id."""
        history = self.load_history(game_id=game_id, limit=1)
        return history[0] if history else None

    def get_stats(self, game_id: Optional[int] = None) -> dict:
        """Calculate statistics from captures, optionally filtered by game_id."""
        captures = self.load_history(game_id=game_id)

        if not captures:
            return {
                "total": 0,
                "count": 0,
                "average": 0,
                "min": 0,
                "max": 0
            }

        values = [c.get("value", 0) for c in captures]

        return {
            "total": sum(values),
            "count": len(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    def get_stats_all_games(self) -> Dict[int, dict]:
        """Get statistics for all games (1-4)."""
        all_stats = {}
        for game_id in range(1, 5):
            all_stats[game_id] = self.get_stats(game_id=game_id)
        return all_stats

    def delete_capture(self, capture_id: int) -> bool:
        """Delete a capture by ID. Returns True if deleted."""
        data = self._read_json(self.data_file)
        captures = data.get("captures", [])

        original_count = len(captures)
        captures = [c for c in captures if c.get("id") != capture_id]

        if len(captures) < original_count:
            data["captures"] = captures
            self._write_json(self.data_file, data)
            return True

        return False

    def clear_history(self):
        """Delete all captured data."""
        self._write_json(self.data_file, {"captures": []})

    def export_to_csv(self, output_file: str):
        """Export capture history to CSV file."""
        import csv

        captures = self.load_history()

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "game_id", "value", "timestamp", "notes"])
            writer.writeheader()
            writer.writerows(captures)
