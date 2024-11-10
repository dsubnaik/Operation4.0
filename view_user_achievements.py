from achievements import get_connection  # or the appropriate module where get_connection is defined

# Function to fetch unique achievements unlocked by each user
def fetch_user_achievements():
    conn = get_connection()
    cursor = conn.cursor()

    # Modified query to retrieve only unique achievements based on the earliest unlock date
    cursor.execute("""
    SELECT users.username, achievements.name, achievements.description, achievements.badge, MIN(user_achievements.unlock_date) AS unlock_date
    FROM user_achievements
    JOIN users ON user_achievements.user_id = users.id
    JOIN achievements ON user_achievements.achievement_id = achievements.id
    GROUP BY users.username, achievements.name
    ORDER BY users.username, unlock_date;
    """)

    # Fetch all results
    results = cursor.fetchall()
    conn.close()

    # Display achievements for each user
    current_user = None
    for row in results:
        username, achievement_name, description, badge, unlock_date = row
        if current_user != username:
            if current_user is not None:
                print("\n" + "-" * 40 + "\n")
            current_user = username
            print(f"User: {username}")
            print("-" * 40)
        print(f"Achievement: {achievement_name}")
        print(f"Description: {description}")
        print(f"Badge: {badge}")
        print(f"Unlocked on: {unlock_date}")
        print()

# Run the function to display unique achievements
fetch_user_achievements()