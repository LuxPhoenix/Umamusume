let s = 0;
let retryButton = document.getElementById("resetGame")
retryButton.disabled = true
let retryTimes = 0

function scoreChange(sign) {
  if (s === 0) {
    s += sign * 5;
  } else {
    s += sign * 10;
  }

  let msg = document.getElementById("message");
  msg.textContent = `Current Score: ${s}!`;

  // Change color based on score
  if (s > 0) {
    msg.style.color = "green";
  } else if (s < 0) {
    msg.style.color = "red";
  } else {
    msg.style.color = "blue";
  }

  if (s >= 50) {
    msg.textContent = "🎉 You have won!";
    disableButtons();
  } else if (s < 0) {
    msg.textContent = "💀 You have lost!";
    disableButtons();
  }
}

function disableButtons() {
  document.getElementById("addScore").disabled = true;
  document.getElementById("subtractScore").disabled = true;
  retryButton.disabled = false
}

function retryGame() {
  retryTimes += 1
  s = 10 * retryTimes;
  let msg = document.getElementById("message");
  msg.textContent = `Current Score: ${s}!`;
  msg.style.color = "blue";

  document.getElementById("addScore").disabled = false;
  document.getElementById("subtractScore").disabled = false;
  retryButton.disabled = true;
}

document.getElementById("addScore").addEventListener("click", function() {
  scoreChange(1);
});

document.getElementById("subtractScore").addEventListener("click", function() {
  scoreChange(-1);
});

retryButton.addEventListener("click", retryGame);