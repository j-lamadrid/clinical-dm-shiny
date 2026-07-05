from __future__ import annotations

from pathlib import Path
import traceback

from shiny import App, reactive, render, ui

from clinical_dm.shiny_app.services import (
    OUTPUT_ROOT,
    SCRIPT_DETAILS,
    SCRIPT_OPTIONS,
    SOFTWARE_OPTIONS,
    TIMELINE_OPTIONS,
    run_add_group,
    run_eye_tracking,
    run_flagger,
    run_group,
    run_macarthur,
    run_treatment_condensed,
    run_treatment_condensed_wv,
    run_treatment_full,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT_DIR / "www"
GROUP_DEMO_FILE = ROOT_DIR / "sample_data" / "test_diff_index.xlsx"


def file_info(uploaded_file):
    if not uploaded_file:
        raise ValueError("Please upload the required file before running the script.")

    file_data = uploaded_file[0]
    if isinstance(file_data, dict):
        return Path(file_data["datapath"]), Path(file_data["name"]).name

    return Path(file_data.datapath), Path(file_data.name).name


def parse_tokens(raw_value: str) -> list[str]:
    return raw_value.split() if raw_value and raw_value.strip() else []


def mac_window(title: str, *children, body_class: str | None = None):
    classes = "window-body"
    if body_class:
        classes = f"{classes} {body_class}"

    return ui.div(
        ui.div(ui.span(title, class_="window-title-text"), class_="window-titlebar"),
        ui.div(*children, class_=classes),
        class_="mac-window",
    )


def eye_tracking_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload the four source files, choose the timeline, and the app will assemble an updated master workbook.",
                class_="window-copy",
            ),
            ui.input_file("eye_export", "Export File (.tsv)", accept=[".tsv"]),
            ui.input_file("eye_master", "Master Sheet (.xlsx)", accept=[".xlsx"]),
            class_="control-group",
        ),
        ui.div(
            ui.input_file("eye_summary", "ET Summary Sheet (.xlsx)", accept=[".xlsx"]),
            ui.input_file("eye_lwr", "LWR File (.csv)", accept=[".csv"]),
            ui.input_select("eye_timeline", "Timeline", TIMELINE_OPTIONS, selected="Geo"),
            class_="control-group",
        ),
        ui.div(
            ui.input_select("eye_software", "Software", SOFTWARE_OPTIONS, selected="Tobii ProLab"),
            ui.input_text("eye_other_software", "Other Software", placeholder="Used only when Software = Other"),
            ui.input_text(
                "eye_project_hint",
                "Project Label Override",
                placeholder="Optional if the uploaded filename does not already include the project number",
            ),
            ui.input_text("eye_output_name", "Output File Name", placeholder="master_updated"),
            class_="control-group",
        ),
        class_="control-grid",
    )


def flagger_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload a CSV export and the app will sort visits by subject and evaluation date before flagging them.",
                class_="window-copy",
            ),
            ui.input_file("flagger_input", "Exported CSV", accept=[".csv"]),
            ui.input_text("flagger_output_name", "Output File Name", placeholder="flagged_visits"),
            class_="control-group",
        ),
        class_="control-grid",
    )


def group_form():
    return ui.div(
        ui.div(
            ui.p(
                "Run the bundled demo workbook or upload a late talker workbook to apply the standard diagnostic grouping logic.",
                class_="window-copy",
            ),
            ui.input_checkbox("group_use_demo", "Use bundled demo workbook", value=True),
            ui.input_file("group_input", "Late Talkers Workbook (.xlsx)", accept=[".xlsx"]),
            ui.input_text("group_output_name", "Output File Name", placeholder="grouped_late_talkers"),
            class_="control-group",
        ),
        class_="control-grid",
    )


