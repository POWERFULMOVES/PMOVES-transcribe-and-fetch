"""
PMOVES Monitoring with Langfuse Python SDK Example

This example demonstrates how to use the updated PMOVES monitoring system
with the Langfuse Python SDK for comprehensive LLM observability.

Features demonstrated:
- @observe decorator for automatic tracing
- OpenAI integration with Langfuse
- Custom metrics tracking
- Structured logging with trace correlation
- Error handling and scoring
"""

import os
import asyncio
from typing import List, Dict, Any

# Set up environment variables for Langfuse
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-your-public-key"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-your-secret-key"
os.environ["LANGFUSE_HOST"] = "http://localhost:3002"  # or https://cloud.langfuse.com

# Import monitoring components
from monitoring.pmoves_monitoring import (
    init_monitoring,
    observe_llm_call,
    observe_agent_operation,
    get_monitor,
)
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai  # Use Langfuse OpenAI integration


# Initialize monitoring
monitor = init_monitoring(
    service_name="pmoves-example",
    langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    langfuse_host=os.getenv("LANGFUSE_HOST"),
)


# Example 1: Simple LLM call with @observe decorator
@observe()
def simple_llm_call(prompt: str) -> str:
    """Simple LLM call with automatic tracing"""
    monitor.log_info("Making simple LLM call", prompt_length=len(prompt))

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
    )

    result = response.choices[0].message.content
    monitor.log_info("LLM call completed", response_length=len(result))

    return result


# Example 2: Complex agent operation with custom metadata
@observe_agent_operation("multimodal", "analyze_content")
def analyze_content(content: str, content_type: str) -> Dict[str, Any]:
    """Analyze content with agent operation tracking"""

    # Update trace with custom metadata
    monitor.update_current_trace(
        name="Content Analysis Pipeline",
        user_id="user-123",
        session_id="session-456",
        tags=["content-analysis", content_type],
    )

    # Update current observation
    monitor.update_current_observation(
        name=f"Analyze {content_type} Content",
        metadata={
            "content_type": content_type,
            "content_length": len(content),
            "analysis_version": "v2.1",
        },
    )

    monitor.log_info(
        "Starting content analysis",
        content_type=content_type,
        content_length=len(content),
    )

    # Simulate analysis
    analysis_result = {
        "sentiment": "positive",
        "topics": ["technology", "innovation"],
        "confidence": 0.85,
        "content_type": content_type,
    }

    # Score the analysis
    monitor.score_current_observation(
        name="analysis_quality",
        value=analysis_result["confidence"],
        comment=f"Analysis confidence for {content_type} content",
    )

    monitor.log_info(
        "Content analysis completed",
        sentiment=analysis_result["sentiment"],
        confidence=analysis_result["confidence"],
    )

    return analysis_result


# Example 3: Multi-step LLM pipeline with nested observations
@observe()
def multi_step_pipeline(user_query: str) -> str:
    """Multi-step pipeline with nested LLM calls"""

    # Update trace metadata
    monitor.update_current_trace(
        name="Multi-Step LLM Pipeline",
        metadata={"pipeline_version": "v1.0", "query": user_query},
    )

    monitor.log_info("Starting multi-step pipeline", query=user_query)

    # Step 1: Query understanding
    understanding = understand_query(user_query)

    # Step 2: Content generation
    content = generate_content(understanding)

    # Step 3: Content refinement
    refined_content = refine_content(content)

    # Score the overall pipeline
    monitor.score_current_trace(
        name="pipeline_success", value=1.0, comment="Pipeline completed successfully"
    )

    monitor.log_info("Pipeline completed", final_length=len(refined_content))

    return refined_content


@observe(name="Query Understanding")
def understand_query(query: str) -> Dict[str, Any]:
    """Understand user query intent"""
    monitor.log_info("Understanding query", query_length=len(query))

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Analyze the user query and extract intent and entities.",
            },
            {"role": "user", "content": f"Query: {query}"},
        ],
        max_tokens=150,
    )

    understanding = {
        "intent": "information_request",
        "entities": ["technology", "AI"],
        "complexity": "medium",
    }

    monitor.update_current_observation(metadata=understanding, output=understanding)

    return understanding


@observe(name="Content Generation")
def generate_content(understanding: Dict[str, Any]) -> str:
    """Generate content based on understanding"""
    monitor.log_info("Generating content", intent=understanding["intent"])

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generate helpful content based on the query understanding.",
            },
            {
                "role": "user",
                "content": f"Intent: {understanding['intent']}, Entities: {understanding['entities']}",
            },
        ],
        max_tokens=200,
    )

    content = response.choices[0].message.content

    # Track content generation metrics
    monitor.track_content_processing("text", "generation", "success")

    return content


@observe(name="Content Refinement")
def refine_content(content: str) -> str:
    """Refine and improve content"""
    monitor.log_info("Refining content", original_length=len(content))

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Improve and refine the given content for clarity and engagement.",
            },
            {"role": "user", "content": content},
        ],
        max_tokens=250,
    )

    refined = response.choices[0].message.content

    # Score the refinement
    monitor.score_current_observation(
        name="refinement_improvement", value=0.9, comment="Content successfully refined"
    )

    return refined


