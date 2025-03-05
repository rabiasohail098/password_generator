import streamlit as st
import requests
import json
import os
import re
import time  # Required for animations

API_URL = "https://fastapi-backend-production-6a7c.up.railway.app/generate-password/"
HISTORY_FILE = "password_history.json"  # JSON file to store history

st.set_page_config(page_title="Secure Password Generator", layout="wide")

# ✅ Load Password History
def load_password_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

def save_password_history(history):
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file)

password_history = load_password_history()

# 📜 Sidebar for Password History
st.sidebar.title("📜 Password History")
for past_password in reversed(password_history):
    st.sidebar.text(past_password)

st.title("🔐 Secure Password Generator")

# 🎛 Password Options
length = st.slider("🔢 Password Length:", min_value=4, max_value=32, value=12)
use_digits = st.checkbox("🔢 Include Numbers", value=True)
use_special = st.checkbox("🔣 Include Special Characters", value=True)

# 📌 Manual Password Input
manual_password = st.text_input("✏️ Enter Your Password (Optional)")

# 🛠️ Password Strength Suggestions
suggestions = {
    "At least 8 characters": len(manual_password) >= 8 if manual_password else False,
    "Contains uppercase (A-Z)": any(c.isupper() for c in manual_password) if manual_password else False,
    "Contains lowercase (a-z)": any(c.islower() for c in manual_password) if manual_password else False,
    "Contains a number (0-9)": any(c.isdigit() for c in manual_password) if manual_password else False,
    "Contains a special character (!@#$%)": bool(re.search(r"[!@#$%^&*()_+]", manual_password)) if manual_password else False,
}

# 🎯 Show Password Strength Suggestions
st.markdown("### 🔍 Password Strength Suggestions")
for tip, met in suggestions.items():
    color = "green" if met else "red"
    st.markdown(f"<p style='color:{color}; font-weight: bold;'>• {tip}</p>", unsafe_allow_html=True)

# 🎯 Generate Password Button
if st.button("Generate Password 🔄"):
    params = {
        "length": length,
        "digits": use_digits,
        "special": use_special
    }

    # ✅ If user entered a manual password, add it to request
    if manual_password:
        params["user_password"] = manual_password

    response = requests.get(API_URL, params=params)

    try:
        data = response.json()
        if "error" in data:
            st.error(data["error"])  # ❌ Show error if backend returns it
        elif "warning" in data:
            st.warning(data["warning"])  # ⚠️ Show warning if backend sends it
        elif "password" in data:
            st.success(data.get("message", "✅ Secure Password Generated!"))
            st.code(data["password"], language="text")

            # ✅ Check for Repeated Password
            if data["password"] in password_history:
                st.warning("⚠️ Warning: You have already used this password!")
            else:
                # ✅ Save Password in History (Keep last 15)
                password_history.append(data["password"])
                password_history = password_history[-15:]
                save_password_history(password_history)

                # 📋 Copy Button
                if st.button("📋 Copy Password"):
                    st.success("✅ Password Copied to Clipboard!")

                # 🎉 Keep Animations!
                st.balloons()  # Fireworks 🎇
                time.sleep(0.5)
                st.snow()  # Snowfall effect ❄️
    except requests.exceptions.JSONDecodeError:
        st.error("❌ Failed to parse JSON response from backend!")
        st.write("Raw Response:", response.text)
