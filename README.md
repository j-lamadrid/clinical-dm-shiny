# ACE Clinical Data Management Scripts

Clinical data processing utilities for ACE workflows, including eye-tracking merges, visit flagging, late-talker grouping, treatment-hour summaries, and MacArthur percentile population.

## Links

- GitHub repository: [j-lamadrid/clinical-dm-scripts](https://github.com/j-lamadrid/clinical-dm-scripts)
- Live app: [ACE Clinical Data Desk](https://j-lamadrid.shinyapps.io/ace_clinical_data_desk/)
- shinyapps.io platform: [shinyapps.io](https://www.shinyapps.io/)
- Shiny for Python docs: [shiny.posit.co/py](https://shiny.posit.co/py/)
- shinyapps.io guide: [Getting started with shinyapps.io](https://docs.posit.co/shinyapps.io/guide/getting_started/)
- Python deployment guide: [rsconnect-python deploy commands](https://docs.posit.co/rsconnect-python/commands/deploy/)

Hosted deployment:
- Public URL: [https://j-lamadrid.shinyapps.io/ace_clinical_data_desk/](https://j-lamadrid.shinyapps.io/ace_clinical_data_desk/)

## Included Workflows

- [UpdateEyeTracking.py](UpdateEyeTracking.py): merges exported eye-tracking data into a matching master sheet using the ET summary and LWR files.
- [Flagger.py](Flagger.py): sorts form exports by subject and visit date, then assigns visit flags.
- [Group.py](Group.py): groups late talker data into the standard diagnostic categories.
- [AddGroup.py](AddGroup.py): applies a custom DxJ grouping rule to an already grouped workbook.
- [TreatmentCondensed.py](TreatmentCondensed.py): totals treatment units in the condensed format.
- [TreatmentCondensedWV.py](TreatmentCondensedWV.py): totals treatment units in the condensed WV format.
- [TreatmentHoursFull.py](TreatmentHoursFull.py): calculates total and average treatment hours from the full treatment workbook.
- [MacArthurPercentiles.py](MacArthurPercentiles.py): populates MacArthur percentile values into the LWR output.
- [modules/ets.py](modules/ets.py): shared eye-tracking transformation logic used by the eye-tracking workflow.

## Requirements

These scripts were written for Python 3.12.

Install dependencies with:

```bash
pip install -r requirements.txt
```

Or with Conda:

```bash
conda install --file requirements.txt
```

## Local Usage

Run a workflow from the repository root with:

```bash
python <script_name>.py
```

Examples:

```bash
python UpdateEyeTracking.py
python Flagger.py
python Group.py
python AddGroup.py
python TreatmentCondensed.py
python TreatmentCondensedWV.py
python TreatmentHoursFull.py
python MacArthurPercentiles.py
```

## Workflow Notes

### Eye Tracking Sheet Merger

Uses four source files:
- exported eye-tracking data
- matching master sheet
- ET summary workbook
- LWR file

The workflow aggregates the selected timeline and appends the transformed output to the running master sheet.

### Flagger

Takes an exported CSV, sorts by `SubjectId` and `EvalDate`, removes duplicate subject/date rows, and assigns sequential visit numbers.

### Group

Groups late talker data into these categories:
- Always Typical
- Transient Language Delay
- Persistent Language Delay
- Persistent Global Delay
- LD to ASD
- Persistent ASD

### AddGroup

Adds a custom diagnostic grouping rule using:
- group name
- allowed starting DxJs
- allowed ending DxJs
- allowed middle DxJs
- minimum number of DxJs

### Treatment Hours

The treatment scripts calculate total units or hours and average weekly values, depending on the selected workflow.

### MacArthur Percentiles

Populates the LWR with the best-fitting percentile by visit and section using the scoring appendix workbook.

## Repository Files

- [requirements.txt](requirements.txt): Python dependencies
- [luminance_calculations.ipynb](luminance_calculations.ipynb): exploratory notebook
- [test_diff_index.xlsx](test_diff_index.xlsx): sample workbook included in the repository

## Notes

- The older tkinter screenshots were intentionally removed from this README so the documentation focuses on the current web/deployment-oriented workflow instead of the legacy desktop UI.
