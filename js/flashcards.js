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

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  loadStudySets();
});

// Fetch and generate study set buttons
async function loadStudySets() {
  try {
    const response = await fetch('/api/get_study_sets');
    if (response.ok) {
      const studySets = await response.json();
      studySetButtonsContainer.innerHTML = ""; // Clear existing buttons
      studySets.forEach(set => {
        const button = document.createElement("button");
        button.textContent = set.name;
        button.classList.add("load-set-btn");
        if (set.id === currentStudySet) {
          button.classList.add("active-set");
        }
        button.addEventListener("click", () => handleStudySetClick(button, set.id));
        studySetButtonsContainer.appendChild(button);
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
      flashcards.forEach(card => addFlashcard(card.question, card.answer));
    } else {
      console.error("Failed to fetch flashcards.");
    }
  } catch (error) {
    console.error("Error loading flashcards:", error);
  }
}

// Add Flashcard to the DOM
function addFlashcard(questionText, answerText) {
  const flashcard = document.createElement("div");
  flashcard.classList.add("card");

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
    deleteFlashcard(questionText);
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
    await fetch('/api/add_flashcard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ study_set_id: currentStudySet, question, answer })
    });
    loadFlashcards(currentStudySet);
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
async function deleteFlashcard(question) {
  try {
    await fetch('/api/delete_flashcard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ study_set_id: currentStudySet, question })
    });
    loadFlashcards(currentStudySet);
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
      loadStudySets(); // Reload study set buttons
      loadFlashcards(currentStudySet); // Load flashcards for the new set
    } else {
      alert("A study set with that name already exists.");
    }
  } catch (error) {
    console.error("Error creating new study set:", error);
  }
});