# Example 4: Error handling with tracing
@observe()
def error_handling_example(should_fail: bool = False) -> str:
    """Demonstrate error handling with tracing"""

    monitor.log_info("Starting operation", should_fail=should_fail)

    try:
        if should_fail:
            raise ValueError("Simulated error for demonstration")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello!"}],
            max_tokens=50,
        )

        result = response.choices[0].message.content

        monitor.score_current_observation(
            name="operation_success",
            value=1.0,
            comment="Operation completed without errors",
        )

        return result

    except Exception as e:
        monitor.log_error("Operation failed", error=str(e), error_type=type(e).__name__)

        monitor.score_current_observation(
            name="operation_success", value=0.0, comment=f"Operation failed: {str(e)}"
        )

        # Track error metrics
        monitor.track_error("operation_error", "error")

        raise


# Example 5: Async function with monitoring
@observe()
async def async_llm_operation(prompts: List[str]) -> List[str]:
    """Async operation with multiple LLM calls"""

    monitor.update_current_trace(
        name="Async LLM Batch Processing", metadata={"batch_size": len(prompts)}
    )

    monitor.log_info("Starting async batch processing", batch_size=len(prompts))

    results = []

    for i, prompt in enumerate(prompts):
        monitor.log_info(f"Processing prompt {i + 1}/{len(prompts)}", prompt_index=i)

        # Each LLM call will be automatically traced
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )

        result = response.choices[0].message.content
        results.append(result)

        # Simulate async delay
        await asyncio.sleep(0.1)

    monitor.log_info("Batch processing completed", total_results=len(results))

    return results


# Example 6: Custom LLM provider integration
@observe_llm_call(name="Custom LLM Call")
def custom_llm_call(
    prompt: str, provider: str = "custom", model: str = "custom-model"
) -> str:
    """Example of integrating a custom LLM provider"""

    monitor.log_info("Making custom LLM call", provider=provider, model=model)

    # Update observation with LLM-specific metadata
    monitor.update_current_observation(
        model=f"{provider}/{model}",
        metadata={"provider": provider, "model": model, "custom_parameter": "value"},
    )

    # Simulate custom LLM call
    import time

    time.sleep(0.5)  # Simulate API call

    result = f"Response from {provider} {model}: Hello! This is a simulated response to: {prompt}"

    # Update with usage information
    monitor.update_current_observation(
        input=prompt,
        output=result,
        usage_details={
            "input_tokens": len(prompt.split()),
            "output_tokens": len(result.split()),
            "total_tokens": len(prompt.split()) + len(result.split()),
        },
    )

    # Track metrics
    monitor.track_llm_call(
        provider=provider,
        model=model,
        status="success",
        duration=0.5,
        input_tokens=len(prompt.split()),
        output_tokens=len(result.split()),
        cost=0.001,
    )

    return result


# Main execution example
async def main():
    """Main function demonstrating all examples"""

    print("🚀 Starting PMOVES Monitoring with Langfuse Examples")
    print(f"📊 Trace URL will be available at: {monitor.get_current_trace_url()}")

    try:
        # Example 1: Simple LLM call
        print("\n1️⃣ Simple LLM Call")
        result1 = simple_llm_call("What is artificial intelligence?")
        print(f"Result: {result1[:100]}...")

        # Example 2: Agent operation
        print("\n2️⃣ Agent Operation")
        analysis = analyze_content("This is a great example of AI technology!", "text")
        print(f"Analysis: {analysis}")

        # Example 3: Multi-step pipeline
        print("\n3️⃣ Multi-step Pipeline")
        pipeline_result = multi_step_pipeline("How does machine learning work?")
        print(f"Pipeline result: {pipeline_result[:100]}...")

        # Example 4: Error handling (success case)
        print("\n4️⃣ Error Handling (Success)")
        success_result = error_handling_example(should_fail=False)
        print(f"Success result: {success_result}")

        # Example 4b: Error handling (failure case)
        print("\n4️⃣ Error Handling (Failure)")
        try:
            error_handling_example(should_fail=True)
        except ValueError as e:
            print(f"Caught expected error: {e}")

        # Example 5: Async operations
        print("\n5️⃣ Async Operations")
        async_prompts = [
            "What is Python?",
            "Explain machine learning",
            "What is cloud computing?",
        ]
        async_results = await async_llm_operation(async_prompts)
        print(f"Async results: {len(async_results)} responses generated")

        # Example 6: Custom LLM provider
        print("\n6️⃣ Custom LLM Provider")
        custom_result = custom_llm_call("Hello custom LLM!", "anthropic", "claude-3")
        print(f"Custom result: {custom_result[:100]}...")

        print("\n✅ All examples completed successfully!")
        print(f"📈 Check your Langfuse dashboard for detailed traces")

        # Get current trace URL
        trace_url = monitor.get_current_trace_url()
        if trace_url:
            print(f"🔗 Trace URL: {trace_url}")

    except Exception as e:
        monitor.log_error("Example execution failed", error=str(e))
        print(f"❌ Error: {e}")

    finally:
        # Flush all observations to Langfuse
        print("\n🔄 Flushing observations to Langfuse...")
        monitor.flush()
        print("✅ Flush completed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
