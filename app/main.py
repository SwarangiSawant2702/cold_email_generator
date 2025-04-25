import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    st.title("📧 Cold Mail Generator")

    url_input = st.text_input("Enter a Job URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Generate Cold Email")

    if submit_button:
        with st.spinner("Loading and analyzing job post..."):
            try:
                # Load and clean webpage content
                loader = WebBaseLoader([url_input])
                content = loader.load().pop().page_content
                cleaned_text = clean_text(content)

                # Load portfolio (if not preloaded)
                portfolio.load_portfolio()

                # Extract job roles and info
                jobs = llm.extract_jobs(cleaned_text)

                if not jobs:
                    st.warning("No job-related content was found on the provided URL.")
                    return

                for job in jobs:
                    # Debugging: print the type and structure of job
                    st.write(f"Job structure: {type(job)} - {job}")

                    # Access role and skills safely (check job type)
                    if isinstance(job, dict):
                        role = job.get("role", "Unknown Role")
                        skills = job.get("skills", "")
                    elif hasattr(job, 'content'):  # If it's an AIMessage or similar
                        # Inspect content (based on the structure of AIMessage)
                        role = getattr(job, 'role', "Unknown Role")
                        skills = getattr(job, 'skills', "")

                    # Display job role and skills
                    st.markdown(f"### 🧠 Role: {role}")
                    if skills:
                        st.markdown(f"**Matched Skills:** `{skills}`")
                    else:
                        st.info("No specific skills matched for this role.")

                    # If skills are empty, handle this case:
                    if not skills:
                        links = []  # If no skills, skip portfolio query
                        st.info("No skills found. Skipping portfolio query.")
                    else:
                        # Match relevant portfolio links
                        links = portfolio.query_links([skills])  # Querying with skills as a list
                        if not links:
                            st.info("No relevant portfolio links found, generating email without links.")

                    # Generate cold email
                    email = llm.write_mail(job, links)
                    if email:
                        st.code(email.strip(), language="markdown")
                    else:
                        st.info("No email could be generated for this job role.")

            except Exception as e:
                st.error(f"🚨 An Error Occurred:\n\n{str(e)}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