def add_group_form():
    return ui.div(
        ui.div(
            ui.p(
                "Define a custom DxJ rule and apply it to an already grouped workbook.",
                class_="window-copy",
            ),
            ui.input_text("add_group_name", "New Group Name", placeholder="ASD Transition"),
            ui.input_numeric("add_group_min_dxj", "Minimum # of DxJ", value=2, min=1, step=1),
            ui.input_file("add_group_input", "Grouped Workbook (.xlsx)", accept=[".xlsx"]),
            class_="control-group",
        ),
        ui.div(
            ui.p(
                "Allowed DxJs: DD, FMD, GDD, GD, LD, MD, Other, TD, ASD, ASD_Features, TypSibASD",
                class_="meta-copy",
            ),
            ui.input_text("add_group_begins", "Begins With", placeholder="Space-separated DxJs"),
            ui.input_text("add_group_ends", "Ends With", placeholder="Space-separated DxJs"),
            ui.input_text("add_group_possibilities", "Possibilities", placeholder="Space-separated DxJs"),
            ui.input_text("add_group_output_name", "Output File Name", placeholder="custom_group"),
            class_="control-group",
        ),
        class_="control-grid",
    )


def treatment_full_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload the full treatment-hours workbook to calculate total hours and average hours per week.",
                class_="window-copy",
            ),
            ui.input_file("treatment_full_input", "Treatment Workbook (.xlsx)", accept=[".xlsx"]),
            ui.input_text("treatment_full_output_name", "Output File Name", placeholder="treatment_hours_full"),
            class_="control-group",
        ),
        class_="control-grid",
    )


def treatment_condensed_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload the condensed treatment workbook to total units by service grouping.",
                class_="window-copy",
            ),
            ui.input_file("treatment_condensed_input", "Condensed Workbook (.xlsx)", accept=[".xlsx"]),
            ui.input_text(
                "treatment_condensed_output_name",
                "Output File Name",
                placeholder="treatment_units_condensed",
            ),
            class_="control-group",
        ),
        class_="control-grid",
    )


def treatment_condensed_wv_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload the condensed WV workbook to total units by service grouping.",
                class_="window-copy",
            ),
            ui.input_file("treatment_condensed_wv_input", "Condensed WV Workbook (.xlsx)", accept=[".xlsx"]),
            ui.input_text(
                "treatment_condensed_wv_output_name",
                "Output File Name",
                placeholder="treatment_units_condensed_wv",
            ),
            class_="control-group",
        ),
        class_="control-grid",
    )


def macarthur_form():
    return ui.div(
        ui.div(
            ui.p(
                "Upload the LWR CSV and scoring appendix workbook to generate MacArthur percentile columns.",
                class_="window-copy",
            ),
            ui.input_file("macarthur_lwr", "LWR File (.csv)", accept=[".csv"]),
            ui.input_file("macarthur_appendix", "Scoring Appendix (.xlsx)", accept=[".xlsx"]),
            ui.input_text("macarthur_output_name", "Output File Name", placeholder="macarthur_percentiles"),
            class_="control-group",
        ),
        class_="control-grid",
    )


TOOL_FORMS = {
    "eye_tracking": eye_tracking_form,
    "flagger": flagger_form,
    "group": group_form,
    "add_group": add_group_form,
    "treatment_full": treatment_full_form,
    "treatment_condensed": treatment_condensed_form,
    "treatment_condensed_wv": treatment_condensed_wv_form,
    "macarthur": macarthur_form,
}


