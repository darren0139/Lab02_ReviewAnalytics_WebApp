"""Streamlit presentation layer for the Review Analytics Platform."""

from datetime import datetime

import streamlit as st

from config import DEFAULT_MODEL , AVAILABLE_MODELS
from database.db_manager import (
    get_summaries_by_category,
    get_summary_by_id,
    init_db,
    save_summary,
)
from services.openai_service import analyze_review_sentiment


st.set_page_config(page_title="Review Analyst Pro", page_icon="📈", layout="wide")

# Initialize database once when the app starts.
init_db()


if "view_mode" not in st.session_state:
    st.session_state.view_mode = "new_analysis"

if "selected_summary_id" not in st.session_state:
    st.session_state.selected_summary_id = None

selected_model = st.selectbox(
    "Choose AI Model",
    AVAILABLE_MODELS,
    index=AVAILABLE_MODELS.index(DEFAULT_MODEL)
)

def format_timestamp(timestamp: str) -> str:
    """Format both ISO timestamps and older sqlite datetime strings safely."""
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        try:
            parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return timestamp

    return parsed.strftime("%b %d, %H:%M")


with st.sidebar:
    st.title("📁 Navigation & History")

    if st.button("➕ Analyze New Reviews", use_container_width=True, type="primary"):
        st.session_state.view_mode = "new_analysis"
        st.session_state.selected_summary_id = None
        st.rerun()

    st.divider()
    st.subheader("📜 Filter Past Summaries")

    categories = {
        "🟢 Good (8-10)": "Good",
        "🟡 Average (4-7)": "Average",
        "🔴 Bad (0-3)": "Bad",
    }

    for label, db_category in categories.items():
        with st.expander(label):
            records = get_summaries_by_category(db_category)

            if not records:
                st.caption("No historical records found.")

            for rec_id, filename, timestamp in records:
                time_str = format_timestamp(timestamp)
                btn_label = f"📄 {filename} ({time_str})"

                if st.button(btn_label, key=f"rec_{rec_id}", use_container_width=True):
                    st.session_state.view_mode = "view_past"
                    st.session_state.selected_summary_id = rec_id
                    st.rerun()


if st.session_state.view_mode == "view_past" and st.session_state.selected_summary_id is not None:
    record = get_summary_by_id(st.session_state.selected_summary_id)

    if record is None:
        st.error("Could not retrieve the specified historical record.")
    else:
        filename, summary, rating, category, created_at = record

        st.title(f"📜 Archived Summary: {filename}")
        st.caption(f"Analyzed on: {created_at} | Category Tier: **{category}**")
        st.markdown("---")
        
        # Display the visual metric card
        metric_col, message_col = st.columns([1, 4])

        with metric_col:
            st.metric(label="Overall Rating", value=f"{rating} / 10")

        with message_col:
            if category == "Good":
                st.success("🎯 This batch reflects overall positive customer sentiment.")
            elif category == "Average":
                st.warning("⚖️ This batch reflects mixed or average customer sentiment.")
            else:
                st.error("⚠️ This batch reflects critical or negative customer sentiment.")

        st.markdown("### 📋 Core Synthesis Summary")
        st.markdown(summary)

else:
    st.title("📊 Customer Review Analytics Engine")
    st.caption(f"Cloud Architecture Backend: **{selected_model}**")
    st.markdown("---")

    st.markdown(
        """
        ### 📥 Processing Pipeline
        Upload a `.txt` file containing customer feedback. The platform will evaluate sentiment,
        generate structured takeaways, and save the result into the database automatically.
        """
    )

    uploaded_file = st.file_uploader("Drop customer feedback .txt file here", type=["txt"])

    if uploaded_file is not None:
        try:
            review_text = uploaded_file.read().decode("utf-8")

            with st.expander("📄 Review File Context Preview", expanded=False):
                st.text(review_text)

            st.markdown("---")

            if st.button("🚀 Execute Sentiment Analysis", use_container_width=True):
                with st.spinner("Openai is interpreting the review and mapping sentiment score..."):
                    try:
                        clean_summary, rating, category = analyze_review_sentiment(review_text, selected_model)
                        save_summary(uploaded_file.name, clean_summary, rating, category)

                        st.success(
                            f"✅ Processing finalized! Saved under **{category}** classification category."
                        )

                        metric_col, detail_col = st.columns([1, 4])
                        metric_col.metric(label="Calculated Score", value=f"{rating} / 10")
                        detail_col.info(
                            f"Database router pipeline assigned this to the **{category}** segment container."
                        )

                        st.markdown("### 📋 AI Generated Synthesis Review")
                        st.markdown(clean_summary)

                    except Exception as api_err:
                        st.error(f"❌ Cloud API request interrupted: {api_err}")

        except Exception as file_err:
            st.error(f"❌ Structural read error: {file_err}")