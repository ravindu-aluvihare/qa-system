from transformers import pipeline

# Load a pre-trained Question Answering model
print("Loading model... (this might take 1-2 minutes first time)")
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Test context (a paragraph)
context = """
Artificial Intelligence (AI) is intelligence demonstrated by machines, 
in contrast to the natural intelligence displayed by humans and animals. 
Leading AI textbooks define the field as the study of intelligent agents. 
AI was founded as an academic discipline in 1956.
"""

# Test questions
questions = [
    "What is AI?",
    "When was AI founded?",
    "Who displays natural intelligence?"
]

print("\n" + "="*50)
print("QUESTION ANSWERING DEMO")
print("="*50 + "\n")

# Ask questions
for question in questions:
    result = qa_pipeline(question=question, context=context)
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['score']:.2%}\n")