# 🗣️ Pronunciation Teacher

Welcome to the **Pronunciation Teacher** project! This application is designed to help users improve their English pronunciation through interactive lessons, real-time feedback, and speech analysis.

## ✨ Features

-   **Speech Recognition (ASR):** Converts user's spoken input into text.
-   **Pronunciation Assessment (GOP):** Provides detailed feedback on individual phonemes and words.
-   **AI-Powered Feedback:** Offers intelligent and constructive feedback on pronunciation accuracy and fluency, potentially leveraging OpenAI's capabilities.
-   **Text-to-Speech (TTS):** Generates natural-sounding audio for words and sentences, using services like gTTS or OpenAI TTS.
-   **Interactive Lessons:** Guides users through various pronunciation exercises.
-   **User-Friendly Interface:** A modern and responsive web interface built with Next.js.

## 🚀 Technologies Used

This project is built with a Python backend (FastAPI) and a Next.js frontend.

### Backend

-   **Python 🐍:** The core programming language.
-   **FastAPI ⚡:** A modern, fast (high-performance) web framework for building APIs.
-   **Uvicorn:** ASGI server for running FastAPI applications.
-   **ASR Service:** Likely uses a speech-to-text library/API (e.g., AssemblyAI, Google Speech-to-Text, or a local model).
-   **GOP Service:** Utilizes a Goodness of Pronunciation (GOP) model for detailed phoneme-level analysis.
-   **Gemini/OpenAI API:** For advanced feedback generation and potentially TTS. (using Gemini)
-   **gTTS/OpenAI API:** Google Text-to-Speech for simpler TTS needs. (using gTTS)

### Frontend

-   **Next.js ⚛️:** A React framework for building performant web applications.
-   **React.js:** For building interactive user interfaces.
-   **JavaScript/TypeScript:** Programming languages for the frontend.
-   **CSS Modules/Tailwind CSS (assumed):** For styling.

## ⚙️ Setup Guide

Follow these steps to get the Pronunciation Teacher project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

-   **Git:** For cloning the repository.
    -   [Download Git](https://git-scm.com/downloads)
-   **Python 3.10+:** For the backend.
    -   [Download Python](https://www.python.org/downloads/)
-   **Node.js (LTS) & npm:** For the frontend.
    -   [Download Node.js](https://nodejs.org/en/download/)
-   **ffmpeg:** For audio processing

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/YOUR_USERNAME/pronunciation-teacher.git
cd pronunciation-teacher
```

### 2. Backend Setup

Navigate to the `backend` directory and set up the Python environment.

```bash
cd backend
```

#### Create and Activate Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the `backend` directory and add your API keys and configurations. An example `.env` file might look like this:

(use gemini api key if you don't want any change in code)
Create free gemini api (limited quota)
['Generate api key'](https://aistudio.google.com/apikey)

```
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (Optional)
# Add other backend-specific environment variables here (e.g., ASR service keys, etc.)
```

**Note:** Replace `your_api_key_here` with your actual OpenAI API key. You might need other keys depending on the specific ASR/GOP services used.

#### Run the Backend Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be accessible at `http://localhost:8000`.

### 3. Frontend Setup

Open a new terminal, navigate to the `frontend` directory, and set up the Node.js environment.

```bash
cd ../frontend
```

#### Install Dependencies

Install the Node.js packages:

```bash
npm install
# or yarn install
```

#### Environment Variables

Create a `.env.local` file in the `frontend` directory for Next.js environment variables. This is typically used for client-side accessible variables.

```
# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
# Add other frontend-specific environment variables here
```

#### Run the Frontend Development Server

Start the Next.js development server:

```bash
npm run dev
# or yarn dev
```

The frontend application will be accessible at `http://localhost:3000`.

## 🚀 Usage

Once both the backend and frontend servers are running:

1.  Open your web browser and navigate to `http://localhost:3000`.
2.  Interact with the application to practice your pronunciation.
3.  The frontend will communicate with the backend API for speech processing and feedback.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by VISHNU PRATAP SINGH
