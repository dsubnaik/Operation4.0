import sqlite3

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Function to identify duplicates in the user_achievements table
def find_duplicates():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query to find duplicates by counting the number of each user_id and achievement_id combination
    cursor.execute('''
        SELECT user_id, achievement_id, COUNT(*) as duplicate_count
        FROM user_achievements
        GROUP BY user_id, achievement_id
        HAVING duplicate_count > 1;
    ''')
    
    duplicates = cursor.fetchall()
    conn.close()
    
    # Display duplicate entries
    if duplicates:
        print("Found duplicate entries:")
        for row in duplicates:
            print(f"User ID: {row[0]}, Achievement ID: {row[1]}, Duplicates: {row[2]}")
    else:
        print("No duplicates found.")
    
    return duplicates

# Function to clean up duplicates, keeping only the earliest unlock date for each duplicate
def clean_up_duplicates():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete duplicates, keeping the first (earliest) instance of each duplicate
    cursor.execute('''
        DELETE FROM user_achievements
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM user_achievements
            GROUP BY user_id, achievement_id
        );
    ''')
    
    conn.commit()
    conn.close()
    print("Duplicate entries removed.")

# Main function to run the duplicate check and clean-up
def main():
    print("Checking for duplicates in user_achievements table...")
    duplicates = find_duplicates()
    
    if duplicates:
        print("\nCleaning up duplicates...")
        clean_up_duplicates()
        print("\nRe-checking for duplicates after cleanup...")
        find_duplicates()  # Re-check to confirm duplicates are removed
    else:
        print("No duplicates to clean up.")

if __name__ == "__main__":
    main()
