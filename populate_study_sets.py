# Import necessary functions from flashcards.py
from flashcards import initialize_flashcards_table, add_study_set, add_flashcard, get_study_sets

# Initialize the database tables (in case they are not already created)
initialize_flashcards_table()

# Function to generate study sets and flashcards for each user
def generate_sample_data(user_id):
    return [
        {
            "user_id": user_id,
            "set_name": f"Math Basics for User {user_id}",
            "flashcards": [
                {"question": "What is 2 + 2?", "answer": "4"},
                {"question": "What is the square root of 9?", "answer": "3"},
                {"question": "What is 10 / 2?", "answer": "5"},
            ]
        },
        {
            "user_id": user_id,
            "set_name": f"Science Fundamentals for User {user_id}",
            "flashcards": [
                {"question": "What planet is known as the Red Planet?", "answer": "Mars"},
                {"question": "What gas do plants absorb?", "answer": "Carbon Dioxide"},
                {"question": "What is H2O commonly known as?", "answer": "Water"},
            ]
        },
        {
            "user_id": user_id,
            "set_name": f"History Basics for User {user_id}",
            "flashcards": [
                {"question": "Who was the first President of the United States?", "answer": "George Washington"},
                {"question": "In which year did World War II end?", "answer": "1945"},
                {"question": "Who wrote the Declaration of Independence?", "answer": "Thomas Jefferson"},
            ]
        }
    ]

# Insert data for 20 users
for user_id in range(1, 21):  # User IDs from 1 to 20
    sample_data = generate_sample_data(user_id)
    for study_set in sample_data:
        set_id = add_study_set(study_set["user_id"], study_set["set_name"])
        if set_id:
            print(f"Created study set '{study_set['set_name']}' for User {user_id} with ID {set_id}")
            for flashcard in study_set["flashcards"]:
                add_flashcard(set_id, flashcard["question"], flashcard["answer"])
                print(f"Added flashcard to User {user_id}'s set: Q='{flashcard['question']}' A='{flashcard['answer']}'")
        else:
            print(f"Study set '{study_set['set_name']}' for User {user_id} already exists.")

# Check to confirm insertion for one example user (e.g., User 1)
user_id = 1
print(f"\nStudy sets for user {user_id}:")
print(get_study_sets(user_id))
