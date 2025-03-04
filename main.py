from fastapi import FastAPI, Query
import random
import string

app = FastAPI()

password_history = []  # Store last 15 passwords

def generate_password(length: int, use_digits: bool, use_special: bool):
    characters = string.ascii_letters
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    password = "".join(random.choice(characters) for _ in range(length))
    return password

@app.get("/generate-password/")
def get_password(
    length: int = 12, 
    digits: bool = True, 
    special: bool = True, 
    user_password: str = Query(None)
):
    global password_history

    # ✅ If user enters a manual password
    if user_password:
        if len(user_password) != length:
            return {"error": f"Password must be exactly {length} characters long!"}
        if not any(char.isdigit() for char in user_password) or not any(char in string.punctuation for char in user_password):
            return {"warning": "Weak password! Consider adding numbers and special characters."}

        # Check if password already exists in history
        if user_password in password_history:
            return {"warning": "This password has been used before! Try a new one."}

        password_history.append(user_password)
        password_history = password_history[-15:]  # Keep last 15

        return {"password": user_password}

    # ✅ Generate new password
    new_password = generate_password(length, digits, special)

    # Check if password is repeated
    if new_password in password_history:
        return {"warning": "This password has been used before! Try generating again."}

    password_history.append(new_password)
    password_history = password_history[-15:]  # Keep last 15

    return {"password": new_password}
