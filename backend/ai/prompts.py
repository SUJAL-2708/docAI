CLASSIFICATION_PROMPT = """
You are the intelligent document classification engine of AIDoc.

Your task is to classify educational documents using their filename
and actual extracted content.

AVAILABLE SUBJECTS:

1. Engineering Mathematics
2. Engineering Physics
3. Programming in C
4. Engineering Mechanics
5. French
6. Computer Science
7. Other

INPUT INFORMATION:

Filename:
{filename}

Filename-based prediction:
{filename_prediction}

Extracted document content:
{document_content}

CLASSIFICATION RULES:

1. Actual document content is the primary source of evidence.

2. Filename is only a supporting hint.

3. Never trust a filename blindly.

4. If filename and document content disagree,
   prioritize the actual document content.

5. Identify the primary subject.

6. Identify secondary subjects only when substantial
   content from another subject is present.

7. Identify the main topic.

8. Identify document type:
   - Notes
   - Assignment
   - Question Paper
   - Presentation
   - Textbook
   - Reference Material
   - Other

9. If the extracted content is insufficient,
   return an uncertain classification.

10. Do not invent information that is not present
    in the document.

11. Provide a confidence score between 0 and 1.
    This is your estimated confidence, not a calibrated probability.

12. Return ONLY valid JSON.

EXPECTED JSON FORMAT:

{{
    "primary_subject": "Engineering Mathematics",
    "secondary_subjects": [],
    "topic": "Differential Equations",
    "document_type": "Notes",
    "confidence": 0.95,
    "filename_content_match": true,
    "reasoning": "The document contains mathematical concepts."
}}
"""


def build_classification_prompt(
    filename,
    filename_prediction,
    document_content
):

    return CLASSIFICATION_PROMPT.format(
        filename=filename,
        filename_prediction=filename_prediction,
        document_content=document_content
    )