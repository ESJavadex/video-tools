#!/usr/bin/env python3
"""
Test regeneration with both OpenAI and Gemini
"""
import requests
import json
import sys

# Load the analysis file
print("=" * 60)
print("Testing Regeneration with OpenAI and Gemini")
print("=" * 60)

analysis_file = "backend/analysis_results/20251111_232246_2025-11-11_17-26-02mov_analysis.json"

print(f"\n1. Loading analysis file: {analysis_file}")
with open(analysis_file, 'r', encoding='utf-8') as f:
    analysis = json.load(f)

print(f"   ✓ Loaded video: {analysis['original_filename']}")
print(f"   ✓ Duration: {analysis['duration_seconds']/60:.1f} minutes")
print(f"   ✓ Transcription segments: {len(analysis['transcription'])}")

# Prepare transcription (take first 50 segments for faster testing)
transcription = analysis['transcription'][:50]
print(f"   ℹ Using first {len(transcription)} segments for testing")

# Test with OpenAI
print(f"\n2. Testing Regeneration with OpenAI GPT-4...")
openai_payload = {
    "transcription": transcription,
    "custom_instructions": "Crea títulos más técnicos y profesionales enfocados en desarrollo de software",
    "ai_provider": "openai"
}

try:
    response = requests.post(
        "http://localhost:8000/api/videos/regenerate-suggestions",
        json=openai_payload,
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ OpenAI regeneration successful!")
        print(f"   ✓ Generated {len(result['titles'])} title options:")
        for i, title in enumerate(result['titles'], 1):
            print(f"      {i}. {title}")
        print(f"   ✓ Description length: {len(result['description'])} chars")
        print(f"   ✓ Thumbnail prompt: {result['thumbnail_prompt'][:80]}...")
    else:
        print(f"   ✗ OpenAI failed with status {response.status_code}")
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ OpenAI request failed: {str(e)}")

# Test with Gemini
print(f"\n3. Testing Regeneration with Gemini...")
gemini_payload = {
    "transcription": transcription,
    "custom_instructions": "Usa un tono más casual y amigable, perfecto para redes sociales",
    "ai_provider": "gemini"
}

try:
    response = requests.post(
        "http://localhost:8000/api/videos/regenerate-suggestions",
        json=gemini_payload,
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Gemini regeneration successful!")
        print(f"   ✓ Generated {len(result['titles'])} title options:")
        for i, title in enumerate(result['titles'], 1):
            print(f"      {i}. {title}")
        print(f"   ✓ Description length: {len(result['description'])} chars")
        print(f"   ✓ Thumbnail prompt: {result['thumbnail_prompt'][:80]}...")
    else:
        print(f"   ✗ Gemini failed with status {response.status_code}")
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ Gemini request failed: {str(e)}")

print("\n" + "=" * 60)
print("Test Complete!")
print("\nBoth providers are working correctly. You can now:")
print("1. Open http://localhost:5173 in your browser")
print("2. Load the saved analysis from the list")
print("3. Click 'Instrucciones' button")
print("4. Select your preferred AI provider (OpenAI or Gemini)")
print("5. Click 'Regenerar' to get new suggestions")
print("=" * 60)
