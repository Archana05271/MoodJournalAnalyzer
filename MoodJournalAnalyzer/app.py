import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import date

# Import the mood booster function from your mood_booster.py file
from mood_booster import render_ai_mood_booster

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="MindScope | Journal Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# LOAD CSS
# ==========================================================

def load_css():
    css_file = "style.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )

load_css()

# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "journal_entries.csv")
os.makedirs(DATA_FOLDER, exist_ok=True)

COLUMNS = ["Date", "Journal", "Emotion", "Sentiment", "Keywords", "Topics"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)

# ==========================================================
# DATA FUNCTIONS
# ==========================================================

def load_entries():
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        for column in COLUMNS:
            if column not in df.columns:
                df[column] = ""
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_entry(journal_date, journal, emotion, sentiment, keywords, topics):
    new_entry = pd.DataFrame([{
        "Date": str(journal_date),
        "Journal": journal,
        "Emotion": emotion,
        "Sentiment": sentiment,
        "Keywords": ", ".join(keywords),
        "Topics": ", ".join(topics)
    }])
    old_data = load_entries()
    final_data = pd.concat([old_data, new_entry], ignore_index=True)
    final_data.to_csv(DATA_FILE, index=False)

# ==========================================================
# TEXT PREPROCESSING & NLP
# ==========================================================

STOP_WORDS = {
    "the", "and", "that", "this", "with", "from", "have", "was",
    "were", "been", "very", "today", "into", "about", "after",
    "before", "then", "they", "them", "their", "there", "here",
    "what", "when", "where", "which", "while", "because", "just",
    "really", "also", "felt", "feel", "feeling", "had", "has",
    "for", "are", "but", "not", "you", "your", "our", "my"
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

EMOTION_KEYWORDS = {
    "Happiness": ["happy", "joy", "joyful", "excited", "great", "amazing", "wonderful", "good", "love", "enjoy", "enjoyed", "proud", "success", "successful", "fun", "smile", "celebrate"],
    "Sadness": ["sad", "unhappy", "lonely", "cry", "crying", "depressed", "disappointed", "heartbroken", "upset", "miss", "missing", "loss"],
    "Anger": ["angry", "anger", "furious", "frustrated", "frustration", "hate", "annoyed", "annoying", "irritated", "irritation"],
    "Fear": ["afraid", "scared", "fear", "worried", "worry", "nervous", "panic", "danger", "uncertain", "anxious"],
    "Stress": ["stress", "stressed", "pressure", "deadline", "deadlines", "overwhelmed", "exhausted", "tired", "busy", "workload", "tension"],
    "Neutral": ["normal", "ordinary", "okay", "fine", "regular", "usual", "routine"]
}

def predict_emotion(text):
    cleaned = clean_text(text)
    words = cleaned.split()
    scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in words)
        scores[emotion] = score
    total = sum(scores.values())
    if total == 0:
        percentages = {emotion: 0 for emotion in EMOTION_KEYWORDS}
        percentages["Neutral"] = 100
        return "Neutral", percentages
    prediction = max(scores, key=scores.get)
    percentages = {emotion: round(score / total * 100, 1) for emotion, score in scores.items()}
    return prediction, percentages

def extract_keywords(text, limit=8):
    words = clean_text(text).split()
    frequency = {}
    for word in words:
        if len(word) > 3 and word not in STOP_WORDS:
            frequency[word] = frequency.get(word, 0) + 1
    ranked = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in ranked[:limit]]

TOPIC_KEYWORDS = {
    "Academic Work": ["study", "studied", "exam", "assignment", "college", "class", "lecture", "project", "homework", "learning", "learn", "student", "presentation"],
    "Work": ["work", "office", "meeting", "job", "manager", "deadline", "task", "employee", "company", "client"],
    "Family": ["family", "mother", "father", "brother", "sister", "parents", "home"],
    "Friends": ["friend", "friends", "party", "hangout", "together", "chat", "conversation"],
    "Health": ["health", "doctor", "hospital", "exercise", "sleep", "tired", "fitness", "walk", "workout"],
    "Travel": ["travel", "trip", "journey", "vacation", "hotel", "beach", "tour", "visit"],
    "Finance": ["money", "salary", "expense", "shopping", "budget", "cost", "payment"]
}

