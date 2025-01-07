import os
import sys
import tkinter as tk
from src.gui.main_window import MainWindow

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    root = tk.Tk()
    app = MainWindow(root, repo_path)
    root.mainloop()

if __name__ == "__main__":
    main() 