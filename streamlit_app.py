import streamlit as st
import re
import pandas as pd
from collections import defaultdict

# Page configuration for a professional data tool appearance
st.set_page_config(
    page_title="AVANA Marketing",
    page_icon="📧",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #4f46e5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Application Header
st.title("📧 AVANA Marketing")
st.markdown("Automated AI-based selection tool for domain-specific email filtering and marketing extraction.")

# Sidebar/Filters Column
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("Data Input")
    raw_text = st.text_area(
        "Paste Email List",
        height=250,
        placeholder="Paste your raw list of emails here (e.g. from CSV or text)...",
        help="Supports any text format containing email addresses."
    )
    
    st.header("Role Filters")
    # Default high-value role keywords
    default_roles = "ceo, founder, cto, cfo, president, director, lead, manager, vp"
    role_input = st.text_input(
        "Filter Keywords (comma separated)", 
        value=default_roles,
        help="Emails matching these prefixes will be prioritized in the top 5 selection."
    )
    keywords = [k.strip().lower() for k in role_input.split(",") if k.strip()]

with col2:
    st.header("Extraction Results")
    
    # Process Button
    if st.button("Run Extraction", type="primary"):
        if not raw_text:
            st.warning("Please enter some email data to process.")
        else:
            # 1. Extraction via Regex
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            found_emails = re.findall(email_pattern, raw_text)
            unique_emails = list(set(e.lower() for e in found_emails))
            
            # 2. Grouping by Domain
            domain_map = defaultdict(list)
            for email in unique_emails:
                try:
                    domain = email.split('@')[1]
                    domain_map[domain].append(email)
                except IndexError:
                    continue
            
            # 3. Selection Logic (Top 5 per domain)
            final_selection = []
            for domain, emails in domain_map.items():
                # Separate by match status
                priority = []
                others = []
                for e in emails:
                    local_part = e.split('@')[0]
                    if any(k in local_part for k in keywords):
                        priority.append(e)
                    else:
                        others.append(e)
                
                # Sort matched by length (shortest is often most direct role)
                priority.sort(key=len)
                others.sort()
                
                # Select top 5 combined
                top_5 = (priority + others)[:5]
                
                for s in top_5:
                    final_selection.append({
                        "Domain": domain,
                        "Email": s,
                        "Status": "Match" if s in priority else "General"
                    })
            
            # 4. Display Results
            if final_selection:
                df = pd.DataFrame(final_selection)
                
                # Summary Statistics
                s1, s2, s3 = st.columns(3)
                s1.metric("Emails Found", len(unique_emails))
                s2.metric("Unique Domains", len(domain_map))
                s3.metric("Selected List", len(final_selection))
                
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.BadgeColumn(
                            "Status",
                            map_format={
                                "Match": "blue",
                                "General": "gray"
                            }
                        )
                    }
                )
                
                # CSV Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Selected Emails (CSV)",
                    data=csv,
                    file_name='selected_emails.csv',
                    mime='text/csv',
                )
            else:
                st.error("No valid emails found in the input text.")
    else:
        # Placeholder state
        st.info("Enter data and click 'Run Extraction' to see the grouped results.")

# Footer
st.divider()
st.caption("Built with Streamlit & AI logic for high-performance marketing filtering.")
