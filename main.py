#!/usr/bin/env python3
"""
Ntropy - Screen Value Capture Application

Main entry point for the application.
"""

import sys
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []

    try:
        import PIL
    except ImportError:
        missing.append("Pillow")

    try:
        import pytesseract
        # Try to get Tesseract version to verify it's installed
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            missing.append("Tesseract OCR (sistema)")
    except ImportError:
        missing.append("pytesseract")

    try:
        import pynput
    except ImportError:
        missing.append("pynput (opcional - para atalhos)")

    return missing


def show_dependency_error(missing):
    """Show error dialog for missing dependencies."""
    root = tk.Tk()
    root.withdraw()

    message = "Dependências faltando:\n\n"

    for dep in missing:
        if dep == "Tesseract OCR (sistema)":
            message += f"• {dep}\n"
            message += "  Instalação no Ubuntu/Debian:\n"
            message += "    sudo apt-get install tesseract-ocr tesseract-ocr-por\n\n"
        else:
            message += f"• {dep}\n"

    message += "\nPara instalar dependências Python:\n"
    message += "  pip install -r requirements.txt\n\n"
    message += "Consulte o README.md para mais detalhes."

    messagebox.showerror("Dependências Faltando", message)
    root.destroy()


def main():
    """Main application entry point."""
    print("=" * 50)
    print("Ntropy - Iniciando...")
    print("=" * 50)

    # Check dependencies
    missing_deps = check_dependencies()

    if missing_deps:
        print("\n❌ Erro: Dependências faltando!")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nExecute: pip install -r requirements.txt")
        print("E instale Tesseract OCR no sistema\n")

        # Show GUI error dialog
        show_dependency_error(missing_deps)
        sys.exit(1)

    print("✓ Todas as dependências estão instaladas\n")

    # Import GUI (after dependency check)
    try:
        from gui import NtropyGUI

        # Create main window
        root = tk.Tk()

        # Create and run application
        app = NtropyGUI(root)

        print("✓ Aplicação iniciada com sucesso!")
        print("  Pressione F9 para capturar valores")
        print("  Use o menu 'Configurações' para definir a região\n")

        app.run()

    except Exception as e:
        print(f"\n❌ Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
