import os
import json
import re
import fitz  # PyMuPDF for PDF processing
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME]):
    raise RuntimeError("Azure OpenAI environment variables are not properly set.")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# --- Configuration ---
PDF_FILE = "Mutual Funds Educational Info.pdf"
OUTPUT_DIR = "processed_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "mutual_funds_qa_dataset.json")
MODEL = AZURE_OPENAI_DEPLOYMENT_NAME
ORG_NAME = "JBS BANK"
CHUNK_SIZE = 3000  # Characters per chunk for processing

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file and return as a single string.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                text += "\n\n"  # Add spacing between pages
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    return text.strip()

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """
    Split text into chunks of approximately chunk_size characters.
    Tries to break at sentence boundaries when possible.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If we're at the end of the text
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Try to find a sentence boundary near the chunk_size
        # Look for sentence endings within 200 characters before the end
        search_start = max(start, end - 200)
        sentence_end = -1
        
        for i in range(end, search_start, -1):
            if text[i] in '.!?':
                # Make sure it's not part of an abbreviation or decimal
                if i + 1 < len(text) and text[i + 1].isspace():
                    sentence_end = i + 1
                    break
        
        if sentence_end != -1:
            chunks.append(text[start:sentence_end].strip())
            start = sentence_end
        else:
            # Fallback: break at the chunk size
            chunks.append(text[start:end].strip())
            start = end
    
    return [chunk for chunk in chunks if chunk.strip()]

def generate_qa_pairs():
    """
    Generate Q&A pairs from PDF file and save to OUTPUT_FILE.
    Returns the total number of Q&A pairs generated.
    """
    all_qas = []
    
    print(f"Processing PDF file: {PDF_FILE}")
    
    # Extract text from PDF
    try:
        full_text = extract_text_from_pdf(PDF_FILE)
        if not full_text.strip():
            print("PDF appears to be empty or text could not be extracted.")
            return 0
        print(f"Extracted {len(full_text)} characters from PDF")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return 0
    
    # Split text into chunks
    text_chunks = chunk_text(full_text)
    print(f"Split text into {len(text_chunks)} chunks")
    
    for i, chunk in enumerate(text_chunks, 1):
        print(f"Processing chunk {i}/{len(text_chunks)}")
        
        if not chunk.strip():
            print(f"  Skipping empty chunk {i}")
            continue
        
        # Generate Q&A pairs for this chunk
        system_prompt = (
            f"You are a {ORG_NAME}'s Customer Support Agent specialized in mutual funds and asset management. "
            "You receive a text excerpt and must reply with a JSON array of question-answer pairs without any arbitrary values. "
            "Each object must contain exactly three keys: 'Question', 'Answer', and 'ChunkNumber'. "
            "Focus on mutual funds, investment strategies, financial planning, and asset management topics. "
            "If the text excerpt contains no substantive information or seems meaningless, return an empty array. "
            "Do not include any explanation or additional text. If the excerpt has no substantive information, return an empty array (i.e., [])."
        )
        user_prompt = (
            f"Text excerpt from chunk {i} of mutual funds educational document:\n" + chunk +
            "\n\nGenerate comprehensive, concise, engaging, human-friendly, conversational Q&A pairs in JSON array format "
            "only if the text excerpt is meaningful. Focus on mutual funds, investment concepts, and financial planning. "
            "##NOTE: DO NOT MISS ANY INFORMATION. ALWAYS PROVIDE COMPLETE INFORMATION IN YOUR ANSWERS. "
            "They should be complete and have all the information. You can create 15-25+ Q&A pairs per chunk "
            "to ensure no information is lost. Data accuracy is critical - do not hallucinate or provide incomplete data."
        )
        
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
            )
            raw = resp.choices[0].message.content.strip()
            
            # Attempt to extract JSON array
            match = re.search(r"(\[.*\])", raw, re.DOTALL)
            json_text = match.group(1) if match else raw
            
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                # Fallback: extract individual JSON objects
                objs = re.findall(r"(\{[^}]*\})", raw, re.DOTALL)
                data = []
                for obj in objs:
                    try:
                        item = json.loads(obj)
                        data.append(item)
                    except json.JSONDecodeError:
                        continue
            
            # Filter and ensure ChunkNumber present
            valid = []
            for qa in data:
                if all(k in qa for k in ("Question", "Answer")):
                    qa.setdefault("ChunkNumber", i)
                    qa.setdefault("Source", "Mutual Funds Educational Info.pdf")
                    valid.append(qa)
            
            print(f"  Generated {len(valid)} Q&A pairs from chunk {i}")
            all_qas.extend(valid)
            
        except Exception as e:
            print(f"  Error processing chunk {i}: {str(e)}")
            continue

    # Write consolidated dataset
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outf:
        json.dump(all_qas, outf, ensure_ascii=False, indent=2)

    print(f"Done! Generated total {len(all_qas)} Q&A pairs → {OUTPUT_FILE}")
    return len(all_qas)

if __name__ == "__main__":
    generate_qa_pairs() 