#!/bin/bash
echo "Updating project requirements files using uv..."

echo ""
echo "Updating root requirements.txt..."
uv pip freeze > requirements.txt

echo ""
echo "Updating backend requirements.txt..."
cd backend
uv pip freeze > requirements.txt
cd ..

echo ""
echo "Updating PMOVES Supabase requirements.txt..."
cd "PMOVES Supabase"
uv pip freeze > requirements.txt
cd ..

echo ""
echo "Requirements files updated successfully!" 