import tkinter as tk
from typing import Optional, Tuple

class RegionSelector:
    """Interactive screen region selector with transparent overlay."""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None

    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Open fullscreen transparent overlay for region selection.

        Returns:
            Tuple of (x, y, width, height) or None if cancelled
        """
        self.region = None

        # Create fullscreen transparent window
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Semi-transparent
        self.root.attributes('-topmost', True)
        self.root.configure(bg='gray')

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            bg='gray',
            highlightthickness=0,
            cursor='cross'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instruction_text = "Arraste para selecionar a região | ESC para cancelar | ENTER para confirmar"
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            50,
            text=instruction_text,
            fill='white',
            font=('Arial', 16, 'bold')
        )

        # Bind events
        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.root.bind('<Escape>', self._on_cancel)
        self.root.bind('<Return>', self._on_confirm)

        # Run the selector
        self.root.mainloop()

        return self.region

    def _on_press(self, event):
        """Handle mouse button press."""
        self.start_x = event.x
        self.start_y = event.y

        # Delete previous rectangle if exists
        if self.rect:
            self.canvas.delete(self.rect)

        # Create new rectangle
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline='red',
            width=3,
            fill='yellow',
            stipple='gray50'  # Semi-transparent fill
        )

    def _on_drag(self, event):
        """Handle mouse drag."""
        if self.rect:
            # Update rectangle coordinates
            self.canvas.coords(
                self.rect,
                self.start_x,
                self.start_y,
                event.x,
                event.y
            )

            # Display dimensions
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)

            # Update or create dimension label
            if hasattr(self, 'dim_label'):
                self.canvas.delete(self.dim_label)

            self.dim_label = self.canvas.create_text(
                (self.start_x + event.x) // 2,
                (self.start_y + event.y) // 2,
                text=f'{width} x {height}',
                fill='white',
                font=('Arial', 14, 'bold')
            )

    def _on_release(self, event):
        """Handle mouse button release."""
        if self.start_x is None or self.start_y is None:
            return

        # Calculate region coordinates
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        width = x2 - x1
        height = y2 - y1

        # Minimum size check
        if width < 10 or height < 10:
            self._show_message("Região muito pequena! Tente novamente.")
            self.canvas.delete(self.rect)
            self.rect = None
            return

        # Store region
        self.region = (x1, y1, width, height)

        # Show confirmation message
        self._show_message(
            f"Região selecionada: {width}x{height}\n"
            f"Pressione ENTER para confirmar ou ESC para cancelar"
        )

    def _on_confirm(self, event):
        """Handle confirmation (Enter key)."""
        if self.region:
            self.root.quit()
            self.root.destroy()
        else:
            self._show_message("Selecione uma região primeiro!")

    def _on_cancel(self, event):
        """Handle cancellation (Escape key)."""
        self.region = None
        self.root.quit()
        self.root.destroy()

    def _show_message(self, message: str):
        """Display a message on the canvas."""
        # Delete previous message if exists
        if hasattr(self, 'msg_label'):
            self.canvas.delete(self.msg_label)

        self.msg_label = self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            100,
            text=message,
            fill='yellow',
            font=('Arial', 14, 'bold')
        )


def select_region_simple() -> Optional[Tuple[int, int, int, int]]:
    """
    Simple function to select a screen region.

    Returns:
        Tuple of (x, y, width, height) or None if cancelled
    """
    selector = RegionSelector()
    return selector.select_region()


# Test the region selector
if __name__ == '__main__':
    print("Iniciando seletor de região...")
    region = select_region_simple()

    if region:
        x, y, width, height = region
        print(f"Região selecionada:")
        print(f"  Posição: ({x}, {y})")
        print(f"  Tamanho: {width}x{height}")
    else:
        print("Seleção cancelada")
