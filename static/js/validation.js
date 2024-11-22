function validateName() {
    const name = document.getElementById('name').value;
    const nameError = document.getElementById('nameError');
    const nameRegex = /^[a-zA-Z\s'-]+$/;

    if (name.trim() === '' || name.length < 2 || name.length > 50 || !nameRegex.test(name)) {
        nameError.style.display = 'block';
        return false;
    } else {
        nameError.style.display = 'none';
        return true;
    }
}

function validateEmail() {
    const email = document.getElementById('email').value;
    const emailError = document.getElementById('emailError');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
        emailError.style.display = 'block';
        return false;
    } else {
        emailError.style.display = 'none';
        return true;
    }
}

function validatePassword() {
    const password = document.getElementById('password').value;
    const passwordError = document.getElementById('passwordError');

    if (password.length < 8 || !/\d/.test(password) || !/[!@#$%^&*]/.test(password)) {
        passwordError.style.display = 'block';
        return false;
    } else {
        passwordError.style.display = 'none';
        return true;
    }
}

document.getElementById('signUpForm').onsubmit = function(event) {
    const isNameValid = validateName();
    const isEmailValid = validateEmail();
    const isPasswordValid = validatePassword();

    if (!isNameValid || !isEmailValid || !isPasswordValid) {
        event.preventDefault();
    }
};