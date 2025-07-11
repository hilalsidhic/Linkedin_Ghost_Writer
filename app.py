import streamlit as st
import os
import tempfile
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

# Custom CSS for modern, aesthetic design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .header {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        font-size: 1.2rem;
        color: #6b7280;
        margin: 0;
    }
    
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .step-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .step-circle.completed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .step-circle.inactive {
        background: #f3f4f6;
        color: #9ca3af;
    }
    
    .step-arrow {
        font-size: 1.5rem;
        color: #d1d5db;
    }
    
    .step-content {
        background: #f8fafc;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .instruction-card {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #a7f3d0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .generated-post {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .navigation-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: 2rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .btn-secondary {
        background: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        background: #f1f5f9;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'mhtml_file' not in st.session_state:
    st.session_state.mhtml_file = None
if 'posts' not in st.session_state:
    st.session_state.posts = None
if 'writing_style' not in st.session_state:
    st.session_state.writing_style = None
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None
if 'linkedin_url' not in st.session_state:
    st.session_state.linkedin_url = ""
if 'topic' not in st.session_state:
    st.session_state.topic = ""

def copy_to_clipboard(text):
    """Copy text to clipboard using JavaScript"""
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

def render_step_indicator():
    """Render the step indicator with circles and arrows"""
    steps = [
        {"number": 1, "title": "LinkedIn URL"},
        {"number": 2, "title": "Upload File"},
        {"number": 3, "title": "Analyze Style"},
        {"number": 4, "title": "Generate Post"}
    ]
    
    indicator_html = '<div class="step-indicator">'
    
    for i, step in enumerate(steps):
        # Determine step state
        if step["number"] < st.session_state.current_step:
            state = "completed"
        elif step["number"] == st.session_state.current_step:
            state = "active"
        else:
            state = "inactive"
        
        # Add circle
        indicator_html += f'<div class="step-circle {state}">{step["number"]}</div>'
        
        # Add arrow (except for last step)
        if i < len(steps) - 1:
            indicator_html += '<div class="step-arrow">→</div>'
    
    indicator_html += '</div>'
    return indicator_html

def next_step():
    """Move to next step"""
    if st.session_state.current_step < 4:
        st.session_state.current_step += 1
        st.rerun()

def previous_step():
    """Move to previous step"""
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1
        st.rerun()

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>✍️ Write Like Me</h1>
    <p>Your Personal LinkedIn Ghostwriter Agent</p>
</div>
""", unsafe_allow_html=True)

# Step indicator
st.markdown(render_step_indicator(), unsafe_allow_html=True)

# Step 1: LinkedIn Profile URL Input
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">🔗 LinkedIn Profile Input</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.session_state.linkedin_url = st.text_input(
        "Paste Your LinkedIn Profile URL",
        value=st.session_state.linkedin_url,
        placeholder="https://linkedin.com/in/yourprofile",
        help="We'll help you export your posts. Nothing is stored on our servers."
    )
    
    # Instructions card
    with st.expander("📋 How to export your LinkedIn posts", expanded=True):
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
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("Next: Upload File →", type="primary", use_container_width=True):
            next_step()

# Step 2: File Upload
elif st.session_state.current_step == 2:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">📁 Upload Your MHTML File</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your LinkedIn posts file",
        type=['mhtml'],
        help="We only read this file locally to analyze your style."
    )
    
    if uploaded_file is not None:
        # Display file info
        st.markdown(f"""
        <div class="success-card">
            <h4>✅ File uploaded successfully!</h4>
            <p><strong>File:</strong> {uploaded_file.name}<br>
            <strong>Size:</strong> {uploaded_file.size} bytes</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mhtml') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.mhtml_file = tmp_file.name
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            previous_step()
    with col2:
        if st.session_state.mhtml_file and st.button("Next: Analyze Style →", type="primary", use_container_width=True):
            next_step()

# Step 3: Analyze Writing Style
elif st.session_state.current_step == 3:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">🔍 Analyze Your Writing Style</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.mhtml_file:
        if not st.session_state.writing_style:
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
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Error analyzing posts: {str(e)}")
                    st.error("Please check that your MHTML file is valid and contains LinkedIn posts.")
        else:
            # Display writing style analysis
            st.markdown(f"""
            <div class="success-card">
                <h4>✨ Your Unique Writing Style</h4>
                <p>Based on your top-performing posts, here's your unique writing style:</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="generated-post">
                {st.session_state.writing_style.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            previous_step()
    with col2:
        if st.session_state.writing_style and st.button("Next: Generate Post →", type="primary", use_container_width=True):
            next_step()

# Step 4: Generate New Post
elif st.session_state.current_step == 4:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">✏️ Generate a New Post</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.session_state.topic = st.text_area(
        "What do you want to write about next?",
        value=st.session_state.topic,
        placeholder="Enter your topic ideas, bullet points, or key messages...",
        height=100,
        help="Be specific about what you want to discuss. The more details you provide, the better the generated post will be."
    )
    
    if st.button("✏️ Generate Post", type="primary", use_container_width=True):
        if st.session_state.topic.strip():
            try:
                with st.spinner("Generating your post... ✨"):
                    # Generate new post
                    generated_post = generate_post(st.session_state.topic, st.session_state.writing_style)
                    st.session_state.generated_post = generated_post
                    
                    # Show success animation
                    st.balloons()
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error generating post: {str(e)}")
                st.error("Please try again or check your internet connection.")
        else:
            st.warning("⚠️ Please enter a topic before generating a post.")
    
    # Display generated post
    if st.session_state.generated_post:
        st.markdown(f"""
        <div class="success-card">
            <h4>🎉 Your Generated Post</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="generated-post">
            {st.session_state.generated_post.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Copy to clipboard button
        if st.button("📋 Copy to Clipboard", type="primary", use_container_width=True):
            copy_to_clipboard(st.session_state.generated_post)
            st.success("✅ Copied to clipboard!")
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            previous_step()
    with col2:
        if st.session_state.generated_post and st.button("Start Over", type="secondary", use_container_width=True):
            # Reset session state
            st.session_state.current_step = 1
            st.session_state.mhtml_file = None
            st.session_state.posts = None
            st.session_state.writing_style = None
            st.session_state.generated_post = None
            st.session_state.linkedin_url = ""
            st.session_state.topic = ""
            st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ for the AI Agent Challenge</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Clean up temporary files
if st.session_state.mhtml_file and os.path.exists(st.session_state.mhtml_file):
    try:
        os.unlink(st.session_state.mhtml_file)
    except:
        pass  # Ignore cleanup errors
