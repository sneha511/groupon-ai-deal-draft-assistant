import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# App setup
# -----------------------------
st.set_page_config(
    page_title="AI Groupon Deal Draft Assistant",
    page_icon="✨",
    layout="wide"
)

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Sample merchants
# -----------------------------
SAMPLE_MERCHANTS = {
    "Sofia Wax & Lash Studio": {
        "business_name": "Sofia Wax & Lash Studio",
        "city": "Chicago",
        "business_type": "Waxing",
        "services": "Brazilian Wax - $70\nLash Lift - $95\nBrow Wax - $25",
        "slow_days": ["Tuesday", "Wednesday"],
        "goal": "Fill empty Tuesday and Wednesday appointments with new customers",
        "max_discount": 40,
    },
    "Glow Nail Bar": {
        "business_name": "Glow Nail Bar",
        "city": "Chicago",
        "business_type": "Nails",
        "services": "Gel Manicure - $45\nPedicure - $55\nGel Mani + Pedi - $90",
        "slow_days": ["Tuesday", "Wednesday"],
        "goal": "Bring in new weekday customers",
        "max_discount": 35,
    },
    "Fresh Face Studio": {
        "business_name": "Fresh Face Studio",
        "city": "Chicago",
        "business_type": "Facials",
        "services": "Express Facial - $60\nSignature Facial - $110\nAcne Facial - $125",
        "slow_days": ["Wednesday", "Thursday"],
        "goal": "Fill unused appointments while protecting margin",
        "max_discount": 30,
    },
}

business_type_options = ["Waxing", "Lashes", "Waxing + Lashes", "Nails", "Facials"]

# -----------------------------
# Header
# -----------------------------
st.title("AI Groupon Deal Draft Assistant")

st.write(
    "Generate AI-powered Groupon deal strategies for small local merchants."
)

st.caption(
    "Prototype demonstrating how AI can reduce friction in Groupon’s merchant deal creation workflow."
)

# -----------------------------
# Sample selector
# -----------------------------
selected_sample = st.selectbox(
    "Choose a sample merchant",
    list(SAMPLE_MERCHANTS.keys())
)

sample_data = SAMPLE_MERCHANTS[selected_sample]

# -----------------------------
# Input form
# -----------------------------
st.subheader("Merchant Information")
st.write("Provide a few details about the business to generate deal strategies.")
with st.form("deal_form"):
    business_name = st.text_input(
        "Business name",
        value=sample_data["business_name"]
    )

    city = st.text_input(
        "City",
        value=sample_data["city"]
    )

    business_type = st.selectbox(
        "Business type",
        business_type_options,
        index=business_type_options.index(sample_data["business_type"])
    )

    services = st.text_area(
        "Services and normal prices",
        value=sample_data["services"]
    )

    slow_days = st.multiselect(
        "Slow days",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        default=sample_data["slow_days"]
    )

    goal = st.text_input(
        "Goal",
        value=sample_data["goal"]
    )

    max_discount = st.slider(
        "Maximum discount comfort (%)",
        min_value=10,
        max_value=70,
        value=sample_data["max_discount"]
    )

    submit = st.form_submit_button("Generate Deal Draft")

