import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class CalcTxGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Treatment Hours Calculator")

        self.file_path_label = tk.Label(master, text="XLSX File Path:")
        self.file_path_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.file_path_entry = tk.Entry(master, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.output_name_label = tk.Label(master, text="Output File Name:")
        self.output_name_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.output_name_entry = tk.Entry(master, width=40)
        self.output_name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_script)
        self.run_button.grid(row=2, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        output_name = self.output_name_entry.get()

        if file_path and output_name:
            try:
                calculate_treatment_hours(file_path, output_name)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")


def calculate_treatment_hours(fp, output_name):
    
    df = pd.read_excel(fp)
    
    tx_df = df[df['Sub-Code'].isin(['01UN', 'ST', 'PT', 'OT'])]
    tx_df = tx_df[~tx_df['Service Code'].isin([455, 862, 861])]
    hours_df = tx_df[tx_df['Unit Type'] == 'HD']
    hours_df['Service Date'] = pd.to_datetime(hours_df['Service Year'].astype(str)  + hours_df['Service Month'], format='%Y%B')

    id_code_group = hours_df.groupby(['UCI#', 'Sub-Code'])

    total_hours = id_code_group['Unit Amount'].sum()
    total_weeks = (id_code_group['Service Date'].max() - id_code_group['Service Date'].min()) / pd.Timedelta(1, unit='W')

    avg_hours = total_hours / total_weeks

    uci_order = [(uci, sc) for uci, sc in df[['UCI#', 'Sub-Code']].values]

    total_col = []
    avg_col = []


    for i in uci_order:

        try:
            total_val = total_hours[i]
            avg_val = avg_hours[i] if avg_hours[i] != float('inf') else total_val / 4
            total_col.append(total_val)
            avg_col.append(avg_val)

        except:
            total_col.append(np.nan)
            avg_col.append(np.nan)

    for i in range(df.shape[0]):

        if df['Service Code'][i] in [455, 862, 861]:
            total_col[i] = np.nan
            avg_col[i] = np.nan


    df['Total Hours'] = total_col
    df['Average Hours per Week'] = avg_col
    
    df.to_excel(output_name + '.xlsx', index=False)
    print(df.head())
    print('File saved as ' + output_name + '.xlsx')


def main():
    root = tk.Tk()
    app = CalcTxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
