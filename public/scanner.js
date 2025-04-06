document.addEventListener("DOMContentLoaded", function() {
    const imageInput = document.getElementById("imageInput");
    const uploadButton = document.getElementById("uploadButton");
    const previewImage = document.getElementById("preview-image");
    const workingIndicator = document.getElementById("working-indicator");
  
    // When upload button is clicked, trigger file input
    uploadButton.addEventListener("click", function() {
      imageInput.click();
    });
  
    // When a file is selected, show preview
    imageInput.addEventListener("change", function() {
      const file = imageInput.files[0];
      
      if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
          previewImage.src = e.target.result;
          previewImage.style.display = "block";
          
          // Update overlay to be hidden when showing an image
          document.querySelector('.camera-overlay').style.opacity = '0';
          
          // Show working indicator
          workingIndicator.classList.add("active");
          uploadButton.classList.add("working");
          
          // Process the file
          processFile(file);
        };
        
        reader.readAsDataURL(file);
      }
    });
  
    async function processFile(file) {
      const formData = new FormData();
      formData.append("image", file); // KEY MUST BE EXACTLY "image"
    
      try {
        const response = await fetch("https://bitecheck2-bjnn.onrender.com/analyze", {
          method: "POST",
          body: formData,
        });
    
        if (!response.ok) {
          throw new Error("Failed to analyze image");
        }
    
        const result = await response.json();
        console.log("Backend Response:", result);
    
        // Create mock data matching the structure expected by results.js if needed
        const mockData = {
          product_name: result.product_name || "Food Item",
          nutrition_quality: result.nutrition_quality || "Average",
          nutrition_totals: {
            calories: result.nutrition_totals?.calories || "250",
            carbs: result.nutrition_totals?.carbs || "30",
            proteins: result.nutrition_totals?.proteins || "15", 
            fats: result.nutrition_totals?.fats || "10"
          },
          suggested_alternatives: result.suggested_alternatives || [
            "Organic Alternative",
            "Lower Sugar Option", 
            "Plant-Based Substitute"
          ]
        };
    
        // Save result to localStorage for results.html to access
        localStorage.setItem("scanResult", JSON.stringify(mockData));
        
        // Hide working indicator
        workingIndicator.classList.remove("active");
        uploadButton.classList.remove("working");
        
        // Redirect to results page
        window.location.href = "results.html";
      } catch (error) {
        // Hide working indicator
        workingIndicator.classList.remove("active");
        uploadButton.classList.remove("working");
        
        alert("Error: " + error.message);
        console.error(error);
      }
    }
  });