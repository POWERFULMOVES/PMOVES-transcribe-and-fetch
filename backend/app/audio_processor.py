import os
import tempfile
import logging
from typing import Generator, Tuple
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile
import torch

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def prepare_audio(self, audio_path: str) -> str:
        """
        Prepare audio file for transcription by normalizing and optimizing it
        Returns path to processed audio file
        """
        try:
            logger.info(f"Preparing audio file: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Normalize audio levels
            normalized_audio = self._normalize_audio(audio)
            
            # Resample if needed
            if audio.frame_rate != self.target_sample_rate:
                normalized_audio = normalized_audio.set_frame_rate(self.target_sample_rate)

            # Export to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                normalized_audio.export(
                    temp_file.name,
                    format='wav',
                    parameters=[
                        "-ac", "1",
                        "-ar", str(self.target_sample_rate),
                        "-acodec", "pcm_s16le"
                    ]
                )
                logger.info(f"Prepared audio saved to: {temp_file.name}")
                return temp_file.name

        except Exception as e:
            logger.error(f"Error preparing audio: {str(e)}")
            raise

    def chunk_audio(self, audio_path: str, chunk_duration_ms: int = 30000) -> Generator[Tuple[str, float, float], None, None]:
        """
        Generate optimized chunks of audio with overlap
        Yields: (chunk_path, start_time, end_time)
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            total_duration = len(audio)
            overlap_ms = 1000  # 1 second overlap
            
            for start_ms in range(0, total_duration, chunk_duration_ms - overlap_ms):
                end_ms = min(start_ms + chunk_duration_ms, total_duration)
                chunk = audio[start_ms:end_ms]
                
                # Skip chunks that are too short
                if len(chunk) < 1000:  # Skip chunks shorter than 1 second
                    continue
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    chunk.export(
                        temp_file.name,
                        format='wav',
                        parameters=[
                            "-ac", "1",
                            "-ar", str(self.target_sample_rate),
                            "-acodec", "pcm_s16le"
                        ]
                    )
                    
                    yield (
                        temp_file.name,
                        start_ms / 1000.0,  # Convert to seconds
                        end_ms / 1000.0
                    )

        except Exception as e:
            logger.error(f"Error chunking audio: {str(e)}")
            raise

    def _normalize_audio(self, audio: AudioSegment) -> AudioSegment:
        """Normalize audio levels"""
        try:
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            
            # Calculate current peak
            peak = np.abs(samples).max()
            if peak == 0:
                return audio
            
            # Calculate scaling factor for -1dB headroom
            target_peak = int(0.89 * 32767)  # -1dB with 16-bit headroom
            scaling_factor = target_peak / peak
            
            # Apply scaling
            normalized_samples = (samples * scaling_factor).astype(np.int16)
            
            # Convert back to AudioSegment
            return AudioSegment(
                normalized_samples.tobytes(),
                frame_rate=audio.frame_rate,
                sample_width=2,
                channels=1
            )

        except Exception as e:
            logger.error(f"Error normalizing audio: {str(e)}")
            raise

    def cleanup_temp_files(self, *file_paths: str):
        """Clean up temporary audio files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Error cleaning up file {file_path}: {str(e)}")