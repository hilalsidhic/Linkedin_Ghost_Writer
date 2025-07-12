import streamlit as st
import os
import tempfile
import time
from loaders import load_mhtml, extract_posts
from style_analyzer import analyze_style
from generator import generate_post
from clean_posts import clean_post_text,clean_posts_parallel
from agent_runner import run_agent_generate,run_agent_rewrite_post,run_agent_estimate_virality

# Page configuration
st.set_page_config(page_title="Write Like Me - LinkedIn Ghostwriter",
                   page_icon="✍️",
                   layout="centered",
                   initial_sidebar_state="collapsed")

# Hide Streamlit branding
st.markdown("""
    <style>
    /* Hide Streamlit main header bar */
    header {
        visibility: hidden;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
    }

    /* Hide MainMenu and footer too */
    #MainMenu {
        visibility: hidden;
        height: 0 !important;
    }

    footer {
        visibility: hidden;
        height: 0 !important;
    }

    /* Also zero out any margin or padding at the top of main block */
    .block-container {
        padding-top: 0rem !important;
    }

    /* Sometimes Streamlit uses a div under header, remove that too */
    div[data-testid="stHeader"] {
        height: 0 !important;
        max-height: 0 !important;
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)



# Custom CSS for clean, aesthetic design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

    .stApp {
        background: #f8fafc;
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* <-- base text color */
    }

    .main-container {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        margin: 1rem auto;
        max-width: 700px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
    }

    .header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }

    .header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }

    .header p {
        font-size: 1rem;
        color: #475569;
        margin: 0;
    }

    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 0.75rem;
    }

    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        border: 2px solid #e2e8f0;
    }

    .step-circle.active {
        background: #1e40af;
        color: white;
        border-color: #1e40af;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
    }

    .step-circle.completed {
        background: #059669;
        color: white;
        border-color: #059669;
    }

    .step-circle.inactive {
        background: #f8fafc;
        color: #94a3b8;
        border-color: #e2e8f0;
    }

    .step-arrow {
        font-size: 1.2rem;
        color: #cbd5e1;
    }

    .step-content {
        background: #f8fafc;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid #e2e8f0;
    }

    .step-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        text-align: center;
    }

    .instruction-card {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1e293b; /* ensure readable text */
    }

    .instruction-card h4 {
        color: #1e40af;
        margin-bottom: 1rem;
    }

    .success-card {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1e293b; /* ensure readable text */
    }

    .success-card h4 {
        color: #059669;
        margin-bottom: 0.5rem;
    }

    .generated-post {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #1e293b; /* ensure readable text */
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"] {
        background: #1e40af !important;
        border-color: #1e40af !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #1e293b !important; /* darker for contrast */
        border: 1px solid #e2e8f0 !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
    }

    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stFileUploader > div {
        border-radius: 8px !important;
        border: 2px dashed #cbd5e1 !important;
    }

    a {
        color: #2563eb; /* consistent link color */
    }

    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 0.875rem;
    }

    /* Remove Streamlit branding */
    .stApp > header {
        display: none;
    }

    .stDeployButton {
        display: none;
    }

    #MainMenu {
        display: none;
    }

    footer {
        display: none;
    }
    .error-card {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #991b1b;
    }

    .error-card h4 {
        margin-bottom: 0.5rem;
    }

    .info-card {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1e3a8a;
    }

    .info-card h4 {
        margin-bottom: 0;
    }
    

      /* Kill header/footer/menu exactly as before */
    header, footer, #MainMenu, .stDeployButton, .stApp > header,
    div[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stFooter"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove default top padding/margin everywhere */
    html, body, main, .block-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Prevent flexbox extra centering */
    .stApp {
        display: block !important;
        min-height: auto !important;
    }

    body {
        display: block !important;
        min-height: auto !important;
    }

    #root {
        display: block !important;
        min-height: auto !important;
    }

    /* Style Streamlit download button */
    .stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        background: #1e40af !important; /* Primary blue */
        color: white !important; /* Text stays white */
        border: none !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background: #1d4ed8 !important; /* Slightly brighter blue on hover */
        transform: translateY(-1px);
    }
</style>

""",
            unsafe_allow_html=True)

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

