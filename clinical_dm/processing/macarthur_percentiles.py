import pandas as pd
import numpy as np
import re
import os
import tkinter as tk
from tkinter import filedialog
import warnings
warnings.filterwarnings("ignore")

class MacArthurRankingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("MacArthur Percentile Generator")

        self.lwr_fp_label = tk.Label(master, text="LWR File Path:")
        self.lwr_fp_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.lwr_fp_entry= tk.Entry(master, width=40)
        self.lwr_fp_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_lwr)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.app_fp_label = tk.Label(master, text="Scoring Appendix File Path:")
        self.app_fp_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.app_fp_entry = tk.Entry(master, width=40)
        self.app_fp_entry.grid(row=1, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_app)
        self.browse_button.grid(row=1, column=2, padx=10, pady=10)

        self.output_dir_label = tk.Label(master, text="Output File Directory:")
        self.output_dir_label.grid(row=4, column=0, sticky="w", padx=10, pady=10)

        self.output_dir_entry = tk.Entry(master, width=40)
        self.output_dir_entry.grid(row=4, column=1, padx=10, pady=10)
        
        self.browse_button = tk.Button(master, text="Browse", command=self.browse_dir)
        self.browse_button.grid(row=4, column=2, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_script)
        self.run_button.grid(row=5, column=0, columnspan=3, pady=10)

    def browse_lwr(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.lwr_fp_entry.delete(0, tk.END)
        self.lwr_fp_entry.insert(0, file_path)
        
    def browse_app(self):
        file_path = filedialog.askopenfilename(filetypes=[("XLSX files", "*.xlsx")])
        self.app_fp_entry.delete(0, tk.END)
        self.app_fp_entry.insert(0, file_path)
        
    def browse_dir(self):
        file_dir = filedialog.askdirectory()
        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(0, file_dir)

    def run_script(self):
        file_path = self.lwr_fp_entry.get()
        app_path = self.app_fp_entry.get()
        output_dir = self.output_dir_entry.get()

        if file_path and app_path and output_dir:
            try:
                populate(file_path, app_path, output_dir)
                tk.messagebox.showinfo("Success", "Script executed successfully!")
            except Exception as e:
                print(type(e))
                print(e.args)
                print(e)
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showerror("Error", "Please provide both input file path and output file name.")

def compute_percentiles(df, calc, form, target='BOTH'):
    
    percentiles = []
    for i in range(df.shape[0]):
        
        try:
            score, age, sex = df.iloc[i]
            if (age < 0):
                percentiles.append(np.nan)
                continue
                
            elif (form == 'wg' and age < 8) or (form == 'ws' and age < 16):
                percentiles.append('age out of range')
                continue
                
            ser = calc[age]    
            if (target != 'BOTH') and (target != sex):
                raise Exception()
            score_ser = ser[ser <= score]
            percentiles.append(score_ser.index[0])
            
        except:
            percentiles.append(np.nan)
        
    return percentiles


def convert_age_wg(age):
    
    try:
        if int(age) <= 18:
            return int(age)
        else:
            return 0
    except:
        return -1

    
def convert_age_ws(age):
    
    try:
        if int(age) <= 30:
            return int(age)
        else:
            return 0
    except:
        return -1

def populate(lwr_fp, app_fp, output_dir):
    
    lwr = pd.read_csv(lwr_fp, low_memory=False)
    lwr.columns = [c.replace('\n', '') for c in lwr.columns]
    
    output = pd.DataFrame()
    idx = 0
    
    print('Computing WG Percentiles')
    for i in range(1, 5):
        df = lwr[[col for col in lwr.columns if 'WG' in col and f'_{i}' in col]]

        phrases_val = df[f'mbWG_EI_IB_Phrases_Und_{i}']
        
        understood_cols = df[[col for col in df.columns[18:75] if '_Und' in col and 'Says' not in col]].sum(axis=1)
        produced_cols = df[[col for col in df.columns[18:75] if 'Und_Says' in col]].sum(axis=1)

        early_gest = (df[f'mbWG_EI_IIA_First_Communicative_Gestures_Sometimes_{i}'] + 
                      df[f'mbWG_EI_IIA_First_Communicative_Gestures_Often_{i}'])
        later_gest = df[[col for col in df.columns[78:] if 'Yes' in col]].sum(axis=1)
        total_gest = early_gest + later_gest

        data = pd.DataFrame({'ScoringAge': df[f'mbWG_AgeMo_{i}'].apply(lambda age: convert_age_wg(age)),
                             'Sex': df[f'mbWG_Sex_{i}'],
                             'Phrases': phrases_val.apply(lambda val: val if not np.isnan(val) else 0),
                             'Understood': understood_cols.apply(lambda val: val if not np.isnan(val) else 0),
                             'Produced': produced_cols.apply(lambda val: val if not np.isnan(val) else 0),
                             'EarlyGestures': early_gest.apply(lambda val: val if not np.isnan(val) else 0),
                             'LaterGestures': later_gest.apply(lambda val: val if not np.isnan(val) else 0),
                             'TotalGestures': total_gest.apply(lambda val: val if not np.isnan(val) else 0)
                            })

        column_order = ['Phrases', 'Understood', 'Produced', 'TotalGestures', 'EarlyGestures', 'LaterGestures']

        grouping = {
            0: 'BOTH',
            1: 'F',
            2: 'M'
        }

        sheet = 0
        for j in range(len(column_order)):
            for k in range(3):
                scoring = pd.read_excel(app_fp, sheet_name=sheet, header=3, index_col=1).drop('Unnamed: 0', axis=1)
                scoring.loc[4] = [max(j - 1, 1) if j > 0 else 0  for j in scoring.loc[5]]
                scoring.loc[3] = [max(j - 1, 1) if j > 0 else 0  for j in scoring.loc[4]]
                scoring.loc[2] = [max(j - 1, 1) if j > 0 else 0  for j in scoring.loc[3]]
                scoring.loc[1] = [0]*scoring.shape[1]
                gathered_data = data[[column_order[j], 'ScoringAge', 'Sex']]
                percentiles = compute_percentiles(gathered_data, scoring, 'wg', grouping[k])
                data[f'Percentile_{column_order[j]}_{grouping[k].lower()}'] = percentiles
                sheet += 1


        for col in lwr.columns[idx:]:

            output[col] = lwr[col]
            idx += 1

            if col == f'SUM_IB_Phrases_{i}':
                output[f'mbWG_Percentile_Phrases_both_{i}'] = data['Percentile_Phrases_both']
                output[f'mbWG_Percentile_Phrases_f_{i}'] = data['Percentile_Phrases_f']
                output[f'mbWG_Percentile_Phrases_m_{i}'] = data['Percentile_Phrases_m']
            elif col == f'SUM_ID19_Quantifiers_{i}':
                output[f'mbWG_Percentile_Understood_both_{i}'] = data['Percentile_Understood_both']
                output[f'mbWG_Percentile_Understood_f_{i}'] = data['Percentile_Understood_f']
                output[f'mbWG_Percentile_Understood_m_{i}'] = data['Percentile_Understood_m']
                output[f'mbWG_Percentile_Produced_both_{i}'] = data['Percentile_Produced_both']
                output[f'mbWG_Percentile_Produced_f_{i}'] = data['Percentile_Produced_f']
                output[f'mbWG_Percentile_Produced_m_{i}'] = data['Percentile_Produced_m']
            elif col == f'SUM_IIE_Imitating_Other_Adult_Actions_{i}':
                output[f'mbWG_Percentile_TotalGestures_both_{i}'] = data['Percentile_TotalGestures_both']
                output[f'mbWG_Percentile_TotalGestures_f_{i}'] = data['Percentile_TotalGestures_f']
                output[f'mbWG_Percentile_TotalGestures_m_{i}'] = data['Percentile_TotalGestures_m']
                output[f'mbWG_Percentile_EarlyGestures_both_{i}'] = data['Percentile_EarlyGestures_both']
                output[f'mbWG_Percentile_EarlyGestures_f_{i}'] = data['Percentile_EarlyGestures_f']
                output[f'mbWG_Percentile_EarlyGestures_m_{i}'] = data['Percentile_EarlyGestures_m']
                output[f'mbWG_Percentile_LaterGestures_both_{i}'] = data['Percentile_LaterGestures_both']
                output[f'mbWG_Percentile_LaterGestures_f_{i}'] = data['Percentile_LaterGestures_f']
                output[f'mbWG_Percentile_LaterGestures_m_{i}'] = data['Percentile_LaterGestures_m']
                break
        print(f'Visit {i} finished')

    for col in lwr.columns[idx:]:
            output[col] = lwr[col]
    
    lwr = output
    idx = 0
    
    print('Computing WS Percentiles')
    for i in range(1, 5):

        df = lwr[[col for col in lwr.columns if 'WS' in col and f'_{i}' in col]]

        produced_cols = df[[col for col in df.columns if '_IA' in col]].sum(axis=1)

        form_cols = df[[f'mbWS_IIB_Word_Forms_nouns_{i}', f'mbWS_IIB_Word_Forms_verbs_{i}']].sum(axis=1)
        ending_cols = df[[f'mbWS_IIC_Word_Endings_nouns_{i}', f'mbWS_IIC_Word_Endings_verbs_{i}']].sum(axis=1)

        m3l_cols = [f'mbWS_IID_Example1_{i}', f'mbWS_IID_Example2_{i}', f'mbWS_IID_Example3_{i}']
        sentence_data = df[f'mbWS_IID_Example1_{i}'].apply(lambda s: 0 if type(s) == float or len(re.sub('[^0-9a-zA-Z]+', ' ', s).strip()) == 0
                                            else len(re.sub('[^0-9a-zA-Z]+', ' ', s).strip().split(' ')))
        for col in m3l_cols[1:]:
            sentence_data += df[col].apply(lambda s: 0 if type(s) == float or len(re.sub('[^0-9a-zA-Z]+', ' ', s).strip()) == 0
                                           else len(re.sub('[^0-9a-zA-Z]+', ' ', s).strip().split(' ')))  
        sentence_data = sentence_data / 3

        try:
            complex_cols = df[[f'mbWS_IIE_Complexity_First_Choice_{i}', 
                               f'mbWS_IIE_Complexity_Second_Choice_{i}']].sum(axis=1)
        except:

            try:
                complex_cols = df[[f'mbWS_IIE_Complexity_First_Correct_{i}', 
                                   f'mbWS_IIE_Complexity_Second_Correct_{i}']].sum(axis=1)
            except:
                complex_cols = df[[f'mbWS_IIE_Complexity_First_Choice_{i}', 
                                   f'mbWS_IIE_Second_Choice_{i}']].sum(axis=1)

        data = pd.DataFrame({'ScoringAge': df[f'mbWS_AgeMo_{i}'].apply(lambda age: convert_age_wg(age)),
                             'Sex': df[f'mbWS_Sex_{i}'],
                             'Produced': produced_cols.apply(lambda val: val if not np.isnan(val) else 0),
                             'Forms': form_cols.apply(lambda val: val if not np.isnan(val) else 0),
                             'Endings': ending_cols.apply(lambda val: val if not np.isnan(val) else 0),
                             'M3L': sentence_data.apply(lambda val: val if not np.isnan(val) else 0),
                             'Complexity': complex_cols.apply(lambda val: val if not np.isnan(val) else 0)
                            })

        column_order = ['Produced', 'Forms', 'Endings', 'M3L', 'Complexity']

        grouping = {
            0: 'BOTH',
            1: 'F',
            2: 'M'
        }

        sheet = 18
        for j in range(len(column_order)):
            for k in range(3):
                if sheet == 27:
                    scoring = pd.read_excel(app_fp, sheet_name=sheet, header=3, index_col=0)
                else:
                    scoring = pd.read_excel(app_fp, sheet_name=sheet, header=3, index_col=1).drop('Unnamed: 0', axis=1)
                scoring.loc[4] = [max(j - 1, 1) if j > 0 else 0 for j in scoring.loc[5]]
                scoring.loc[3] = [max(j - 1, 1) if j > 0 else 0 for j in scoring.loc[4]]
                scoring.loc[2] = [max(j - 1, 1) if j > 0 else 0 for j in scoring.loc[3]]
                scoring.loc[1] = [0]*scoring.shape[1]
                gathered_data = data[[column_order[j], 'ScoringAge', 'Sex']]
                percentiles = compute_percentiles(gathered_data, scoring, 'ws', grouping[k])
                data[f'Percentile_{column_order[j]}_{grouping[k].lower()}'] = percentiles
                sheet += 1

        for col in lwr.columns[idx:]:

            output[col] = lwr[col]
            idx += 1

            if (col == f'mbWS_IA22_Connecting_Verbs_{i}' or
                col == f'mbWS_IA22_Connecting_Words_{i}'):
                output[f'mbWS_Percentile_Produced_both_{i}'] = data['Percentile_Produced_both']
                output[f'mbWS_Percentile_Produced_f_{i}'] = data['Percentile_Produced_f']
                output[f'mbWS_Percentile_Produced_m_{i}'] = data['Percentile_Produced_m']
            elif col == f'mbWS_IIB_Word_Forms_verbs_{i}':
                output[f'mbWS_Percentile_Forms_both_{i}'] = data['Percentile_Forms_both']
                output[f'mbWS_Percentile_Forms_f_{i}'] = data['Percentile_Forms_f']
                output[f'mbWS_Percentile_Forms_m_{i}'] = data['Percentile_Forms_m']
            elif col == f'mbWS_IIC_Word_Endings_verbs_{i}':
                output[f'mbWS_Percentile_Endings_both_{i}'] = data['Percentile_Endings_both']
                output[f'mbWS_Percentile_Endings_f_{i}'] = data['Percentile_Endings_f']
                output[f'mbWS_Percentile_Endings_m_{i}'] = data['Percentile_Endings_m']
            elif col == f'mbWS_IID_Example3_{i}':
                output[f'mbWS_Percentile_M3L_both_{i}'] = data['Percentile_M3L_both']
                output[f'mbWS_Percentile_M3L_f_{i}'] = data['Percentile_M3L_f']
                output[f'mbWS_Percentile_M3L_m_{i}'] = data['Percentile_M3L_m']
            elif (col == f'mbWS_IIE_Complexity_Second_Correct_{i}' or 
                  col == f'mbWS_IIE_Complexity_Second_Choice_{i}' or
                  col == f'mbWS_IIE_Second_Choice_{i}'):
                output[f'mbWS_Percentile_Complexity_both_{i}'] = data['Percentile_Complexity_both']
                output[f'mbWS_Percentile_Complexity_f_{i}'] = data['Percentile_Complexity_f']
                output[f'mbWS_Percentile_Complexity_m_{i}'] = data['Percentile_Complexity_m']
                break
        print(f'Visit {i} finished')

    for col in lwr.columns[idx:]:
        output[col] = lwr[col]
    
    print('Outputting sheet')
    output.to_excel(os.path.join(output_dir, 'macarthur_percentiles.xlsx'), index=False)
    print(f'File available at {output_dir}/macarthur_percentiles.xlsx')

def main():
    root = tk.Tk()
    app = MacArthurRankingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
