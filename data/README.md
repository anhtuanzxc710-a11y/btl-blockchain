# Bàn giao dữ liệu cho Sơn

Sao chép parameters_demo.csv thành parameters.csv và thay các khoảng giả lập bằng bộ tham số nhóm đã duyệt. Giữ 11 dòng (mỗi cặp group, parameter xuất hiện một lần). Python sinh 200 tác tử từ bảng tham số nhóm. Hiện các liên kết đối tác được mô phỏng theo seed. Nếu thu được dữ liệu cạnh hoặc hồ sơ từng doanh nghiệp, cần bổ sung bộ nạp riêng trước khi dùng trực tiếp các bảng đó.

| Cột | Sơn điền |
|---|---|
| group | large = tập đoàn, sme = nhà cung ứng SME, green = dự án xanh |
| parameter | Tên tham số giống trong mẫu |
| low, high | Khoảng lấy mẫu khép kín. Một giá trị cố định thì điền low = high. Dùng dấu chấm thập phân. |
| unit | demand, issuance cùng chọn tCO2e_per_tick hoặc cùng chọn model_unit_per_tick. Các dòng khác dùng ratio. |
| evidence | observed (quan sát), proxy (tham chiếu) hoặc assumption (giả định) |
| source_ref | Mã nguồn trong workbook kèm sheet/dòng, hoặc URL, hoặc mã giả định đã ghi trong báo cáo |
| reference_period | Năm, giai đoạn hoặc synthetic nếu là giả định |
| model_use | Ý nghĩa, cách chuyển số liệu gốc thành giá trị mỗi tác tử mỗi kỳ, công thức và giả định liên quan |

**Quy tắc đơn vị.** CSV ghi lượng mỗi tác tử mỗi tick. Chọn tCO2e_per_tick thì nhập 70 cho 70 tCO₂e. Python đọc dạng Decimal, nhân 1000, làm tròn xuống và lưu 70000. Chọn model_unit_per_tick thì 70 trở thành 70 đơn vị mô hình, lấy phần nguyên. Các tỷ lệ ghi 0.30 cho 30%. Không đưa lượng chuẩn hóa lên Remix như tCO₂e khi chưa có hệ số hiệu chỉnh.

**Cách dùng hai workbook.** Hạn ngạch tổng, cơ cấu ba ngành, giá CEA và hồ sơ dự án là nguồn tham chiếu. Ghi rõ cách phân bổ từ tổng theo năm về tác tử và cách quy số liệu về tick. Tick trong bản demo là kỳ trừu tượng. Nếu chưa thống nhất thời lượng một tick, dùng chế độ chuẩn hóa và ghi giả định. Giá CEA và số liệu JETRO có thể lưu trong workbook nguồn để giải thích hoặc hiệu chỉnh. Lõi hiện tại tự tính giá khớp từ thị trường song phương và tự sinh mạng cung ứng. Chỉ tiêu giá do mô hình xuất là chỉ số tương đối.

**Ý nghĩa tham số.** demand và issuance đo khối lượng. quota_ratio nhân nhu cầu cơ sở để tính cấp mới trong S0. cash_ratio nhân giá trị nhu cầu cơ sở tại giá gốc bằng 1 để tính tiền ban đầu. margin và fixed_cost là hệ số thu trên lượng sản xuất và chi trên quy mô cơ sở trong mô hình. Nếu tham số là giả định, ghi căn cứ và khoảng nhạy cảm đề xuất. Số liệu công bố ở cấp ngành cần ghi proxy nếu nhóm dùng làm giá trị cho từng tác tử.
