async function searchRecipes() {
  const ingredient = document.getElementById("ingredientInput").value.trim();
  const resultsDiv = document.getElementById("results");

  if (!ingredient) {
    resultsDiv.innerHTML = "<p>⚠️ Please enter a meal.</p>"; 
    return;
  }

  resultsDiv.innerHTML = "<p>⏳ Loading recipes...</p>"; 

  try {
    const response = await fetch(`http://127.0.0.1:5000/recommend?ingredient=${ingredient}`);
    const data = await response.json();

    if (!data.recipes || data.recipes.length === 0) {
      resultsDiv.innerHTML = "<p>😢 Oops, no recipes found.</p>"; 
      return;
    }

    resultsDiv.innerHTML = "";
    data.recipes.forEach(recipe => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <img src="${recipe.image || `https://source.unsplash.com/400x300/?${ingredient}`}" alt="${recipe.name}">
        <div class="card-body">
          <h3>${recipe.name}</h3>
          <p><b>Ingredients:</b> ${recipe.ingredients ? recipe.ingredients.join(", ") : "N/A"}</p>
        </div>
      `;
      resultsDiv.appendChild(card);
    });

  } catch (error) {
    console.error("Error fetching recipes:", error);
    resultsDiv.innerHTML = "<p>❌ Error fetching recipes.</p>"; 
  }
}

// Sidebar and theme functions same as before...
function goHome() {
  document.getElementById("results").innerHTML = `
    <h2>🏠 Welcome to FoodieAI</h2>
    <p>Start by typing an ingredient in the search bar!</p>
  `;
}

function showSaved() {
  document.getElementById("results").innerHTML = `
    <h2>❤️ Saved Recipes</h2>
    <p>You haven’t saved any recipes yet.</p>
  `;
}

function showPopular() {
  document.getElementById("results").innerHTML = `
    <h2>🔥 Popular Recipes</h2>
    <ul>
      <li>🍕 Pizza</li>
      <li>🍔 Burger</li>
      <li>🥗 Caesar Salad</li>
    </ul>
  `;
}

function showAbout() {
  document.getElementById("results").innerHTML = `
    <h2>About FoodieAI</h2>
    <p>FoodieAI helps you discover recipes instantly using ingredients you already have.</p>
  `;
}

function openSettings() {
  document.getElementById("results").innerHTML = `
    <h2>⚙️ Settings</h2>
    <p>Choose a theme:</p>
    <button onclick="setTheme('light')"> Light</button>
    <button onclick="setTheme('dark')"> Dark</button>
  `;
}

function setTheme(theme) {
  if (theme === "dark") document.body.classList.add("dark-theme");
  else document.body.classList.remove("dark-theme");
}

/*validate form

function validateEmail(email) {
    let format = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return format.test(email); 
}

function validatePassword(password) {
    // Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character
    let format = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return format.test(password);
}


function validateSignUp(){
    let username = document.getElementById('username').value.trim();
    let email = document.getElementById('email').value.trim();
    let password = document.getElementById('password').value.trim();

    //not empty
    if(!username || !email || !password){
        alert('All fields are required!');
        return false; //prevent form submission
    }

    if(!validateEmail(email)){
        alert('Please enter a valid email address.');
        return false; //prevent form submission
    }

    if(!validatePassword(password)){
        alert('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.');
        return false; //prevent form submission
    }

    alert('Form submitted successfully!');
    return true; //allow form submission

}*/

const API_URL = "http://127.0.0.1:5000";

// -------- Login --------
async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!email || !password) {
    alert("Please enter email and password.");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      alert("Login successful!");
      localStorage.setItem("token", data.token); // save token
    } else {
      alert(data.message || "Invalid login.");
    }
  } catch (err) {
    console.error("Login error:", err);
    alert("Error logging in. Try again.");
  }
}