# -----------------------------
# AI generation
# -----------------------------
if submit:
    prompt = f"""
You are an expert in local marketplace promotions helping a small beauty business create Groupon-style deal options.

Merchant info:
Business name: {business_name}
City: {city}
Business type: {business_type}
Services: {services}
Slow days: {slow_days}
Goal: {goal}
Maximum discount allowed: {max_discount}%

Generate 3 practical deal options for this merchant:

1. One optimized for volume
2. One optimized for margin
3. One optimized for repeat customers

Also choose the single best option overall for this merchant.

Return ONLY valid JSON in exactly this format:

{{
  "best_option_label": "",
  "best_option_reason": "",
  "deal_options": [
    {{
      "label": "",
      "recommended_service": "",
      "regular_price": "",
      "deal_price": "",
      "discount_percent": "",
      "title": "",
      "description": "",
      "fine_print": "",
      "category": "",
      "voucher_limit": "",
      "redemption_schedule": "",
      "expected_outcome": "",
      "rationale": "",
      "risk_flags": []
    }},
    {{
      "label": "",
      "recommended_service": "",
      "regular_price": "",
      "deal_price": "",
      "discount_percent": "",
      "title": "",
      "description": "",
      "fine_print": "",
      "category": "",
      "voucher_limit": "",
      "redemption_schedule": "",
      "expected_outcome": "",
      "rationale": "",
      "risk_flags": []
    }},
    {{
      "label": "",
      "recommended_service": "",
      "regular_price": "",
      "deal_price": "",
      "discount_percent": "",
      "title": "",
      "description": "",
      "fine_print": "",
      "category": "",
      "voucher_limit": "",
      "redemption_schedule": "",
      "expected_outcome": "",
      "rationale": "",
      "risk_flags": []
    }}
  ]
}}

Rules:
- Return exactly 3 options in the deal_options array.
- Keep all discounts at or below the allowed maximum.
- Make all options realistic for a small 2-chair beauty studio.
- "voucher_limit" must describe actual inventory/capacity control.
- "risk_flags" must contain at least 3 short, practical risks per option.
- Each option should feel meaningfully different from the others.
- Choose the best overall option based on the merchant's stated goal.
- Fine print must be grammatically correct and customer-facing.
- Use "voucher may be forfeited" for late cancellation/no-show language, not "voucher may be redeemed".
- Prices must always include the $ symbol and be formatted clearly.
- Keep titles concise.
- Keep descriptions brief and readable.
- Output ONLY JSON and nothing else.
"""

    with st.spinner("Generating deal..."):
        try:
            response = client.responses.create(
                model="gpt-5.4",
                input=prompt
            )

            result_text = response.output_text

            try:
                result = json.loads(result_text)

                best_option_label = result.get("best_option_label", "No recommendation")
                best_option_reason = result.get("best_option_reason", "No explanation provided.")
                options = result.get("deal_options", [])
                st.divider()
                st.subheader("AI Best Recommendation")
                st.success(f"⭐ **Recommended: {best_option_label}** — {best_option_reason}")
                st.markdown("---")
                st.subheader("Generated Deal Options")

                if not options:
                    st.warning("No deal options were returned.")
                else:
                    cols = st.columns(3)

                    for i, option in enumerate(options[:3]):
                        with cols[i]:
                            with st.container(border=True):
                                st.markdown(f"### {option.get('label', f'Option {i+1}')}")

                                st.write("**Service:**", option.get("recommended_service", ""))
                                st.write("**Regular Price:**", option.get("regular_price", ""))
                                st.markdown(f"### 💰 Deal Price: {option.get('deal_price', '')}")
                                st.write("**Discount:**", option.get("discount_percent", ""))

                                st.write("**Title:**", option.get("title", ""))
                                st.write("**Description:**", option.get("description", ""))
                                st.write("**Category:**", option.get("category", ""))
                                st.write("**Voucher Limit:**", option.get("voucher_limit", ""))
                                st.write("**Redemption Schedule:**", option.get("redemption_schedule", ""))
                                st.write("**Expected Outcome:**", option.get("expected_outcome", ""))

                                with st.expander("See details"):
                                    st.write("**Fine Print:**", option.get("fine_print", ""))
                                    st.write("**Rationale:**", option.get("rationale", ""))

                                    st.write("**Risk Flags:**")
                                    risk_flags = option.get("risk_flags", [])
                                    if risk_flags:
                                        for risk in risk_flags:
                                            st.write("-", risk)
                                    else:
                                        st.write("No major risks identified.")

            except json.JSONDecodeError:
                st.error("AI response was not valid JSON.")
                st.write(result_text)

        except Exception as e:
            st.error(f"OpenAI API error: {e}")