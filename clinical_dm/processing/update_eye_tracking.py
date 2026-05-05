import tkinter as tk

from .modules.ets_gui import etsGUI


def main():
    root = tk.Tk()
    etsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
