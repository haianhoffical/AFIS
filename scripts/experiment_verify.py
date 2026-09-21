import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system import AFISSystem


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


# Genuine: cùng người nhưng dùng ảnh khác ảnh đăng ký
GENUINE_TESTS = [
    ("person01", "data/raw/101_3.tif"),
    ("person01", "data/raw/101_4.tif"),
    ("person02", "data/raw/102_2.tif"),
    ("person02", "data/raw/102_3.tif"),
    ("person02", "data/raw/102_4.tif"),
]


# Impostor: khác người
IMPOSTOR_TESTS = [
    ("person01", "data/raw/102_2.tif"),
    ("person02", "data/raw/101_3.tif"),
]


def setup_system(config, db_path):
    """
    Tạo AFISSystem với database riêng cho từng cấu hình.
    """

    # Đảm bảo database cũ của cấu hình này không tồn tại
    if os.path.exists(db_path):
        os.remove(db_path)

    # AFISSystem mở database sau khi file cũ đã được xóa
    system = AFISSystem(db_path=db_path)

    # Thay đổi các tham số preprocessing
    for key, value in config.items():
        if key in system.preprocessor.config:
            system.preprocessor.config[key] = value

    return system


def prepare_database(system):
    """
    Đăng ký đúng 1 mẫu cho mỗi người.

    person01 -> 101_1
    person02 -> 102_1
    """

    result1 = system.enroll(
        "data/raw/101_1.tif",
        "person01",
        finger_position=1
    )

    result2 = system.enroll(
        "data/raw/102_1.tif",
        "person02",
        finger_position=1
    )

    if result1 is None or result2 is None:
        raise RuntimeError(
            "Enrollment failed. Không thể tiếp tục đo FRR/FAR."
        )


def run_config(name, config):
    print("\n" + "=" * 70)
    print(f"CONFIGURATION: {name}")
    print("=" * 70)

    db_path = f"data/{name}_experiment.db"

    system = setup_system(config, db_path)

    try:
        # -----------------------------
        # ENROLLMENT
        # -----------------------------
        prepare_database(system)

        # -----------------------------
        # GENUINE
        # -----------------------------
        genuine_rejects = 0
        genuine_total = len(GENUINE_TESTS)

        print("\n--- GENUINE TESTS ---")

        for claimed_id, image_path in GENUINE_TESTS:

            is_match, score, details = system.verify(
                image_path,
                claimed_id
            )

            result = "MATCH" if is_match else "NO MATCH"

            print(
                f"{claimed_id} | "
                f"{os.path.basename(image_path)} | "
                f"{result} | "
                f"score={score:.3f}"
            )

            # Genuine bị từ chối = False Reject
            if not is_match:
                genuine_rejects += 1

        # -----------------------------
        # IMPOSTOR
        # -----------------------------
        impostor_accepts = 0
        impostor_total = len(IMPOSTOR_TESTS)

        print("\n--- IMPOSTOR TESTS ---")

        for claimed_id, image_path in IMPOSTOR_TESTS:

            is_match, score, details = system.verify(
                image_path,
                claimed_id
            )

            result = "MATCH" if is_match else "NO MATCH"

            print(
                f"{claimed_id} | "
                f"{os.path.basename(image_path)} | "
                f"{result} | "
                f"score={score:.3f}"
            )

            # Impostor được chấp nhận = False Accept
            if is_match:
                impostor_accepts += 1

        # -----------------------------
        # METRICS
        # -----------------------------
        frr = genuine_rejects / genuine_total * 100
        far = impostor_accepts / impostor_total * 100

        print("\n--- RESULTS ---")

        print(f"Genuine attempts : {genuine_total}")
        print(f"False Rejects    : {genuine_rejects}")
        print(f"FRR              : {frr:.2f}%")

        print(f"Impostor attempts: {impostor_total}")
        print(f"False Accepts    : {impostor_accepts}")
        print(f"FAR              : {far:.2f}%")

        return frr, far

    finally:
        # Đóng SQLite connection trước khi chuyển sang configuration khác
        system.database.close()


def main():

    results = {}

    for name, config in CONFIGS.items():

        results[name] = run_config(
            name,
            config
        )

    # -----------------------------
    # FINAL COMPARISON
    # -----------------------------

    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        f"{'Configuration':<25}"
        f"{'FRR':>10}"
        f"{'FAR':>10}"
    )

    print("-" * 50)

    for name, (frr, far) in results.items():

        print(
            f"{name:<25}"
            f"{frr:>9.2f}%"
            f"{far:>9.2f}%"
        )


if __name__ == "__main__":
    main()
