import pandas as pd
import numpy as np
import os
import warnings
import tkinter as tk
from tkinter import filedialog
import traceback
warnings.filterwarnings("ignore")

class GroupingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Late Talker DxJ Grouper")

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
        file_path = filedialog.askopenfilename(filetypes=[("XSLX files", "*.xlsx")])
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def run_script(self):
        file_path = self.file_path_entry.get()
        output_name = self.output_name_entry.get()

        if file_path and output_name:
            try:
                group_late_talkers(file_path, output_name)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                traceback.print_exc()
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")


def group_late_talkers(sheet_path, output_name):
    
    talkers_df = pd.read_excel(sheet_path)

    diags = ['DD', 'FMD', 'GDD', 'GD', 'LD', 'MD', 'Other', 'TD', 'ASD', 'ASD_Features', 'TypSibASD', np.nan]

    def check_dxj(x):
        if (type(x) == str) and (x[:4] == 'Prev') and (x[:-3] == 'Typ'):
            return 'TD'
        elif (type(x) == str) and (x == 'ASD Features'):
            return 'ASD_Features'
        elif (type(x) == str) and (x == 'Typ Sib ASD'):
            return 'TypSibASD'
        else:
            return x

    talkers_df['DxJ_DxGroup_1'] = talkers_df['DxJ_DxGroup_1'].apply(lambda dxj: check_dxj(dxj))
    talkers_df['DxJ_DxGroup_2'] = talkers_df['DxJ_DxGroup_2'].apply(lambda dxj: check_dxj(dxj))
    talkers_df['DxJ_DxGroup_3'] = talkers_df['DxJ_DxGroup_3'].apply(lambda dxj: check_dxj(dxj))
    talkers_df['DxJ_DxGroup_4'] = talkers_df['DxJ_DxGroup_4'].apply(lambda dxj: check_dxj(dxj))
    talkers_df['DxJ_DxGroup_5'] = talkers_df['DxJ_DxGroup_5'].apply(lambda dxj: check_dxj(dxj))

    talkers_df = talkers_df[talkers_df.DxJ_DxGroup_1.isin(['ADHD']) == False]
    talkers_df = talkers_df[talkers_df.DxJ_DxGroup_2.isin(['ADHD']) == False]
    talkers_df = talkers_df[talkers_df.DxJ_DxGroup_3.isin(['ADHD']) == False]
    talkers_df = talkers_df[talkers_df.DxJ_DxGroup_4.isin(['ADHD']) == False]
    talkers_df = talkers_df[talkers_df.DxJ_DxGroup_5.isin(['ADHD']) == False]

    talkers_df['DxJ_DxGroup_1'] = talkers_df['DxJ_DxGroup_1'].apply(lambda dxj: 'Other' if dxj not in diags else dxj)
    talkers_df['DxJ_DxGroup_2'] = talkers_df['DxJ_DxGroup_2'].apply(lambda dxj: 'Other' if dxj not in diags else dxj)
    talkers_df['DxJ_DxGroup_3'] = talkers_df['DxJ_DxGroup_3'].apply(lambda dxj: 'Other' if dxj not in diags else dxj)
    talkers_df['DxJ_DxGroup_4'] = talkers_df['DxJ_DxGroup_4'].apply(lambda dxj: 'Other' if dxj not in diags else dxj)
    talkers_df['DxJ_DxGroup_5'] = talkers_df['DxJ_DxGroup_5'].apply(lambda dxj: 'Other' if dxj not in diags else dxj)

    classes = ['Always Typical', 
               'Transient Language Delay', 
               'Persistent Language Delay', 
               'Persistent Global Delay',
               'LD to ASD',
               'Persistent ASD']

    groups = []
    for i in range(talkers_df.shape[0]):

        arr = talkers_df.iloc[i]
        dxj = arr[['DxJ_DxGroup_1', 'DxJ_DxGroup_2', 'DxJ_DxGroup_3', 'DxJ_DxGroup_4', 'DxJ_DxGroup_5']]
        dxj = dxj[dxj.notnull()].values

        try:

            if all((x in ['TD', 'Other']) for x in dxj):
                c = classes[0]

            elif (dxj[-1] in ['TD', 'Other']):
                c = classes[1]

            elif (dxj[-1] == 'LD'):
                c = classes[2]

            elif ((dxj[-1] in ['GD', 'GDD', 'DD']) and not any((x in ['TD', 'Other']) for x in dxj)):
                c = classes[3]

            elif ((dxj[-1] == 'ASD') and (dxj[0] == 'LD') and all((x in ['ASD', 'LD']) for x in dxj[:-1])):
                c = classes[4]

            elif all((x == 'ASD' for x in dxj)):
                c = classes[5]

            else:
                c = np.nan

        except:

            c = np.nan

        groups.append(c)

    talkers_df['DxJ_group'] = groups
    talkers_df.reset_index(drop=True, inplace=True)

    def reset_dxj(x):
        try:
            return x.replace('_', ' ')
        except:
            return x

    talkers_df['DxJ_DxGroup_1'] = talkers_df['DxJ_DxGroup_1'].apply(lambda dxj: reset_dxj(dxj))
    talkers_df['DxJ_DxGroup_2'] = talkers_df['DxJ_DxGroup_2'].apply(lambda dxj: reset_dxj(dxj))
    talkers_df['DxJ_DxGroup_3'] = talkers_df['DxJ_DxGroup_3'].apply(lambda dxj: reset_dxj(dxj))
    talkers_df['DxJ_DxGroup_4'] = talkers_df['DxJ_DxGroup_4'].apply(lambda dxj: reset_dxj(dxj))
    talkers_df['DxJ_DxGroup_5'] = talkers_df['DxJ_DxGroup_5'].apply(lambda dxj: reset_dxj(dxj))
    
    print(talkers_df['DxJ_group'].value_counts())
    
    filename = output_name + '.xlsx'
    
    talkers_df.to_excel(os.path.join(os.getcwd(), filename.replace(" ", "_").replace(":", "-")), index=False)
    
    print('File exported as {}'.format(filename.replace(" ", "_").replace(":", "-")))

def main():
    root = tk.Tk()
    app = GroupingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
