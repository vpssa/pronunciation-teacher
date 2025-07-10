# backend/app/services/gop_service.py

import io
import os
import torch
import numpy as np
import librosa
import subprocess
from g2p_en import G2p
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from app.core.config import GOP_MODEL_NAME

ARPABET_TO_IPA = {
    # Vowels (Monophthongs)
    'AA': 'ɑ', 'AA0': 'ɑ', 'AA1': 'ɑ', 'AA2': 'ɑ',       # bot
    'AE': 'æ', 'AE0': 'æ', 'AE1': 'æ', 'AE2': 'æ',       # bat
    'AH': 'ʌ', 'AH0': 'ə', 'AH1': 'ʌ', 'AH2': 'ʌ',       # butt (stressed vs. unstressed)
    'AO': 'ɔ', 'AO0': 'ɔ', 'AO1': 'ɔ', 'AO2': 'ɔ',       # bought
    'EH': 'ɛ', 'EH0': 'ɛ', 'EH1': 'ɛ', 'EH2': 'ɛ',       # bet
    'ER': 'ɝ', 'ER0': 'ɚ', 'ER1': 'ɝ', 'ER2': 'ɝ',       # bird (stressed vs. unstressed)
    'IH': 'ɪ', 'IH0': 'ɪ', 'IH1': 'ɪ', 'IH2': 'ɪ',       # bit
    'IY': 'i', 'IY0': 'i', 'IY1': 'i', 'IY2': 'i',       # beat
    'UH': 'ʊ', 'UH0': 'ʊ', 'UH1': 'ʊ', 'UH2': 'ʊ',       # book
    'UW': 'u', 'UW0': 'u', 'UW1': 'u', 'UW2': 'u',       # boot

    # Vowels (Diphthongs)
    'AW': 'aʊ', 'AW0': 'aʊ', 'AW1': 'aʊ', 'AW2': 'aʊ',     # bout
    'AY': 'aɪ', 'AY0': 'aɪ', 'AY1': 'aɪ', 'AY2': 'aɪ',     # bite
    'EY': 'eɪ', 'EY0': 'eɪ', 'EY1': 'eɪ', 'EY2': 'eɪ',     # bait
    'OW': 'oʊ', 'OW0': 'oʊ', 'OW1': 'oʊ', 'OW2': 'oʊ',     # boat
    'OY': 'ɔɪ', 'OY0': 'ɔɪ', 'OY1': 'ɔɪ', 'OY2': 'ɔɪ',     # boy

    # Consonants
    'P': 'p', 'B': 'b', 'T': 't', 'D': 'd', 'K': 'k', 'G': 'g',
    'CH': 'tʃ', 'JH': 'dʒ', 'F': 'f', 'V': 'v', 'TH': 'θ', 'DH': 'ð',
    'S': 's', 'Z': 'z', 'SH': 'ʃ', 'ZH': 'ʒ', 'HH': 'h', 'M': 'm',
    'N': 'n', 'NG': 'ŋ', 'L': 'l', 'R': 'ɹ', 'W': 'w', 'Y': 'j',

    # Syllabic Consonants (less common, but useful for completeness)
    'EM': 'm̩', 'EN': 'n̩', 'EL': 'l̩', 'NX': 'ɾ̃',
}

