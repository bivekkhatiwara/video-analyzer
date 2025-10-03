import cv2
import pytesseract
import json
import time
from flask import Flask, request, jsonify, send_from_directory, render_template
import os

app = Flask(__name__)

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processing_status = {
    "is_processing": False,
    "current_frame": 0
}

def extract_text_from_video(video_path, frame_interval=30):
    global processing_status
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Could not open video file.")

    frame_count = 0
    extracted_texts = []
    
    processing_status["is_processing"] = True
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            if text.strip():
                extracted_texts.append(text.strip())
        
        frame_count += 1
        processing_status["current_frame"] = frame_count
    
    cap.release()
    processing_status["is_processing"] = False
    return " ".join(extracted_texts), frame_count

def heuristic_visibility(text):
    is_met = text.strip()
    message = "✅ Visibility present" if is_met else "⚠️ No visible text detected"
    prevention = "" if is_met else "Ensure system status is visible through clear, readable text or visual indicators on screen."
    return (is_met, message, prevention)

def heuristic_match_system(text):
    keywords = ["file", "edit", "view", "help"]
    is_met = any(k in text.lower() for k in keywords)
    message = "✅ Matches system language" if is_met else "⚠️ No standard system terms found"
    prevention = "" if is_met else "Use familiar and standard language, icons, and conventions that users already understand from the real world."
    return (is_met, message, prevention)

def heuristic_user_control(text):
    is_met = "cancel" in text.lower() or "back" in text.lower()
    message = "✅ User control available" if is_met else "⚠️ No clear user control options"
    prevention = "" if is_met else "Give users a sense of control and freedom with clear 'undo' and 'redo' options, and easy exits from actions."
    return (is_met, message, prevention)

def heuristic_consistency(text):
    is_met = "ok" in text.lower() or "yes" in text.lower()
    message = "✅ Consistent wording" if is_met else "⚠️ Possible inconsistency in wording"
    prevention = "" if is_met else "Maintain consistent terminology and design across all platforms. Don't make users wonder if different words mean the same thing."
    return (is_met, message, prevention)

def heuristic_error_prevention(text):
    is_met = "warning" in text.lower() or "required" in text.lower()
    message = "✅ Error prevention hints" if is_met else "⚠️ No error prevention hints"
    prevention = "" if is_met else "Design to prevent errors from happening in the first place by providing warnings and confirmations."
    return (is_met, message, prevention)

def heuristic_recognition(text):
    is_met = "search" in text.lower() or "find" in text.lower()
    message = "✅ Recognition supported" if is_met else "⚠️ No recognition terms"
    prevention = "" if is_met else "Make objects, actions, and options visible. Don't force users to rely on memory."
    return (is_met, message, prevention)

def heuristic_flexibility(text):
    is_met = "shortcut" in text.lower() or "customize" in text.lower()
    message = "✅ Flexible use supported" if is_met else "⚠️ No shortcuts or flexibility"
    prevention = "" if is_met else "Provide flexibility and efficiency for both novice and experienced users, such as accelerators or customization."
    return (is_met, message, prevention)

def heuristic_aesthetic(text):
    is_met = text.strip()
    message = "✅ Text available for aesthetic evaluation" if is_met else "⚠️ Cannot evaluate aesthetics without text"
    prevention = "" if is_met else "Ensure all visual elements are clean, clear, and focused on essential information. Remove anything that doesn't add value."
    return (is_met, message, prevention)

def heuristic_help(text):
    is_met = "help" in text.lower() or "support" in text.lower()
    message = "✅ Help/support info available" if is_met else "⚠️ No help options visible"
    prevention = "" if is_met else "Provide clear, concise, and easy-to-find help and documentation to assist users when they get stuck."
    return (is_met, message, prevention)

def heuristic_error_recovery(text):
    is_met = "retry" in text.lower() or "reset" in text.lower()
    message = "✅ Error recovery options" if is_met else "⚠️ No error recovery terms"
    prevention = "" if is_met else "Help users recognize, diagnose, and recover from errors with simple, plain-language messages."
    return (is_met, message, prevention)

heuristics = [
    ("Visibility of system status", heuristic_visibility),
    ("Match between system and real world", heuristic_match_system),
    ("User control and freedom", heuristic_user_control),
    ("Consistency and standards", heuristic_consistency),
    ("Error prevention", heuristic_error_prevention),
    ("Recognition rather than recall", heuristic_recognition),
    ("Flexibility and efficiency of use", heuristic_flexibility),
    ("Aesthetic and minimalist design", heuristic_aesthetic),
    ("Help and documentation", heuristic_help),
    ("Error recovery support", heuristic_error_recovery),
]

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')

@app.route('/ai')
def ai():
    return render_template("ai.html")

@app.route('/analyze', methods=['POST'])
def analyze_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if video_file:
        start_time = time.time()
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
        video_file.save(file_path)

        try:
            video_text, frame_count = extract_text_from_video(file_path)
            
            report = {}
            for name, func in heuristics:
                report[name] = func(video_text)
            
            end_time = time.time()
            report["Processing Time"] = f"{end_time - start_time:.2f} seconds"
            report["total_frames"] = frame_count
            report["extracted_text"] = video_text
            
            return jsonify(report)
        
        except IOError as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

@app.route('/status')
def get_status():
    return jsonify(processing_status)

if __name__ == '__main__':
    app.run(debug=True)

