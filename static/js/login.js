
function ensureAstrongPass(password){
    return password
}
document.querySelector('#submitTosignUP').addEventListener('click',async (event) => {
    const password = document.querySelector('#signupPassword').value;

    const confirmPassword = document.querySelector('#signupConfirmPassword').value;
    const name = document.querySelector('#signupUsername').value;
    const email = document.querySelector('#signupEmail').value;
    const phone_number = document.querySelector('#phoneNumber').value;
  
    // Ensure all fields are filled out
    if (name === "" || email === "" || password === "" || confirmPassword === "") {
      displayMessage("Please fill in all fields.", 'ERROR');
      return;
    }
  
    // Check if passwords match
    if (password !== confirmPassword) {
      displayMessage("Passwords do not match.", 'ERROR');
      return;
    }
  
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      displayMessage("Invalid email format.", 'ERROR');
      return;
    }
  
    // Check password length
    if (password.length < 8) {
      displayMessage("Password must be at least 8 characters long.", 'ERROR');
      return;
    }
    const termsConditions = document.querySelector('#termsAndConditionsCheckbox');
    if (!termsConditions.checked) {
      // Display error message
      displayMessage("You must agree to the terms and conditions.", 'ERROR');
      
      // Highlight the checkbox with a red border
      termsConditions.style.outline = '2px solid red'; // Better visibility with `outline`
      
      // Remove the red outline when the user interacts with the checkbox
      termsConditions.addEventListener('change', function () {
        if (termsConditions.checked) {
          termsConditions.style.outline = 'none';
        }
      });
    
      return;
    }
    
  
    console.log("submitted", email);
    
    const loaderDiv = document.createElement('div');
    loaderDiv.classList.add('loader');
    document.querySelector('#submitTosignUP').appendChild(loaderDiv);
  
    setTimeout(() => {
      loaderDiv.remove();
    }, 3000);
    try {
      const response = await fetch('/create', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password, name ,phone_number})
      });
  
      if (!response.ok) {
          const error = await response.json();
          console.error('Error response:', error);
          displayMessage(`${error.message || error.error}`, 'ERROR');
          return;
      }
  
      const data = await response.json();
      console.log('User created:', data);
      displayMessage(data.message, 'SUCCESS');
      // Handle additional UI changes for success
  } catch (e) {
      console.error('Request failed:', e);
      displayMessage("Failed to authenticate user.", 'ERROR');
  }
  loaderDiv.remove();
  
  });
  
  document.querySelector('#submitlogin').addEventListener('click', async (event) => {
    event.preventDefault(); // Prevent the default form submission
  
    const email = document.querySelector('#loginEmail').value.trim();
    const password = document.querySelector('#loginPassword').value.trim();
    const rememberMe = document.querySelector('#rememberMe')?.checked; // Optional
  
    // Validate input fields
    if (!email || !password) {
      displayMessage("Please fill in all fields.", 'ERROR');
      return;
    }
  
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      displayMessage("Invalid email format.", 'ERROR');
      return;
    }
  
    // Validate password length
    if (password.length < 8) {
      displayMessage("Password must be at least 8 characters long.", 'ERROR');
      return;
    }
  
    console.log("Submitting login for:", email);
  
    // Show loader
    const submitButton = document.querySelector('#submitlogin');
    const loaderDiv = document.createElement('div');
    loaderDiv.classList.add('loader'); // Ensure CSS styles are defined for `.loader`
    submitButton.appendChild(loaderDiv);
  
    try {
      // Send a POST request to the server
      const response = await fetch('/login/email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, rememberMe }),
      });
  
      // Check response status
      if (!response.ok) {
        const error = await response.json();
        displayMessage(`${error.message || error.error || "Failed to log in."}`, 'ERROR');
        return;
      }
  
      const result = await response.json();
      console.log('Login successful:', result);
      
      // Set a cookie with user_info — only if it's safe and NOT sensitive!
      document.cookie = `user_info=${encodeURIComponent(JSON.stringify(result.user_info))}; path=/`;
      
  
      window.location.href = "/";
    } catch (error) {
      console.error('Error logging in:', error);
      displayMessage('An unexpected error occurred. Please try again later.', 'ERROR');
    } finally {
      // Remove loader
      loaderDiv.remove();
    }
  });
  
  async function updateProfile(newPicture, userId) {
    if (!userId) {
        console.error("User ID is missing.");
        displayMessage("User ID is required", "ERROR");
        return;
    }
  
    console.log("Updating User ID:", userId, "Profile:", newPicture);
  
    const formData = new FormData();
    formData.append("userId", userId);
  
    if (newPicture instanceof File) { 
        formData.append("newPicture", newPicture); // File Upload
    } else {
        formData.append("newPicture", newPicture); // Base64 Upload
    }
  
    try {
        const response = await fetch("/user/updateProfile", {
            method: "POST",
            body: formData,
        });
  
        const result = await response.json();
        console.log("Profile update result:", result);
  
        if (result.success) {
            displayMessage("Profile updated successfully!","SUCCESS");
        } else {
            displayMessage("Profile update failed!", "ERROR");
        }
    } catch (error) {
        console.error("Error updating profile:", error);
        displayMessage("Error processing image", "ERROR");
    }
  }


  function displayMessage(msg,type){
    console.log("info:: ",msg)
    const hd = document.getElementById('msg-holder');
    hd.innerText = msg;
  }