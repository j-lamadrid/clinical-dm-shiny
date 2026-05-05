import tkinter as tk
from tkinter import filedialog
from functools import partial
import pandas as pd
import numpy as np
from collections import Counter
import os
import traceback

class IDDateSortGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ID Date Sorter")

        self.file_path_label = tk.Label(master, text="CSV File Path:")
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
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        output_name = self.output_name_entry.get()

        if file_path and output_name:
            try:
                id_date_sort(file_path, output_name)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                traceback.print_exc()
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")

def id_date_sort(fp, output_name):
    
    df = pd.read_csv(fp)
    
    df = df.dropna(subset=['SubjectId'])
    df['SubjectId'] = df['SubjectId'].apply(lambda s: s.upper())
    df['EvalDate'] = pd.to_datetime(df['EvalDate'])
    df = df.sort_values(['SubjectId', 'EvalDate'], ascending=[True, True])
    df = df.reset_index(drop=True)
    
    tups = [(i, j) for i, j in df[['SubjectId', 'EvalDate']].values]
    counts = Counter(tups)

    if any(np.array([i for i in counts.values()]) > 1):
        to_drop = []
        for k, v in counts.items():

            if v > 1:
                sub_df = df[df['SubjectId'] == k[0]]
                sub_df = sub_df[sub_df['EvalDate'] == k[1]]

            for i in range(v-1):
                to_drop.append(sub_df.index[-i])

        df = df.drop(labels=to_drop)
        df = df.reset_index(drop=True)

    visit_flags = []
    idx = 0
    for i in df['SubjectId'].unique():
        current = i
        flag = 1
        
        while idx < df.shape[0] and df['SubjectId'][idx] == i:
            visit_flags.append(flag)
            idx += 1
            flag += 1

    df.insert(0, 'visitFlags', visit_flags)
    
    dir_name = os.path.dirname(fp)
    output = os.path.join(dir_name, output_name)
    
    df.to_csv(output + '.csv', index=False)

def main():
    root = tk.Tk()
    app = IDDateSortGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

    
