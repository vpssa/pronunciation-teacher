/**
 * Fetches TTS audio from the backend.
 * @param {string} text - The text to synthesize.
 * @returns {Promise<Blob>} - A blob containing the audio data.
 */
export async function getTTSAudio(text) {
  const API_URL = "http://localhost:8000/api/v1/tts/";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "An unknown server error occurred." }));
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    const audioBlob = await response.blob();
    return audioBlob;

  } catch (error) {
    console.error("Failed to fetch TTS audio:", error);
    throw error;
  }
}

// frontend/src/services/api.js

/**
 * Sends the audio and reference text to the backend for assessment.
 * @param {Blob} audioBlob - The recorded audio blob.
 * @param {string} referenceText - The text the user was supposed to say.
 * @returns {Promise<object>} - The assessment result from the backend.
 */
export async function submitAssessment(audioBlob, referenceText) {
  // Make sure your backend FastAPI server is running on port 8000
  const API_URL = "http://localhost:8000/api/v1/assessment/";

  // We use FormData to send a file and a string together,
  // which is required for a `multipart/form-data` request.
  const formData = new FormData();
  formData.append("audio_file", audioBlob, "user_recording.webm");
  formData.append("reference_text", referenceText);

  

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData,
      // IMPORTANT: Do not set the 'Content-Type' header yourself.
      // The browser will automatically set it to 'multipart/form-data'
      // with the correct boundary when the body is a FormData object.
    });

    if (!response.ok) {
      // If the server returns an error (like 500), handle it
      const errorData = await response.json().catch(() => ({ detail: "An unknown server error occurred." }));
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    const result = await response.json();
    
    return result;
    
  } catch (error) {
    console.error("Failed to submit assessment:", error);
    // Re-throw the error so the calling component can catch it and update the UI
    throw error;
  }
}