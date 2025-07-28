# PDF Structural Outline Extractor

## Overview

A robust Python-based tool for machine comprehension of PDFs: this solution reads any provided PDF file and automatically extracts a **structured document outline** — including the Title and all Heading levels (H1, H2, H3) — ready for semantic search, recommendation, or downstream AI processing. Output is a clean, machine-friendly JSON.

---

## Directory Layout

ROOT/
│_app
  ├─ input/
  │ └─ *.pdf # Place your input PDFs here
  │
  ├─ output/
  │  └─ *.json # Extracted outline (per-PDF) will be saved here
│
├─ main.py # (Your extractor implementation)
└─ Dockerfile # For containerization

text

---

## Installation & Usage

### 1. Prerequisites

- [Docker](https://www.docker.com/get-started/)
- You do **not** need to install Python or dependencies locally if using Docker.

---

### 2. Build the Docker Image

From your project folder:

docker build --platform linux/amd64 -t mysolution:abc124 .

text

---

### 3. Prepare Input

- Place all your PDFs to extract in the `input/` directory.
- Example: `C:/DOCKER_SAMPLE/ADOBE_1A/app/input/yourfile.pdf`
- Sample input has been provided.

---

### 4. Run the Pipeline

Execute:

docker run --rm
-v C:/DOCKER_SAMPLE/ADOBE_1A/app/input:/app/input
-v C:/DOCKER_SAMPLE/ADOBE_1A/app/output:/app/output
--network none
mysolution:abc124

text

- Adjust the `-v` mount paths for your directory structure.

---

### 5. View Results

- For every `.pdf` file in `input/`, you’ll see a corresponding `.json` in `output/`.
- Each `.json` describes:
    - The **document title**
    - A list of all outline headings, each with its level (`H1`/`H2`/`H3`), text, and page number

---

## Input and Output Format

### Input

One or more PDF files (up to 50 pages each) in the `input/` directory.

### Output

For `example.pdf`:
{
"title": "Understanding AI",
"outline": [
{ "level": "H1", "text": "Introduction", "page": 1 },
{ "level": "H2", "text": "What is AI?", "page": 2 },
{ "level": "H3", "text": "History of AI", "page": 3 }
]
}

text

---

## Algorithm & Code Structure

_All logic is contained in `main.py` for easy inspection:_

- **PDF Parsing:**  
  Uses [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/en/latest/) to extract lines, spans, and font info from every page.

- **Text Cleaning:**  
  Cleans up smart quotes, apostrophes, and collapses whitespace for consistency.

- **Font Style Analysis:**  
  - Collects font sizes & boldness across all text blocks.
  - Determines the **body text size** (most common size).
  - Any text with a larger font or bold is considered a **potential heading**.
  - All unique "heading styles" are sorted & mapped to levels (`H1`, `H2`, `H3`, etc).

- **Title Extraction:**  
  Picks the largest, uppermost bold text(s) on page 1 as Title — combines those on the same line.

- **Outline Building:**  
  For each candidate heading:
    - Assigns the appropriate `H1`/`H2`/`H3` based on style ranking.
    - Avoids low-value/duplicate headings, content at the very bottom, or headings shorter than 3 chars.
    - Applies extra handling for patterns like `"Appendix A:"` → H2 and `"1. "` → H3.
    - Captures the heading’s text, level, and original page number in order.

---

## Technologies Used

- Python 3.x
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) for structural PDF access.
- Standard library: `os`, `re`, `json`, `collections`
- Docker for guaranteed reproducibility and isolation.

---

## Security & Best Practices

- Runs with `--network none` for maximum container isolation.
- No outbound connections, no data leaving your system.
- Suitable for sensitive or proprietary documents.

---

## Troubleshooting

- Ensure input/output folders exist and are correctly mapped to the container.
- For very complex or image-based/scanned PDFs, heading detection may be limited.
- Tune font and heading heuristics in `main.py` for challenging new formats.

---

## Credits

Raj Gaurav Tiwari 9667782966
Abhay Kumar 7857923401

---

### *Enabling machine understanding of any PDF's structure in one step!*
