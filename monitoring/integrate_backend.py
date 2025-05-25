#!/usr/bin/env python3
"""
PMOVES Backend Monitoring Integration Script

This script automatically integrates monitoring with your existing PMOVES backend.
It adds the necessary imports and setup code to your main.py file.

Usage:
    python monitoring/integrate_backend.py

This will:
1. Backup your existing main.py
2. Add monitoring imports and setup
3. Create necessary environment variables
4. Provide next steps for testing
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


def backup_file(file_path: Path) -> Path:
    """Create a backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".backup_{timestamp}.py")
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def add_monitoring_to_main(main_py_path: Path):
    """Add monitoring integration to main.py"""

    if not main_py_path.exists():
        print(f"❌ Error: {main_py_path} not found")
        print("Please run this script from the project root directory")
        return False

    # Read the current main.py
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if monitoring is already integrated
    if "setup_backend_monitoring" in content:
        print("✅ Monitoring already integrated in main.py")
        return True

    # Create backup
    backup_file(main_py_path)

    # Add monitoring import after other imports
    import_line = (
        "from monitoring.backend_integration import setup_backend_monitoring\n"
    )

    # Find where to insert the import (after FastAPI import)
    lines = content.split("\n")
    insert_import_at = -1
    insert_setup_at = -1

    for i, line in enumerate(lines):
        # Find where to add import
        if "from fastapi import" in line and insert_import_at == -1:
            insert_import_at = i + 1

        # Find where to add setup (after app creation)
        if "app = FastAPI" in line and insert_setup_at == -1:
            insert_setup_at = i + 1

    if insert_import_at == -1:
        print("❌ Could not find FastAPI import in main.py")
        print("Please add monitoring manually using the integration guide")
        return False

    if insert_setup_at == -1:
        print("❌ Could not find FastAPI app creation in main.py")
        print("Please add monitoring manually using the integration guide")
        return False

    # Insert the import
    lines.insert(insert_import_at, import_line)

    # Insert the setup (adjust index due to previous insertion)
    setup_line = '\n# Initialize monitoring\nmonitor = setup_backend_monitoring(app, "pmoves-backend")\n'
    lines.insert(insert_setup_at + 2, setup_line)

    # Write the modified content
    modified_content = "\n".join(lines)

    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    print(f"✅ Monitoring integration added to {main_py_path}")
    return True


def create_env_template():
    """Create environment template for monitoring"""

    env_template = """# PMOVES Monitoring Configuration
# Copy this to your .env file and update with your actual values

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_HOST=http://localhost:3002

# Monitoring Configuration
REDIS_URL=redis://localhost:6379
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin123

# Optional: Debug mode
LANGFUSE_DEBUG=false
LOG_LEVEL=INFO
"""

    env_file = Path("monitoring/.env.template")
    with open(env_file, "w") as f:
        f.write(env_template)

    print(f"✅ Environment template created: {env_file}")
    print("📝 Please copy this to monitoring/.env and update with your actual values")


def check_dependencies():
    """Check if monitoring dependencies are available"""

    try:
        import prometheus_client
        import structlog
        import redis

        print("✅ Core monitoring dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install monitoring dependencies:")
        print("pip install -r monitoring/requirements.txt")
        return False

    return True


def create_docker_compose_env():
    """Create docker-compose environment file"""

    compose_env = """# Docker Compose Environment for Monitoring
GRAFANA_ADMIN_PASSWORD=admin123
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
LANGFUSE_PORT=3002
REDIS_PORT=6379

# Langfuse Database
POSTGRES_DB=langfuse
POSTGRES_USER=langfuse
POSTGRES_PASSWORD=langfuse123
"""

    env_file = Path("monitoring/monitoring.env")
    with open(env_file, "w") as f:
        f.write(compose_env)

    print(f"✅ Docker Compose environment created: {env_file}")


def main():
    """Main integration function"""

    print("🚀 PMOVES Backend Monitoring Integration")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("backend/app/main.py").exists():
        print("❌ Error: backend/app/main.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first:")
        print("pip install -r monitoring/requirements.txt")
        sys.exit(1)

    # Create monitoring directory if it doesn't exist
    monitoring_dir = Path("monitoring")
    monitoring_dir.mkdir(exist_ok=True)

    # Integrate monitoring with main.py
    main_py_path = Path("backend/app/main.py")
    if add_monitoring_to_main(main_py_path):
        print("✅ Backend integration completed")
    else:
        print("❌ Backend integration failed")
        sys.exit(1)

    # Create environment templates
    create_env_template()
    create_docker_compose_env()

    print("\n🎉 Integration Complete!")
    print("=" * 50)
    print("\nNext Steps:")
    print("1. Update monitoring/.env with your Langfuse credentials")
    print("2. Start the monitoring stack:")
    print("   cd monitoring")
    print("   docker-compose -f docker-compose.monitoring.yml up -d")
    print("3. Restart your backend server")
    print("4. Test the integration:")
    print("   curl http://localhost:8000/health")
    print("   curl http://localhost:8000/metrics")
    print("   curl http://localhost:8000/monitoring/status")
    print("\nDashboards:")
    print("- Grafana: http://localhost:3001 (admin/admin123)")
    print("- Prometheus: http://localhost:9090")
    print("- Langfuse: http://localhost:3002")

    print("\n📚 For detailed integration guide, see:")
    print("monitoring/BACKEND_INTEGRATION_GUIDE.md")


if __name__ == "__main__":
    main()
