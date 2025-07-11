import streamlit as st
import os
import tempfile
import pyperclip
from loaders import load_mhtml, extract_posts
from style_analyzer import analyze_style
from generator import generate_post

# Page configuration
st.set_page_config(
    page_title="Write Like Me - LinkedIn Ghostwriter",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .step-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        color: #0A66C2;
    }
    .instruction-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0A66C2;
        margin: 1rem 0;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .generated-post {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mhtml_file' not in st.session_state:
    st.session_state.mhtml_file = None
if 'posts' not in st.session_state:
    st.session_state.posts = None
if 'writing_style' not in st.session_state:
    st.session_state.writing_style = None
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None

def copy_to_clipboard(text):
    """Copy text to clipboard using JavaScript"""
    # Escape backticks and quotes for JavaScript
    escaped_text = text.replace('`', r'\`').replace('"', r'\"').replace("'", r"\'")
    html_content = f"""
    <script>
        navigator.clipboard.writeText(`{escaped_text}`).then(function() {{
            console.log('Copied to clipboard');
        }}, function(err) {{
            console.error('Could not copy text: ', err);
        }});
    </script>
    """
    st.components.v1.html(html_content, height=0)

# Main header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("✍️ Write Like Me")
st.markdown("**Your Personal LinkedIn Ghostwriter Agent**")
st.markdown("</div>", unsafe_allow_html=True)

# Step 1: LinkedIn Profile URL Input
st.markdown('<div class="step-header">🔗 Step 1: LinkedIn Profile Input</div>', unsafe_allow_html=True)

linkedin_url = st.text_input(
    "Paste Your LinkedIn Profile URL",
    placeholder="https://linkedin.com/in/yourprofile",
    help="We'll help you export your posts. Don't worry, nothing is stored on our servers."
)

# Instructions card
with st.expander("📋 How to export your LinkedIn posts", expanded=False):
    st.markdown("""
    <div class="instruction-card">
        <h4>Follow these steps to export your posts:</h4>
        <ol>
            <li><strong>Go to your LinkedIn Profile</strong> → Activity → Posts</li>
            <li><strong>Expand all posts</strong> you want the AI to learn from</li>
            <li><strong>Scroll down</strong> to load more posts</li>
            <li><strong>Right-click</strong> → Save As → choose <strong>Webpage, Single File (.mhtml)</strong></li>
        </ol>
        <p><em>💡 Tip: The more posts you include, the better we can understand your writing style!</em></p>
    </div>
    """, unsafe_allow_html=True)

# Step 2: File Upload
st.markdown('<div class="step-header">📁 Step 2: Upload Your MHTML File</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your LinkedIn posts file",
    type=['mhtml'],
    help="We only read this file locally to analyze your style."
)

if uploaded_file is not None:
    # Display file info
    st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mhtml') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state.mhtml_file = tmp_file.name

# Step 3: Analyze Writing Style
st.markdown('<div class="step-header">🔍 Step 3: Analyze Your Writing Style</div>', unsafe_allow_html=True)

if st.session_state.mhtml_file:
    if st.button("🔍 Analyze My Posts", type="primary", use_container_width=True):
        try:
            with st.spinner("Analyzing your writing style... This may take a moment."):
                # Load and extract posts
                docs = load_mhtml(st.session_state.mhtml_file)
                posts = extract_posts(docs)
                
                if not posts:
                    st.error("❌ No posts found in the uploaded file. Please make sure you've exported your LinkedIn posts correctly.")
                else:
                    # Sort posts by engagement score and take top 5
                    sorted_posts = sorted(posts, key=lambda x: x[1], reverse=True)
                    top_posts = sorted_posts[:5]
                    
                    # Analyze writing style
                    style = analyze_style([p[0] for p in top_posts])
                    
                    # Store in session state
                    st.session_state.posts = posts
                    st.session_state.writing_style = style
                    
                    st.success(f"✅ Successfully analyzed {len(posts)} posts!")
                    
        except Exception as e:
            st.error(f"❌ Error analyzing posts: {str(e)}")
            st.error("Please check that your MHTML file is valid and contains LinkedIn posts.")

# Display writing style analysis
if st.session_state.writing_style:
    st.markdown('<div class="step-header">✨ Your Unique Writing Style</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="success-card">
        <h4>📊 Analysis Results</h4>
        <p>Based on your top-performing posts, here's your unique writing style:</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(st.session_state.writing_style)

# Step 4: Generate New Post
if st.session_state.writing_style:
    st.markdown('<div class="step-header">✏️ Step 4: Generate a New Post</div>', unsafe_allow_html=True)
    
    topic = st.text_area(
        "What do you want to write about next?",
        placeholder="Enter your topic ideas, bullet points, or key messages...",
        height=100,
        help="Be specific about what you want to discuss. The more details you provide, the better the generated post will be."
    )
    
    if st.button("✏️ Generate Post", type="primary", use_container_width=True):
        if topic.strip():
            try:
                with st.spinner("Generating your post... ✨"):
                    # Generate new post
                    generated_post = generate_post(topic, st.session_state.writing_style)
                    st.session_state.generated_post = generated_post
                    
                    # Show success animation
                    st.balloons()
                    
            except Exception as e:
                st.error(f"❌ Error generating post: {str(e)}")
                st.error("Please try again or check your internet connection.")
        else:
            st.warning("⚠️ Please enter a topic before generating a post.")

# Display generated post
if st.session_state.generated_post:
    st.markdown('<div class="step-header">🎉 Your Generated Post</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="generated-post">
        {st.session_state.generated_post.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    # Copy to clipboard button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            copy_to_clipboard(st.session_state.generated_post)
            st.success("✅ Copied to clipboard!")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 2rem;">Built with ❤️ for the AI Agent Challenge</div>',
    unsafe_allow_html=True
)

# Clean up temporary files
if st.session_state.mhtml_file and os.path.exists(st.session_state.mhtml_file):
    try:
        os.unlink(st.session_state.mhtml_file)
    except:
        pass  # Ignore cleanup errors
