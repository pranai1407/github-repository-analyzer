import streamlit as st
import requests

st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 GitHub Repository Analyzer")

repo_url = st.text_input("Enter GitHub Repository URL")

if st.button("Analyze Repository"):

    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
        st.stop()

    with st.spinner("Analyzing repository..."):

        response = requests.post(
            "http://127.0.0.1:8000/analyze",
            params={
                "repo_url": repo_url
            }
        )

        data = response.json()

    st.success("Analysis Complete!")

    # ============================================
    # Repository Overview
    # ============================================

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

    # ============================================
    # Languages
    # ============================================

    st.divider()

    st.header("🐍 Languages")

    languages = data["languages"]

    if languages:

        total_files = sum(languages.values())

        for language, count in languages.items():

            percentage = (count / total_files) * 100

            st.write(f"**{language}** ({percentage:.1f}%)")

            st.progress(percentage / 100)

    else:
        st.info("No programming languages detected.")

    # ============================================
    # AI Summary
    # ============================================

    st.divider()

    st.header("🤖 AI Summary")

    with st.expander("View AI Summary", expanded=True):
        st.markdown(data["ai_summary"])
    # ============================================
# Ask AI
# ============================================

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
                        "repo_url": repo_url,
                        "question": question
                    }
                )

                answer = response.json()

            st.success("Answer")

            st.markdown(answer["answer"])
