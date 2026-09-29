import streamlit as st

MOOD_DATA = {
    "Happiness": {
        "icon": "🌟",
        "theme_color": "#eab308",
        "badge": "ANCHOR & CELEBRATE",
        "affirmation": "My happiness is a reflection of my inner peace and growth. I deserve this moment.",
        "micro_actions": [
            "Write down 3 specific choices you made that helped bring this joy about.",
            "Send a 1-sentence gratitude message to someone who brightened your week.",
            "Take a 10-second pause to deeply feel this sensation so you can recall it later."
        ],
        "reflection_question": "How can you use this positive energy to support one of your goals today?",
        "suggested_resource": "🎵 **Vibe Check:** Play an upbeat playlist or take a walk outside to sustain this momentum."
    },
    "Stress": {
        "icon": "🌿",
        "theme_color": "#06b6d4",
        "badge": "RESET & UNBURDEN",
        "affirmation": "I don't have to tackle everything right now. One focused step is enough.",
        "micro_actions": [
            "Practice Box Breathing: Inhale for 4s, hold for 4s, exhale for 4s, hold for 4s (repeat 3x).",
            "Pick the single highest-priority task and hide everything else for 20 minutes.",
            "Unclench your jaw, drop your shoulders away from your ears, and drink water."
        ],
        "reflection_question": "What is one item on your task list today that can realistically wait until tomorrow?",
        "suggested_resource": "☕ **Micro-Break:** Step away from all digital screens for exactly 5 minutes."
    },
    "Sadness": {
        "icon": "💙",
        "theme_color": "#3b82f6",
        "badge": "COMFORT & COMPASSION",
        "affirmation": "It is completely okay to feel down. I treat myself with patience and grace.",
        "micro_actions": [
            "Wrap up in a comfortable blanket and listen to a gentle, low-tempo track.",
            "Step outside or near an open window for 3 minutes of natural daylight.",
            "Engage in a low-demand activity: drink hot tea, wash your face, or stretch softly."
        ],
        "reflection_question": "What is one small kindness you can offer yourself right now without judgment?",
        "suggested_resource": "🎧 **Audio Comfort:** Listen to ambient rain sounds or a gentle meditation track."
    },
    "Anger": {
        "icon": "🔥",
        "theme_color": "#ef4444",
        "badge": "PAUSE & CHANNEL",
        "affirmation": "Anger is just a signal that a boundary matters to me. I choose how I respond.",
        "micro_actions": [
            "Do 10 rapid jumping jacks, pushups, or wall-sits to release physical tension.",
            "Write down everything infuriating you on a scrap piece of paper, then delete or shred it.",
            "Put a 30-minute delay on sending any emotional emails or text responses."
        ],
        "reflection_question": "What personal boundary or core value feels threatened in this scenario?",
        "suggested_resource": "⏸️ **Pause Protocol:** Walk away from the current room before making any quick decisions."
    },
    "Fear": {
        "icon": "🛡️",
        "theme_color": "#a855f7",
        "badge": "GROUND & REASSURE",
        "affirmation": "Uncertainty is temporary. I am capable of handling whatever comes step by step.",
        "micro_actions": [
            "Use the 5-4-3-2-1 technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "Recall two past situations where you felt uncertain but managed to pull through.",
            "Focus only on planning the next 15 minutes instead of predicting the full week."
        ],
        "reflection_question": "What is the most likely realistic outcome here, and what is one thing you can control?",
        "suggested_resource": "📝 **Fact vs. Worry:** Write down facts in one column and your worries in another."
    },
    "Neutral": {
        "icon": "☕",
        "theme_color": "#64748b",
        "badge": "REFLECT & ALIGN",
        "affirmation": "Quiet days are opportunity spaces. Clear calm leads to clear thinking.",
        "micro_actions": [
            "Tidy one small space around you (desk, email inbox, or phone home screen).",
            "Review your personal goals for the month and track your current status.",
            "Take a short 10-minute walk without listening to podcasts or looking at notifications."
        ],
        "reflection_question": "What is one minor habit or project you would like to initiate this week?",
        "suggested_resource": "🎯 **Focus Time:** Use this balanced energy to draft or outline your upcoming plans."
    }
}


def render_ai_mood_booster(emotion: str):
    """Renders the AI Mood Booster Hub reliably using Streamlit's native st.html."""
    data = MOOD_DATA.get(emotion, MOOD_DATA["Neutral"])

    html_content = f"""<div style="
background: linear-gradient(135deg, rgba(22, 27, 46, 0.85), rgba(13, 15, 23, 0.95));
border: 1px solid {data['theme_color']}66;
border-left: 6px solid {data['theme_color']};
border-radius: 20px;
padding: 24px;
margin-top: 25px;
margin-bottom: 20px;
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
font-family: sans-serif;
">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
<span style="
background: {data['theme_color']}22;
color: {data['theme_color']};
border: 1px solid {data['theme_color']}44;
padding: 4px 14px;
border-radius: 30px;
font-size: 11px;
font-weight: 700;
letter-spacing: 1px;
">
{data['icon']} {data['badge']}
</span>
<span style="color: #94a3b8; font-size: 12px;">AI Wellness Guidance</span>
</div>
<h3 style="color: #ffffff; margin: 8px 0; font-size: 20px; font-weight: bold;">
Mood Booster: {emotion} Support Hub
</h3>
<p style="
color: #e2e8f0;
font-size: 15px;
font-style: italic;
background: rgba(255, 255, 255, 0.03);
padding: 12px 16px;
border-radius: 12px;
border: 1px dashed rgba(255, 255, 255, 0.1);
margin-top: 14px;
margin-bottom: 0;
">
💬 <b>Affirmation:</b> "{data['affirmation']}"
</p>
</div>"""

    st.html(html_content)

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("#### ⚡ Interactive Micro-Actions")
        st.caption("Check off small actions to help reset your mindset:")
        for idx, action in enumerate(data["micro_actions"]):
            st.checkbox(action, key=f"action_{emotion}_{idx}")

    with col2:
        st.markdown("#### 🤔 Reflection & Prompt")
        st.info(data["reflection_question"])

        reflection_response = st.text_input(
            "Quick thoughts on this prompt (optional):",
            placeholder="Type a sentence...",
            key=f"reflection_input_{emotion}",
        )

        if reflection_response:
            st.toast("💡 Reflection recorded!", icon="✅")

        st.markdown("---")
        st.markdown(data["suggested_resource"])