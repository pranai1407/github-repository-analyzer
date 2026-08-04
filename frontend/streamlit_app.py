import streamlit as st
import requests

# ----------------------------------------
# Page Configuration
# ----------------------------------------

st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------
# Session State
# ----------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""

# ----------------------------------------
# Title
# ----------------------------------------

st.title("📊 GitHub Repository Analyzer")

repo_url = st.text_input(
    "Enter GitHub Repository URL",
    value=st.session_state.repo_url
)

# ----------------------------------------
# Analyze Button
# ----------------------------------------

if st.button("Analyze Repository"):

    if repo_url.strip() == "":
        st.error("Please enter a GitHub repository URL.")
    else:

        with st.spinner("Analyzing repository..."):

            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                params={
                    "repo_url": repo_url
                }
            )

            if response.status_code == 200:
                st.session_state.analysis = response.json()
                st.session_state.repo_url = repo_url
            else:
                st.error("Failed to analyze repository.")

# ----------------------------------------
# Display Analysis
# ----------------------------------------

if st.session_state.analysis:

    data = st.session_state.analysis

    st.success("Analysis Complete!")

    # =====================================
    # Repository Overview
    # =====================================

    st.header("📁 Repository Overview")

    st.write(f"**Repository:** {data['repository_name']}")
    st.write(f"**Default Branch:** {data['default_branch']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Branches", data["total_branches"])

    with col2:
        st.metric("Commits", data["total_commits"])

    with col3:
        st.metric("Contributors", data["total_contributors"])

    # =====================================
    # Languages
    # =====================================

    st.divider()

    st.header("🐍 Languages")

    languages = data["languages"]

    if languages:

        total_files = sum(languages.values())

        for language, count in languages.items():

            percentage = count / total_files

            st.write(f"**{language}** ({percentage*100:.1f}%)")

            st.progress(percentage)

    else:

        st.info("No programming languages detected.")
    # =====================================
    # Dependencies
    # =====================================

    st.divider()

    st.header("📦 Dependencies")

    dependencies = data["dependencies"]

    if dependencies:

        for dependency in dependencies:
            st.write(f"✅ {dependency}")

    else:

        st.info("No dependencies found.")
    # =====================================
    # Hotspot Files
    # =====================================

    st.divider()

    st.header("🔥 Hotspot Files")

    hotspot_files = data["hotspot_files"]

    if hotspot_files:

        for file_name, changes in hotspot_files:

            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(file_name)

            with col2:
                st.write(f"**{changes} commits**")

    else:

        st.info("No hotspot files found.")
    # =====================================
    # File Statistics
    # =====================================
    st.divider()

    st.header("📊 Repository Statistics")

    statistics = data["statistics"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📄 Total Files", statistics["total_files"])

    with col2:
        st.metric("📁 Total Directories", statistics["total_directories"])

        # =====================================
        # AI Summary
        # =====================================

    st.divider()

    st.header("🤖 AI Summary")

    with st.expander("View AI Summary", expanded=True):
        st.markdown(data["ai_summary"])
    # =====================================
    # Generate PDF Report
    # =====================================

    st.divider()

    st.header("📄 Export Analysis Report")

    if st.button("Generate PDF Report"):

        with st.spinner("Generating report..."):

            response = requests.post(
                "http://127.0.0.1:8000/generate-report",
                params={
                    "repo_url": st.session_state.repo_url
                }
            )

            if response.status_code == 200:

                with open("Repository_Analysis_Report.pdf", "wb") as file:
                    file.write(response.content)

                st.success("PDF Generated Successfully!")

                with open("Repository_Analysis_Report.pdf", "rb") as file:

                    st.download_button(
                        label="⬇ Download Repository Report",
                        data=file,
                        file_name="Repository_Analysis_Report.pdf",
                        mime="application/pdf"
                    )

            else:

                st.error("Unable to generate PDF.")
    # =====================================
    # Ask AI
    # =====================================

    st.divider()

    st.header("💬 Ask AI")

    question = st.text_input(
        "Ask anything about this repository"
    )

    if st.button("Ask AI"):

        if question.strip() == "":
            st.warning("Please enter a question.")

        else:

            with st.spinner("Thinking..."):

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    params={
                        "repo_url": st.session_state.repo_url,
                        "question": question
                    }
                )

                if response.status_code == 200:

                    answer = response.json()

                    st.success("Answer")

                    st.markdown(answer["answer"])

                else:

                    st.error("Unable to get AI response.")