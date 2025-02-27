import requests
import random
import json
import string
from time import sleep

def generate_random_email():
    """Generate a random email address"""
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@purdue.edu"

def generate_random_preferences():
    """Generate random preferences for a user"""
    return {
        "cleanliness": random.randint(0, 5),
        "noise": random.randint(0, 5),
        "social": random.randint(0, 5),
        "sleep_schedule": random.randint(0, 5),
        "alcohol": random.randint(0, 5),
        "age": random.randint(0, 5),
        "politics": random.randint(0, 5),
        "doesSmoke": random.choice([True, False]),
        "hasPets": random.choice([True, False]),
        "gender": random.choice(["M", "F"]),
        "smoking_dealbreaker": random.choice([True, False]),
        "pets_dealbreaker": random.choice([True, False]),
        "gender_dealbreaker": random.choice([True, False])
    }

def populate_database():
    base_url = "http://127.0.0.1:3020"
    created_users = []

    for i in range(99):
        # Generate random user data
        email = generate_random_email()
        password = "testpassword123"  # Using same password for all test users
        
        # Create account
        create_response = requests.post(
            f"{base_url}/create_account",
            json={
                "email": email,
                "password": password,
                "school": "Purdue University"
            }
        )
        
        if create_response.status_code != 200:
            print(f"Failed to create user {i+1}: {email}")
            continue
            
        # Login to get session token
        login_response = requests.post(
            f"{base_url}/login",
            json={
                "email": email,
                "password": password
            }
        )
        
        if login_response.status_code != 200:
            print(f"Failed to login user {i+1}: {email}")
            continue
            
        session_token = login_response.json()["session_token"]
        
        # Set preferences
        preferences_response = requests.post(
            f"{base_url}/set_preferences",
            headers={"Authorization": session_token},
            json={
                "email": email,
                "preferences": generate_random_preferences()
            }
        )
        
        if preferences_response.status_code != 200:
            print(f"Failed to set preferences for user {i+1}: {email}")
            continue
            
        print(f"Successfully created user {i+1}: {email}")
        created_users.append(email)
        
        # Small delay to prevent overwhelming the server
        sleep(0.1)

    print(f"\nSuccessfully created {len(created_users)} users")
    
    # Save created emails to a file for potential cleanup later
    with open('created_users.txt', 'w') as f:
        for email in created_users:
            f.write(f"{email}\n")

def cleanup_users():
    """Optional cleanup function to delete test users"""
    base_url = "http://127.0.0.1:3020"
    
    try:
        with open('created_users.txt', 'r') as f:
            emails = f.readlines()
        
        for email in emails:
            email = email.strip()
            response = requests.delete(f"{base_url}/delete_account/{email}")
            if response.status_code == 200:
                print(f"Deleted user: {email}")
            else:
                print(f"Failed to delete user: {email}")
                
    except FileNotFoundError:
        print("No created_users.txt file found")

if __name__ == "__main__":
    print("Starting database population...")
    populate_database()
    
    # cleanup_users()
