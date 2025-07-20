import gradio as gr
import PyPDF2
import difflib

def extract_text_from_pdf(pdf_path):
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {e}"

def analyze_resume_and_jd(resume_path, jd_path):
    if not resume_path or not jd_path:
        return {"error": "Please upload both resume and job description."}, "", ""

    try:
        # Extract Resume Text
        resume_text = extract_text_from_pdf(resume_path)
        if resume_text.startswith("Error"):
            return {"error": resume_text}, "", ""

        # Extract JD Text
        with open(jd_path, "rb") as f:
            jd_raw = f.read()

        try:
            jd_text = jd_raw.decode("utf-8")
        except UnicodeDecodeError:
            jd_text = jd_raw.decode("latin-1")

        if not jd_text.strip():
            return {"error": "Job description file is empty or unreadable."}, "", ""

        # Entity count
        entities = {
            "resume_words": len(resume_text.split()),
            "jd_words": len(jd_text.split())
        }

        # Similarity %
        similarity = difflib.SequenceMatcher(None, resume_text.lower(), jd_text.lower()).ratio()
        similarity_percent = round(similarity * 100, 2)

        return entities, f"{similarity_percent}%", jd_text

    except Exception as e:
        return {"error": str(e)}, "", ""

# ✅ Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📄 Resume and Job Description Analyzer")
    gr.Markdown("Upload your **Resume (PDF)** and **Job Description (TXT)** to analyze similarity.")

    with gr.Row():
        with gr.Column():
            resume_file = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"], type="filepath")
            jd_file = gr.File(label="Upload Job Description (TXT)", file_types=[".txt"], type="filepath")
            submit_btn = gr.Button("Submit")
            clear_btn = gr.Button("Clear")
        with gr.Column():
            extracted_entities = gr.JSON(label="Extracted Entities / Errors")
            similarity_output = gr.Textbox(label="Similarity %", lines=1)
            jd_text_output = gr.Textbox(label="Job Description Text", lines=10)

    submit_btn.click(
        analyze_resume_and_jd,
        inputs=[resume_file, jd_file],
        outputs=[extracted_entities, similarity_output, jd_text_output]
    )

    clear_btn.click(
        lambda: (None, "", ""),
        inputs=[],
        outputs=[extracted_entities, similarity_output, jd_text_output]
    )

demo.launch()
