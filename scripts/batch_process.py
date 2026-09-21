import os
import sys
import cv2
import numpy as np

# Cho phép import các module nằm ở thư mục gốc của project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing import PreprocessingPipeline
from features import FeatureExtractor


INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Khởi tạo pipeline tiền xử lý và bộ trích xuất đặc trưng
    preprocessor = PreprocessingPipeline()
    extractor = FeatureExtractor()

    image_files = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".tif", ".png", ".jpg", ".jpeg"))
    )

    print(f"Found {len(image_files)} images.")

    for filename in image_files:
        input_path = os.path.join(INPUT_DIR, filename)

        # Đọc ảnh vân tay ở dạng grayscale
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            print(f"[ERROR] Cannot read: {filename}")
            continue

        print(f"\nProcessing: {filename}")

        # Chạy toàn bộ pipeline tiền xử lý
        result = preprocessor.preprocess(image)

        skeleton = result["skeleton"]
        orientation = result["orientation"]

        # Trích xuất minutiae
        minutiae = extractor.extract_minutiae(
            skeleton,
            orientation
        )

        # Chuẩn hóa dữ liệu về X, Y, Theta
        data = np.array(
            [
                [m.x, m.y, m.orientation]
                for m in minutiae
            ],
            dtype=np.float32
        )

        # Nếu không có minutiae thì tạo mảng rỗng đúng kích thước
        if len(data) == 0:
            data = np.empty((0, 3), dtype=np.float32)

        output_name = os.path.splitext(filename)[0] + ".npy"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        np.save(output_path, data)

        print(f"  Minutiae: {len(minutiae)}")
        print(f"  Quality : {result['quality_score']:.3f}")
        print(f"  Saved   : {output_path}")

    print("\nBatch processing completed.")


if __name__ == "__main__":
    main()
