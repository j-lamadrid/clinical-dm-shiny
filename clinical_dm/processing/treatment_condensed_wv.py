import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class CalcTxGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Treatment Units Calculator")

        self.file_path_label = tk.Label(master, text="XLSX File Path:")
        self.file_path_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.file_path_entry = tk.Entry(master, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.output_dir_label = tk.Label(master, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        self.output_dir_entry = tk.Entry(master, width=40)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.browse_dir = tk.Button(master, text="Browse", command=self.browse_folder)
        self.browse_dir.grid(row=1, column=2, padx=10, pady=10)

        self.output_name_label = tk.Label(master, text="Output File Name:")
        self.output_name_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.output_name_entry = tk.Entry(master, width=40)
        self.output_name_entry.grid(row=2, column=1, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_script)
        self.run_button.grid(row=4, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
    
    def browse_folder(self):
        dir_path = filedialog.askdirectory()
        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(0, dir_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        output_dir = self.output_dir_entry.get()
        output_name = self.output_name_entry.get()

        if file_path and output_name:
            try:
                calculate_treatment_units(file_path, output_dir + '/' + output_name)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")

def calculate_treatment_units(fp, output_name):
    
    df = pd.read_excel(fp)
    
    df['Service Date'] = pd.to_datetime(df['Service Year'].astype(str)  + df['Service Month'], format='%Y%B')
    id_code_group = df.groupby(['UCI#', 'Vendor Name', 'Service Code', 'Service Code Description', 'Sub-Code', 'Sub-Code Description', 'Unit Type'])
    min_years = id_code_group['Service Year'].min()
    max_years = id_code_group['Service Year'].max()
    total_units = id_code_group['Unit Amount'].sum()
    total_months = id_code_group['Service Date'].nunique()
    first_name = id_code_group['First Name'].max()
    last_name = id_code_group['Last Name'].max()
    
    out_df = total_units.reset_index()
    out_df['First Name'] = first_name.values
    out_df['Last Name'] = last_name.values
    out_df['Min Year'] = min_years.values
    out_df['Max Year'] = max_years.values
    out_df['Total Months'] = total_months.values
    out_df['Units Per Week'] = out_df['Unit Amount'] / (out_df['Total Months'] * 4)

    out_df.to_excel(output_name + '.xlsx', index=False)
    print(out_df.head())
    print('File saved as ' + output_name + '.xlsx')

def main():
    root = tk.Tk()
    app = CalcTxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
