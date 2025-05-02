import requests
import random
import json
import string
from time import sleep
import base64

# Lists for generating names
FIRST_NAMES = ["Alex", "Jamie", "Taylor", "Jordan", "Morgan", "Casey", "Riley", "Avery", "Peyton", "Skyler"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Martinez", "Wilson"]
HOBBIES = ["Reading", "Gaming", "Hiking", "Cooking", "Traveling", "Music", "Sports", "Photography", "Dancing", "Coding"]

#upload user image
def upload_profile_image(session_token, image_path="default.jpg"):
    with open(image_path, "rb") as img_file:
        files = {"file": img_file}
        response = requests.post(
            "http://127.0.0.1:3020/upload",
            headers={"Authorization": session_token},
            files=files
        )
    if response.status_code != 200:
        print(f"Upload failed with status {response.status_code}: {response.text}")
    return response.status_code == 200

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@purdue.edu"

def generate_random_preferences():
    return {
        "cleanliness": random.randint(0, 5),
        "noise": random.randint(0, 5),
        "social": random.randint(0, 5),
        "sleep_schedule": random.randint(0, 5),
        "alcohol": random.randint(0, 5),
        "age": random.randint(0, 5),
        "politics": random.randint(0, 5),
        "doesSmoke": random.choice([0, 1]),
        "hasPets": random.choice([0, 1]),
        "gender": random.choice(["M", "F"]),
        "smoking_dealbreaker": random.choice([0, 1]),
        "pets_dealbreaker": random.choice([0, 1]),
        "gender_dealbreaker": random.choice([0, 1])
    }

def generate_random_user_info():
    return {
        "first_name": random.choice(FIRST_NAMES),
        "last_name": random.choice(LAST_NAMES),
        "age": random.randint(18, 30),
        "bio": "I'm a student at Purdue, interested in meeting new people!",
        "hobbies": str(random.sample(HOBBIES, k=random.randint(2, 4)))
    }

def generate_random_user_info_with_image():

    image_filename = f"image{random.randint(1, 4)}.jpg"  # ✅ random image
    with open(image_filename, "rb") as image_file:
        base64_img = base64.b64encode(image_file.read()).decode("utf-8")
        profile_image = f"data:image/jpeg;base64,{base64_img}"

    return {
        "userInfo": {
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "age": str(random.randint(18, 30)),  # as string to match frontend
            "bio": "I'm a student at Purdue, interested in meeting new people!",
            "hobbies": random.sample(HOBBIES, k=random.randint(2, 4))
        },
        "profile_image": profile_image
    }


def populate_database():
    base_url = "http://127.0.0.1:3020"
    created_users = []

    for i in range(60):
        email = generate_random_email()
        password = "testpassword123"
        
        create_response = requests.post(
            f"{base_url}/create_account",
            json={"email": email, "password": password, "school": "Purdue University-Main Campus"}
        )
        if create_response.status_code != 200:
            print(f"Failed to create user {i+1}: {email}")
            continue

        login_response = requests.post(
            f"{base_url}/login",
            json={"email": email, "password": password}
        )
        if login_response.status_code != 200:
            print(f"Failed to login user {i+1}: {email}")
            continue

        session_token = login_response.json().get("session_token")
        if not session_token:
            print(f"Failed to retrieve session token for {email}")
            continue

        preferences_response = requests.post(
            f"{base_url}/set_preferences",
            headers={"Authorization": session_token},
            json={"email": email, "preferences": generate_random_preferences()}
        )
        if preferences_response.status_code != 200:
            print(f"Failed to set preferences for user {i+1}: {email}")
            continue

        user_info_response = requests.post(
            f"{base_url}/set_user_info",
            headers={"Authorization": session_token},
            json={"email": email, "user_info": generate_random_user_info_with_image()}
        )
        if user_info_response.status_code != 200:
            print(f"Failed to set user info for user {i+1}: {email}")
            continue

        # ✅ Upload profile image
        # if not upload_profile_image(session_token, "default.jpg"):
        #     print(f"Failed to upload profile image for user {i+1}: {email}")
        #     continue

        print(f"Successfully created user {i+1}: {email}")
        created_users.append(email)
        sleep(0.1)

    print(f"\nSuccessfully created {len(created_users)} users")
    with open('created_users.txt', 'w') as f:
        for email in created_users:
            f.write(f"{email}\n")

if __name__ == "__main__":
    print("Starting database population...")
    populate_database()
