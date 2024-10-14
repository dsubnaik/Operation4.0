const container = document.querySelector(".container");
const addQuestionCard = document.getElementById("add-question-card");
const cardButton = document.getElementById("save-btn");
const question = document.getElementById("question");
const answer = document.getElementById("answer");
const errorMessage = document.getElementById("error");
const addQuestion = document.getElementById("add-flashcard");
const closeBtn = document.getElementById("close-btn");
let editBool = false;

// Add question when user clicks 'Add Flashcard' button
addQuestion.addEventListener("click", () => {
  container.classList.add("hide");
  question.value = "";
  answer.value = "";
  addQuestionCard.classList.remove("hide");
});

// Hide Create flashcard Card
closeBtn.addEventListener(
  "click",
  (hideQuestion = () => {
    container.classList.remove("hide");
    addQuestionCard.classList.add("hide");
    if (editBool) {
      editBool = false;
      submitQuestion();
    }
  })
);

// Submit Question and send data to server
cardButton.addEventListener(
  "click",
  (submitQuestion = () => {
    editBool = false;
    let tempQuestion = question.value.trim();
    let tempAnswer = answer.value.trim();
    
    if (!tempQuestion || !tempAnswer) {
      errorMessage.classList.remove("hide");
    } else {
      // Hide the error message
      errorMessage.classList.add("hide");

      // Prepare the data to be sent to the server
      let flashcardData = {
        question: tempQuestion,
        answer: tempAnswer,
        user_id: null // Add user ID if you plan to associate flashcards with users
      };

      // Send the data to the server via a POST request
      fetch("/add_flashcard", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(flashcardData), // Convert data to JSON
      })
      .then((response) => {
        if (response.ok) {
          // Clear the input fields
          question.value = "";
          answer.value = "";
          // Optionally reload or update the flashcards list
          container.classList.remove("hide");
          addQuestionCard.classList.add("hide");
          // Fetch the updated flashcards list
          viewlist();
        } else {
          console.error("Failed to add flashcard.");
        }
      })
      .catch((error) => console.error("Error:", error));
    }
  })
);

// Card Generate and fetch flashcards from the server
function viewlist() {
  fetch("/flashcards")
    .then(response => response.json())
    .then(data => {
      let listCard = document.getElementsByClassName("card-list-container")[0];
      listCard.innerHTML = ""; // Clear the current list

      data.forEach(flashcard => {
        let div = document.createElement("div");
        div.classList.add("card");

        // Question
        div.innerHTML += `<p class="question-div">${flashcard.question}</p>`;

        // Answer
        let displayAnswer = document.createElement("p");
        displayAnswer.classList.add("answer-div", "hide");
        displayAnswer.innerText = flashcard.answer;

        // Link to show/hide answer
        let link = document.createElement("a");
        link.setAttribute("href", "#");
        link.setAttribute("class", "show-hide-btn");
        link.innerHTML = "Show/Hide";
        link.addEventListener("click", () => {
          displayAnswer.classList.toggle("hide");
        });

        div.appendChild(link);
        div.appendChild(displayAnswer);

        // Edit and delete buttons (same as before)
        let buttonsCon = document.createElement("div");
        buttonsCon.classList.add("buttons-con");
        // Edit Button
        let editButton = document.createElement("button");
        editButton.setAttribute("class", "edit");
        editButton.innerHTML = `<i class="fa-solid fa-pen-to-square"></i>`;
        editButton.addEventListener("click", () => {
          editBool = true;
          question.value = flashcard.question;
          answer.value = flashcard.answer;
          addQuestionCard.classList.remove("hide");
        });
        buttonsCon.appendChild(editButton);
        disableButtons(false);

        // Delete Button
        let deleteButton = document.createElement("button");
        deleteButton.setAttribute("class", "delete");
        deleteButton.innerHTML = `<i class="fa-solid fa-trash-can"></i>`;
        deleteButton.addEventListener("click", () => {
          modifyElement(deleteButton);
        });
        buttonsCon.appendChild(deleteButton);

        div.appendChild(buttonsCon);
        listCard.appendChild(div);
      });
    })
    .catch(error => console.error("Error fetching flashcards:", error));
}
