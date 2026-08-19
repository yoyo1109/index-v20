#!/usr/bin/env python3
"""
Extract base64-encoded images from a single-file HTML
and save them as separate files, replacing data URIs with relative paths.
"""
import re
import base64
import os
import hashlib

INPUT = "deploy/index.html"
OUTPUT_DIR = "deploy/assets"
OUTPUT_HTML = "deploy/index.html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT, "r", encoding="utf-8") as f:
    html = f.read()

# Match data URIs: data:image/png;base64,xxxxx or data:image/jpeg;base64,xxxxx etc.
pattern = r'data:image/(png|jpeg|jpg|gif|webp|svg\+xml);base64,([A-Za-z0-9+/=\s]+)'

counter = 0
replacements = {}

def replace_data_uri(match):
    global counter
    full_match = match.group(0)
    if full_match in replacements:
        return replacements[full_match]
    
    img_type = match.group(1)
    b64_data = match.group(2).replace('\n', '').replace('\r', '').replace(' ', '')
    
    # Determine extension
    ext = img_type.replace('+xml', '')
    if ext == 'jpeg':
        ext = 'jpg'
    
    # Use hash for unique filename
    short_hash = hashlib.md5(b64_data[:100].encode()).hexdigest()[:8]
    counter += 1
    filename = f"img_{counter:02d}_{short_hash}.{ext}"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Decode and save
    try:
        img_bytes = base64.b64decode(b64_data)
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        size_kb = len(img_bytes) / 1024
        print(f"  ✅ Extracted: {filename} ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"  ❌ Failed: {filename} - {e}")
        return full_match
    
    relative_path = f"assets/{filename}"
    replacements[full_match] = relative_path
    return relative_path

print(f"📂 Processing {INPUT}...")
print(f"   Original size: {os.path.getsize(INPUT) / 1024 / 1024:.1f} MB")
print()

new_html = re.sub(pattern, replace_data_uri, html)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(new_html)

new_size = os.path.getsize(OUTPUT_HTML) / 1024 / 1024
print(f"\n📊 Results:")
print(f"   Images extracted: {counter}")
print(f"   New HTML size: {new_size:.1f} MB")
print(f"   Assets saved to: {OUTPUT_DIR}/")

if new_size > 25:
    print(f"\n⚠️  HTML is still {new_size:.1f} MB (Cloudflare limit: 25 MB)")
else:
    print(f"\n✅ HTML is now under 25 MB - ready for Cloudflare!")
