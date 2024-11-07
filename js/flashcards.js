const container = document.querySelector(".container");
const addQuestionCard = document.getElementById("add-question-card");
const cardButton = document.getElementById("save-btn");
const question = document.getElementById("question");
const answer = document.getElementById("answer");
const errorMessage = document.getElementById("error");
const addQuestion = document.getElementById("add-flashcard");
const closeBtn = document.getElementById("close-btn");
const createStudySetBtn = document.getElementById("create-study-set");
const studySetDropdown = document.getElementById("study-set-dropdown");
let currentStudySet = "default"; // Track the current study set
let editBool = false;

// Initialize and load study sets on page load
window.onload = () => {
  populateStudySetDropdown();
  loadStudySet(currentStudySet); // Load the default study set initially
};

// Populate dropdown with study sets
function populateStudySetDropdown() {
  const studySets = JSON.parse(localStorage.getItem("studySets")) || ["default"];
  studySetDropdown.innerHTML = ""; // Clear existing options
  studySets.forEach((setName) => {
    const option = document.createElement("option");
    option.value = setName;
    option.textContent = setName;
    studySetDropdown.appendChild(option);
  });
  studySetDropdown.value = currentStudySet; // Set dropdown to current set
}

// Event to create a new study set
createStudySetBtn.addEventListener("click", () => {
  const newSetName = prompt("Enter a name for the new study set:");
  if (newSetName) {
    const studySets = JSON.parse(localStorage.getItem("studySets")) || ["default"];
    if (!studySets.includes(newSetName)) {
      studySets.push(newSetName);
      localStorage.setItem("studySets", JSON.stringify(studySets));
      populateStudySetDropdown();
      currentStudySet = newSetName;
      loadStudySet(newSetName);
    } else {
      alert("A study set with that name already exists.");
    }
  }
});

// Load an existing study set
studySetDropdown.addEventListener("change", () => {
  currentStudySet = studySetDropdown.value;
  loadStudySet(currentStudySet);
});

// Load cards from a study set
function loadStudySet(setName) {
  document.querySelector(".card-list-container").innerHTML = ""; // Clear existing cards
  const flashcards = JSON.parse(localStorage.getItem(setName)) || [];
  flashcards.forEach((flashcard) => addFlashcard(flashcard.question, flashcard.answer));
}

// Save flashcard to the current study set in localStorage
function saveFlashcardToSet(setName, question, answer) {
  const flashcards = JSON.parse(localStorage.getItem(setName)) || [];
  flashcards.push({ question, answer });
  localStorage.setItem(setName, JSON.stringify(flashcards));
}

// Add question when user clicks 'Add Flashcard' button
addQuestion.addEventListener("click", () => {
  container.classList.add("hide");
  question.value = "";
  answer.value = "";
  addQuestionCard.classList.remove("hide");
});

// Hide Create flashcard Card
closeBtn.addEventListener("click", () => {
  container.classList.remove("hide");
  addQuestionCard.classList.add("hide");
  errorMessage.classList.add("hide");
  editBool = false;
});

// Submit Question
cardButton.addEventListener("click", () => {
  const tempQuestion = question.value.trim();
  const tempAnswer = answer.value.trim();
  if (!tempQuestion || !tempAnswer) {
    errorMessage.classList.remove("hide");
  } else {
    errorMessage.classList.add("hide");
    container.classList.remove("hide");
    addQuestionCard.classList.add("hide");
    addFlashcard(tempQuestion, tempAnswer);
    saveFlashcardToSet(currentStudySet, tempQuestion, tempAnswer);
    question.value = "";
    answer.value = "";
  }
});

// Function to add flashcard to the view
function addFlashcard(questionText, answerText) {
  const listCard = document.querySelector(".card-list-container");
  const div = document.createElement("div");
  div.classList.add("card");

  // Question
  div.innerHTML = `<p class="question-div">${questionText}</p>`;

  // Answer
  const displayAnswer = document.createElement("p");
  displayAnswer.classList.add("answer-div", "hide");
  displayAnswer.innerText = answerText;

  // Link to show/hide answer
  const link = document.createElement("a");
  link.href = "#";
  link.className = "show-hide-btn";
  link.innerText = "Show/Hide";
  link.addEventListener("click", (e) => {
    e.preventDefault();
    displayAnswer.classList.toggle("hide");
  });

  div.appendChild(link);
  div.appendChild(displayAnswer);

  // Edit button
  const buttonsCon = document.createElement("div");
  buttonsCon.classList.add("buttons-con");
  const editButton = document.createElement("button");
  editButton.className = "edit";
  editButton.innerHTML = `<i class="fa-solid fa-pen-to-square"></i>`;
  editButton.addEventListener("click", () => {
    editBool = true;
    modifyElement(editButton, true);
    addQuestionCard.classList.remove("hide");
  });
  buttonsCon.appendChild(editButton);

  // Delete Button
  const deleteButton = document.createElement("button");
  deleteButton.className = "delete";
  deleteButton.innerHTML = `<i class="fa-solid fa-trash-can"></i>`;
  deleteButton.addEventListener("click", () => {
    div.remove();
  });
  buttonsCon.appendChild(deleteButton);

  div.appendChild(buttonsCon);
  listCard.appendChild(div);
}

// Modify Elements
const modifyElement = (element, edit = false) => {
  const parentDiv = element.closest(".card");
  const parentQuestion = parentDiv.querySelector(".question-div").innerText;
  if (edit) {
    const parentAnswer = parentDiv.querySelector(".answer-div").innerText;
    answer.value = parentAnswer;
    question.value = parentQuestion;
    parentDiv.remove();
  }
};
