document.addEventListener("DOMContentLoaded", () => {
    const data = JSON.parse(localStorage.getItem("scanResult"));
  
    if (!data) {
      document.querySelector(".results-container").innerHTML = "<p>No scan data found. Please scan a product first.</p>";
      return;
    }
  
    // Populate food item details
    const resultsList = document.getElementById("results-list");
    
    // Create the main food item
    const foodItem = document.createElement("div");
    foodItem.className = "food-item";
    
    // Determine food quality rating
    let qualityClass = "average";
    let qualityEmoji = "😐";
    
    if (data.nutrition_quality && typeof data.nutrition_quality === 'string') {
      if (data.nutrition_quality.toLowerCase().includes("good")) {
        qualityClass = "good";
        qualityEmoji = "👍";
      } else if (data.nutrition_quality.toLowerCase().includes("poor")) {
        qualityClass = "poor";
        qualityEmoji = "👎";
      }
    }
    
    foodItem.innerHTML = `
      <div class="food-details">
        <div class="food-name">${data.product_name || "Unknown Product"}</div>
        <div class="calories">${data.nutrition_totals?.calories || "N/A"} calories</div>
        <div class="food-stats">
          <div class="stat">
            <span class="stat-value">${data.nutrition_totals?.carbs || "0"}g</span>
            <span class="stat-label">Carbs</span>
          </div>
          <div class="stat">
            <span class="stat-value">${data.nutrition_totals?.proteins || "0"}g</span>
            <span class="stat-label">Protein</span>
          </div>
          <div class="stat">
            <span class="stat-value">${data.nutrition_totals?.fats || "0"}g</span>
            <span class="stat-label">Fats</span>
          </div>
        </div>
      </div>
      <div class="food-quality ${qualityClass}">${qualityEmoji}</div>
    `;
    
    resultsList.appendChild(foodItem);
  
    // Populate alternatives
    const alternativesList = document.getElementById("alternatives-list");
    
    // If no alternatives, show a message
    if (!data.suggested_alternatives || data.suggested_alternatives.length === 0) {
      const noAlt = document.createElement("p");
      noAlt.textContent = "No alternatives found for this product.";
      alternativesList.appendChild(noAlt);
    } else {
      // Emojis for food alternatives
      const foodEmojis = ["🥗", "🥦", "🍎", "🥑", "🥕", "🍇", "🥝"];
      
      // Add each alternative
      data.suggested_alternatives.forEach((alt, index) => {
        const card = document.createElement("div");
        card.className = "alternative-card";
        
        const emoji = foodEmojis[index % foodEmojis.length];
        
        card.innerHTML = `
          <span class="alternative-emoji">${emoji}</span>
          <div class="alternative-name">${alt}</div>
          <p class="alternative-desc">Healthier alternative with similar taste profile</p>
        `;
        
        alternativesList.appendChild(card);
      });
    }
    
    // Add event listeners for buttons
    document.querySelector(".action-button").addEventListener("click", () => {
      alert("Results saved!");
    });
    
    document.querySelector(".action-button.secondary").addEventListener("click", () => {
      localStorage.removeItem("scanResult");
      window.location.href = "index.html"; // Assuming scan page is index.html
    });
  });