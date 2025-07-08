import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

from dotenv import load_dotenv
load_dotenv()

from entities.embedder import embedder
from entities.llm import llm
from entities.variables import SOURCE_DOC_DIR, IMAGE_DIR, FAISS_INDEX_DIR
from langchain_community.vectorstores import FAISS
from unstructured.partition.pdf import partition_pdf
from langchain_core.documents import Document
import traceback
import shutil
import base64
import os

try:
    os.makedirs(IMAGE_DIR, exist_ok=True)

    image_captions = []
    text_docs = []
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    image_captions = []
    text_docs = []
    for file in os.listdir(SOURCE_DOC_DIR):
        if not file.endswith(".pdf"):
            continue
        print(f"\n\nPDF: {file}")
        PDF_PATH = os.path.join(SOURCE_DOC_DIR, file)
        print("Partitioning PDF...")
        elements = partition_pdf(
            filename=PDF_PATH,
            extract_images_in_pdf=True,
            chunking_strategy="by_title",
            max_characters=3000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=2800,
            image_output_dir_path=IMAGE_DIR,
        )
    
        pdf_name = os.path.splitext(os.path.basename(PDF_PATH))[0]
        destination_dir = os.path.join(IMAGE_DIR, pdf_name)

        os.makedirs(destination_dir, exist_ok=True)

        image_paths = []
        figures_dir = "figures"
        if os.path.exists(figures_dir):
            for item in os.listdir(figures_dir):
                source_item_path = os.path.join(figures_dir, item)
                destination_item_path = os.path.join(destination_dir, item)
                shutil.move(source_item_path, destination_item_path)
                image_paths.append(destination_item_path)
            shutil.rmtree(figures_dir)
        else:
            print(f"Extracted figures directory '{figures_dir}' not found.")

        print("Creating text documents...")
        for el in elements:
            text_docs.append(Document(page_content=el.text.strip(), metadata={"source": os.path.basename(PDF_PATH)}))

        print("Captioning images...")

        for path in image_paths:
            with open(path, "rb") as img_file:
                image_data = img_file.read()
                image_b64 = base64.b64encode(image_data).decode("utf-8")
                message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is shown in this image? Provide a description, detailed if required.",
                        },
                        {
                            "type": "image",
                            "source_type": "base64",
                            "data": image_b64,
                            "mime_type": "image/jpeg",
                        },
                    ],
                }
                response = llm.invoke([message])
                caption = response.content
                image_captions.append(Document(page_content=caption, metadata={"source": path}))

    all_docs = text_docs + image_captions

    print("Creating FAISS index...")
    faiss_db = FAISS.from_documents(all_docs, embedder)

    print("Saving FAISS index...")
    faiss_db.save_local(FAISS_INDEX_DIR)

    print("Done!")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()