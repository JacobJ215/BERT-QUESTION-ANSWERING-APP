from flask import Flask, render_template, request
from transformers import pipeline

app = Flask(__name__)

# Function to chunk the passage into smaller parts
def chunk_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        passage = request.form.get("passage")
        question = request.form.get("question")
        chunk_size = request.form.get("chunk-size")

        if not passage:
            return render_template("index.html", error="Please enter a passage.")
        if not question:
            return render_template("index.html", error="Please enter a question")
        if chunk_size is None:
            chunk_size = 400

        chunk_size = int(chunk_size)

        # Chunk the passage into smaller parts using the selected chunk size
        passage_chunks = chunk_text(passage, chunk_size=chunk_size)

        # Initialize the BERT questoin-answering pipeline
        qna_pipeline = pipeline("question-answering",
                                 model="bert-large-uncased-whole-word-masking-finetuned-squad",
                                 tokenizer="bert-large-uncased")

        # Initialize variables to store answer and highlight chunks
        answer = ""
        highlighted_chunks = []

        # Process each chunk and get answers
        for idx, chunk in enumerate(passage_chunks):
            # Perform question-answering on the chunk
            result = qna_pipeline({"question": question, "context": chunk})

            # Combine answers from chunks
            if idx == 0:
                answer = result["answer"]
            else:
                answer += " " + result["answer"]
            
            # Highlight chunks that contain the answer
            if result["score"] > 0.1:
                highlighted_chunks.append(chunk)

        # Display the final answer with highlighted chunks
        return render_template("index.html", answer=answer, highlighted_chunks=highlighted_chunks)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()

