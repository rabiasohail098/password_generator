import streamlit as st
import requests
import json
import os
import re
import time  

API_URL = "https://fastapi-backend-production-6a7c.up.railway.app/generate-password/"
HISTORY_FILE = "password_history.json"  
COMMON_PASSWORDS = ["password", "123456", "password123", "qwerty", "abc123"]  

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

st.title("🔐 Secure Password Generator & Strength Checker")

# 🎛 Password Options
length = st.slider("🔢 Password Length:", min_value=4, max_value=32, value=12)
use_digits = st.checkbox("🔢 Include Numbers", value=True)
use_special = st.checkbox("🔣 Include Special Characters", value=True)

# 📌 Manual Password Input
manual_password = st.text_input("✏️ Enter Your Password (Optional)", type="password")

# 🛠️ Password Strength Checker Function
def check_password_strength(password, required_length):
    score = 0
    feedback = []

    if len(password) != required_length:
        feedback.append(f"⚠️ Password must be exactly {required_length} characters long.")

    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("❌ Include both uppercase and lowercase letters.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("❌ Add at least one number (0-9).")

    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        feedback.append("❌ Include at least one special character (!@#$%^&*).")

    if password in COMMON_PASSWORDS:
        feedback.append("❌ This password is too common. Choose a stronger one.")

    if score == 4:
        return "✅ Strong Password!", feedback
    elif score == 3:
        return "⚠️ Moderate Password - Consider adding more security features.", feedback
    else:
        return "❌ Weak Password - Improve it using the suggestions above.", feedback

# 🎯 Show Password Strength Checker
if manual_password:
    strength, feedback = check_password_strength(manual_password, length)
    st.markdown(f"### {strength}")
    for tip in feedback:
        st.markdown(f"- {tip}")

# 🎯 Generate Password Button
if st.button("Generate Password 🔄"):
    params = {"length": length, "digits": use_digits, "special": use_special}

    # ✅ If user entered a manual password, use that first
    if manual_password:
        params["user_password"] = manual_password

    response = requests.get(API_URL, params=params)

    try:
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                st.error(data["error"])  
            elif "warning" in data:
                st.warning(data["warning"])  
            elif "password" in data:
                st.success(data.get("message", "✅ Password Generated!"))
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
                    st.balloons()  
                    time.sleep(0.5)
                    st.snow()  
        else:
            st.error(f"❌ Failed to connect to API. Status Code: {response.status_code}")
    except requests.exceptions.JSONDecodeError:
        st.error("❌ Failed to parse JSON response from backend!")
        st.write("Raw Response:", response.text)
