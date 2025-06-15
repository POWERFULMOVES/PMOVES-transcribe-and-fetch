"""Multimodal Pipecat pipeline example.

This module demonstrates how a future agent could
assemble a full pipeline with TTS, STT, WebRTC and
basic image frame handling. It uses simple stub
processors so the code can run without optional
dependencies.
"""

import asyncio
from typing import Optional


class Frame:
    """Very small frame placeholder."""
    pass


class TextFrame(Frame):
    def __init__(self, text: str):
        self.text = text


class AudioFrame(Frame):
    def __init__(self, audio: bytes):
        self.audio = audio


class ImageFrame(Frame):
    def __init__(self, image: bytes):
        self.image = image


class FrameProcessor:
    """Minimal processor base class."""

    async def process(self, frame: Frame) -> Optional[Frame]:
        return frame


class STTService(FrameProcessor):
    async def process(self, frame: Frame) -> Optional[Frame]:
        if isinstance(frame, AudioFrame):
            text = "<transcribed>"
            return TextFrame(text)
        return await super().process(frame)


class TTSService(FrameProcessor):
    async def process(self, frame: Frame) -> Optional[Frame]:
        if isinstance(frame, TextFrame):
            return AudioFrame(frame.text.encode())
        return await super().process(frame)


class ImageProcessor(FrameProcessor):
    async def process(self, frame: Frame) -> Optional[Frame]:
        return await super().process(frame)


class WebRTCTransport:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def input(self) -> Frame:
        return await self.queue.get()

    async def output(self, frame: Frame) -> None:
        await self.queue.put(frame)


class Pipeline:
    def __init__(self, processors):
        self.processors = processors

    async def run(self, frame: Frame) -> Optional[Frame]:
        current = frame
        for p in self.processors:
            current = await p.process(current)
            if current is None:
                break
        return current


def create_pipeline() -> Pipeline:
    """Create a simple multimodal pipeline with stub processors."""
    return Pipeline([
        STTService(),
        ImageProcessor(),
        TTSService(),
    ])


async def demo() -> None:
    pipeline = create_pipeline()
    text = TextFrame("hello")
    audio = await pipeline.run(text)
    print("Processed", type(audio).__name__)


if __name__ == "__main__":
    asyncio.run(demo())
