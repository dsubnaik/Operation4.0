//Program Name: flashcards.js
//Developer: Hunter Nichols, Derrick Subnaik
//Date Created: 11/17/2024
//Version: 1.0
//Purpose: Allows for easy interactions between the flashcards page

// DOM Elements
const container = document.querySelector(".container");
const addQuestionCard = document.getElementById("add-question-card");
const saveButton = document.getElementById("save-btn");
const questionInput = document.getElementById("question");
const answerInput = document.getElementById("answer");
const errorMessage = document.getElementById("error");
const addFlashcardButton = document.getElementById("add-flashcard");
const closeButton = document.getElementById("close-btn");
const createStudySetButton = document.getElementById("create-study-set");
const studySetButtonsContainer = document.getElementById("study-set-buttons-container");
const cardListContainer = document.querySelector(".card-list-container");

let currentStudySet = null; // Track the active study set
const displayedAchievements = new Set(); // Keep track of displayed achievements
let pageStartTime = null; // Track the time when the user enters the page

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    pageStartTime = Date.now(); // Start the timer when the page loads
    loadStudySets();
});

// Fetch and generate study set buttons
async function loadStudySets() {
    try {
        const response = await fetch('/api/get_study_sets');
        if (response.ok) {
            const studySets = await response.json();
            studySetButtonsContainer.innerHTML = ""; // Clear existing buttons

            if (studySets.length === 0) {
                // Display a message if no study sets are found
                studySetButtonsContainer.innerHTML = "<p>No study sets available. Create a new one to get started!</p>";
                currentStudySet = null;
                return;
            }

            studySets.forEach(set => {
                const buttonContainer = document.createElement("div");
                buttonContainer.classList.add("study-set-container");

                const button = document.createElement("button");
                button.textContent = set.name;
                button.classList.add("load-set-btn");
                if (set.id === currentStudySet) {
                    button.classList.add("active-set");
                }
                button.addEventListener("click", () => handleStudySetClick(button, set.id));
                buttonContainer.appendChild(button);

                const deleteButton = document.createElement("button");
                deleteButton.classList.add("delete-set-btn");
                deleteButton.textContent = "Delete";
                deleteButton.addEventListener("click", () => deleteStudySet(set.id));
                buttonContainer.appendChild(deleteButton);

                studySetButtonsContainer.appendChild(buttonContainer);
            });
        } else {
            console.error("Failed to fetch study sets.");
        }
    } catch (error) {
        console.error("Error fetching study sets:", error);
    }
}


// Handle study set button click
function handleStudySetClick(button, studySetId) {
    // Remove active class from all study set buttons
    document.querySelectorAll(".load-set-btn").forEach(btn => btn.classList.remove("active-set"));
    
    // Set clicked button as active
    button.classList.add("active-set");
    currentStudySet = studySetId;

    // Load flashcards for the selected study set
    loadFlashcards(studySetId);
}

// Fetch and display flashcards for the selected study set
async function loadFlashcards(studySetId) {
    try {
        const response = await fetch(`/api/get_flashcards?study_set_id=${studySetId}`);
        if (response.ok) {
            const flashcards = await response.json();
            cardListContainer.innerHTML = ""; // Clear existing flashcards
            flashcards.forEach(card => addFlashcard(card.question, card.answer, card.id));
        } else {
            console.error("Failed to fetch flashcards.");
        }
    } catch (error) {
        console.error("Error loading flashcards:", error);
    }
}

// Add Flashcard to the DOM
function addFlashcard(questionText, answerText, flashcardId) {
    const flashcard = document.createElement("div");
    flashcard.classList.add("card");
    flashcard.setAttribute("data-id", flashcardId);

    // Question text
    const questionDiv = document.createElement("p");
    questionDiv.classList.add("question-div");
    questionDiv.textContent = questionText;

    // Answer text (initially hidden)
    const answerDiv = document.createElement("p");
    answerDiv.classList.add("answer-div", "hide");
    answerDiv.textContent = answerText;

    // Show/Hide button
    const toggleAnswerButton = document.createElement("button");
    toggleAnswerButton.classList.add("show-hide-btn");
    toggleAnswerButton.textContent = "Show/Hide";
    toggleAnswerButton.addEventListener("click", () => answerDiv.classList.toggle("hide"));

    // Edit button
    const editButton = document.createElement("button");
    editButton.classList.add("edit");
    editButton.innerHTML = `<i class="fa-solid fa-pen-to-square"></i>`;
    editButton.addEventListener("click", () => {
        questionInput.value = questionText;
        answerInput.value = answerText;
        saveButton.textContent = "Update";
        addQuestionCard.classList.remove("hide");
    });

    // Delete button
    const deleteButton = document.createElement("button");
    deleteButton.classList.add("delete");
    deleteButton.innerHTML = `<i class="fa-solid fa-trash-can"></i>`;
    deleteButton.addEventListener("click", () => {
        deleteFlashcard(flashcardId); // Pass the flashcardId
        flashcard.remove();
    });

    // Button container
    const buttonsCon = document.createElement("div");
    buttonsCon.classList.add("buttons-con");
    buttonsCon.append(editButton, deleteButton);

    // Append elements to the flashcard div
    flashcard.append(questionDiv, toggleAnswerButton, answerDiv, buttonsCon);
    cardListContainer.appendChild(flashcard);
}

