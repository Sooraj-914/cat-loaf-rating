document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("upload-area");
  const fileInput = document.getElementById("file-input");
  const rateBtn = document.getElementById("rate-btn");
  const uploadContent = document.getElementById("upload-content");
  const previewContent = document.getElementById("preview-content");
  const previewImage = document.getElementById("preview-image");
  const resultsSection = document.getElementById("results-section");
  const loadingSection = document.getElementById("loading");
  const errorMessage = document.getElementById("error-message");
  const tryAgainBtn = document.getElementById("try-again-btn");

  // Handle drag and drop
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("border-orange-400");
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("border-orange-400");
  });

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("border-orange-400");
    handleFiles(e.dataTransfer.files);
  });

  // Handle click upload
  uploadArea.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", (e) => {
    handleFiles(e.target.files);
  });

  // Handle file selection
  function handleFiles(files) {
    const file = files[0];
    if (file && file.type.startsWith("image/")) {
      // Show preview
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadContent.classList.add("hidden");
        previewContent.classList.remove("hidden");
        rateBtn.disabled = false;
      };
      reader.readAsDataURL(file);
    }
  }

  // Handle rating submission
  rateBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    // Show loading state
    loadingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    errorMessage.classList.add("hidden");

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("/rate", {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      const data = await response.json();

      // DETAILED DEBUGGING - This will show us exactly what the backend returns
      console.log("Raw server response:", data);
      console.log("Response type:", typeof data);
      console.log("Response keys:", Object.keys(data));
      console.log("Has loaf_score?", "loaf_score" in data);
      console.log("Has score?", "score" in data);
      console.log("loaf_score value:", data.loaf_score);
      console.log("score value:", data.score);

      if (!response.ok) {
        throw new Error(data.error || "Server error");
      }

      // Check if data has the expected structure - REMOVE THIS CHECK FOR NOW
      // if (!data.loaf_score) {
      //   throw new Error("Invalid response format");
      // }

      // Try to find the score in different possible locations
      let score;
      if (data.loaf_score !== undefined) {
        score = data.loaf_score;
        console.log("Using loaf_score:", score);
      } else if (data.score !== undefined) {
        // If score is a decimal (0-1), convert to percentage
        score = data.score > 1 ? data.score : data.score * 100;
        console.log("Using score (converted):", score);
      } else {
        console.error("No score found! Available data:", data);
        throw new Error(
          "No score found in response. Available keys: " +
            Object.keys(data).join(", ")
        );
      }

      // Update results
      document.getElementById("score-value").textContent = Math.round(score);
      document.getElementById("score-percentage").textContent = `${Math.round(
        score
      )}%`;
      document.getElementById("score-bar").style.width = `${score}%`;

      // Update technical details
      if (data.details) {
        console.log("Details found:", data.details);
        document.getElementById("aspect-ratio").textContent =
          data.details.aspect_ratio || "N/A";
        document.getElementById("area-ratio").textContent =
          data.details.area_ratio || "N/A";
        document.getElementById("symmetry-score").textContent =
          data.details.symmetry_score || data.details.symmetry || "N/A";
        document.getElementById("posture-score").textContent =
          data.details.posture_score || data.details.posture || "N/A";
      } else {
        console.log("No details found in response");
      }

      document.getElementById("score-feedback").textContent =
        data.feedback || "No feedback available";

      // Update emoji based on score
      document.getElementById("score-emoji").textContent =
        score >= 90 ? "🏆" : score >= 70 ? "🍞" : score >= 50 ? "😺" : "😿";

      // Show results
      loadingSection.classList.add("hidden");
      resultsSection.classList.remove("hidden");
    } catch (error) {
      console.error("Full error details:", error);
      console.error("Error message:", error.message);
      console.error("Error stack:", error.stack);
      loadingSection.classList.add("hidden");
      errorMessage.classList.remove("hidden");
      document.getElementById("error-text").textContent =
        error.message || "Failed to analyze image. Please try again.";
    }
  });

  // Handle try again button
  tryAgainBtn.addEventListener("click", () => {
    // Reset form
    fileInput.value = "";
    uploadContent.classList.remove("hidden");
    previewContent.classList.add("hidden");
    resultsSection.classList.add("hidden");
    rateBtn.disabled = true;
  });
});
