'use client';

import { useState, useEffect, useRef } from 'react';
import { minimalPairLessons } from '../lessons/minimal_pairs.js';
import { submitAssessment, getTTSAudio } from '../services/api.js'; // MODIFIED: Import getTTSAudio

export default function HomePage() {
  // --- STATE MANAGEMENT ---
  const [currentLesson, setCurrentLesson] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null); // For playing TTS audio

  // API communication and results
  const [isLoading, setIsLoading] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [error, setError] = useState(null);

  // NEW: State for TTS audio playback
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const [audioLoading, setAudioLoading] = useState(null); // Can be 'sentence' or a word index
  const [audioError, setAudioError] = useState(null);


  // --- EFFECTS ---
  useEffect(() => {
    if (minimalPairLessons.length > 0) {
      setCurrentLesson(minimalPairLessons[0]);
    }
  }, []);

  // --- HANDLERS ---
  const handleLessonChange = (event) => {
    const lessonId = parseInt(event.target.value, 10);
    const selectedLesson = minimalPairLessons.find(l => l.id === lessonId);
    setCurrentLesson(selectedLesson);
    setAudioBlob(null);
    setAssessmentResult(null);
    setError(null);
    setAudioError(null);
  };

  const startRecording = async () => {
    setAudioBlob(null);
    setAssessmentResult(null);
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];
      mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        setAudioBlob(blob);
      };
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Could not access microphone. Please check browser permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleAssessment = async () => {
    if (!audioBlob || !currentLesson) {
      setError("Please record your audio before submitting.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setAudioError(null);
    setAssessmentResult(null);

    try {
      const result = await submitAssessment(audioBlob, currentLesson.reference_text);
      setAssessmentResult(result);
    } catch (err) {
      setError(err.message || "An unknown error occurred during assessment.");
    } finally {
      setIsLoading(false);
    }
  };
  
  // NEW: Handler to play TTS audio
  const handlePlayAudio = async (text, identifier) => {
    if (isAudioPlaying) return;

    setAudioLoading(identifier);
    setAudioError(null);
    try {
      const blob = await getTTSAudio(text);
      const url = URL.createObjectURL(blob);
      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.play();
        setIsAudioPlaying(true);
      }
    } catch (err) {
      setAudioError("Could not load audio. Please try again.");
    } finally {
      setAudioLoading(null);
    }
  };

  // NEW: Effect to manage audio element events
  useEffect(() => {
    const audio = audioRef.current;
    const onEnded = () => setIsAudioPlaying(false);
    const onError = () => {
        setIsAudioPlaying(false);
        setAudioError("Error playing audio file.");
    };

    if (audio) {
      audio.addEventListener('ended', onEnded);
      audio.addEventListener('error', onError);
    }

    return () => {
      if (audio) {
        audio.removeEventListener('ended', onEnded);
        audio.removeEventListener('error', onError);
      }
    };
  }, []);


  const getPhonemeColorClass = (score) => {
    if (score >= 4.0) return 'phoneme-good';
    if (score >= 2.5) return 'phoneme-ok';
    return 'phoneme-bad';
  };

  return (
    <main>
      <h1>Pronunciation Teacher</h1>

      <div className="lesson-selector">
        <h2>1. Select a Sentence</h2>
        <select onChange={handleLessonChange} value={currentLesson?.id || ''} disabled={isLoading || isAudioPlaying}>
          {minimalPairLessons.map(lesson => (
            <option key={lesson.id} value={lesson.id}>{lesson.reference_text}</option>
          ))}
        </select>
      </div>

      <div className="practice-area">
        <h2>2. Practice This Sentence</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <p style={{ fontSize: '1.2rem', color: '#a5d6a7', margin: 0 }}>
              {currentLesson?.id ? currentLesson.reference_text : "Please select a lesson."}
            </p>
            {currentLesson && (
                <button 
                    onClick={() => handlePlayAudio(currentLesson.reference_text, 'sentence')}
                    disabled={isAudioPlaying || isLoading || audioLoading === 'sentence'}
                    className="listen-button"
                >
                    {audioLoading === 'sentence' ? '...' : '\uD83D\uDD0A'} {/* Speaker Icon */}
                </button>
            )}
        </div>
      </div>
      
      <div className="recorder-area">
        <h2>3. Record and Assess</h2>
        <button onClick={startRecording} disabled={isRecording || isLoading || isAudioPlaying}>Start Recording</button>
        <button onClick={stopRecording} disabled={!isRecording || isLoading || isAudioPlaying}>Stop Recording</button>
        
        {audioBlob && <audio controls src={URL.createObjectURL(audioBlob)} style={{width: '100%', marginTop: '1rem'}} />}
        
        <button onClick={handleAssessment} disabled={!audioBlob || isLoading || isAudioPlaying} style={{marginTop: '1rem', width: '100%'}}>
          {isLoading ? 'Assessing...' : 'Submit for Assessment'}
        </button>
      </div>

      {/* Hidden Audio Player for TTS */}
      <audio ref={audioRef} style={{ display: 'none' }} />

      {error && <div className="results-card" style={{borderColor: '#ef5350'}}><p style={{color: '#ef5350'}}>Error: {error}</p></div>}
      {audioError && <div className="results-card" style={{borderColor: '#ef5350', marginTop: '1rem'}}><p style={{color: '#ef5350'}}>{audioError}</p></div>}
      
      {assessmentResult && (
        <div className="results-card">
          <h2>Results</h2>
          <p>
            <strong>Your Pronunciation: </strong> 
            {assessmentResult.is_correct 
              ? <span style={{color: '#66bb6a'}}>Correct!</span>
              : <span style={{color: '#ef5350'}}>Incorrect. We heard:</span>
            }
          </p>
          <p style={{fontStyle: 'italic'}}>"{assessmentResult.user_transcript}"</p>
          
          {assessmentResult.is_correct && (
            <div style={{marginTop: '1rem'}}>
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                    <h3>Detailed Feedback:</h3>
                </div>
              {assessmentResult.words.map((word, wordIndex) => (
                <div key={word.word + wordIndex} style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
                  <strong style={{fontSize: '1.2rem'}}>{word.word}: </strong>
                  <div style={{display: 'flex', flexWrap: 'wrap', alignItems: 'center'}}>
                    {word.phonemes.map((ph, phIndex) => (
                        <span key={ph.phoneme + phIndex} style={{margin: '0 0.2rem'}}>
                        <span className={getPhonemeColorClass(ph.score)} style={{fontSize: '1.2rem', fontWeight: 'bold'}}>
                            {ph.phoneme}
                        </span>
                        {ph.feedback_tip && (
                            <div className="feedback-tip">{ph.feedback_tip}</div>
                        )}
                        </span>
                    ))}
                  </div>
                  <button 
                    onClick={() => handlePlayAudio(word.word, wordIndex)}
                    disabled={isAudioPlaying || isLoading || audioLoading === wordIndex}
                    className="listen-button-small"
                   >
                    {audioLoading === wordIndex ? '...' : '\uD83D\uDD0A'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </main>
  );
}