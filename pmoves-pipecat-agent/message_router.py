class MessageRouter:
    """Simple message router based on call words."""

    def __init__(self, call_word: str):
        self.call_word = call_word

    def extract_prompt(self, text: str) -> str | None:
        if self.call_word in text:
            return text.split(self.call_word, 1)[-1].strip()
        return None

