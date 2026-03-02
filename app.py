import streamlit as st
from exercises import bicep_curls, dips, situps, plank, squats
import tempfile

st.set_page_config(page_title="AI Fitness Trainer", layout="centered")
st.title("🏋️ AI-Powered Fitness Trainer")

st.markdown("Select an exercise to begin:")

exercises = {
    "Bicep Curls": {
        "desc": "Track your bicep curl reps using pose estimation.",
        "func": bicep_curls
    },
    "Dips": {
        "desc": "Bodyweight dips using elbow angle tracking.",
        "func": dips
    },
    "Sit-Ups": {
        "desc": "Track sit-up reps by measuring torso angle.",
        "func": situps
    },
    "Plank": {
        "desc": "Real-time plank posture checker.",
        "func": plank
    },
    "Squats": {
        "desc": "Count squat reps using knee and hip angles.",
        "func": squats
    }
}

for name, val in exercises.items():

    st.subheader(name)

    with st.expander("ℹ️ Description"):
        st.write(val["desc"])

    mode = st.radio(
        f"Choose mode for {name}",
        ["Camera (Quick)", "Upload Video"],
        key=f"{name}_mode"
    )

    # ================= CAMERA MODE =================
    if mode == "Camera (Quick)":

        picture = st.camera_input(f"Take a picture for {name}")

        if picture is not None:
            st.image(picture)

            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(picture.getvalue())

            ai_reps = val["func"](tfile.name, live=False)

            st.success(f"Detected Reps (Single Frame): {ai_reps}")

    # ================= UPLOAD MODE =================
    else:

        uploaded_file = st.file_uploader(
            f"Upload video for {name}",
            type=["mp4", "mov", "avi"],
            key=f"{name}_upload"
        )

        if uploaded_file is not None:

            actual_reps_upload = st.number_input(
                f"Enter Actual Reps for {name}",
                min_value=1,
                step=1,
                key=f"{name}_upload_actual"
            )

            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())

            if st.button(f"▶️ Process {name} Video"):

                ai_reps = val["func"](tfile.name, live=False)

                accuracy = (
                    1 - abs(actual_reps_upload - ai_reps)
                    / actual_reps_upload
                ) * 100

                st.success(f"🏆 AI Reps: {ai_reps}")
                st.success(f"🎯 Accuracy: {accuracy:.2f}%")

    st.markdown("---")
