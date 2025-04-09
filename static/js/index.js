const modeSwitch = document.getElementById("mode_switch");

// Add event listener to the button
modeSwitch.addEventListener("click", function() {
    document.body.classList.toggle("dark_mode");
    if (document.body.classList.contains("dark_mode")) {
        modeSwitch.textContent = "Switch to Light Mode";
    } else {
        modeSwitch.textContent = "Switch to Dark Mode";
    }
});
