# Bài tập lớn Blockchain · Thị trường carbon

Mô phỏng sự thay đổi phân bố tài sản carbon và sức chịu đựng của SME khi giảm hạn ngạch cấp mới. Đây là lõi chạy với dữ liệu giả lập để nhóm phát triển song song. Tất cả kết quả trong results/demo chỉ dùng để kiểm tra mô hình. Các quy tắc hành vi dưới đây là giả định triển khai ban đầu cần được Tuấn và Nguyên đối chiếu trước khi viết kết luận.

## Chạy từ thư mục gốc

Dùng Python 3.11 trở lên trong môi trường riêng.
~~~bash
python -m pip install -r requirements.txt
python blockchain/check_quota.py
python -m abm.run
python -m abm.run --input data/parameters.csv --out results/calibrated
~~~
Lệnh cuối dùng sau khi Sơn bàn giao parameters.csv theo data/README.md. Kết quả chạy bằng bộ tham số thay thế có run.json ghi SHA-256 đầu vào, đơn vị, danh sách seed và cấu hình.

## Hợp đồng đã bàn giao

contracts/CarbonCreditRegistry.sol đi cùng contracts/SHA256SUMS. Hướng dẫn và nhật ký 57 bước của lần chạy simulator ở blockchain/Ket_qua_Remix_VM.md. Sơn tự chạy các ca trên Remix IDE để ghi log của nhóm. Kiểm tra hash từ thư mục gốc bằng sha256sum -c contracts/SHA256SUMS hoặc Get-FileHash contracts/CarbonCreditRegistry.sol -Algorithm SHA256 trên PowerShell. Tag blockchain-v1.1 lưu mốc mã đã kiểm thử.

Python tính cấp mới, Solidity thực thi trần. Từ tick 30, S1 cấp mới = EA cơ sở × 70 // 100. S0 cấp EA cơ sở suốt 100 tick. Cả hai có trần CC = EA cấp mới × 30 // 100 theo doanh nghiệp, kỳ. Chỉ phần cấp mới chịu cú sốc. Tồn kho cũ chuyển sang kỳ sau. Repo demo đối chiếu quy tắc và đơn vị, không tự gửi giao dịch lên chuỗi.

## Hai mạng và một chu kỳ

Mỗi seed khởi tạo 20 tập đoàn, 140 SME và 40 dự án. Sinh mạng carbon Barabási–Albert (m = 3), hoán vị nhãn tác tử để loại doanh nghiệp không mặc định quyết định vị trí hub. Mạng cung ứng có hướng từ SME đến tập đoàn. Mỗi tập đoàn lấy 6–10 nhà cung ứng, trọng số đầu vào chuẩn hóa về 1. Trong bản đầu, chỉ mất nhà cung ứng SME mới làm giảm đầu vào của tập đoàn. Quan hệ cung ứng được giữ cố định để đo phần bị mất.

1. Tính phần đầu vào còn lại sau các lần rời mạng trước. Tính nhu cầu phát thải theo quy mô, đầu vào và nhiễu 0.96–1.04. Cấp EA mới cho doanh nghiệp còn hoạt động, tính trần CC. Dự án xanh phát hành CC hợp lệ theo công suất.
2. Mỗi bên thiếu hụt lần lượt thương lượng với láng giềng trên mạng carbon, mua EA trước rồi mua CC còn thiếu trong trần. Chỉ bán EA dư trên nhu cầu kỳ này và chỉ dự án bán CC. Giá tham chiếu kỳ = tổng nhu cầu / lượng EA khả dụng của các tác tử còn hoạt động, giới hạn trong [0.25, 5]. Giá gốc chuẩn hóa bằng 1. Giá chào bán phụ thuộc bậc kết nối của hai bên, giá chào mua phụ thuộc tiền/quy mô bên mua. Khi chào mua đủ cao, giá khớp là trung bình hai mức chào và lượng khớp bị giới hạn bởi tồn kho, nhu cầu và tiền.
3. Dùng EA và CC đã mua để duy trì sản xuất, trừ đơn vị đã sử dụng. Tiền thay đổi theo giao dịch, thu hoạt động và chi cố định. Doanh nghiệp rời mạng khi tiền < −0.15 × quy mô, hoặc khi sản lượng/quy mô < 0.78 trong 5 kỳ liên tiếp và tiền < quy mô. Tồn kho dở dang của doanh nghiệp rời mạng được giữ cố định và vẫn nằm trong tập tính Gini. Dự án xanh tiếp tục phát hành, có thể tích lũy CC. Quy tắc này có thể ảnh hưởng mạnh đến số dư nhóm dự án và Gini.
4. Ghi chỉ số cuối kỳ. Cùng seed có cùng trạng thái khởi tạo, hai mạng và thứ tự tìm đối tác/nhiễu nhu cầu theo tick. Giá, tài chính, giao dịch và rời mạng sau cú sốc do hai kịch bản tính riêng.

## Đầu ra và cách dùng

| Chỉ số | Cách đọc |
|---|---|
| ea_price_index | Giá EA khớp bình quân gia quyền theo lượng từng giao dịch trong kỳ. Tick không có giao dịch ghi trống, ea_trade_volume = 0. Bình quân qua các kỳ chỉ dùng giá quan sát được. |
| gini | Gini trên lượng EA + CC cuối kỳ của toàn bộ 200 tác tử, gồm cả số dư bằng 0. Nếu tổng bằng 0, ghi trống. balance_large, balance_sme, balance_green là tổng tồn kho cuối kỳ của ba nhóm, cùng đơn vị carbon với sổ mô phỏng. |
| sme_survival | Số SME còn hoạt động chia 140. |
| supply_loss | Trọng số các cạnh từ SME đã rời mạng chia tổng trọng số mạng cung ứng ban đầu. |

Mỗi bộ kết quả có timeseries.csv (2 kịch bản × 12 seed × 100 kỳ), by_tick.csv (trung bình theo kỳ), postshock_by_seed.csv (trung bình kỳ 30–100 của từng seed), postshock_summary.csv (trung bình và độ lệch chuẩn mẫu giữa 12 seed) và paired_difference.csv (S1 trừ S0 trên cùng seed). Bốn ảnh PNG tương ứng với bốn chỉ số chính. Nguyên có thể dùng các tệp cùng thư mục và mã đầu vào trong run.json để truy vết bảng và hình.

## Phân công tại mốc này

Sơn nhận mẫu data/parameters_demo.csv và data/README.md. Tuấn duyệt đơn vị và quy tắc hành vi, đưa CSV mới vào lệnh chạy ở trên, kiểm tra các cặp seed. Nguyên dùng README để viết phương pháp và dùng kết quả từ thư mục đã được nhóm duyệt để hoàn thiện phần thực nghiệm. Với GitHub, thêm remote của nhóm và push nhánh main kèm tag blockchain-v1.1 sau khi chốt đúng repo đích.
