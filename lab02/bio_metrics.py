# -*- coding: utf-8 -*-
"""bio_metrics.py: thư viện đo hiệu năng do sinh viên tự viết trong TH01."""

from __future__ import annotations

import numpy as np

try:
    from scipy.stats import norm
except ImportError:
    norm = None


def _as_array(x):
    arr = np.asarray(x, dtype=np.float64).ravel()
    if arr.size == 0:
        raise ValueError("Mảng điểm rỗng: kiểm tra lại bước đọc dữ liệu.")
    return arr


def error_rates(genuine, impostor, thresholds=None, higher_is_better=True):
    """Tính FMR và FNMR tại từng ngưỡng."""
    gen = _as_array(genuine)
    imp = _as_array(impostor)

    if not higher_is_better:
        gen, imp = -gen, -imp
        if thresholds is not None:
            thresholds = -np.asarray(thresholds, dtype=np.float64)

    if thresholds is None:
        all_scores = np.unique(np.concatenate([gen, imp]))
        thresholds = np.append(all_scores, all_scores[-1] + 1e-9)
    else:
        thresholds = np.sort(np.asarray(thresholds, dtype=np.float64))

    gen_sorted = np.sort(gen)
    imp_sorted = np.sort(imp)

    # score < threshold bị từ chối.
    # side="left" => score == threshold được chấp nhận.
    fnmr = np.searchsorted(
        gen_sorted, thresholds, side="left"
    ) / gen.size

    # score >= threshold được chấp nhận.
    imp_below = np.searchsorted(
        imp_sorted, thresholds, side="left"
    )
    fmr = (imp.size - imp_below) / imp.size

    if not higher_is_better:
        thresholds = -thresholds

    return thresholds, fmr, fnmr


def eer(genuine, impostor, higher_is_better=True):
    """Tính tỷ lệ lỗi cân bằng (EER)."""
    thresholds, fmr, fnmr = error_rates(
        genuine, impostor, higher_is_better=higher_is_better
    )

    diff = fmr - fnmr
    crossing = np.where(diff <= 0)[0]

    if crossing.size == 0:
        k = len(diff) - 1
        eer_interp = float((fmr[k] + fnmr[k]) / 2)
    else:
        i = int(crossing[0])

        if i == 0:
            k = 0
            eer_interp = float((fmr[k] + fnmr[k]) / 2)
        else:
            candidates = [i - 1, i]
            k = min(candidates, key=lambda j: abs(diff[j]))
            eer = float((fmr[k] + fnmr[k]) / 2)

            if diff[i - 1] == diff[i]:
                eer_interp = eer
            else:
                w = diff[i - 1] / (diff[i - 1] - diff[i])
                eer_interp = float(
                    fmr[i - 1] + w * (fmr[i] - fmr[i - 1])
                )

    return {
        "eer": float((fmr[k] + fnmr[k]) / 2),
        "eer_interp": float(eer_interp),
        "threshold": float(thresholds[k]),
        "fmr": float(fmr[k]),
        "fnmr": float(fnmr[k]),
    }


def fnmr_at_fmr(genuine, impostor, target_fmr, higher_is_better=True):
    """FNMR tại ngưỡng dễ dãi nhất vẫn bảo đảm FMR <= target_fmr."""
    thresholds, fmr, fnmr = error_rates(
        genuine, impostor, higher_is_better=higher_is_better
    )

    valid = np.where(fmr <= target_fmr)[0]
    if valid.size == 0:
        raise ValueError("Không có ngưỡng nào đạt target_fmr.")

    i = int(valid[0])
    return float(fnmr[i]), float(thresholds[i]), float(fmr[i])


def decidability(genuine, impostor):
    """Chỉ số phân tách d'."""
    gen = _as_array(genuine)
    imp = _as_array(impostor)

    mu_g = np.mean(gen)
    mu_i = np.mean(imp)
    var_g = np.var(gen)
    var_i = np.var(imp)

    return float(
        abs(mu_g - mu_i) / np.sqrt((var_g + var_i) / 2)
    )


def roc_auc(fmr, fnmr):
    """Diện tích dưới đường ROC."""
    fmr = np.asarray(fmr, dtype=np.float64)
    fnmr = np.asarray(fnmr, dtype=np.float64)
    tpr = 1.0 - fnmr

    order = np.lexsort((tpr, fmr))
    fmr_sorted = fmr[order]
    tpr_sorted = tpr[order]

    return float(np.trapezoid(tpr_sorted, fmr_sorted))


def fpir_from_fmr(fmr, n_gallery):
    """Xấp xỉ FPIR của tìm kiếm 1:N."""
    fmr = np.asarray(fmr, dtype=np.float64)
    return 1.0 - np.power(1.0 - fmr, n_gallery)


DET_TICKS = [0.0001, 0.001, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
DET_TICK_LABELS = ["0,01", "0,1", "1", "2", "5", "10", "20", "40"]
EER_MARKERS = ["o", "s", "^", "D", "v"]


def _probit(p, lo=1e-5):
    """Biến đổi xác suất sang normal deviate cho trục DET."""
    if norm is None:
        raise ImportError("scipy.stats.norm cần thiết cho _probit.")

    p = np.asarray(p, dtype=np.float64)
    p = np.clip(p, lo, 1.0 - lo)
    return norm.ppf(p)


def plot_det(curves, path, title="Đường cong DET", eer_points=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    for i, (name, (fmr, fnmr)) in enumerate(curves.items()):
        line, = ax.plot(_probit(fmr), _probit(fnmr), lw=2, label=name)
        if eer_points and name in eer_points:
            e = eer_points[name]
            ax.plot(_probit(e), _probit(e), EER_MARKERS[i % len(EER_MARKERS)],
                    color=line.get_color(), ms=7, mfc="none", mew=1.8)
    ticks = _probit(np.array(DET_TICKS))
    ax.set_xticks(ticks, DET_TICK_LABELS)
    ax.set_yticks(ticks, DET_TICK_LABELS)
    lim = (_probit(0.00005), _probit(0.5))
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.plot(lim, lim, ls=":", color="grey", lw=1)
    ax.set_xlabel("FMR (%)")
    ax.set_ylabel("FNMR (%)")
    ax.set_title(title)
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_roc(curves, path, title="Đường cong ROC"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    for name, (fmr, fnmr) in curves.items():
        ax.plot(np.clip(fmr, 1e-5, 1), 1 - np.asarray(fnmr), lw=2, label=name)
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1)
    ax.set_xlabel("FMR (thang log)")
    ax.set_ylabel("1 - FNMR")
    ax.set_title(title)
    ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_distributions(systems, path, title="Phân bố điểm so khớp"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(systems)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 3.4), squeeze=False)
    for ax, (name, (gen, imp)) in zip(axes[0], systems.items()):
        bins = np.linspace(min(np.min(gen), np.min(imp)), max(np.max(gen), np.max(imp)), 60)
        ax.hist(imp, bins=bins, density=True, alpha=0.55, label="khác người")
        ax.hist(gen, bins=bins, density=True, alpha=0.55, label="cùng người")
        ax.set_yscale("log")
        ax.set_title(name)
        ax.set_xlabel("điểm")
        ax.set_ylabel("mật độ (thang log)")
        ax.legend(fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
