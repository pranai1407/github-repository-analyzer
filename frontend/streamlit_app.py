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

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/analyze",
                    params={
                        "repo_url": repo_url
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    if result.get("status") == "error":
                        st.error(result.get("message", "Repository analysis failed."))

                    else:
                        st.session_state.analysis = result
                        st.session_state.repo_url = repo_url
                        st.success("Analysis Complete!")

                else:

                    st.error(
                        f"Repository analysis failed "
                        f"(HTTP {response.status_code})."
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Unable to connect to the backend. "
                    "Please make sure FastAPI is running on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱ Repository analysis is taking too long. "
                    "Please try again."
                )

            except requests.exceptions.RequestException:

                st.error(
                    "❌ Unable to communicate with the backend."
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

    summary = data["ai_summary"]

    st.subheader("📌 Repository Purpose")
    st.write(summary["repository_purpose"])

    st.subheader("🛠 Technologies Used")

    for tech in summary["technologies_used"]:
        st.write(f"• {tech}")

    st.subheader("🏗 Project Organization")
    st.write(summary["project_organization"])

    st.subheader("👥 Intended Users")
    st.write(summary["intended_users"])

    st.subheader("📖 Beginner Summary")
    st.write(summary["beginner_summary"])
    # =====================================
    # Generate PDF Report
    # =====================================

    st.divider()

    st.header("📄 Export Analysis Report")

    if st.button("Generate PDF Report"):

        with st.spinner("Generating report..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/generate-report",
                    params={
                        "repo_url": st.session_state.repo_url
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    with open(
                        "Repository_Analysis_Report.pdf",
                        "wb"
                    ) as file:

                        file.write(response.content)

                    st.success("PDF Generated Successfully!")

                    with open(
                        "Repository_Analysis_Report.pdf",
                        "rb"
                    ) as file:

                        st.download_button(
                            label="⬇ Download Repository Report",
                            data=file,
                            file_name="Repository_Analysis_Report.pdf",
                            mime="application/pdf"
                        )

                else:

                    try:

                        error_data = response.json()

                        st.error(
                            error_data.get(
                                "message",
                                "Unable to generate PDF."
                            )
                        )

                    except ValueError:

                        st.error(
                            "Unable to generate PDF."
                        )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Unable to connect to the backend. "
                    "Please make sure FastAPI is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱ PDF generation is taking too long. "
                    "Please try again."
                )

            except requests.exceptions.RequestException:

                st.error(
                    "❌ Unable to communicate with the backend."
                )
    # =====================================
    # AI Recommendations
    # =====================================

    st.divider()

    st.header("💡 AI Recommendations")

    recommendations = data["ai_recommendations"]

    st.subheader("✅ Repository Strengths")

    for strength in recommendations["strengths"]:
        st.write(f"✔ {strength}")

    st.subheader("⚠ Areas for Improvement")

    for improvement in recommendations["areas_for_improvement"]:
        st.write(f"• {improvement}")

    st.subheader("⭐ Best Practices")

    for practice in recommendations["best_practices"]:
        st.write(f"• {practice}")

    st.subheader("🏆 Overall Repository Quality")

    st.success(recommendations["overall_quality"])
    st.header("💬 Ask AI")

    question = st.text_input(
        "Ask anything about this repository"
    )

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

        elif not st.session_state.repo_url:
            st.warning("Please analyze a repository first.")

        else:

            with st.spinner("Thinking..."):

                try:

                    response = requests.post(
                        "http://127.0.0.1:8000/ask",
                        params={
                            "repo_url": st.session_state.repo_url,
                            "question": question
                        },
                        timeout=120
                    )

                    if response.status_code == 200:

                        answer = response.json()

                        if answer.get("status") == "error":

                            st.error(
                                answer.get(
                                    "message",
                                    "Unable to answer the question."
                                )
                            )

                        else:

                            st.success("Answer")

                            st.markdown(answer["answer"])

                    else:

                        st.error(
                            f"AI request failed "
                            f"(HTTP {response.status_code})."
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Unable to connect to the backend. "
                        "Please make sure FastAPI is running."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "⏱ AI is taking too long to respond. "
                        "Please try again."
                    )

                except requests.exceptions.RequestException:

                    st.error(
                        "❌ Unable to communicate with the AI service."
                    )