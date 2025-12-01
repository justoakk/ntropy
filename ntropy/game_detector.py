import sys
import platform
from typing import Optional, Dict, List
import psutil


class GameDetector:
    """Detects which game is currently active based on process names."""

    def __init__(self, game_configs: Dict[int, dict]):
        """
        Initialize game detector with game configurations.

        Args:
            game_configs: Dictionary mapping game_id to game config
                         {1: {"name": "Game 1", "process_name": "game1.exe"}, ...}
        """
        self.game_configs = game_configs
        self.system = platform.system()

    def get_active_game(self) -> Optional[int]:
        """
        Detect which configured game is currently the active window.

        Returns:
            Game ID (1-4) if a configured game is active, None otherwise
        """
        active_process = self._get_active_window_process()

        if not active_process:
            return None

        # Check if active process matches any configured game
        for game_id, config in self.game_configs.items():
            process_name = config.get("process_name", "")
            if not process_name:
                continue

            # Case-insensitive comparison
            if self._process_matches(active_process, process_name):
                return game_id

        return None

    def get_running_games(self) -> List[int]:
        """
        Get list of all configured games that are currently running.

        Returns:
            List of game IDs that are running
        """
        running = []

        try:
            # Get all running processes
            running_processes = {p.name() for p in psutil.process_iter(['name'])}

            # Check each configured game
            for game_id, config in self.game_configs.items():
                process_name = config.get("process_name", "")
                if not process_name:
                    continue

                # Check if process is running
                for running_proc in running_processes:
                    if self._process_matches(running_proc, process_name):
                        running.append(game_id)
                        break

        except Exception as e:
            print(f"Error getting running games: {e}")

        return running

    def _process_matches(self, proc_name: str, target_name: str) -> bool:
        """
        Check if process name matches target name (case-insensitive).

        Args:
            proc_name: Actual process name
            target_name: Target process name to match

        Returns:
            True if they match
        """
        proc_name = proc_name.lower()
        target_name = target_name.lower()

        # Direct match
        if proc_name == target_name:
            return True

        # Without extension (e.g., "game.exe" matches "game")
        proc_base = proc_name.rsplit('.', 1)[0] if '.' in proc_name else proc_name
        target_base = target_name.rsplit('.', 1)[0] if '.' in target_name else target_name

        if proc_base == target_base:
            return True

        # Partial match (if target is contained in process name)
        if target_base in proc_base or proc_base in target_base:
            return True

        return False

    def _get_active_window_process(self) -> Optional[str]:
        """
        Get the process name of the currently active/focused window.

        Returns:
            Process name string or None if unable to detect
        """
        try:
            if self.system == "Windows":
                return self._get_active_window_windows()
            elif self.system == "Linux":
                return self._get_active_window_linux()
            elif self.system == "Darwin":  # macOS
                return self._get_active_window_macos()
            else:
                print(f"Unsupported OS: {self.system}")
                return None

        except Exception as e:
            print(f"Error getting active window: {e}")
            return None

    def _get_active_window_windows(self) -> Optional[str]:
        """Get active window process on Windows."""
        try:
            import win32process
            import win32gui

            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()

            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # Get process info
            process = psutil.Process(pid)
            return process.name()

        except ImportError:
            # Fallback if win32 modules not available
            print("pywin32 not installed. Install with: pip install pywin32")
            return None
        except Exception as e:
            print(f"Windows detection error: {e}")
            return None

    def _get_active_window_linux(self) -> Optional[str]:
        """Get active window process on Linux."""
        try:
            import subprocess

            # Try xdotool first
            try:
                pid_output = subprocess.check_output(
                    ['xdotool', 'getactivewindow', 'getwindowpid'],
                    stderr=subprocess.DEVNULL
                )
                pid = int(pid_output.strip())
                process = psutil.Process(pid)
                return process.name()

            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

            # Try wmctrl as fallback
            try:
                output = subprocess.check_output(
                    ['wmctrl', '-lp'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8')

                # Find the line with the active window (marked with *)
                active_output = subprocess.check_output(
                    ['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8')

                # Parse window ID
                window_id = active_output.split()[-1]

                # Find PID for that window
                for line in output.split('\n'):
                    if window_id.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            pid = int(parts[2])
                            process = psutil.Process(pid)
                            return process.name()

            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

            print("xdotool or wmctrl not found. Install with: sudo apt-get install xdotool wmctrl")
            return None

        except Exception as e:
            print(f"Linux detection error: {e}")
            return None

    def _get_active_window_macos(self) -> Optional[str]:
        """Get active window process on macOS."""
        try:
            from AppKit import NSWorkspace

            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            app_name = active_app['NSApplicationName']

            # Try to find process by name
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == app_name or app_name in proc.info['name']:
                    return proc.info['name']

            return app_name

        except ImportError:
            print("pyobjc not installed. Install with: pip install pyobjc-framework-Cocoa")
            return None
        except Exception as e:
            print(f"macOS detection error: {e}")
            return None


# Test function
if __name__ == '__main__':
    # Example game configs
    test_configs = {
        1: {"name": "Genshin Impact", "process_name": "GenshinImpact.exe"},
        2: {"name": "Honkai Star Rail", "process_name": "StarRail.exe"},
        3: {"name": "Zenless Zone Zero", "process_name": "ZenlessZoneZero.exe"},
        4: {"name": "Wuthering Waves", "process_name": "Wuthering Waves.exe"}
    }

    detector = GameDetector(test_configs)

    print("Sistema:", platform.system())
    print("\nProcesso ativo:", detector._get_active_window_process())
    print("\nJogo ativo:", detector.get_active_game())
    print("\nJogos rodando:", detector.get_running_games())
