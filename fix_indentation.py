import re

def fix_indentation_in_file(file_path, output_path):
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix indentation issues
    
    # 1. Fix the TokenCounter class
    content = re.sub(
        r'class TokenCounter:.*?def __init__\(\).*?self\.generation_tokens = \{.*?\'output\': 0\s+\}.*?self\.encoders = \{.*?\}.*?\}.*?except Exception as e:',
        '''class TokenCounter:
    """Counts tokens for embeddings and LLM generation."""
    
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {
            'input': 0,
            'output': 0
        }
        try:
            self.encoders = {
                'cl100k_base': get_encoding('cl100k_base'),  # For text-embedding-3-small
                'gpt-4': get_encoding('cl100k_base'),  # For GPT-4 models
            }
        except Exception as e:''',
        content, 
        flags=re.DOTALL
    )
    
    # 2. Fix the count_generation_tokens method
    content = re.sub(
        r'def count_generation_tokens.*?return result\s+\}\s+',
        '''def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
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
        
        return result
    
    ''',
        content,
        flags=re.DOTALL
    )
    
    # 3. Fix try/except blocks in ModelSelector.generate_analysis
    content = re.sub(
        r'(if provider == \'openai\':)\s+try:\s+(response = openai_client\.chat\.completions\.create\(.*?)\s+except Exception as e:',
        r'\1\n            try:\n                \2\n            except Exception as e:',
        content, 
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'(elif provider == \'groq\':)\s+try:\s+(response = groq_client\.chat\.completions\.create\(.*?)\s+except Exception as e:',
        r'\1\n            try:\n                \2\n            except Exception as e:',
        content,
        flags=re.DOTALL
    )
    
    # Write the fixed content to the output file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed indentation issues and saved to {output_path}")

if __name__ == "__main__":
    fix_indentation_in_file('backend/app/psearchworking.py', 'backend/app/psearchworking.py.fixed2') 