app_ui = ui.page_fluid(
    ui.tags.link(rel="stylesheet", href="assets/macintosh.css"),
    ui.div(
        ui.div(
            ui.div(
                ui.span("ACE Clinical Data Desk", class_="menu-strong"),
                ui.span("Shiny Workstation"),
                class_="menu-status",
            ),
            class_="menu-bar",
        ),
        ui.div(
            mac_window(
                "About This Desk",
                ui.p(
                    "This workstation wraps the clinical data scripts into one Shiny app while keeping the original processing logic intact.",
                    class_="intro-text",
                ),
                ui.p(
                    "Choose a script from the Finder-style list, fill in its control panel, run it, and download the result from the status window.",
                    class_="intro-text",
                ),
            ),
            ui.div(
                ui.div(
                    mac_window(
                        "Script Chooser",
                        ui.p("Select the tool to open in the control panel.", class_="window-copy"),
                        ui.div(
                            ui.div(
                                ui.div(ui.span("", class_="finder-icon"), ui.span("Clinical Scripts", class_="finder-label"), class_="finder-row"),
                                ui.div(ui.span("", class_="finder-icon"), ui.span("Outputs Folder"), class_="finder-row"),
                                class_="finder-list",
                            ),
                            ui.input_select(
                                "tool",
                                "Available Scripts",
                                SCRIPT_OPTIONS,
                                selected="group",
                                size="8",
                            ),
                            class_="script-select",
                        ),
                        ui.output_ui("tool_help"),
                    ),
                    mac_window(
                        "Desktop Notes",
                        ui.div(
                            ui.p("Outputs Folder", class_="desk-note-title"),
                            ui.p(str(OUTPUT_ROOT.resolve()), class_="desk-note-copy"),
                            class_="desk-note",
                        ),
                        ui.div(
                            ui.p("Legacy Launchers", class_="desk-note-title"),
                            ui.p("Standalone tkinter launchers now live in the scripts folder.", class_="desk-note-copy"),
                            class_="desk-note",
                        ),
                    ),
                    class_="desktop-column",
                ),
                ui.div(
                    mac_window(
                        "Control Panel",
                        ui.p("Load the fields for the selected script and run the workflow from here.", class_="window-copy"),
                        ui.p("Current Script", class_="section-title"),
                        ui.output_ui("tool_form"),
                        ui.input_action_button("run_tool", "Run Selected Script"),
                    ),
                    mac_window(
                        "Status Monitor",
                        ui.output_ui("result_status"),
                        ui.output_ui("download_ui"),
                        ui.output_text_verbatim("run_log"),
                    ),
                    class_="desktop-column",
                ),
                class_="desktop-grid",
            ),
            class_="desktop",
        ),
        class_="mac-app",
    ),
    title="ACE Clinical Data Desk",
)


