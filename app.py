import streamlit as st
from exercises import bicep_curls, dips, situps, plank, squats
import tempfile

st.set_page_config(page_title="AI Fitness Trainer", layout="centered")
st.title("🏋️ AI-Powered Fitness Trainer")

st.markdown("Upload a video to analyze your exercise form and count reps.")

exercises = {
    "Bicep Curls": {
        "desc": "Track your bicep curl reps using elbow angle.",
        "func": bicep_curls
    },
    "Dips": {
        "desc": "Bodyweight dips using elbow and shoulder tracking.",
        "func": dips
    },
    "Sit-Ups": {
        "desc": "Track sit-up reps by measuring torso angle.",
        "func": situps
    },
    "Plank": {
        "desc": "Check plank posture alignment.",
        "func": plank
    },
    "Squats": {
        "desc": "Count squat reps using knee angle.",
        "func": squats
    }
}

for name, val in exercises.items():

    st.subheader(name)

    with st.expander("ℹ️ Description"):
        st.write(val["desc"])

    uploaded_file = st.file_uploader(
        f"Upload video for {name}",
        type=["mp4", "mov", "avi"],
        key=f"{name}_upload"
    )

    if uploaded_file is not None:

        actual_reps = st.number_input(
            f"Enter Actual Reps for {name}",
            min_value=1,
            step=1,
            key=f"{name}_actual"
        )

        # Save uploaded file temporarily
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        if st.button(f"▶️ Process {name} Video"):

            with st.spinner("Processing video... Please wait."):
                ai_reps = val["func"](tfile.name)

            accuracy = (
                1 - abs(actual_reps - ai_reps)
                / actual_reps
            ) * 100

            st.success(f"🏆 AI Counted Reps: {ai_reps}")
            st.success(f"✅ Accuracy: {accuracy:.2f}%")

    st.markdown("---")
