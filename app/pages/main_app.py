# pages/main_app.py
import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import zipfile

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Main App", layout="wide")

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.district = None
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.switch_page("app.py")

def upload_file(category, report_type, report_code, title, description, file):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    files = {"file": (file.name, file, "multipart/form-data")}
    params = {"category": category, "report_type": report_type, "report_code": report_code, "title": title, "description": description}
    
    try:
        response = requests.post(f"{API_URL}/upload/", headers=headers, files=files, params=params)
        if response.status_code == 200:
            st.success(response.json()["message"])
            return True
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Upload failed: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"Upload failed with non-JSON response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return False

def update_report(report_code, title, description):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.put(f"{API_URL}/reports/{report_code}", headers=headers, json={"title": title, "description": description})
    if response.status_code == 200:
        st.success(response.json()["message"])
        st.rerun()
    else:
        st.error(response.json()["detail"])

def delete_report(report_code):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.delete(f"{API_URL}/reports/{report_code}", headers=headers)
    if response.status_code == 200:
        st.success(response.json()["message"])
        st.rerun()
    else:
        st.error(response.json()["detail"])

def delete_selected_reports(report_codes, reports_df):
    deleted = []
    skipped = []
    for report_code in report_codes:
        report = reports_df[reports_df["report_code"] == report_code].iloc[0]
        checker_status = report["checker_status"]
        reviewer_status = report["reviewer_status"]
        if checker_status == "Checked" or reviewer_status == "Approved":
            skipped.append(report_code)
        else:
            delete_report(report_code)
            deleted.append(report_code)
    if skipped:
        st.warning(f"Skipped deletion of reports with 'Checked' or 'Approved' status: {', '.join(skipped)}")
    if deleted:
        st.success(f"Deleted reports: {', '.join(deleted)}")

def download_report(report_code):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/reports/{report_code}/download", headers=headers)
    if response.status_code == 200:
        data = response.json()
        file_content = bytes.fromhex(data["file_content"])
        return file_content, data["filename"]
    else:
        st.error(response.json()["detail"])
        return None, None

def update_status(report_code, checker_status=None, reviewer_status=None, comment=""):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    data = {"checker_status": checker_status, "reviewer_status": reviewer_status, "comment": comment}
    response = requests.post(f"{API_URL}/reports/{report_code}/status", headers=headers, json=data)
    if response.status_code == 200:
        st.success(response.json()["message"])
        st.rerun()  # Refresh the page to reflect the updated status
    else:
        st.error(response.json()["detail"])

def fetch_reports():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/reports/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data:
            return pd.DataFrame(columns=["select", "report_code", "title", "description", "prepared_by", "district", 
                                         "created_date", "checker_status", "reviewer_status", "checker_comment", 
                                         "reviewer_comment"])
        df = pd.DataFrame(data)
        df.insert(0, "select", False)  # Add selection checkbox column
        return df
    else:
        st.error(f"Failed to fetch reports: {response.json().get('detail', response.text)}")
        return pd.DataFrame(columns=["select", "report_code", "title", "description", "prepared_by", "district", 
                                     "created_date", "checker_status", "reviewer_status", "checker_comment", 
                                     "reviewer_comment"])

def fetch_merged_reports():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/reports/merged/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(response.json()["detail"])
        return None

# Initialize session state
if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False
if "edit_report_code" not in st.session_state:
    st.session_state.edit_report_code = None

st.title("District Data Management")

