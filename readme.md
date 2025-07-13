# Write Like Me – LinkedIn Ghostwriter ✍️

**📌 Hosted Demo:** [Write-Like-Me](https://write-like-me.streamlit.app/)

---

## Overview

**Problem:**  
Writing consistent, authentic LinkedIn posts is time-consuming—particularly mimicking your own voice. Where do you start?

**Solution:**  
*Write Like Me* learns your unique writing style from past posts and generates new, on-brand LinkedIn content with minimal input.

---

## 🧭 What It Does

1. **Upload your LinkedIn posts** (via MHTML export).  
2. The app **extracts and scores** posts for engagement.  
3. It uses Google Gemini to **analyze your tone, structure, emojis, keywords, openings, closings**.  
4. You can **copy your personal Style Guide** or enter a topic.  
5. **New posts are generated automatically**, matched to your voice—with copy and download options.

---

## 🛠️ System Architecture & Tools

| Component             | Technology                             | Purpose                                               |
|-----------------------|----------------------------------------|-------------------------------------------------------|
| **Frontend**          | Streamlit + HTML/CSS                   | Clean, step-by-step wizard UI                        |
| **Backend**           | Python modules                         | Handles file parsing, analysis, content generation   |
| **HTML Parsing**      | BeautifulSoup                          | Extracts LinkedIn text comfortably                  |
| **Style & Generation**| Gemini 2.5‑Flash via LangChain         | Fast AI-powered insights and writing aid             |
| **Text Cleanup**      | Regex / Local NLP                      | Removes UI artifacts, ensures readability            |
| **Clipboard/Download**| Custom JS + Streamlit components       | Instant copy, user-friendly download                 |

---

## 🧠 Skills Showcased

- Modern web app UI with **Streamlit** and refined custom CSS  
- Integration with **Google's Gemini AI** using LangChain  
- Data parsing with **BeautifulSoup**, regex, and NLP  
- JavaScript for in-browser **copy-to-clipboard** and UX feedback  
- UX design: clear 4‑step wizard, consistent styling, progressive feedback  
- Secure handling of local files and sensitive API keys  

---

## 🚀 Quick Start (Local)

1. Clone repo  
2. Set env variable: `export GEMINI_API_KEY="your_key"`  
3. Install dependencies: `pip install -r requirements.txt`  
4. Run app: `streamlit run app.py`

---

## 🌐 Production

- Hosted on Streamlit Cloud or similar  
- Secures API key via environment variables  
- Cleans up temporary MHTML files after use  
- Built-in error handling and adaptive feedback  
- AI usage optimized to minimize quota usage  

---

## 🛡️ Security & Privacy

- Posts are **processed locally**, without permanent storage  
- API key never exposed publicly  
- No logging or retention of personal LinkedIn content  

---

## 💬 Feedback & Contact

- GitHub: [@hilalsidhic](https://github.com/hilalsidhic)  
- Email: hilalsidhic21@gmail.com

*Want to see this integrated into your personal website? Reach out—I’d love to help build your custom AI content assistant.*

---

