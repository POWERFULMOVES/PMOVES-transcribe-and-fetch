from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class FrontendAdapter:
    """Adapts search results for frontend consumption."""
    
    @staticmethod
    def format_result(result: Dict[str, Any], search_method: str) -> Dict[str, Any]:
        """Format a single search result for frontend display."""
        try:
            # Extract video ID from watch URL if present
            video_id = None
            watch_url = result.get('watch_url', '')
            if watch_url and 'watch?v=' in watch_url:
                video_id = watch_url.split('watch?v=')[1].split('&')[0]

            # Format time range
            start_time = result.get('start_time', 'N/A')
            end_time = result.get('end_time', 'N/A')
            
            # Format content
            content = result.get('content', '').strip()
            if len(content) > 200:
                content = content[:197] + '...'

            return {
                'search_method': search_method,
                'similarity': float(result.get('similarity', 0)),
                'video_id': video_id,
                'start_time': start_time,
                'end_time': end_time,
                'content': content,
                'source_file': result.get('source_file', 'N/A'),
                'line': result.get('line', 'N/A'),
                'watch_url': watch_url,
                'source': result.get('source', 'unknown'),
                'styling': {
                    'content': 'text-green-500',
                    'similarity': 'text-cyan-500',
                    'source': 'text-yellow-500',
                    'timestamp': 'text-blue-500'
                }
            }
        except Exception as e:
            print(f"Error formatting result: {str(e)}")
            return None

    @staticmethod
    def format_search_results(results: List[Dict[str, Any]], search_method: str) -> List[Dict[str, Any]]:
        """Format a list of search results for frontend display."""
        formatted_results = []
        for result in results:
            formatted_result = FrontendAdapter.format_result(result, search_method)
            if formatted_result:
                formatted_results.append(formatted_result)
        return formatted_results

    @staticmethod
    def create_sse_message(data: Any, message_type: str) -> str:
        """Create a properly formatted SSE message."""
        message = {
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
        }

        if message_type == 'results':
            message['results'] = data
        elif message_type == 'log':
            message['message'] = data
        elif message_type == 'token_usage':
            message['usage'] = data
        elif message_type == 'error':
            message['message'] = str(data)
        elif message_type == 'complete':
            message['message'] = 'Search complete'
        elif message_type in ['ai_response_groq', 'ai_response_openai']:
            message['analysis'] = {
                'provider': message_type.replace('ai_response_', ''),
                'content': data
            }
        else:
            message['data'] = data

        return f"data: {json.dumps(message)}\n\n"

    @staticmethod
    def format_token_usage(token_counter) -> Dict[str, int]:
        """Format token usage statistics for frontend display."""
        stats = token_counter.get_stats()
        return {
            'sent': stats['embedding_tokens'] + stats['generation_tokens']['input'],
            'received': stats['generation_tokens']['output']
        }

    @staticmethod
    def format_error(error: Exception) -> str:
        """Format error message for frontend display."""
        return f"Error: {str(error)}"

    @staticmethod
    def create_search_summary(results: List[Dict[str, Any]], search_method: str) -> Dict[str, Any]:
        """Create a summary of search results for frontend display."""
        if not results:
            return {
                'method': search_method,
                'count': 0,
                'top_match': None
            }

        # Sort results by similarity
        sorted_results = sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)
        top_match = sorted_results[0] if sorted_results else None

        return {
            'method': search_method,
            'count': len(results),
            'top_match': {
                'similarity': top_match.get('similarity', 0) if top_match else 0,
                'content': top_match.get('content', '') if top_match else ''
            }
        }
