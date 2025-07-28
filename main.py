import fitz  # PyMuPDF
import json
import os
import re
from collections import Counter, defaultdict

def clean_text(text):
    """
    Cleans extracted text by removing redundant whitespace and non-standard characters.
    """
    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def analyze_font_styles(blocks):
    font_sizes = []
    style_counts = Counter()

    for block in blocks:
        if block['text'] and len(block['text']) > 2:
            font_sizes.append(block['font_size'])
            style = (block['font_size'], block['is_bold'])
            style_counts[style] += 1

    if not font_sizes:
        return 12.0, []

    body_size = Counter(font_sizes).most_common(1)[0][0]
    potential_heading_styles = {
        style for style, count in style_counts.items()
        if style[0] > body_size or style[1]
    }

    heading_styles = sorted(list(potential_heading_styles), key=lambda x: (-x[0], -x[1]))
    return body_size, heading_styles

def extract_document_structure(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return {"title": "Error processing file", "outline": []}

    all_blocks = []

    for page_num, page in enumerate(doc):
        # ✅ FIXED LINE — removed invalid flag
        page_blocks = page.get_text("dict")["blocks"]
        for block in page_blocks:
            if block.get("type") == 0 and "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = clean_text(span["text"])
                        if text:
                            all_blocks.append({
                                "text": text,
                                "font_size": round(span["size"], 2),
                                "font_name": span["font"],
                                "is_bold": "bold" in span["font"].lower(),
                                "bbox": span["bbox"],
                                "page": page_num + 1,
                            })

    if not all_blocks:
        doc.close()
        return {"title": "No text found", "outline": []}

    body_size, heading_styles = analyze_font_styles(all_blocks)
    style_to_level = {style: f"H{i+1}" for i, style in enumerate(heading_styles)}

    title = "Title Not Found"
    title_candidates = [b for b in all_blocks if b['page'] == 1 and b['font_size'] > body_size]
    if title_candidates:
        title_candidates.sort(key=lambda b: b['bbox'][1])
        first_title_block = title_candidates[0]
        title_text = [first_title_block['text']]
        for i in range(1, len(title_candidates)):
            if (title_candidates[i]['bbox'][1] - title_candidates[i-1]['bbox'][3] < 10 and
                title_candidates[i]['font_size'] == first_title_block['font_size']):
                title_text.append(title_candidates[i]['text'])
            else:
                break
        title = ' '.join(title_text)

    outline = []
    processed_texts = {title}

    for block in all_blocks:
        text = block['text']
        style = (block['font_size'], block['is_bold'])

        if style not in style_to_level or text in processed_texts or len(text) < 3:
            continue
        if block['bbox'][1] > doc[block['page']-1].rect.height * 0.9:
            continue

        level = style_to_level.get(style)

        if re.match(r'^Appendix [A-Z]:', text, re.IGNORECASE):
            level = "H2"
        elif re.match(r'^\d+\.\s', text):
            level = "H3"

        if level:
            outline.append({
                "level": level,
                "text": text,
                "page": block["page"]
            })
            processed_texts.add(text)

    outline.sort(key=lambda x: (
        x['page'],
        [b['bbox'][1] for b in all_blocks if b['text'] == x['text'] and b['page'] == x['page']][0]
    ))

    doc.close()
    return {"title": title, "outline": outline}

def main():
    input_dir = "C:/DOCKER_SAMPLE/DOCKER_SAMPLE/ADOBE_1A/app/input"
    output_dir = "C:/DOCKER_SAMPLE/DOCKER_SAMPLE/ADOBE_1A/app/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            print(f"Processing {filename}...")
            pdf_path = os.path.join(input_dir, filename)
            json_data = extract_document_structure(pdf_path)

            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)

            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                print(f"✅ Successfully created {output_filename}")
            except Exception as e:
                print(f"Error writing JSON for {filename}: {e}")

if __name__ == "__main__":
    main()