// Add or update flashcard in the database
saveButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();
    const answer = answerInput.value.trim();

    if (question === "" || answer === "") {
        errorMessage.classList.remove("hide");
        return;
    }
    errorMessage.classList.add("hide");

    try {
        const response = await fetch('/api/add_flashcard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ study_set_id: currentStudySet, question, answer })
        });

        if (response.ok) {
            loadFlashcards(currentStudySet);

            // Fetch achievements to check for any new unlocks
            fetchAndShowAchievements();
        } else {
            console.error("Failed to save flashcard.");
        }
    } catch (error) {
        console.error("Error saving flashcard:", error);
    }

    questionInput.value = "";
    answerInput.value = "";
    addQuestionCard.classList.add("hide");
});

// Open flashcard input form
addFlashcardButton.addEventListener("click", () => {
    questionInput.value = "";
    answerInput.value = "";
    saveButton.textContent = "Save";
    addQuestionCard.classList.remove("hide");
});

// Close flashcard input form
closeButton.addEventListener("click", () => {
    addQuestionCard.classList.add("hide");
});

// Delete flashcard from the database
async function deleteFlashcard(flashcardId) {
    try {
        const response = await fetch('/api/delete_flashcard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ flashcard_id: flashcardId })
        });

        if (response.ok) {
            const flashcardElement = document.querySelector(`.card[data-id="${flashcardId}"]`);
            if (flashcardElement) {
                flashcardElement.remove();
            }
        } else {
            console.error("Failed to delete flashcard.");
        }
    } catch (error) {
        console.error("Error deleting flashcard:", error);
    }
}

// Create new study set
createStudySetButton.addEventListener("click", async () => {
    const newSetName = prompt("Enter a name for the new study set:");
    if (!newSetName) return;

    try {
        const response = await fetch('/api/add_study_set', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ set_name: newSetName })
        });

        if (response.ok) {
            const newStudySet = await response.json();
            currentStudySet = newStudySet.id;
            loadStudySets();
            loadFlashcards(currentStudySet);

            // Fetch achievements to check for any new unlocks
            fetchAndShowAchievements();
        } else {
            alert("A study set with that name already exists.");
        }
    } catch (error) {
        console.error("Error creating new study set:", error);
    }
});

// Delete a study set from the database
async function deleteStudySet(studySetId) {
    if (confirm("Are you sure you want to delete this study set? This action cannot be undone.")) {
        try {
            const response = await fetch('/api/delete_study_set', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ study_set_id: studySetId })
            });

            if (response.ok) {
                loadStudySets();
                cardListContainer.innerHTML = "";
                currentStudySet = null;
            } else {
                console.error("Failed to delete study set.");
            }
        } catch (error) {
            console.error("Error deleting study set:", error);
        }
    }
}

// Show toast notifications
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.display = "block"; // Make the notification visible
    
    // Hide the toast automatically after the animation ends
    setTimeout(() => {
        toast.style.display = "none";
    }, 5000); // Matches fadeOut animation timing (4.5s delay + fade duration)
}


// Fetch and show achievements
async function fetchAndShowAchievements() {
    try {
        const response = await fetch('/api/get_user_achievements');
        if (response.ok) {
            const achievements = await response.json();
            let newAchievementsUnlocked = false;

            achievements.forEach(achievement => {
                if (!displayedAchievements.has(achievement.name)) {
                    showToast(`🎉 Achievement Unlocked: ${achievement.name}`);
                    displayedAchievements.add(achievement.name);
                    newAchievementsUnlocked = true;
                }
            });

            if (newAchievementsUnlocked) {
                showToast("🎉 You have unlocked a notification!");
            }
        }
    } catch (error) {
        console.error("Error fetching achievements:", error);
    }
}

// Track page time when the user leaves the page
function trackPageTime() {
    if (!pageStartTime) return; // Exit if `pageStartTime` is not set

    const timeSpent = Math.floor((Date.now() - pageStartTime) / 1000); // Time in seconds
    pageStartTime = null; // Reset to avoid duplicate calls

    const payload = JSON.stringify({
        page: window.location.pathname, // Identify the page (e.g., '/quiz.html' or '/flashcards.html')
        time_spent: timeSpent
    });

    try {
        // Attempt to send via `sendBeacon` for reliability
        const success = navigator.sendBeacon('/api/track_page_time', payload);
        if (!success) throw new Error("sendBeacon failed"); // Fallback if `sendBeacon` is unsuccessful
    } catch (error) {
        // Fallback to `fetch` in case of `sendBeacon` failure
        fetch('/api/track_page_time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: payload
        }).catch(err => console.error("Failed to send time tracking data via fetch:", err));
    }
}

// Attach `beforeunload` event listener
window.addEventListener("beforeunload", trackPageTime);
