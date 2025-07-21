const options = ["customizacja lamp", "kodowanie", "naprawa elektroniki", "dbanie o auto", "magia, by amerykańskie auto stało się europejskie"];
const typingSpeed = 100; // ms per character
const erasingSpeed = 50;
const delayBetween = 1500; // delay between options

let optionIndex = 0;
let charIndex = 0;
const typedTextSpan = document.getElementById("typed-text");

function type() {
    if (charIndex < options[optionIndex].length) {
        typedTextSpan.textContent += options[optionIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, typingSpeed);
    } else {
        setTimeout(erase, delayBetween);
    }
}

function erase() {
    if (charIndex > 0) {
        typedTextSpan.textContent = options[optionIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingSpeed);
    } else {
        optionIndex = (optionIndex + 1) % options.length;
        setTimeout(type, typingSpeed);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    if (options.length) setTimeout(type, delayBetween);
});
