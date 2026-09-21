import os
import cv2
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing import PreprocessingPipeline
from features import FeatureExtractor


INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/experiments"


CONFIGS = {
    "baseline": {
        "gabor_kernel_size": 21,
        "gabor_sigma": 4.0,
        "gabor_gamma": 0.5,
        "adaptive_block_size": 11,
        "adaptive_c": 2,
    },

    "gabor_changed": {
        "gabor_kernel_size": 31,
        "gabor_sigma": 5.0,
        "gabor_gamma": 0.5,
        "adaptive_block_size": 11,
        "adaptive_c": 2,
    },

    "binarization_changed": {
        "gabor_kernel_size": 21,
        "gabor_sigma": 4.0,
        "gabor_gamma": 0.5,
        "adaptive_block_size": 15,
        "adaptive_c": 3,
    },
}


def process_config(name, config):
    print("\n" + "=" * 60)
    print(f"CONFIGURATION: {name}")
    print("=" * 60)

    output_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(output_dir, exist_ok=True)

    preprocessor = PreprocessingPipeline(config)
    extractor = FeatureExtractor()

    image_files = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".tif", ".png", ".jpg", ".jpeg"))
    )

    for filename in image_files:
        path = os.path.join(INPUT_DIR, filename)

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            print(f"[ERROR] Cannot read {filename}")
            continue

        result = preprocessor.preprocess(image)

        minutiae = extractor.extract_minutiae(
            result["skeleton"],
            result["orientation"]
        )

        data = np.array(
            [[m.x, m.y, m.orientation] for m in minutiae],
            dtype=np.float32
        )

        if len(data) == 0:
            data = np.empty((0, 3), dtype=np.float32)

        output_path = os.path.join(
            output_dir,
            os.path.splitext(filename)[0] + ".npy"
        )

        np.save(output_path, data)

        print(
            f"{filename}: "
            f"minutiae={len(minutiae)}, "
            f"quality={result['quality_score']:.3f}"
        )


def main():
    for name, config in CONFIGS.items():
        process_config(name, config)

    print("\nAll experiments completed.")


if __name__ == "__main__":
    main()
