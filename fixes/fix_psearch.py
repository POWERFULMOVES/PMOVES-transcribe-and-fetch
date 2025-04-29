import re

def fix_class_indent(text):
    """Fix class indentation"""
    # Fix TokenCounter class
    pattern = r'class TokenCounter:.*?def __init__\(\):'
    replacement = '''class TokenCounter:
    """Counts tokens for embeddings and LLM generation."""
    
    def __init__(self):'''
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    
    # Fix self.encoders block
    pattern = r'(\s+self\.generation_tokens = \{.*?\'output\': 0\s+\}).*?self\.encoders = \{.*?\}.*?\}'
    replacement = r'\1\n        try:\n            self.encoders = {\n                \'cl100k_base\': get_encoding(\'cl100k_base\'),  # For text-embedding-3-small\n                \'gpt-4\': get_encoding(\'cl100k_base\'),  # For GPT-4 models\n            }'
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    
    # Fix count_generation_tokens method
    pattern = r'def count_generation_tokens.*?try:.*?input_tokens = len.*?return result'
    replacement = '''def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
        """Count tokens for generation (input and output)."""
        result = {'input': 0, 'output': 0}
        
        if not self.encoders:
            return result
            
        try:
            input_tokens = len(self.encoders['gpt-4'].encode(input_text))
            self.generation_tokens['input'] += input_tokens
            result['input'] = input_tokens
        
            if output_text:
                output_tokens = len(self.encoders['gpt-4'].encode(output_text))
                self.generation_tokens['output'] += output_tokens
                result['output'] = output_tokens
        except Exception as e:
            console.print(f"[yellow]Warning: Could not count generation tokens: {str(e)}[/yellow]")
        
        return result'''
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    
    return text

def fix_display_results(text):
    """Fix indentation in display_results function"""
    pattern = r'(console\.print\(Panel\(str\(openai_analysis\), title="OpenAI Analysis", border_style="green", highlight=True\)\))\s+else:'
    replacement = r'\1\n        else:'
    text = re.sub(pattern, replacement, text)
    
    pattern = r'(console\.print\(Panel\(str\(groq_analysis\), title="Groq Analysis", border_style="blue"\)\))\s+else:'
    replacement = r'\1\n        else:'
    text = re.sub(pattern, replacement, text)
    
    return text

def fix_adjust_tier_params(text):
    """Fix indentation in adjust_tier_params function"""
    pattern = r'def adjust_tier_params\(tier\):.*?"""Helper function to adjust parameters for a specific search tier"""\s+params = search_params\.get_params\(tier\)'
    replacement = '''def adjust_tier_params(tier):
    """Helper function to adjust parameters for a specific search tier"""
    params = search_params.get_params(tier)'''
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    
    return text

def main():
    # Read the file
    try:
        with open('backend/app/psearchworking.py', 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        with open('backend/app/psearchworking.py', 'r', encoding='latin-1') as f:
            text = f.read()
    
    # Fix indentation issues
    text = fix_class_indent(text)
    text = fix_display_results(text)
    text = fix_adjust_tier_params(text)
    
    # Write the fixed file
    with open('backend/app/psearchworking.py.fixed3', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print("Fixed file saved as backend/app/psearchworking.py.fixed3")

if __name__ == "__main__":
    main() 