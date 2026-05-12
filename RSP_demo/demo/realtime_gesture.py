import cv2
import mediapipe as mp
import joblib
import numpy as np
import os

# 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

def preprocess_landmarks(landmarks):
    """將 MediaPipe 傳回的 landmarks 轉為模型可用的相對座標"""
    wrist = landmarks[0]
    relative_coords = []
    for lm in landmarks:
        relative_coords.extend([lm.x - wrist.x, lm.y - wrist.y])
    return np.array(relative_coords).reshape(1, -1)

def main():
    # 載入模型
    model_path = os.path.join(os.path.dirname(__file__), 'rps_mediapipe_svm.pkl')
    if not os.path.exists(model_path):
        print(f"❌ 錯誤：找不到模型 {model_path}，請確認是否已訓練。")
        return
        
    clf = joblib.load(model_path)
    label_map = {0: 'Rock (石頭)', 1: 'Paper (布)', 2: 'Scissors (剪刀)'}
    
    cap = cv2.VideoCapture(0)
    print("🚀 啟動相機中... 按下 'q' 鍵退出。")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # 為了提升效能，先將影像轉為唯讀並轉換顏色空間
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # 轉回 BGR 準備畫圖
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 取得影像的寬度與高度
        h, w, _ = image.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                
                # 1. 計算並繪製手部邊界框 (Bounding Box)
                x_max = 0
                y_max = 0
                x_min = w
                y_min = h
                
                for lm in hand_landmarks.landmark:
                    x, y = int(lm.x * w), int(lm.y * h)
                    if x > x_max: x_max = x
                    if x < x_min: x_min = x
                    if y > y_max: y_max = y
                    if y < y_min: y_min = y
                
                # 加上一點 padding，繪製矩形框 (顏色為綠色，粗細為 2)
                cv2.rectangle(image, (max(0, x_min - 20), max(0, y_min - 20)), 
                              (min(w, x_max + 20), min(h, y_max + 20)), (0, 255, 0), 2)

                # 2. 繪製手部骨架
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                # 3. 預測手勢
                features = preprocess_landmarks(hand_landmarks.landmark)
                prediction = clf.predict(features)[0]
                probability = clf.predict_proba(features)[0][prediction]
                label = label_map.get(prediction, "Unknown")

                # 3. 顯示結果 (在畫面上方顯示文字)
                text = f"{label} ({probability*100:.1f}%)"
                cv2.putText(image, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                            1.2, (0, 255, 0), 3, cv2.LINE_AA)

        cv2.imshow('RSP Hand Gesture Recognition', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
