import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

from .ets import EyeTrackingSheet

class etsGUI:


    def __init__(self, master):
        self.master = master
        self.master.title("Eye Tracking Sheet Merger")

        self.file_path_label = tk.Label(master, text="Export File Path:")
        self.file_path_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.file_path_entry = tk.Entry(master, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_tsv)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.master_fp_label = tk.Label(master, text="Master File Path:")
        self.master_fp_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.master_fp_entry = tk.Entry(master, width=40)
        self.master_fp_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.browse_button_master = tk.Button(master, text="Browse", command=self.browse_xlsx_master)
        self.browse_button_master.grid(row=1, column=2, padx=10, pady=10)
        
        self.sum_fp_label = tk.Label(master, text="ET Summary File Path:")
        self.sum_fp_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.sum_fp_entry = tk.Entry(master, width=40)
        self.sum_fp_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.browse_button_sum = tk.Button(master, text="Browse", command=self.browse_xlsx_et)
        self.browse_button_sum.grid(row=2, column=2, padx=10, pady=10)
        
        self.lwr_fp_label = tk.Label(master, text="LWR File Path:")
        self.lwr_fp_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        self.lwr_fp_entry = tk.Entry(master, width=40)
        self.lwr_fp_entry.grid(row=3, column=1, padx=10, pady=10)
        
        self.browse_button_lwr = tk.Button(master, text="Browse", command=self.browse_csv)
        self.browse_button_lwr.grid(row=3, column=2, padx=10, pady=10)

        self.timeline_label = tk.Label(master, text="Timeline:")
        self.timeline_label.grid(row=4, column=0, sticky="w", padx=10, pady=10)

        self.timeline_var = tk.StringVar(master)
        self.timeline_var.set("Original GeoPref")  # default value
        self.timeline_options = ["Original GeoPref", "Complex Social GeoPref", "Peer Play GeoPref", "Motherese QL vs Traffic", "Motherese LK vs Techno"]
        self.timeline_dropdown = tk.OptionMenu(master, self.timeline_var, *self.timeline_options)
        self.timeline_dropdown.grid(row=4, column=1, padx=10, pady=10)

        self.software_label = tk.Label(master, text="Software:")
        self.software_label.grid(row=5, column=0, sticky="w", padx=10, pady=10)

        self.software_var = tk.StringVar(master)
        self.software_var.set("Tobii ProLab")  # default value
        self.software_options = ["Tobii ProLab", "Tobii Studio", "Other"]
        self.software_dropdown = tk.OptionMenu(master, self.software_var, *self.software_options)
        self.software_dropdown.grid(row=5, column=1, padx=10, pady=10)

        self.other_software_label = tk.Label(master, text="Other Software:")
        self.other_software_label.grid(row=6, column=0, sticky="w", padx=10, pady=10)
        
        self.other_software_entry = tk.Entry(master, width=20)
        self.other_software_entry.grid(row=6, column=1, padx=10, pady=10)
        self.other_software_entry.grid_remove()
        
        self.software_var.trace("w", self.show_hide_other_software_entry)

        self.run_button = tk.Button(master, text="Run", command=self.run_script)
        self.run_button.grid(row=8, column=0, columnspan=3, pady=10)
    
    def show_hide_other_software_entry(self, *args):
        if self.software_var.get() == "Other":
            self.other_software_entry.grid()
        else:
            self.other_software_entry.grid_remove()

    def browse_tsv(self):
        file_path = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def browse_xlsx_master(self):
        file_path = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        self.master_fp_entry.delete(0, tk.END)
        self.master_fp_entry.insert(0, file_path)
        
    def browse_xlsx_et(self):
        file_path = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        self.sum_fp_entry.delete(0, tk.END)
        self.sum_fp_entry.insert(0, file_path)
        
    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.lwr_fp_entry.delete(0, tk.END)
        self.lwr_fp_entry.insert(0, file_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        master_fp = self.master_fp_entry.get()
        et_summary_fp = self.sum_fp_entry.get()
        lwr_fp = self.lwr_fp_entry.get()

        if self.timeline_var.get() == "Original GeoPref":
                timeline = 'Geo'
        elif self.timeline_var.get() ==  "Complex Social GeoPref":
                timeline = 'Soc'
        elif self.timeline_var.get() ==  "Peer Play GeoPref":
                timeline = 'Play'
        elif self.timeline_var.get() == "Motherese QL vs Traffic":
                timeline = 'Traffic'
        elif self.timeline_var.get() == "Motherese LK vs Techno":
                timeline = 'Techno'

        if self.software_var.get() != 'Other':
            software = self.software_var.get()
        else:
            software = self.other_software_entry.get()

        if file_path and master_fp and et_summary_fp and timeline and software:
            try:
                ets = EyeTrackingSheet(file_path, master_fp, et_summary_fp, lwr_fp, timeline, software)
                ets.generate()
                ets.fill()
                ets.push()
                output_name = master_fp[:-5] + '_updated.xlsx' if 'updated' not in master_fp else master_fp
                ets.master_df.to_excel(output_name, index=False)
                messagebox.showinfo("Success", "Script executed successfully!")
                print("File exported at " + master_fp[:-5] + "_updated.xlsx")
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            messagebox.showerror("Error", "Please provide all necessary information.")
