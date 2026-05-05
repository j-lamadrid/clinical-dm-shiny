import pandas as pd
import numpy as np
import os
import warnings
import tkinter as tk
from tkinter import filedialog
warnings.filterwarnings("ignore")

class AddGroupGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Late Talker DxJ Adding Group")
        
        self.allowed_dxjs_text = tk.Text(master, width=81, height=1)
        self.allowed_dxjs_text.insert(tk.END, "Allowed DxJs: [DD, FMD, GDD, GD, LD, MD, Other, TD, ASD, ASD_Features, TypSibASD]")
        self.allowed_dxjs_text.config(state=tk.DISABLED)
        self.allowed_dxjs_text.grid(row=0, column=0, columnspan=10, padx=10, pady=10)

        self.new_group_label = tk.Label(master, text="New Group:")
        self.new_group_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.new_group_entry = tk.Entry(master, width=40)
        self.new_group_entry.grid(row=1, column=1, padx=10, pady=10)

        self.begins_with_label = tk.Label(master, text="Begins With (space-separated):")
        self.begins_with_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        self.begins_with_entry = tk.Entry(master, width=40)
        self.begins_with_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.ends_with_label = tk.Label(master, text="Ends With (space-separated):")
        self.ends_with_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        self.ends_with_entry = tk.Entry(master, width=40)
        self.ends_with_entry.grid(row=3, column=1, padx=10, pady=10)

        self.possibilities_label = tk.Label(master, text="Possibilities (space-separated):")
        self.possibilities_label.grid(row=4, column=0, sticky="w", padx=10, pady=10)

        self.possibilities_entry = tk.Entry(master, width=40)
        self.possibilities_entry.grid(row=4, column=1, padx=10, pady=10)

        self.min_dxj_label = tk.Label(master, text="Minimum # of DxJ:")
        self.min_dxj_label.grid(row=5, column=0, sticky="w", padx=10, pady=10)

        self.min_dxj_entry = tk.Entry(master, width=40)
        self.min_dxj_entry.grid(row=5, column=1, padx=10, pady=10)

        self.file_path_label = tk.Label(master, text="XLSX File Path:")
        self.file_path_label.grid(row=6, column=0, sticky="w", padx=10, pady=10)

        self.file_path_entry = tk.Entry(master, width=40)
        self.file_path_entry.grid(row=6, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=6, column=2, sticky="w", padx=10, pady=10)

        self.output_name_label = tk.Label(master, text="Output File Name:")
        self.output_name_label.grid(row=7, column=0, sticky="w", padx=10, pady=10)

        self.output_name_entry = tk.Entry(master, width=40)
        self.output_name_entry.grid(row=7, column=1, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_script)
        self.run_button.grid(row=8, column=0, columnspan=3, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XSLX files", "*.xlsx")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        output_name = self.output_name_entry.get()
        new_group = self.new_group_entry.get()
        begins_with = [str(item) for item in self.begins_with_entry.get().split()]
        ends_with = [str(item) for item in self.ends_with_entry.get().split()]
        possibilities = [str(item) for item in self.possibilities_entry.get().split()]
        min_dxj = int(self.min_dxj_entry.get())

        if file_path and output_name:
            try:
                add_group(file_path, output_name, new_group=new_group, begins_with=begins_with, 
                          ends_with=ends_with, possibilities=possibilities, min_dxj=min_dxj)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                print(e)
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")


def add_group(sheet_path, output_name, new_group, begins_with=None, ends_with=None, possibilities=None, min_dxj=2):
    
    df = pd.read_excel(sheet_path) # read excel sheet in as a dataframe
    
    diags = ['DD', 'FMD', 'GDD', 'GD', 'LD', 'MD', 'Other', 'TD', 'ASD', 'ASD_Features', 'TypSibASD', np.nan] # list of all allowed diagnoses

    def check_dxj(x):
        """
        x: diagnosis category
        
        normalizes TD diagnosis and ASD features + Typ Sib ASD to remove space
        """
        if (type(x) == str) and (x[:4] == 'Prev') and (x[:-3] == 'Typ'):
            return 'TD'
        elif (type(x) == str) and (x == 'ASD Features'):
            return 'ASD_Features'
        elif (type(x) == str) and (x == 'Typ Sib ASD'):
            return 'TypSibASD'
        else:
            return x

    df['DxJ_DxGroup_1'] = df['DxJ_DxGroup_1'].apply(lambda dxj: check_dxj(dxj))
    df['DxJ_DxGroup_2'] = df['DxJ_DxGroup_2'].apply(lambda dxj: check_dxj(dxj))
    df['DxJ_DxGroup_3'] = df['DxJ_DxGroup_3'].apply(lambda dxj: check_dxj(dxj))
    df['DxJ_DxGroup_4'] = df['DxJ_DxGroup_4'].apply(lambda dxj: check_dxj(dxj))
    df['DxJ_DxGroup_5'] = df['DxJ_DxGroup_5'].apply(lambda dxj: check_dxj(dxj))
    
    if len(begins_with) == 0:
        begins_with = diags
        
    if len(ends_with) == 0:
        ends_with = diags
    
    if len(possibilities) == 0:
        possibilities = diags
    
    
    prev_groups = df['DxJ_group']
    new_groups = []
    
    for i in range(df.shape[0]):

        arr = df.iloc[i]
        dxj = arr[['DxJ_DxGroup_1', 'DxJ_DxGroup_2', 'DxJ_DxGroup_3', 'DxJ_DxGroup_4', 'DxJ_DxGroup_5']]
        dxj = dxj[dxj.notnull()].values
            
        try:
            if len(dxj) == 2:
                
                if min_dxj > 2:
                    
                    c = prev_groups[i]
                    
                else:

                    if (dxj[0] in begins_with) and (dxj[-1] in ends_with):
                        c = new_group
                    else:
                        c = prev_groups[i]
                    
            else:
                
                if (dxj[0] in begins_with) and (dxj[-1] in ends_with) and all((x in possibilities) for x in dxj[1:-1]):
                    c = new_group
                else:
                    c = prev_groups[i]
                
        except:
            c = prev_groups[i]

        new_groups.append(c)

    df['DxJ_group'] = new_groups

    def reset_dxj(x):
        try:
            return x.replace('_', ' ')
        except:
            return x

    df['DxJ_DxGroup_1'] = df['DxJ_DxGroup_1'].apply(lambda dxj: reset_dxj(dxj))
    df['DxJ_DxGroup_2'] = df['DxJ_DxGroup_2'].apply(lambda dxj: reset_dxj(dxj))
    df['DxJ_DxGroup_3'] = df['DxJ_DxGroup_3'].apply(lambda dxj: reset_dxj(dxj))
    df['DxJ_DxGroup_4'] = df['DxJ_DxGroup_4'].apply(lambda dxj: reset_dxj(dxj))
    df['DxJ_DxGroup_5'] = df['DxJ_DxGroup_5'].apply(lambda dxj: reset_dxj(dxj))
    
    filename = output_name + '.xlsx'
    
    df.to_excel(os.path.join(os.getcwd(), filename.replace(" ", "_").replace(":", "-")), index=False)
        
    print('{} Added'.format(new_group))
    
    print(df['DxJ_group'].value_counts())
    
    print('File exported as {}'.format(filename.replace(" ", "_").replace(":", "-")))


def main():
    root = tk.Tk()
    app = AddGroupGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
