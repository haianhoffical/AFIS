# LAB 2 - TỰ TÍNH CÁC CHỈ SỐ ĐÁNH GIÁ HIỆU NĂNG SINH TRẮC

**Mã sinh viên:** 2305CT2348

## Kết quả thực hành

### Kết quả kiểm thử

Đã hoàn thiện các TODO trong `bio_metrics.py` và kiểm thử chương trình.

Kết quả:

- Hệ thống A: EER tự tính = 2.805%, pyeer = 2.805%, lệch 0.000 điểm phần trăm.
- Hệ thống B: EER tự tính = 2.715%, pyeer = 2.715%, lệch 0.000 điểm phần trăm.
- Hệ thống C: EER tự tính = 2.595%, pyeer = 2.595%, lệch 0.000 điểm phần trăm.

Cả ba hệ thống đều đạt yêu cầu sai lệch EER không quá 0.5 điểm phần trăm so với pyeer.

---

## Câu 1

Hai hệ thống A và B có thể có EER gần nhau nhưng FMR tại một mức ngưỡng cụ thể vẫn có thể khác nhau. EER chỉ thể hiện một điểm cân bằng giữa FMR và FNMR, vì vậy không mô tả đầy đủ hành vi của hệ thống ở vùng FMR rất thấp.

Nếu yêu cầu FMR không vượt quá 0.1%, cần xem xét thêm phân bố điểm của các cặp impostor, đặc biệt là phần đuôi của phân bố. Một số ít điểm impostor có giá trị rất cao có thể làm tăng FMR ở vùng ngưỡng nghiêm ngặt.

Do đó, khi đánh giá hệ thống cần xem xét EER cùng với FMR/FNMR tại các ngưỡng quan tâm và biểu đồ phân bố điểm.

---

## Câu 2

Hệ thống C sử dụng khoảng cách thay vì điểm tương đồng. Với khoảng cách, giá trị càng nhỏ thì hai mẫu càng giống nhau.

Nếu sử dụng tham số `higher_is_better=True` không đúng với bản chất của điểm khoảng cách thì hướng so sánh sẽ bị đảo ngược. Khi đó kết quả EER không còn phản ánh đúng cách ra quyết định của hệ thống.

Để tính EER đúng với hệ thống C, điểm khoảng cách cần được chuẩn hóa về cùng quy ước so sánh, trong đó giá trị điểm cao hơn đại diện cho mức độ giống nhau cao hơn.

---

## Câu 3

Nếu có 0 lần false match trong 10.000 cặp impostor thì FMR quan sát được bằng:

FMR = 0 / 10.000 = 0%.

Tuy nhiên, điều này không có nghĩa là FMR thực tế bằng 0. Với 0 lỗi quan sát được, cận trên xấp xỉ 95% có thể lấy theo:

3 / N

Với N = 10.000:

3 / 10.000 = 0.0003 = 0.03%.

Như vậy, kết quả 0 lỗi trong mẫu thử chỉ cho biết chưa quan sát thấy lỗi trong 10.000 lần thử, chứ không thể khẳng định xác suất false match thực tế bằng 0.

---

## Câu 4

Nếu yêu cầu FMR < 0.01%, thì 10.000 cặp impostor chưa đủ để xác minh chắc chắn yêu cầu này chỉ dựa trên việc quan sát 0 lỗi.

Theo quy tắc cận trên xấp xỉ 95%:

3 / N < 0.0001

Suy ra:

N > 30.000

Vì vậy cần ít nhất hơn 30.000 cặp impostor để cận trên xấp xỉ 95% nhỏ hơn 0.01%. Trong thực tế nên sử dụng số lượng mẫu lớn hơn để có bằng chứng thống kê tốt hơn.

---

## Câu 5

Với 50 sinh viên, nếu tạo tất cả các cặp sinh viên thì số cặp là:

50 × 49 / 2 = 1.225 cặp.

Nếu FMR = 1%, số false match kỳ vọng là:

1.225 × 0.01 = 12.25

Tức là trung bình kỳ vọng khoảng 12.25 false match trong 1.225 cặp impostor.

Với hệ thống nhận dạng 1:N có 100 triệu bản ghi và FMR = 0.01%, số false match kỳ vọng cho một truy vấn là:

100.000.000 × 0.0001 = 10.000

Như vậy, FMR nhỏ khi xét trên một phép so khớp vẫn có thể tạo ra số lượng false match kỳ vọng lớn khi số lượng phép so khớp rất lớn.

---

## Kết luận

Qua bài thực hành, các chỉ số FMR, FNMR, EER, ROC AUC, decidability và FPIR được tính tự động bằng chương trình.

Kết quả EER của ba hệ thống A, B và C đều khớp với pyeer, với sai lệch 0.000 điểm phần trăm.

Các kết quả cho thấy khi đánh giá sinh trắc học không nên chỉ xem EER mà cần xem xét thêm FMR, FNMR, ngưỡng quyết định, phân bố điểm và tác động của kích thước tập so khớp.
