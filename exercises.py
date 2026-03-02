import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# ------------------ Angle Calculator ------------------ #
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


# ------------------ Main Processing Engine ------------------ #
def process_exercise(source, exercise_type, live):

    counter = 0
    stage = None

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        st.error("❌ Could not open video source.")
        return 0

    frame_placeholder = st.empty()

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65
    ) as pose:

        angle_history = []
        SMOOTH_WINDOW = 4

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                # ================= BICEP =================
                if exercise_type == "bicep":

                    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

                    if shoulder.visibility < 0.6 or elbow.visibility < 0.6:
                        continue

                    angle = calculate_angle(
                        [shoulder.x, shoulder.y],
                        [elbow.x, elbow.y],
                        [wrist.x, wrist.y]
                    )

                # ================= SQUAT =================
                elif exercise_type == "squat":

                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                    ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

                    if hip.visibility < 0.6 or knee.visibility < 0.6:
                        continue

                    angle = calculate_angle(
                        [hip.x, hip.y],
                        [knee.x, knee.y],
                        [ankle.x, ankle.y]
                    )

                # ================= SITUP =================
                elif exercise_type == "situp":

                    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]

                    if shoulder.visibility < 0.6 or hip.visibility < 0.6:
                        continue

                    angle = calculate_angle(
                        [shoulder.x, shoulder.y],
                        [hip.x, hip.y],
                        [knee.x, knee.y]
                    )

                # ================= DIPS =================
                elif exercise_type == "dips":

                    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

                    if shoulder.visibility < 0.6 or elbow.visibility < 0.6:
                        continue

                    angle = calculate_angle(
                        [shoulder.x, shoulder.y],
                        [elbow.x, elbow.y],
                        [hip.x, hip.y]
                    )

                # ================= PLANK =================
                elif exercise_type == "plank":

                    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

                    if shoulder.visibility < 0.6 or hip.visibility < 0.6:
                        continue

                    angle = calculate_angle(
                        [shoulder.x, shoulder.y],
                        [hip.x, hip.y],
                        [ankle.x, ankle.y]
                    )

                    if 160 < angle < 180:
                        cv2.putText(image, "GOOD POSTURE",
                                    (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 255, 0), 2)
                    else:
                        cv2.putText(image, "BAD POSTURE",
                                    (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (0, 0, 255), 2)

                # ---------- Angle Smoothing ----------
                angle_history.append(angle)
                if len(angle_history) > SMOOTH_WINDOW:
                    angle_history.pop(0)

                angle = np.mean(angle_history)

                # ---------- REP LOGIC ----------
                if exercise_type != "plank":

                    if angle > 160:
                        stage = "down"

                    if angle < 90 and stage == "down":
                        stage = "up"
                        counter += 1

                cv2.putText(image, f'REPS: {counter}',
                            (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            # ---------- DISPLAY ----------
            if live:
                cv2.imshow("Exercise", image)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                frame_placeholder.image(image, channels="BGR")
                time.sleep(0.02)

    cap.release()
    cv2.destroyAllWindows()

    if not live:
        st.success(f"🏆 Total Reps: {counter}")

    return counter


# ------------------ Wrappers ------------------ #
def bicep_curls(source, live):
    return process_exercise(source, "bicep", live)


def squats(source, live):
    return process_exercise(source, "squat", live)


def situps(source, live):
    return process_exercise(source, "situp", live)


def dips(source, live):
    return process_exercise(source, "dips", live)


def plank(source, live):
    return process_exercise(source, "plank", live)