class GOPService:
    _instance = None
    _processor = None
    _model = None
    _g2p = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating GOPService instance and loading models...")
            cls._instance = super(GOPService, cls).__new__(cls)
            try:
                print(f"Loading processor from: {GOP_MODEL_NAME}")
                cls._processor = Wav2Vec2Processor.from_pretrained(GOP_MODEL_NAME)
                print(f"Loading model from: {GOP_MODEL_NAME}")
                cls._model = Wav2Vec2ForCTC.from_pretrained(GOP_MODEL_NAME)
                cls._g2p = G2p()
                print("GOP models and converters loaded successfully.")
                if torch.cuda.is_available():
                    cls._model = cls._model.to('cuda')
                    print("GOP model moved to GPU.")
            except Exception as e:
                print(f"Error loading GOP models: {e}")
                raise RuntimeError(f"Failed to load GOP models: {e}") from e
        return cls._instance

    def get_phoneme_scores(self, audio_bytes: bytes, reference_text: str) -> list:
        if not all([self._processor, self._model, self._g2p]):
            raise Exception("GOP service is not initialized correctly.")

        arpabet_phonemes = self._g2p(reference_text)
        arpabet_phonemes = [p for p in arpabet_phonemes if p.strip() and p not in [' ', ',', '.', '!', '?']]
        print(f"Step 1: Generated ARPAbet phonemes: {arpabet_phonemes}")

        ipa_phonemes_str = " ".join([ARPABET_TO_IPA.get(p, '') for p in arpabet_phonemes])
        ipa_phonemes = [char for char in ipa_phonemes_str if char != ' ']
        print(f"Step 2: Converted to IPA phonemes: {ipa_phonemes}")

        # --- MODIFIED PART 1: Get the full processed input object ---
        processed_input, _ = self._process_audio(audio_bytes)
        
        if torch.cuda.is_available():
            # .to(device) works on the entire batch object
            processed_input = processed_input.to('cuda')

        with torch.no_grad():
            # --- MODIFIED PART 2: Use ** to unpack the object for the model call ---
            logits = self._model(**processed_input).logits[0]
        
        scores = self._calculate_gop(logits, ipa_phonemes)
        normalized_scores = self._normalize_scores(scores)
        result = self._map_scores_to_arpabet(arpabet_phonemes, ipa_phonemes_str, normalized_scores)
        print(f"Final phoneme scores: {result}")
        return result
    
    def _map_scores_to_arpabet(self, arpabet_list, ipa_str, scores):
        result = []
        score_cursor = 0
        ipa_words = ipa_str.split(' ')
        if len(arpabet_list) != len(ipa_words):
             print("Warning: Mismatch between ARPAbet and IPA word counts. Falling back to simple pairing.")
             return [{"phoneme": arp, "score": score} for arp, score in zip(arpabet_list, scores)]
        for i, arp_phoneme in enumerate(arpabet_list):
            ipa_word = ipa_words[i]
            num_chars = len(ipa_word)
            word_scores = scores[score_cursor : score_cursor + num_chars]
            avg_score = round(sum(word_scores) / len(word_scores), 1) if word_scores else 2.5
            result.append({"phoneme": arp_phoneme, "score": avg_score})
            score_cursor += num_chars
        return result

    def _process_audio(self, audio_bytes: bytes):
        try:
            command = ['ffmpeg', '-i', '-', '-f', 's16le', '-ac', '1', '-ar', '16000', '-']
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            wav_bytes, err = proc.communicate(input=audio_bytes)
            if proc.returncode != 0:
                raise IOError(f"ffmpeg failed to decode audio: {err.decode()}")
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found. Please ensure it's installed and in your system's PATH.")
        
        print("Audio decoded and processed successfully.")
        
        # --- MODIFIED: Return the entire processor output object, not just .input_values ---
        processed_input = self._processor(audio_np, sampling_rate=16000, return_tensors="pt")
        return processed_input, 16000

    def _calculate_gop(self, logits, ipa_phonemes):
        vocab = self._processor.tokenizer.get_vocab()
        phoneme_ids = [vocab.get(p) for p in ipa_phonemes]
        if any(pid is None for pid in phoneme_ids):
            unknown_phonemes = [p for p, pid in zip(ipa_phonemes, phoneme_ids) if pid is None]
            print(f"Warning: IPA Phoneme(s) {unknown_phonemes} not in model vocabulary. They will be ignored.")
            valid_phonemes = [(p, pid) for p, pid in zip(ipa_phonemes, phoneme_ids) if pid is not None]
            ipa_phonemes = [p for p, pid in valid_phonemes]
            phoneme_ids = [pid for p, pid in valid_phonemes]

        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
        scores = []
        current_frame = 0
        for pid in phoneme_ids:
            best_score_for_phoneme = -float('inf')
            best_frame = current_frame
            search_end = min(current_frame + 150, len(log_probs))
            if current_frame >= len(log_probs):
                scores.append(-float('inf'))
                continue
            for i in range(current_frame, search_end):
                score = log_probs[i, pid].item()
                if score > best_score_for_phoneme:
                    best_score_for_phoneme = score
                    best_frame = i
            scores.append(best_score_for_phoneme)
            current_frame = best_frame + 1
        return scores

    def _normalize_scores(self, scores: list, v_min=-10.0, v_max=0.0) -> list:
        clamped_scores = [max(v_min, min(s, v_max)) for s in scores]
        normalized = [1 + 4 * (s - v_min) / (v_max - v_min) for s in clamped_scores]
        return [round(n, 1) for n in normalized]