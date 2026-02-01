"""vLLM Orchestrator Service - Dynamic parallelism configuration.

Provides automatic TP/PP sizing for vLLM inference based on available hardware.
Integrates with node registry for resource discovery across the P2P network.

Usage:
    from pmoves.services.vllm_orchestrator import (
        create_vllm_config,
        VLLMOrchestrator,
        run_orchestrator,
    )

    # Create configuration for specific hardware
    config = create_vllm_config(
        model_name="llama-3-70b",
        available_gpus=4,
        vram_per_gpu_mb=24576,
    )
    print(f"TP size: {config.tensor_parallel_size}")

    # Run as standalone service
    await run_orchestrator(nats_url="nats://localhost:4222")

Supported Models:
    - llama-3-8b, llama-3-70b
    - mixtral-8x7b, mixtral-8x22b
    - gemma-2-27b
    - qwen-2-72b
"""

from .config import (
    VLLMConfig,
    ModelConfig,
    MODEL_CONFIGS,
    ParallelismStrategy,
    create_vllm_config,
    calculate_optimal_tp_size,
    calculate_optimal_pp_size,
)

from .server import VLLMOrchestrator, run_orchestrator

__all__ = [
    "VLLMConfig",
    "ModelConfig",
    "MODEL_CONFIGS",
    "ParallelismStrategy",
    "create_vllm_config",
    "calculate_optimal_tp_size",
    "calculate_optimal_pp_size",
    "VLLMOrchestrator",
    "run_orchestrator",
]
