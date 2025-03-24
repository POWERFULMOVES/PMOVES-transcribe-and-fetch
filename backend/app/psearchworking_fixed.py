class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    
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
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize encoders: {str(e)}[/yellow]")
            console.print("[yellow]Token counting will be disabled.[/yellow]")
            self.encoders = None
    
    def count_embedding_tokens(self, text: str) -> int:
        """Count tokens for embedding."""
        if not self.encoders:
            return 0
            
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            console.print(f"[yellow]Warning: Could not count embedding tokens: {str(e)}[/yellow]")
            return 0
    
    def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
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
    
    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': self.embedding_tokens + sum(self.generation_tokens.values())
        } 

class ModelSelector:
    """Manages model selection and execution for different AI providers."""
    
    # (Assume other class methods and variables are defined earlier)
    
    @staticmethod
    def generate_analysis(text: str, provider: str = 'openai') -> str:
        """Generate analysis from search results text using the specified provider."""
        # Assume system_prompt, token_counter, and clients are defined elsewhere
        
        # Count input tokens for stats
        token_counter.count_generation_tokens(system_prompt + text)
        
        if provider == 'openai':
            try:
                response = openai_client.chat.completions.create(
                    model=ModelSelector.get_chat_model('openai'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=2000  # Limit response size
                )
                output_text = response.choices[0].message.content
                # Count output tokens
                token_counter.count_generation_tokens("", output_text)
                return output_text
            except Exception as e:
                error_msg = str(e)
                if "maximum context length" in error_msg or "context_length_exceeded" in error_msg:
                    console.print(f"[red]OpenAI context length exceeded. Try reducing the number of search results.[/red]")
                    return "Error: The amount of search result data exceeds OpenAI's token limits. Please try a more specific search or reduce the number of results."
                else:
                    raise
            
        elif provider == 'groq':
            try:
                response = groq_client.chat.completions.create(
                    model=ModelSelector.get_chat_model('groq'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=1000  # Limit response size even more for Groq
                )
                output_text = response.choices[0].message.content
                # Count output tokens
                token_counter.count_generation_tokens("", output_text)
                return output_text
            except Exception as e:
                error_msg = str(e)
                if "Request too large" in error_msg or "rate_limit_exceeded" in error_msg:
                    console.print(f"[red]Groq token limit exceeded. Try reducing the number of search results.[/red]")
                    return "Error: The amount of search result data exceeds Groq's token limits. Please try a more specific search or reduce the number of results."
                else:
                    raise 

def search_all(query, max_results=30, skip_prompts=False, run_analysis=True):
    """
    Perform a comprehensive search across all tiers with the given query.
    Returns combined results from all search tiers.
    """
    # Assume variable initialization happens earlier
    
    # Step 1: Keyword search
    progress.update(search_task, advance=1, description="Running keyword search...")
    keyword_results = keyword_search(query, params['overview']['max_results'])
    
    # Add keyword results to the combined set, tracking IDs to avoid duplicates
    for result in keyword_results:
        result_id = f"{result.content_id}_{result.segment_id or '0'}"
        if result_id not in seen_ids:
            all_results.append(result)
            seen_ids.add(result_id)
    
    # Step 2: Fine-grained search (high threshold, high content weight)
    progress.update(search_task, advance=1, description="Running fine-grained search...") 

# Fragment of a function that adjusts parameters
def adjust_parameter(tier, param_name):
    """Helper function to adjust a specific parameter"""
    # Get current value
    current_value = params[param_name]
    value_type = type(current_value)
    
    if param_name.endswith("threshold") or param_name.endswith("weight"):
        console.print(f"\n[cyan]Enter new value for {param_name} (0.0-1.0, current: {current_value}):[/cyan]")
        try:
            new_value = float(input().strip() or str(current_value))
            if 0 <= new_value <= 1:
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            else:
                console.print("[yellow]Value must be between 0 and 1. No changes made.[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]")
            
    elif param_name.endswith("percentage"):
        console.print(f"\n[cyan]Enter new value for {param_name} (0.0-1.0, current: {current_value}):[/cyan]")
        try:
            new_value = float(input().strip() or str(current_value))
            if 0 <= new_value <= 1:
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            else:
                console.print("[yellow]Value must be between 0 and 1. No changes made.[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]") 

def adjust_tier_params(tier):
    """Helper function to adjust parameters for a specific search tier"""
    params = search_params.get_params(tier)
    
    console.print(f"\n[bold cyan]{tier.title()} Parameters[/bold cyan]")
    console.print(f"[cyan]Current values:[/cyan]")
    
    # Display current values
    for param, value in params.items():
        console.print(f"- {param}: {value}")
    
    # List parameters
    valid_params = list(params.keys())
    for i, param in enumerate(valid_params, 1):
        console.print(f"{i}. [bold]{param}[/bold]: {params[param]}")
    
    # Get parameter choice
    param_choice = input("\nSelect parameter to adjust (number or name, blank to cancel): ").strip()
    
    if not param_choice:
        return
    
    # Get parameter name
    param_name = None
    if param_choice.isdigit() and 1 <= int(param_choice) <= len(valid_params):
        param_name = valid_params[int(param_choice) - 1]
    elif param_choice in valid_params:
        param_name = param_choice
    
    if not param_name:
        console.print("[yellow]Invalid parameter. Please try again.[/yellow]")
        return
            
    # Get new value
    current_value = params[param_name]
    value_type = type(current_value)
    
    if param_name.endswith("threshold") or param_name.endswith("weight"):
        console.print(f"\n[cyan]Enter new value for {param_name} (0.0-1.0, current: {current_value}):[/cyan]")
        try:
            new_value = float(input().strip() or str(current_value))
            if 0 <= new_value <= 1:
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            else:
                console.print("[yellow]Value must be between 0 and 1. No changes made.[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]")
            
    elif param_name.endswith("percentage"):
        console.print(f"\n[cyan]Enter new value for {param_name} (0.0-1.0, current: {current_value}):[/cyan]")
        try:
            new_value = float(input().strip() or str(current_value))
            if 0 <= new_value <= 1:
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            else:
                console.print("[yellow]Value must be between 0 and 1. No changes made.[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]")
    
    elif param_name.endswith("max_results"):
        console.print(f"\n[cyan]Enter new value for {param_name} (1-100, current: {current_value}):[/cyan]")
        try:
            new_value = int(input().strip() or str(current_value))
            if 1 <= new_value <= 100:
                # Update parameter
                search_params.update_params(tier, **{param_name: new_value})
                console.print(f"[green]Updated {param_name} to {new_value}[/green]")
            else:
                console.print("[yellow]Value must be between 1 and 100. No changes made.[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]")
    
    else:
        console.print(f"\n[cyan]Enter new value for {param_name} (current: {current_value}):[/cyan]")
        try:
            new_value_str = input().strip() or str(current_value)
            # Try to convert to the same type as current value
            if value_type == bool:
                new_value = new_value_str.lower() in ('true', 'yes', 'y', '1')
            else:
                new_value = value_type(new_value_str)
            
            # Update parameter
            search_params.update_params(tier, **{param_name: new_value})
            console.print(f"[green]Updated {param_name} to {new_value}[/green]")
        except ValueError:
            console.print("[yellow]Invalid value. No changes made.[/yellow]")

def load_preset_menu():
    """Helper function to load a preset"""
    console.print("\n[bold cyan]Available Presets[/bold cyan]")
    presets = search_params.list_presets()
    
    if not presets:
        console.print("[yellow]No saved presets found.[/yellow]")
        return
    
    for i, preset in enumerate(presets, 1):
        console.print(f"{i}. [bold]{preset}[/bold]")
    
    preset_choice = input("\nSelect preset to load (number or name, blank to cancel): ").strip()
    
    if not preset_choice:
        return
    
    # Get preset name
    preset_name = None
    if preset_choice.isdigit() and 1 <= int(preset_choice) <= len(presets):
        preset_name = presets[int(preset_choice) - 1]
    elif preset_choice in presets:
        preset_name = preset_choice
    
    if not preset_name:
        console.print("[yellow]Invalid preset. Please try again.[/yellow]")
        return
    
    # Load the preset
    success = search_params.load_preset(preset_name)
    if success:
        console.print(f"[green]Loaded preset '{preset_name}'[/green]")
    else:
        console.print(f"[red]Failed to load preset '{preset_name}'[/red]") 

def save_preset_menu():
    """Helper function to save a preset"""
    console.print("\n[bold cyan]Save Current Parameters as Preset[/bold cyan]")
    
    # Get preset name
    preset_name = input("Enter preset name (blank to cancel): ").strip()
    
    if not preset_name:
        return
    
    # Confirm if preset exists
    if preset_name in search_params.list_presets():
        confirm = input(f"Preset '{preset_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            console.print("[yellow]Save cancelled.[/yellow]")
            return
    
    # Save preset
    search_params.save_preset(preset_name)
    console.print(f"[green]Saved preset '{preset_name}'[/green]")

if __name__ == "__main__":
    main() 