def render_copy_button(label: str, text_to_copy: str, button_id: str = "copyBtn"):
    """
    Render a styled HTML+JS copy button.
    - label: Button label to show.
    - text_to_copy: The text to copy.
    - button_id: Unique ID if you have multiple on one page.
    """
    escaped_text = text_to_copy.replace("`", "\\`").replace("\\", "\\\\").replace("\n", "\\n")

    st.components.v1.html(
        f"""
        <button id="{button_id}" style="
            background: #1e40af; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            padding: 0.75rem 1.25rem; 
            font-size: 1rem;
            cursor: pointer;
            margin-top: 10px;
        ">
            📋 {label}
        </button>

        <script>
        const btn = document.getElementById('{button_id}');
        btn.addEventListener('click', () => {{
            const text = `{escaped_text}`;
            navigator.clipboard.writeText(text).then(() => {{
                btn.innerText = '✅ Copied!';
                setTimeout(() => {{
                    btn.innerText = '📋 {label}';
                }}, 2000);
            }});
        }});
        </script>
        """,
        height=80
    )

def copy_to_clipboard(text):
    """Copy text to clipboard using JavaScript"""
    escaped_text = text.replace('`', r'\`').replace('"',
                                                    r'\"').replace("'", r"\'")
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
    steps = [{
        "number": 1,
        "title": "LinkedIn URL"
    }, {
        "number": 2,
        "title": "Upload File"
    }, {
        "number": 3,
        "title": "Analyze Style"
    }, {
        "number": 4,
        "title": "Generate Post"
    }]

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

# --- Helper Functions ---
def reset_session_state():
    """Reset all session state variables to initial values."""
    if st.session_state.mhtml_file and os.path.exists(st.session_state.mhtml_file):
        try:
            os.unlink(st.session_state.mhtml_file)
        except:
            pass
    st.session_state.current_step = 1
    st.session_state.mhtml_file = None
    st.session_state.posts = None
    st.session_state.writing_style = None
    st.session_state.generated_post = None
    st.session_state.linkedin_url = ""
    st.session_state.topic = ""

def render_top_posts_summary(posts, top_n=5):
    """Render a summary of the top N posts used for style analysis."""
    if not posts:
        return
    sorted_posts = sorted(posts, key=lambda x: x[1], reverse=True)
    top_posts = sorted_posts[:top_n]
    st.markdown("""
    <div class="success-card">
        <h4>Top Posts Used for Style Analysis</h4>
    </div>
    """, unsafe_allow_html=True)
    cleaned_texts = clean_posts_parallel(top_posts)
    for i, ((original_text, score), cleaned) in enumerate(zip(top_posts, cleaned_texts), 1):
        st.markdown(f"""
        <div class="generated-post">
            <b>Post #{i} (Score: {score:.1f})</b><br>
            {cleaned[:350].replace(chr(10), '<br>')}...<br>
        </div>
        """, unsafe_allow_html=True)

def navigation_buttons(show_back=True, show_next=True, next_label="Next", next_callback=None):
    col1, col2 = st.columns([1, 1])
    with col1:
        if show_back and st.button("Back", type="secondary", use_container_width=True):
            previous_step()
    with col2:
        if show_next and st.button(next_label, type="primary", use_container_width=True):
            if next_callback:
                next_callback()


