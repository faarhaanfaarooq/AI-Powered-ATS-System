import streamlit as st
import json
import re
from prompt import input_prompt1, input_prompt2, input_prompt3
from backend import get_gemini_response, input_pdf_setup

st.set_page_config(page_title="ATS Resume Expert")
st.header("AI Powered Applicant Tracking System(ATS)")
input_text = st.text_area("Job Description: ", key="input", height=300)
uploaded_file = st.file_uploader("Upload your resume(PDF)...", type=["pdf"])


if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")


# ---- Layout with columns ----
col1, col2 = st.columns([1, 1])  # two equal columns (you can tweak ratios)
col3 = st.columns([1])[0]

with col2:
    submit1 = st.button("Tell me about the resume")
    submit2 = st.button("Percentage match")


def parse_json_response(response: str):
    """
    Clean and parse a model response that should be JSON but may contain
    markdown code fences or extra whitespace.
    Returns a Python dict if valid, otherwise None.
    """
    if not response:
        return None

    if isinstance(response, str):
        # Remove leading/trailing whitespace
        cleaned = response.strip()

        # Remove markdown-style code fences (```json ... ```)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "",
                         cleaned, flags=re.DOTALL).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    if isinstance(response, dict):
        return response

    return None


# ---- Resume Description According to Job Description ----
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The response is")
        st.write(response)
    else:
        st.write("Please upload your resume")

# ---- Percentage Match ----
elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt2)

        st.subheader("The response is")
        # st.write(response)  # optional, for debugging

        # Parse JSON safely
        parsed = parse_json_response(response)

        if parsed:
            # Overall Score
            st.subheader("Overall Score")
            overall_score = parsed["overall_score"]
            st.metric("Overall Score", f"{overall_score}/100")
            st.progress(overall_score / 100)

            # Section Analysis
            st.subheader("Section Analysis")

            for section, score in parsed["sections"].items():
                st.write(
                    f"**{section.replace('_', ' ').title()}**: {score}/100")
                st.progress(score / 100)

            # Missing Keywords
            st.subheader("Missing Keywords")
            if parsed["missing_keywords"]:
                st.write(", ".join(parsed["missing_keywords"]))
            else:
                st.write("✅ No critical keywords missing")

            # Final Thoughts
            st.subheader("Final Thoughts")
            st.write(parsed["final_thoughts"])

    else:
        st.write("Please upload your resume")


# ---- Cover Letter / Email Generator ----
with col1:
    st.subheader("AI Cover Letter & Email Generator")
    if uploaded_file is not None:
        doc_type = st.radio("Select document type:", [
                            "Cover Letter", "Email"], key="doc_type")
        tone = st.radio("Select tone:", [
                        "Formal", "Enthusiastic", "Concise"], key="tone")
        generate_doc = st.button("Generate Cover Letter / Email")
    else:
        st.warning("Please upload your resume and provide job description.")
        generate_doc = False


if uploaded_file is not None and generate_doc:
    pdf_content = input_pdf_setup(uploaded_file)
    prompt = input_prompt3.format(
        doc_type=doc_type,
        job_description=input_text,
        resume=pdf_content,
        tone=tone
    )
    response = get_gemini_response(input_text, pdf_content, prompt)
    st.subheader(f"Generated {doc_type}")
    st.write(response)