if "token" not in st.session_state or st.session_state.token is None:
    st.error("Please log in first.")
    st.switch_page("app.py")
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Reports", "Users"]) if st.session_state.role == "main_office" else "Reports"
    
    st.subheader(f"Welcome, {st.session_state.username} ({st.session_state.role})")
    if st.button("Logout"):
        logout()

    if page == "Reports":
        st.subheader("Your Reports")
        reports_df = fetch_reports()
        
        if not reports_df.empty:
            # Conditionally configure columns based on role
            column_config = {
                "select": st.column_config.CheckboxColumn("Select", default=False),
                "report_code": "Report Code",
                "title": "Title",
                "description": "Description",
                "prepared_by": "Prepared By",
                "created_date": "Created Date",
                "checker_status": "Checker Status",
                "reviewer_status": "Reviewer Status",
                "checker_comment": "Checker Comment",
                "reviewer_comment": "Reviewer Comment"
            }
            if st.session_state.role == "main_office":
                column_config["district"] = "District"  # Add District column for main_office user

            # Use st.data_editor for interactive checkboxes
            edited_df = st.data_editor(
                reports_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                disabled=["report_code", "title", "description", "prepared_by", "district", "created_date", 
                          "checker_status", "reviewer_status", "checker_comment", "reviewer_comment"],
                key="reports_table"
            )

            # Get selected rows
            selected_rows = edited_df[edited_df["select"] == True]
            selected_reports = selected_rows["report_code"].tolist()

            # Debug output
            st.write("Selected Report Codes:", selected_reports)

            # Action buttons for selected rows
            if selected_reports:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Download Selected"):
                        if len(selected_reports) == 1:
                            # Single file download
                            file_content, filename = download_report(selected_reports[0])
                            if file_content:
                                st.download_button(
                                    label=f"Download {filename}",
                                    data=file_content,
                                    file_name=filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"direct_download_{selected_reports[0]}"
                                )
                        else:
                            # Multiple files: Create a ZIP
                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                for report_code in selected_reports:
                                    file_content, filename = download_report(report_code)
                                    if file_content:
                                        zip_file.writestr(filename, file_content)
                            zip_buffer.seek(0)
                            st.download_button(
                                label="Download Selected Reports (ZIP)",
                                data=zip_buffer,
                                file_name="selected_reports.zip",
                                mime="application/zip",
                                key="download_zip"
                            )
                with col2:
                    if st.session_state.role == "district_user" and st.button("Delete Selected"):
                        delete_selected_reports(selected_reports, reports_df)
            else:
                st.info("Select one or more reports to enable Download/Delete actions.")

            # Edit form (if applicable)
            if st.session_state.role == "district_user" and st.session_state.edit_report_code:
                report_to_edit = reports_df[reports_df["report_code"] == st.session_state.edit_report_code].iloc[0]
                with st.form(key=f"edit_form_{report_to_edit['report_code']}"):
                    edit_title = st.text_input("New Title", report_to_edit["title"])
                    edit_desc = st.text_input("New Description", report_to_edit["description"])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes"):
                            update_report(report_to_edit["report_code"], edit_title, edit_desc)
                            st.session_state.edit_report_code = None
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.edit_report_code = None
                            st.rerun()

            # Status updates
            if st.session_state.role == "district_manager":
                with st.expander("Update Checker Status"):
                    report_to_check = st.selectbox("Select Report", reports_df["report_code"].tolist())
                    checker_status = st.selectbox("Checker Status", ["Pending", "Checked", "Rejected"])
                    checker_comment = st.text_input("Comment (required for Rejected)")
                    if st.button("Update Checker Status"):
                        if checker_status == "Rejected" and not checker_comment:
                            st.error("Comment required for rejection")
                        else:
                            update_status(report_to_check, checker_status=checker_status, comment=checker_comment)

            if st.session_state.role == "main_office":
                with st.expander("Update Reviewer Status"):
                    report_to_review = st.selectbox("Select Report", reports_df["report_code"].tolist())
                    reviewer_status = st.selectbox("Reviewer Status", ["Pending", "Approved", "Rejected"])
                    reviewer_comment = st.text_input("Comment (required for Rejected)")
                    if st.button("Update Reviewer Status"):
                        if reviewer_status == "Rejected" and not reviewer_comment:
                            st.error("Comment required for rejection")
                        else:
                            update_status(report_to_review, reviewer_status=reviewer_status, comment=reviewer_comment)

        else:
            st.info("No reports available yet.")

        if st.session_state.role == "district_user" and not st.session_state.show_upload_form:
            if st.button("Add Report"):
                st.session_state.show_upload_form = True
                st.rerun()

        if st.session_state.role == "district_user" and st.session_state.show_upload_form:
            st.subheader("Upload Report")
            with st.form(key="upload_form"):
                
                report_type = st.selectbox("Report Type", ["balance_sheet", "income_statement", "cash_flow"])
                report_code = st.text_input("Report Code (e.g., FIN-001)")
                title = st.text_input("Report Title")
                description = st.text_input("Description")
                category = st.selectbox("Category", ["Operation", "Finance", "Risk", "HR", "IT"])
                uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
                submit_button = st.form_submit_button(label="Upload Report")

                if submit_button and uploaded_file:
                    success = upload_file(report_type, report_code, title, description, category, uploaded_file)
                    if success:
                        st.session_state.show_upload_form = False
                        st.rerun()

        if st.session_state.role == "main_office":
            st.subheader("Merged Reports")
            merged_data = fetch_merged_reports()
            if merged_data:
                for report_type, data in merged_data.items():
                    st.write(f"{report_type.capitalize()} Reports:")
                    st.dataframe(pd.DataFrame(data))
                    buffer = BytesIO()
                    pd.DataFrame(data).to_excel(buffer, index=False)
                    st.download_button(
                        label=f"Download {report_type} Merged Report",
                        data=buffer.getvalue(),
                        file_name=f"{report_type}_merged.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    elif page == "Users":
        st.switch_page("pages/users.py")