# Header at top of page
if st.session_state.current_step == 1:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #1e40af; margin: 0;">✍️ Write Like Me</h1>
        <p style="font-size: 1.2rem; color: #64748b; margin: 0.5rem 0;">Your Personal LinkedIn Ghostwriter Agent</p>
    </div>
    """, unsafe_allow_html=True)

# Main container
# st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Step indicator
st.markdown(render_step_indicator(), unsafe_allow_html=True)
st.components.v1.html(
    """
    <script>
        document.querySelector('.step-indicator').scrollIntoView({ behavior: 'smooth' });
    </script>
    """,
    height=0,
)

# Step 1: LinkedIn Profile URL Input
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">🔗 LinkedIn Profile Input</div>
    </div>
    """, unsafe_allow_html=True)

    # LinkedIn URL input
    linkedin_url = st.text_area(
        "Paste Your LinkedIn Profile URL",
        value=st.session_state.linkedin_url,
        placeholder="https://linkedin.com/in/yourprofile",
        height=68
    )

    # Update session state
    st.session_state.linkedin_url = linkedin_url
    
    # Generate activity URL if profile URL is provided
    if linkedin_url.strip():
        # Extract username from LinkedIn URL
        if "/in/" in linkedin_url:
            username = linkedin_url.split("/in/")[1].split("/")[0]
            activity_url = f"https://linkedin.com/in/{username}/recent-activity/all/"
            
            st.markdown(f"""
            <div class="success-card">
                <h4>Your LinkedIn Activity URL</h4>
                <p><a href="{activity_url}" target="_blank">{activity_url}</a></p>
                <p><em>Click the link above to go to your LinkedIn activity page</em></p>
            </div>
            """, unsafe_allow_html=True)

    # Instructions card
    with st.expander("How to export your LinkedIn posts", expanded=False):
        st.markdown("""
        <div class="instruction-card">
            <h4>Export Steps:</h4>
            <ol>
                <li>Go to your LinkedIn Profile → Activity → Posts</li>
                <li>Expand all posts you want the AI to learn from</li>
                <li>Scroll down to load more posts</li>
                <li>Right-click → Save As → choose Webpage, Single File (.mhtml)</li>
            </ol>
        </div>
        """,
                    unsafe_allow_html=True)

    # Navigation
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("Next: Upload File",
                     type="primary",
                     use_container_width=True):
            next_step()

# Step 2: File Upload

