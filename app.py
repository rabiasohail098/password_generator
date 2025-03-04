import streamlit as st
import requests
import time
import json
import os
import re

API_URL = "https://your-fastapi-deployment-url.com/generate-password/"
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

# 🎉 Sidebar for Password History
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

# 🎯 Show Password Strength Suggestions with Bullet Points
st.markdown("### 🔍 Password Strength Suggestions")
for tip, met in suggestions.items():
    color = "green" if met else "red"
    st.markdown(f"<p style='color:{color}; font-weight: bold;'>• {tip}</p>", unsafe_allow_html=True)

# 🎯 Generate Password Button
if st.button("Generate Password 🔄"):
    params = {"length": length, "digits": use_digits, "special": use_special}

    if manual_password:
        params["user_password"] = manual_password

    response = requests.get(API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # 🛑 Error Handling
        if "error" in data:
            st.error(data["error"])
            st.toast("🚨 Invalid Password Length!", icon="⚠️")
        elif "warning" in data:
            st.warning(data["warning"])
            st.toast("⚠️ Consider changing your password!", icon="❗")
        else:
            password = data["password"]

            # ✅ Check for Repeated Password
            if password in password_history:
                st.warning("⚠️ Warning: You have already used this password!")
                st.toast("⚠️ This password is repeated!", icon="🚨")
            else:
                st.success("✅ Secure Password Generated!")
                st.code(password, language="text")

                # ✅ Save Password in History (Keep last 15)
                password_history.append(password)
                password_history = password_history[-15:]
                save_password_history(password_history)  # Save to file

                # 📋 Copy Button with Animation
                if st.button("📋 Copy Password"):
                    st.toast("✅ Password Copied to Clipboard!", icon="📌")
                    time.sleep(0.5)

                # 🎉 Fun Animation on Password Generation
                st.balloons()  # Fireworks 🎇
                time.sleep(0.5)
                st.snow()  # Snowfall effect ❄️
    else:
        st.error("❌ Failed to generate password!")
