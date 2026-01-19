import streamlit as st
from transformers import pipeline
import time
import sys
import os

# Add src to path so we can import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.utils import process_uploaded_file, truncate_text

# Page configuration
st.set_page_config(
    page_title="AI Question Answering System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 20px;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='main-header'>🤖 AI Question Answering System</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <p style='font-size: 18px;'>Upload documents or paste text, then ask questions and get AI-powered answers instantly!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📚 About This Project")
st.sidebar.info("""
**Question Answering System**

This AI model can extract answers from any text you provide.

**Supported Formats:**
- 📄 PDF files
- 📝 Word documents (.docx)
- 📃 Text files (.txt)
- ⌨️ Direct text input

**Model:** RoBERTa fine-tuned on SQuAD 2.0
""")

st.sidebar.header("💡 Tips")
st.sidebar.success("""
- Ask specific questions
- Keep context relevant
- Questions work best when the answer is explicitly in the text
- Check confidence scores
""")

st.sidebar.header("🎯 Example Questions")
st.sidebar.code("""
• What is the main topic?
• When did this happen?
• Who is mentioned?
• What are the key points?
• How does it work?
""")

# Load model (with caching to avoid reloading)
@st.cache_resource
def load_model():
    return pipeline("question-answering", model="deepset/roberta-base-squad2")

# Show loading message
with st.spinner("🔄 Loading AI model... (first time only)"):
    qa_pipeline = load_model()

st.success("✅ Model loaded and ready!")

# Initialize session state for context
if 'context' not in st.session_state:
    st.session_state.context = """Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents. AI was founded as an academic discipline in 1956. AI research has tried and discarded many different approaches, including simulating the brain, modeling human problem solving, formal logic, large databases of knowledge, and imitating animal behavior. In the first decades of the 21st century, highly mathematical statistical machine learning has dominated the field."""

# File upload section
st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
st.subheader("📁 Upload Document or Enter Text")

upload_method = st.radio(
    "Choose input method:",
    ["📤 Upload File", "⌨️ Type/Paste Text"],
    horizontal=True
)

if upload_method == "📤 Upload File":
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=['pdf', 'txt', 'docx'],
        help="Supported formats: PDF, TXT, DOCX (Max 10MB)"
    )
    
    if uploaded_file is not None:
        with st.spinner(f"📖 Reading {uploaded_file.name}..."):
            extracted_text = process_uploaded_file(uploaded_file)
            
            # Truncate if too long
            extracted_text = truncate_text(extracted_text, max_length=5000)
            
            st.session_state.context = extracted_text
            st.success(f"✅ Successfully loaded: {uploaded_file.name}")
            
            # Show preview
            with st.expander("👀 Preview extracted text"):
                st.text_area("Extracted content:", extracted_text, height=200, disabled=True)
else:
    context_input = st.text_area(
        "Paste or type your text here:",
        value=st.session_state.context,
        height=250,
        help="Paste any text you want to ask questions about"
    )
    st.session_state.context = context_input

# Character count
char_count = len(st.session_state.context)
word_count = len(st.session_state.context.split())
st.caption(f"📊 Characters: {char_count} | Words: {word_count}")

st.markdown("</div>", unsafe_allow_html=True)

# Question section
st.markdown("---")
st.subheader("❓ Ask Your Question")

col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What is the main topic discussed?",
        help="Ask anything about the context you provided",
        label_visibility="collapsed"
    )

with col2:
    ask_button = st.button("🔍 Get Answer", type="primary", use_container_width=True)

# Process question
if ask_button:
    if not st.session_state.context.strip():
        st.error("⚠️ Please provide some context text first!")
    elif not question.strip():
        st.error("⚠️ Please enter a question!")
    else:
        with st.spinner("🤔 AI is thinking..."):
            # Get answer
            start_time = time.time()
            try:
                result = qa_pipeline(question=question, context=st.session_state.context)
                end_time = time.time()
                
                # Display results
                st.markdown("---")
                st.markdown("### 💡 Answer")
                
                # Answer box with better styling
                st.markdown(f"""
                <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;'>
                    <h3 style='margin: 0; color: #155724;'>{result['answer']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("")  # Spacing
                
                # Metrics in columns
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    confidence = result['score'] * 100
                    st.metric("🎯 Confidence", f"{confidence:.1f}%")
                
                with metric_col2:
                    st.metric("⚡ Response Time", f"{(end_time - start_time):.2f}s")
                
                with metric_col3:
                    answer_length = len(result['answer'].split())
                    st.metric("📝 Answer Length", f"{answer_length} words")
                
                # Confidence indicator
                if confidence >= 80:
                    st.success("✅ High confidence - Answer is very likely correct")
                elif confidence >= 50:
                    st.warning("⚠️ Medium confidence - Answer might be approximate")
                else:
                    st.error("❌ Low confidence - Answer may not be reliable")
                
                # Show context with highlighted answer
                st.markdown("---")
                st.markdown("### 📍 Answer Location in Context")
                
                answer_start = st.session_state.context.lower().find(result['answer'].lower())
                if answer_start != -1:
                    answer_end = answer_start + len(result['answer'])
                    
                    # Get surrounding context (100 chars before and after)
                    context_start = max(0, answer_start - 100)
                    context_end = min(len(st.session_state.context), answer_end + 100)
                    
                    before = st.session_state.context[context_start:answer_start]
                    answer = st.session_state.context[answer_start:answer_end]
                    after = st.session_state.context[answer_end:context_end]
                    
                    # Add ellipsis if truncated
                    if context_start > 0:
                        before = "..." + before
                    if context_end < len(st.session_state.context):
                        after = after + "..."
                    
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; line-height: 1.8;'>
                        {before}<span style='background-color: #ffeb3b; padding: 3px; font-weight: bold;'>{answer}</span>{after}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Answer extracted but exact location not found in context")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p style='font-size: 14px;'>🤖 Built with Streamlit & Hugging Face Transformers</p>
    <p style='font-size: 12px;'>Model: deepset/roberta-base-squad2 | Framework: PyTorch</p>
</div>
""", unsafe_allow_html=True)

# Additional information in expandable sections
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("💡 How This Works"):
        st.markdown("""
        **Technology Stack:**
        - **Model:** RoBERTa (Robustly Optimized BERT)
        - **Training Data:** SQuAD 2.0 (100k+ questions)
        - **Framework:** Hugging Face Transformers
        - **Architecture:** Transformer-based neural network
        
        **Process:**
        1. Text is tokenized into smaller units
        2. Model analyzes semantic relationships
        3. Identifies most relevant answer span
        4. Returns answer with confidence score
        """)

with col_exp2:
    with st.expander("🎯 Use Cases"):
        st.markdown("""
        **This QA system can help with:**
        - 📚 Study notes and textbook comprehension
        - 📰 News article analysis
        - 📄 Legal document review
        - 🔍 Research paper Q&A
        - 💼 Business report summarization
        - 📖 Book and literature analysis
        - 🎓 Educational content creation
        - 📋 Meeting notes extraction
        """)