elif st.session_state.current_step == 2:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">📁 Upload Your MHTML File & Auto-Analyze</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose your LinkedIn posts file (.mhtml)",
        type=['mhtml'],
        help="Your file stays local. We only read it to learn your style."
    )

    if uploaded_file is not None:
        # Save temp
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mhtml') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.mhtml_file = tmp_file.name

        st.markdown(f"""
        <div class="success-card">
            <h4>✅ File Uploaded Successfully</h4>
            <p>{uploaded_file.name}</p>
        </div>
        """, unsafe_allow_html=True)

        # Stream-like progressive feedback
        progress = st.empty()
        time.sleep(0.5)
        progress.markdown("""
        <div class="info-card">
            <h4>📂 Loading MHTML file...</h4>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

        try:
            docs = load_mhtml(st.session_state.mhtml_file)
            progress.markdown("""
            <div class="info-card">
                <h4>🔍 Extracting posts from file...</h4>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

            posts = extract_posts(docs)
            if not posts:
                progress.markdown("""
                <div class="error-card">
                    <h4>❌ No posts found</h4>
                    <p>Please check your MHTML export and try again.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                progress.markdown(f"""
                <div class="success-card">
                    <h4>✅ Posts Found</h4>
                    <p>Found {len(posts)} posts. Sorting by engagement...</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)

                sorted_posts = sorted(posts, key=lambda x: x[1], reverse=True)
                top_posts = sorted_posts[:5]

                progress.markdown("""
                <div class="info-card">
                    <h4>🧠 Analyzing your writing style...</h4>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1.5)

                style = analyze_style([p[0] for p in top_posts])
                st.session_state.posts = posts
                st.session_state.writing_style = style

                progress.markdown("""
                <div class="success-card">
                    <h4>✨ Writing Style Learned Successfully!</h4>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)

                st.session_state.current_step = 3  # Auto move to next
                st.rerun()
        except Exception as e:
            progress.markdown(f"""
            <div class="error-card">
                <h4>❌ Error Analyzing Posts</h4>
                <p>{str(e)}</p>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Back", type="secondary"):
        previous_step()


# --- Main App Logic ---
# Step 3: Analyze Writing Style
elif st.session_state.current_step == 3:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">✏️ Your Writing Style & New Topic</div>
    </div>
    """, unsafe_allow_html=True)

    # Render posts + style
    render_top_posts_summary(st.session_state.posts)
    st.markdown(f"""
    <div class="success-card">
        <h4>Your Writing Style</h4>
    </div>
    <div id="writing-style" class="generated-post">
        {st.session_state.writing_style.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

    render_copy_button("Copy Writing Style", st.session_state.writing_style, button_id="copyWritingStyle")

    st.session_state.topic = st.text_area(
        "What do you want to write about?",
        value=st.session_state.topic,
        placeholder="e.g. How to grow on LinkedIn, career tips, industry trends...",
        height=100
    )

    progress = st.empty()

    if st.button("Generate Post ✨", type="primary"):
        if st.session_state.topic.strip():
            progress.markdown("""
            <div class="info-card">
                <h4>🧠 Thinking about your topic...</h4>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

            progress.markdown("""
            <div class="info-card">
                <h4>✍️ Mixing it with your style...</h4>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

            generated_post = run_agent_generate(
                st.session_state.topic,
                st.session_state.writing_style
            )

            st.session_state.generated_post =  generated_post["output"]

            progress.markdown("""
            <div class="success-card">
                <h4>✅ Post generated successfully!</h4>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()
            st.session_state.current_step = 4
            st.rerun()
        else:
            st.warning("⚠️ Please enter a topic before generating a post.")

    if st.button("Back", type="secondary"):
        previous_step()



# Step 4: Generate New Post
elif st.session_state.current_step == 4:
    st.markdown("""
    <div class="step-content">
        <div class="step-title">🎉 Your Generated Post</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="success-card">
        <h4>Here’s what your LinkedIn post looks like:</h4>
    </div>
    <div id="generated-post" class="generated-post">
        {st.session_state.generated_post.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        render_copy_button("Copy Post", st.session_state.generated_post, button_id="copyPost")

    with col2:
        st.download_button(
            "Download as .txt",
            st.session_state.generated_post,
            "linkedin_post.txt",
            "text/plain"
        )

    with col3:
        if st.button("Start Over 🔄", type="secondary"):
            reset_session_state()

    st.markdown("---")
    progress = st.empty()

    # 👉 Extra controls below
    col4, col5 = st.columns([1, 1])

    with col4:
        if st.button("Estimate Virality 📊"):
            virality_result = run_agent_estimate_virality(st.session_state.generated_post)
            st.session_state.virality_score = virality_result["output"]
            progress.markdown(f"""
                <div class="success-card">
                    <h4>✅ Estimated Virality: {st.session_state.virality_score}</h4>
                </div>
            """, unsafe_allow_html=True)

    with col5:
        rewrite_instruction = st.text_input(
            "Rewrite Instruction",
            placeholder="e.g., make it more emotional"
        )
        if st.button("Rewrite Post ✏️"):
            if rewrite_instruction.strip():
                rewritten_post = run_agent_rewrite_post(
                    st.session_state.generated_post,
                    rewrite_instruction
                )
                st.session_state.generated_post = rewritten_post["output"]
                st.success("Post rewritten successfully!")
                st.rerun()
            else:
                st.warning("Please enter a rewrite instruction.")

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ for the AI Agent Challenge</p>
</div>
""",
            unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# # Clean up temporary files
# if st.session_state.mhtml_file and os.path.exists(st.session_state.mhtml_file):
#     try:
#         os.unlink(st.session_state.mhtml_file)
#     except:
#         pass  # Ignore cleanup errors
