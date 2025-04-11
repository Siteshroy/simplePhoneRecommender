const modeSwitch = document.getElementById("mode_switch");

const ToggleMode = () => {
  document.body.classList.toggle("dark-mode");
  var modeIcon = modeSwitch.childNodes[0];
  modeIcon.classList.contains("fa-moon")
    ? modeIcon.classList.replace("fa-moon", "fa-sun")
    : modeIcon.classList.replace("fa-sun", "fa-moon");
};

modeSwitch.addEventListener("click", ToggleMode);
