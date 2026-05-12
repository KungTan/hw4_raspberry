import os
import cv2
import mediapipe as mp
import pandas as pd
import numpy as np

# 初始化 MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)

def extract_landmarks(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        # 只取第一隻手
        hand_landmarks = results.multi_hand_landmarks[0]
        landmark_list = []
        for lm in hand_landmarks.landmark:
            # 儲存 x, y 座標 (z 座標在 2D 圖片中較不精確，可先忽略)
            landmark_list.extend([lm.x, lm.y])
        return landmark_list
    return None

def process_dataset(base_path):
    data = []
    label_map = {'rock': 0, 'paper': 1, 'scissors': 2}
    
    for category, label in label_map.items():
        category_path = os.path.join(base_path, category)
        if not os.path.exists(category_path):
            print(f"⚠️ 跳過 {category}，路徑不存在: {category_path}")
            continue
            
        print(f"📂 正在處理 {category}...")
        for filename in os.listdir(category_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(category_path, filename)
                landmarks = extract_landmarks(img_path)
                if landmarks:
                    data.append(landmarks + [label])
                    
    return data

def main():
    # 取得專案根目錄
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'dataset')
    
    all_data = []
    
    print("=== 開始提取訓練集特徵 ===")
    train_data = process_dataset(os.path.join(dataset_path, 'train'))
    all_data.extend(train_data)
    
    print("\n=== 開始提取測試集特徵 ===")
    test_data = process_dataset(os.path.join(dataset_path, 'test'))
    all_data.extend(test_data)
    
    if not all_data:
        print("❌ 錯誤：未提取到任何特徵，請檢查圖片是否清晰或路徑是否正確。")
        return
        
    # 轉換為 DataFrame 並儲存
    columns = [f'lm_{i}' for i in range(42)] + ['label']
    df = pd.DataFrame(all_data, columns=columns)
    
    output_path = os.path.join(base_dir, 'train', 'landmarks.csv')
    df.to_csv(output_path, index=False)
    print(f"\n✅ 特徵提取完成！總樣本數: {len(df)}")
    print(f"💾 已儲存至: {output_path}")

if __name__ == "__main__":
    main()
