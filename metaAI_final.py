import streamlit as st
from openai import AzureOpenAI
import random

# ------------------- OpenAI Setup -------------------
endpoint = "https://<endpoint_name>.openai.azure.com"
deployment = "gpt-4o"
api_key = "api key"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

st.set_page_config(page_title="💼 MetaAI: Explainable AI for Confident Decisions", page_icon="🤖", layout="wide")

# ------------------- Session State Initialization -------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are an AI assistant that helps business users understand the outputs of ML/AI models. "
            "You explain model decisions, clarify features, and answer follow-up questions in clear, non-technical language."
        )},
        {"role": "assistant", "content": (
            "👋 Hello! I am MetaAI. Like Metadata is for explaining data, am MetaAI for explaining ML/AI model output to users. "
            "Ask me about any ML / AI model decision, or click on any predicted output on the left that you want validate and explained."
        )}
    ]
if "active_user" not in st.session_state:
    st.session_state.active_user = "You"
if "peers" not in st.session_state:
    st.session_state.peers = set()

# ------------------- Custom Styles -------------------
st.markdown("""
    <style>
    .msg-bubble {
        max-width: 75%;
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 20px;
        font-size: 16px;
        line-height: 1.6;
        color: black !important;
    }
    .user-msg {
        background-color: #e3f2fd;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    .bot-msg {
        background-color: #c8e6c9;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    .peer-label {
        color: #1976d2;
        font-weight: bold;
        margin-left: 5px;
    }
    .stButton>button {
        background-color: #1976d2 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- LEFT SIDEBAR: Loan/Offer Models -------------------
with st.sidebar:
    st.header("ML Predictions for validations")
    if st.button("Loan decision model"):
        applicant_id = f"APP{random.randint(1000,9999)}"
        demographics = {
            "Age": random.randint(22, 60),
            "Gender": random.choice(["Male", "Female", "Other"]),
            "Income": f"${random.randint(30000, 120000):,}"
        }
        credit_score = random.randint(550, 820)
        past_issues = random.choice([
            "No significant issues",
            "1 late payment in last year",
            "Multiple late payments in last 2 years",
            "Defaulted on a loan 3 years ago"
        ])
        risk_factor = random.choice(["Low", "Medium", "High"])
        decision = "Approved" if credit_score > 670 and risk_factor != "High" and "Defaulted" not in past_issues else "Rejected"
        loan_decision = {
            "Applicant ID": applicant_id,
            "Demographics": demographics,
            "Credit Score": credit_score,
            "Past Payment Issues": past_issues,
            "Risk Factor": risk_factor,
            "Decision": decision
        }
        st.session_state["latest_loan_decision"] = loan_decision

        explanation_prompt = (
            f"Applicant ID: {applicant_id}\n"
            f"Demographics: {demographics}\n"
            f"Credit Score: {credit_score}\n"
            f"Past Payment Issues: {past_issues}\n"
            f"Risk Factor: {risk_factor}\n"
            f"Loan Decision: {decision}\n\n"
            "As an AI assistant, explain in plain language why this loan was approved or rejected. "
            "Highlight the most influential factors and suggest what could improve the outcome if rejected."
        )
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an expert AI assistant that explains ML model decisions to business users in clear, concise language."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        explanation = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "user",
            "content": f"You: Loan decision record:\n"
                       f"Applicant ID: {applicant_id}\n"
                       f"Demographics: {demographics}\n"
                       f"Credit Score: {credit_score}\n"
                       f"Past Payment Issues: {past_issues}\n"
                       f"Risk Factor: {risk_factor}\n"
                       f"Decision: {decision}",
            "author": "You"
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": explanation
        })
        st.rerun()

    if st.session_state.get("latest_loan_decision"):
        ld = st.session_state["latest_loan_decision"]
        st.subheader("Latest Loan Decision")
        st.markdown(f"**Applicant ID:** {ld['Applicant ID']}")
        st.markdown(f"**Demographics:** {ld['Demographics']}")
        st.markdown(f"**Credit Score:** {ld['Credit Score']}")
        st.markdown(f"**Past Payment Issues:** {ld['Past Payment Issues']}")
        st.markdown(f"**Risk Factor:** {ld['Risk Factor']}")
        st.markdown(f"**Decision:** :{'green' if ld['Decision']=='Approved' else 'red'}[{ld['Decision']}]")

    if st.button("Offer Recommendation Model"):
        customer_profile = {
            "Customer ID": f"CUST{random.randint(1000,9999)}",
            "Age": random.randint(25, 60),
            "Gender": random.choice(["Male", "Female", "Other"]),
            "Income": random.randint(40000, 150000),
            "Existing Products": random.sample(
                ["Home Loan", "Personal Loan", "Credit Card", "Savings Account", "Travel Card"], 
                k=random.randint(1, 3)
            ),
            "Spend Patterns": random.choice([
                {"category": "Travel", "annual_spend": random.randint(5000, 20000)},
                {"category": "Shopping", "annual_spend": random.randint(3000, 15000)},
                {"category": "Dining", "annual_spend": random.randint(2000, 10000)},
                {"category": "Groceries", "annual_spend": random.randint(4000, 12000)},
            ])
        }

        offers = [
            {"name": "Travel Credit Card", "criteria": lambda p: p["Spend Patterns"]["category"] == "Travel" and p["Spend Patterns"]["annual_spend"] > 8000},
            {"name": "Dining Cashback Card", "criteria": lambda p: p["Spend Patterns"]["category"] == "Dining" and p["Spend Patterns"]["annual_spend"] > 5000},
            {"name": "Personal Loan Top-up", "criteria": lambda p: "Personal Loan" in p["Existing Products"] and p["Income"] > 60000},
            {"name": "High-Yield Savings Account", "criteria": lambda p: "Savings Account" in p["Existing Products"] and p["Income"] > 80000},
            {"name": "Shopping Rewards Card", "criteria": lambda p: p["Spend Patterns"]["category"] == "Shopping" and p["Spend Patterns"]["annual_spend"] > 7000},
        ]

        recommended = [offer["name"] for offer in offers if offer["criteria"](customer_profile)]
        if not recommended:
            recommended = ["Standard Credit Card Offer"]

        explanation_prompt = (
            f"Customer Profile: {customer_profile}\n"
            f"Recommended Offers: {recommended}\n\n"
            "Explain in plain language why these offers were recommended, referencing the customer's products and spend patterns."
        )
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an expert AI assistant that explains ML model decisions to business users in clear, concise language."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        explanation = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "user",
            "content": f"You: Offer recommendation record:\nCustomer Profile: {customer_profile}\nRecommended Offers: {recommended}",
            "author": "You"
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": explanation
        })
        st.session_state["latest_offer_recommendation"] = {"Profile": customer_profile, "Offers": recommended}
        st.rerun()

    if st.session_state.get("latest_offer_recommendation"):
        orc = st.session_state["latest_offer_recommendation"]
        st.subheader("Latest Offer Recommendation")
        st.markdown(f"**Customer Profile:** {orc['Profile']}")
        st.markdown(f"**Recommended Offers:** {', '.join(orc['Offers'])}")

# ------------------- RIGHT SIDEBAR: Peer/Manager Validation -------------------
main_col, right_col = st.columns([5, 1], gap="large")
with right_col:
    st.markdown("### Validation Panel")
    if "Colleague A" not in st.session_state.peers:
        if st.button("Invite for Peer Validation", key="peer"):
            st.session_state.peers.add("Colleague A")
            st.session_state.active_user = "Colleague A"
            st.session_state.messages.append({
                "role": "user",
                "content": "Colleague A: Hi how are you. what can i do for you?",
                "author": "Colleague A"
            })
            st.rerun()
    if "Manager" not in st.session_state.peers:
        if st.button("Invite for Manager Validation", key="manager"):
            st.session_state.peers.add("Manager")
            st.session_state.active_user = "Manager"
            st.session_state.messages.append({
                "role": "user",
                "content": "Manager: Hi how are you. what can i do for you?",
                "author": "Manager"
            })
            st.rerun()
    # Switch user dropdown if multiple users
    if len(st.session_state.peers) > 0:
        user_list = ["You"] + sorted(list(st.session_state.peers))
        selected_user = st.selectbox("Active User", user_list, index=user_list.index(st.session_state.active_user))
        if selected_user != st.session_state.active_user:
            st.session_state.active_user = selected_user
            st.rerun()

# ------------------- Main Chat Interface -------------------
with main_col:
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0.2em;'>🤖 MetaAI: Explainable AI for Confident Decisions</h1>
        <p style='text-align: center; color: #555; font-size: 1.2em; margin-top: 0;'>
            Chat with me to understand AI decisions and get clear explanations of why ML/AI models made these decisions.
        </p>
    """, unsafe_allow_html=True)

    # Display chat history with correct prefixes
    for msg in st.session_state.get("messages", []):
        if msg["role"] == "system":
            continue
        bubble_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(
            f'<div class="msg-bubble {bubble_class}">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

    # Chat input at the bottom with Send and Clear buttons
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            f"{st.session_state.active_user}, ask a question about the loan decision or model output...",
            label_visibility="collapsed"
        )
        col1, col2 = st.columns([4, 1])
        send_clicked = col1.form_submit_button("Send")
        clear_clicked = col2.form_submit_button("Clear Chat")

        if send_clicked and user_input:
            author = st.session_state.active_user
            if author == "You":
                prefix = "You: "
            elif author == "Colleague A":
                prefix = "Colleague A: "
            elif author == "Manager":
                prefix = "Manager: "
            else:
                prefix = ""
            msg_content = f"{prefix}{user_input}"
            st.session_state.messages.append({
                "role": "user",
                "content": msg_content,
                "author": author
            })

            # Only call MetaAI if message contains "MetaAI" (case-insensitive)
            if "metaai" in user_input.lower():
                try:
                    response = client.chat.completions.create(
                        model=deployment,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        temperature=0.7,
                        max_tokens=250
                    )
                    reply = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.rerun()

        if clear_clicked:
            if "messages" in st.session_state:
                del st.session_state["messages"]
            st.rerun()