def server(input, output, session):
    del session

    run_state = reactive.value("idle")
    run_message = reactive.value(
        "The Group demo workbook is bundled with the app. Press Run Selected Script to try it."
    )
    run_log_value = reactive.value(
        "Ready.\n\nThe default Group workflow uses sample_data/test_diff_index.xlsx. "
        "Script messages and processing logs will appear in this window."
    )
    output_path_value = reactive.value(None)

    @output
    @render.ui
    def tool_help():
        details = SCRIPT_DETAILS[input.tool()]
        return ui.div(
            ui.p(details["description"], class_="window-copy"),
            ui.p(
                ui.tags.strong("Launcher: "),
                ui.tags.code(details["script"]),
                class_="meta-line",
            ),
        )

    @output
    @render.ui
    def tool_form():
        return TOOL_FORMS[input.tool()]()

    @output
    @render.ui
    def result_status():
        state = run_state.get()
        message = run_message.get()
        output_path = output_path_value.get()

        status_class = "status-box"
        if state == "success":
            status_class += " success"
        elif state == "error":
            status_class += " error"

        children = [ui.p(message)]
        if output_path:
            children.append(ui.p("Saved Output", class_="status-label"))
            children.append(ui.tags.code(str(output_path)))

        return ui.div(*children, class_=status_class)

    @output
    @render.ui
    def download_ui():
        if run_state.get() != "success" or output_path_value.get() is None:
            return ui.div()

        return ui.div(ui.download_button("download_result", "Download Last Output"), class_="download-area")

    @output(id="download_result")
    @render.download()
    def _download_result():
        output_path = output_path_value.get()
        if output_path is None:
            raise RuntimeError("No output file is available to download.")
        return str(output_path)

    @output
    @render.text
    def run_log():
        return run_log_value.get()

    @reactive.effect
    @reactive.event(input.run_tool)
    def _run_selected_tool():
        output_path_value.set(None)
        run_state.set("idle")
        run_message.set(f"Running {SCRIPT_OPTIONS[input.tool()]}...")
        run_log_value.set("Processing...")

        try:
            selected_tool = input.tool()

            if selected_tool == "eye_tracking":
                export_path, _ = file_info(input.eye_export())
                master_path, _ = file_info(input.eye_master())
                summary_path, _ = file_info(input.eye_summary())
                lwr_path, _ = file_info(input.eye_lwr())
                software = input.eye_software()
                if software == "Other":
                    software = (input.eye_other_software() or "").strip()
                    if not software:
                        raise ValueError("Please enter a software name when selecting Other.")
                result = run_eye_tracking(
                    export_path=export_path,
                    master_path=master_path,
                    summary_path=summary_path,
                    lwr_path=lwr_path,
                    timeline=input.eye_timeline(),
                    software=software,
                    project_hint=input.eye_project_hint(),
                    output_name=input.eye_output_name(),
                )

            elif selected_tool == "flagger":
                file_path, _ = file_info(input.flagger_input())
                result = run_flagger(file_path=file_path, output_name=input.flagger_output_name())

            elif selected_tool == "group":
                if input.group_use_demo():
                    if not GROUP_DEMO_FILE.exists():
                        raise FileNotFoundError(
                            f"The bundled demo workbook is missing: {GROUP_DEMO_FILE}"
                        )
                    file_path = GROUP_DEMO_FILE
                else:
                    file_path, _ = file_info(input.group_input())
                result = run_group(file_path=file_path, output_name=input.group_output_name())

            elif selected_tool == "add_group":
                file_path, _ = file_info(input.add_group_input())
                new_group = (input.add_group_name() or "").strip()
                if not new_group:
                    raise ValueError("Please enter a name for the new group.")
                result = run_add_group(
                    file_path=file_path,
                    new_group=new_group,
                    begins_with=parse_tokens(input.add_group_begins()),
                    ends_with=parse_tokens(input.add_group_ends()),
                    possibilities=parse_tokens(input.add_group_possibilities()),
                    min_dxj=int(input.add_group_min_dxj() or 2),
                    output_name=input.add_group_output_name(),
                )

            elif selected_tool == "treatment_full":
                file_path, _ = file_info(input.treatment_full_input())
                result = run_treatment_full(
                    file_path=file_path,
                    output_name=input.treatment_full_output_name(),
                )

            elif selected_tool == "treatment_condensed":
                file_path, _ = file_info(input.treatment_condensed_input())
                result = run_treatment_condensed(
                    file_path=file_path,
                    output_name=input.treatment_condensed_output_name(),
                )

            elif selected_tool == "treatment_condensed_wv":
                file_path, _ = file_info(input.treatment_condensed_wv_input())
                result = run_treatment_condensed_wv(
                    file_path=file_path,
                    output_name=input.treatment_condensed_wv_output_name(),
                )

            elif selected_tool == "macarthur":
                lwr_path, _ = file_info(input.macarthur_lwr())
                appendix_path, _ = file_info(input.macarthur_appendix())
                result = run_macarthur(
                    lwr_path=lwr_path,
                    appendix_path=appendix_path,
                    output_name=input.macarthur_output_name(),
                )

            else:
                raise ValueError(f"Unknown tool selection: {selected_tool}")

            output_path_value.set(result.output_path.resolve())
            run_state.set("success")
            run_message.set(f"{SCRIPT_OPTIONS[selected_tool]} finished successfully.")
            run_log_value.set(result.log)

        except Exception as exc:
            run_state.set("error")
            run_message.set(str(exc))
            run_log_value.set(traceback.format_exc())
            output_path_value.set(None)


app = App(app_ui, server, static_assets={"/assets": str(ASSET_DIR)})