def detect_topics(text):
    words = clean_text(text).split()
    results = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        count = sum(1 for keyword in keywords if keyword in words)
        if count > 0:
            results.append((topic, count))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

POSITIVE_WORDS = {"happy", "good", "great", "amazing", "wonderful", "excited", "love", "success", "completed", "enjoyed", "proud", "fun", "joy", "excellent", "beautiful"}
NEGATIVE_WORDS = {"sad", "bad", "stress", "stressed", "angry", "hate", "worried", "afraid", "terrible", "difficult", "tired", "lonely", "frustrated", "upset", "nervous", "pressure"}

def analyze_sentiment(text):
    words = clean_text(text).split()
    positive = sum(word in POSITIVE_WORDS for word in words)
    negative = sum(word in NEGATIVE_WORDS for word in words)
    if positive > 0 and negative > 0:
        return "Mixed"
    if positive > negative:
        return "Positive"
    if negative > positive:
        return "Negative"
    return "Neutral"

SAMPLE_JOURNAL = (
    "Today I had a lot of work and felt stressed in the morning. I had an important project deadline "
    "and was worried about completing it. In the afternoon, I finished my project and felt very happy "
    "and proud. I also talked with my friends and enjoyed the evening."
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown(
        """<div class="sidebar-brand">
            <div class="brand-icon">🧠</div>
            <div class="brand-name">MindScope</div>
            <div class="brand-subtitle">Personal Journal Intelligence</div>
        </div>""",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown('<div class="nav-title">EXPLORE</div>', unsafe_allow_html=True)

    menu = st.radio(
        "",
        [
            "🏠 Home",
            "✍️ Journal Studio",
            "😊 Emotion Timeline",
            "📚 Life Themes",
            "📊 Insight Center",
            "🔍 Entry Search & Export"
        ]
    )

    st.markdown("---")
    st.markdown(
        """<div class="sidebar-footer">
            <b>MindScope NLP</b><br>
            Emotion • Keywords • Themes • Trends
        </div>""",
        unsafe_allow_html=True
    )

# ==========================================================
# HOME
# ==========================================================

if menu == "🏠 Home":
    st.markdown(
        """<div class="hero">
            <div class="hero-content">
                <div class="hero-badge">✦ NLP • Emotion • Personal Insights</div>
                <h1>Understand Your Words.<br>Discover Your Patterns.</h1>
                <p>MindScope transforms everyday journal entries into meaningful emotional, thematic and linguistic insights using Natural Language Processing.</p>
            </div>
            <div class="hero-emoji">🧠</div>
        </div>""",
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">What can MindScope discover?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">A simple NLP pipeline that turns free-form journal text into structured insights.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("😊", "Emotional Signal", "Identify the dominant emotional pattern in your journal."),
        ("🔑", "Key Phrases", "Extract meaningful words that represent your entry."),
        ("📚", "Life Themes", "Discover recurring areas such as study, work and family."),
        ("📈", "Personal Trends", "Explore how your journal patterns change over time.")
    ]

    for column, card in zip([c1, c2, c3, c4], cards):
        with column:
            st.markdown(
                f"""<div class="feature-card">
                    <div class="feature-icon">{card[0]}</div>
                    <h3>{card[1]}</h3>
                    <p>{card[2]}</p>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-heading">How MindScope works</div>', unsafe_allow_html=True)
    pipeline = [
        ("01", "📝", "Input", "Journal Entry"),
        ("02", "🧹", "Prepare", "Text Cleaning"),
        ("03", "😊", "Classify", "Emotion Detection"),
        ("04", "🔑", "Extract", "Keyword Extraction"),
        ("05", "📚", "Discover", "Topic Detection"),
        ("06", "💭", "Analyze", "Sentiment Analysis"),
        ("07", "💾", "Store", "CSV Storage"),
        ("08", "📊", "Visualize", "Interactive Dashboard")
    ]

    pipeline_columns = st.columns(4)
    for index, item in enumerate(pipeline):
        with pipeline_columns[index % 4]:
            st.markdown(
                f"""<div class="pipeline-card">
                    <span class="pipeline-number">{item[0]}</span>
                    <div class="pipeline-icon">{item[1]}</div>
                    <div class="pipeline-title">{item[2]}</div>
                    <div class="pipeline-description">{item[3]}</div>
                </div>""",
                unsafe_allow_html=True
            )

# ==========================================================
# JOURNAL STUDIO
# ==========================================================

elif menu == "✍️ Journal Studio":
    st.markdown('<div class="page-title">✍️ Journal Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Write freely. Let MindScope transform your words into insights.</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown(
            """<div class="studio-info">
                <div class="studio-icon">✍️</div>
                <h2>Your Journal</h2>
                <p>Write about your day, studies, work, friends, family, achievements or challenges.</p>
                <div class="tip">💡 Tip: Write at least a few sentences for better analysis.</div>
            </div>""",
            unsafe_allow_html=True
        )

        journal_date = st.date_input("Entry Date", value=date.today())

        if st.button("✨ Load Sample", use_container_width=True):
            st.session_state["journal_text"] = SAMPLE_JOURNAL
            st.rerun()

    with right:
        journal = st.text_area(
            "Journal Entry",
            value=st.session_state.get("journal_text", ""),
            height=280,
            placeholder="Start writing here..."
        )

        word_count = len(journal.split())
        st.caption(f"📝 {word_count} words")

        generate = st.button("🧠 Analyze My Journal", use_container_width=True)

    if generate:
        if not journal.strip():
            st.warning("Please write something before analyzing.")
            st.stop()

        if word_count < 5:
            st.warning("Please write at least 5 words.")
            st.stop()

        with st.spinner("MindScope is analyzing your journal..."):
            emotion, emotion_scores = predict_emotion(journal)
            keywords = extract_keywords(journal)
            topics = detect_topics(journal)
            sentiment = analyze_sentiment(journal)

        topic_names = [topic for topic, count in topics]
        save_entry(journal_date, journal, emotion, sentiment, keywords, topic_names)

        st.success("✨ Analysis complete! Your journal insights are ready.")

        st.markdown('<div class="section-heading">Your Journal Snapshot</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(f"""<div class="result-card"><div class="result-icon">😊</div><div class="result-label">MAIN EMOTION</div><div class="result-value">{emotion}</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="result-card"><div class="result-icon">💭</div><div class="result-label">OVERALL TONE</div><div class="result-value">{sentiment}</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="result-card"><div class="result-icon">🔑</div><div class="result-label">KEY PHRASES</div><div class="result-value">{len(keywords)}</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="result-card"><div class="result-icon">📚</div><div class="result-label">LIFE THEMES</div><div class="result-value">{len(topics)}</div></div>""", unsafe_allow_html=True)

        # Calls function directly from mood_booster.py
        render_ai_mood_booster(emotion)

        st.markdown('<div class="section-heading">😊 Emotional Signals</div>', unsafe_allow_html=True)
        emotion_columns = st.columns(3)
        sorted_scores = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

        for index, (emotion_name, score) in enumerate(sorted_scores):
            with emotion_columns[index % 3]:
                st.markdown(f"""<div class="emotion-card"><div class="emotion-name">{emotion_name}</div><div class="emotion-score">{score:.1f}%</div></div>""", unsafe_allow_html=True)
                st.progress(int(score))

        st.markdown('<div class="section-heading">🔑 Key Phrases</div>', unsafe_allow_html=True)
        if keywords:
            keyword_html = "".join([f'<span class="keyword-tag">#{keyword}</span>' for keyword in keywords])
            st.markdown(keyword_html, unsafe_allow_html=True)

        st.markdown('<div class="section-heading">📚 Life Themes</div>', unsafe_allow_html=True)
        if topics:
            topic_columns = st.columns(min(3, len(topics)))
            for index, (topic, count) in enumerate(topics):
                with topic_columns[index % len(topic_columns)]:
                    st.markdown(f"""<div class="theme-card"><div class="theme-icon">📚</div><b>{topic}</b><p>{count} signal(s) detected</p></div>""", unsafe_allow_html=True)

# ==========================================================
# EMOTION TIMELINE
# ==========================================================

elif menu == "😊 Emotion Timeline":
    st.markdown('<div class="page-title">😊 Emotion Timeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Explore how emotional signals appear across your journal history.</div>', unsafe_allow_html=True)

    df = load_entries()
    if df.empty:
        st.info("No journal entries yet. Start with Journal Studio.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    total = len(df)
    common_emotion = df["Emotion"].mode().iloc[0] if not df["Emotion"].mode().empty else "None"
    positive = len(df[df["Sentiment"] == "Positive"])
    negative = len(df[df["Sentiment"] == "Negative"])

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("📖 Entries", total)
    with m2: st.metric("😊 Common Emotion", common_emotion)
    with m3: st.metric("🌱 Positive", positive)
    with m4: st.metric("🌧️ Negative", negative)

    st.markdown('<div class="section-heading">📊 Emotion Frequency</div>', unsafe_allow_html=True)
    emotion_counts = df["Emotion"].value_counts().reset_index()
    emotion_counts.columns = ["Emotion", "Count"]

    fig = px.bar(emotion_counts, x="Emotion", y="Count", text="Count", color="Emotion", title="Detected Emotional Signals", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# LIFE THEMES
# ==========================================================

elif menu == "📚 Life Themes":
    st.markdown('<div class="page-title">📚 Life Themes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Discover recurring subjects hidden inside your journal history.</div>', unsafe_allow_html=True)

    df = load_entries()
    if df.empty:
        st.info("No journal entries available yet.")
        st.stop()

    topic_counts = {}
    for topics in df["Topics"].dropna():
        for topic in str(topics).split(","):
            topic = topic.strip()
            if topic:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

    if not topic_counts:
        st.warning("No themes have been detected yet.")
        st.stop()

    topic_df = pd.DataFrame(list(topic_counts.items()), columns=["Theme", "Entries"]).sort_values("Entries", ascending=False)

    st.markdown('<div class="section-heading">📊 Theme Frequency</div>', unsafe_allow_html=True)
    fig = px.bar(topic_df, x="Theme", y="Entries", text="Entries", color="Theme", title="Recurring Journal Themes", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# INSIGHT CENTER
# ==========================================================

elif menu == "📊 Insight Center":
    st.markdown('<div class="page-title">📊 Insight Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">A visual overview of your journal activity and NLP results.</div>', unsafe_allow_html=True)

    df = load_entries()
    if df.empty:
        st.info("Your dashboard is waiting for data. Create journal entries first.")
        st.stop()

    left, right = st.columns(2)
    with left:
        emotion_counts = df["Emotion"].value_counts().reset_index()
        emotion_counts.columns = ["Emotion", "Count"]
        fig1 = px.pie(emotion_counts, names="Emotion", values="Count", hole=0.45, title="Emotion Distribution", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        sentiment_counts = df["Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        fig2 = px.pie(sentiment_counts, names="Sentiment", values="Count", hole=0.45, title="Overall Tone", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# ENTRY SEARCH & EXPORT
# ==========================================================

elif menu == "🔍 Entry Search & Export":
    st.markdown('<div class="page-title">🔍 Entry Search & Export</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-description">Filter through your journal history and export data for backup.</div>', unsafe_allow_html=True)

    df = load_entries()
    if df.empty:
        st.info("No entries to search or export.")
        st.stop()

    search_query = st.text_input("🔍 Search entries by keyword or text:")
    selected_emotion = st.selectbox("Filter by Emotion:", ["All"] + list(EMOTION_KEYWORDS.keys()))

    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["Journal"].str.contains(search_query, case=False, na=False)]
    if selected_emotion != "All":
        filtered_df = filtered_df[filtered_df["Emotion"] == selected_emotion]

    st.markdown(f"### Found {len(filtered_df)} Entry(ies)")
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Journal Entries to CSV",
        data=csv_data,
        file_name="mindscope_journal_export.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """<div class="footer">
        <b>MindScope</b> • Personal Journal Intelligence
        <br>
        Built with Python • Streamlit • NLP • Pandas • Plotly
    </div>""",
    unsafe_allow_html=True
)