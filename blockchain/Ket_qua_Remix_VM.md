# Bảng thao tác và kết quả Remix VM

Đã chạy 57 bước bằng bộ máy Remix VM (gói chính thức @remix-project/remix-simulator 0.2.91, fork Shanghai) qua RPC. Trình biên dịch solc 0.8.24+commit.e11b9ed9.Emscripten.clang. Các giao dịch ghi được đối chiếu receipt, selector lỗi hoặc sự kiện và tham số sự kiện. Các hàm đọc được đối chiếu với dữ liệu trả về.

## Chuẩn bị trong Remix IDE

Mở CarbonCreditRegistry.sol, chọn compiler 0.8.24 và EVM Shanghai rồi bấm Compile. Chọn Deploy & Run Transactions → Remix VM. Ghi lại địa chỉ ba tài khoản đầu tiên. Đổi Account theo cột Ví trước mỗi bước. Deploy nhận một đối số là địa chỉ verifier. Khi kiểm tra constructor lỗi, giữ nguyên ví A cho cả ba lần thử. Các bước sau lần deploy thành công dùng cùng một hợp đồng. Với giao dịch dự kiến revert, hãy đối chiếu tên custom error đã giải mã.

| Ký hiệu | Giá trị của lần chạy |
|---|---|
| A | `0x5B38Da6a701c568545dCfcB03FcB875f56beddC4` |
| V | `0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2` |
| B | `0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db` |
| Z | `0x0000000000000000000000000000000000000000` |
| MAX | `115792089237316195423570985008687907853269984665640564039457584007913129639935` |
| A01 | `0x4130310000000000000000000000000000000000000000000000000000000000` |
| A02 | `0x4130320000000000000000000000000000000000000000000000000000000000` |
| P01 | `0x5030310000000000000000000000000000000000000000000000000000000000` |
| H1 | `0x1111111111111111111111111111111111111111111111111111111111111111` |
| H2 | `0x2222222222222222222222222222222222222222222222222222222222222222` |
| H0 | `0x0000000000000000000000000000000000000000000000000000000000000000` |
| A03 | `0x4130330000000000000000000000000000000000000000000000000000000000` |
| H3 | `0x3333333333333333333333333333333333333333333333333333333333333333` |

A là regulator, V là verifier, B là company. H0 là bytes32 rỗng. A03 và H3 dùng cho ca chưa cấp hạn ngạch. Khi thao tác hãy thay ký hiệu bằng giá trị trong bảng, dùng địa chỉ A/V/B của phiên Remix đang mở.

## Thứ tự thao tác

| Bước | Ví | Nút Remix và đối số | Kết quả đã ghi nhận |
|---:|---|---|---|
| 1 | A | `Deploy(Z)` | Revert · `ZeroAddress` |
| 2 | A | `Deploy(A)` | Revert · `RolesMustDiffer` |
| 3 | A | `Deploy(V)` | Thành công · `PeriodOpened` |
| 4 | A | `currentPeriod()` | Đọc · `1` |
| 5 | A | `regulator()` | Đọc · `A` |
| 6 | A | `verifier()` | Đọc · `V` |
| 7 | V | `advancePeriod(30)` | Revert · `NotRegulator` |
| 8 | A | `advancePeriod(30)` | Thành công · `PeriodOpened` |
| 9 | A | `advancePeriod(30)` | Revert · `InvalidPeriod` |
| 10 | B | `setQuota(30, B, 70000)` | Revert · `NotRegulator` |
| 11 | A | `setQuota(29, B, 70000)` | Revert · `InvalidPeriod` |
| 12 | A | `setQuota(30, Z, 70000)` | Revert · `ZeroAddress` |
| 13 | A | `setQuota(30, B, 70000)` | Thành công · `QuotaSet` |
| 14 | A | `setQuota(30, B, 70001)` | Revert · `QuotaAlreadySet` |
| 15 | B | `quotaStatus(30, B)` | Đọc · `true, 70000, 21000, 0` |
| 16 | V | `mintVerifiedCredit(A01, P01, B, 40000, H1)` | Thành công · `CreditIssued` |
| 17 | B | `lotStatus(A01)` | Đọc · `P01, B, 40000, 40000, H1` |
| 18 | V | `mintVerifiedCredit(A01, P01, B, 40000, H2)` | Revert · `DuplicateSerial` |
| 19 | V | `mintVerifiedCredit(A02, P01, B, 40000, H1)` | Revert · `DuplicateMrvHash` |
| 20 | V | `mintVerifiedCredit(A01, P01, B, 40000, H1)` | Revert · `DuplicateSerial` |
| 21 | B | `recordOffset(30, A01, 21000)` | Thành công · `OffsetRecorded` |
| 22 | B | `recordOffset(30, A01, 1000)` | Revert · `OffsetCapExceeded` |
| 23 | B | `quotaStatus(30, B)` | Đọc · `true, 70000, 21000, 21000` |
| 24 | B | `lotStatus(A01)` | Đọc · `P01, B, 40000, 19000, H1` |
| 25 | B | `mintVerifiedCredit(A02, P01, B, 1000, H2)` | Revert · `NotVerifier` |
| 26 | V | `mintVerifiedCredit(A02, P01, B, 1000, H0)` | Revert · `EmptyMrvHash` |
| 27 | V | `mintVerifiedCredit(H0, P01, B, 1000, H2)` | Revert · `EmptySerial` |
| 28 | V | `mintVerifiedCredit(A02, H0, B, 1000, H2)` | Revert · `EmptyProjectId` |
| 29 | V | `mintVerifiedCredit(A02, P01, Z, 1000, H2)` | Revert · `ZeroAddress` |
| 30 | V | `mintVerifiedCredit(A02, P01, B, 0, H2)` | Revert · `ZeroAmount` |
| 31 | V | `recordOffset(29, A02, 0)` | Revert · `InvalidPeriod` |
| 32 | V | `recordOffset(30, A02, 0)` | Revert · `LotNotFound` |
| 33 | A | `lotStatus(A02)` | Revert · `LotNotFound` |
| 34 | V | `recordOffset(30, A01, 0)` | Revert · `NotLotOwner` |
| 35 | B | `recordOffset(30, A01, 0)` | Revert · `ZeroAmount` |
| 36 | B | `recordOffset(30, A01, 19001)` | Revert · `InsufficientBalance` |
| 37 | V | `mintVerifiedCredit(A02, P01, B, 1000, H2)` | Thành công · `CreditIssued` |
| 38 | B | `recordOffset(30, A02, 1)` | Revert · `OffsetCapExceeded` |
| 39 | B | `lotStatus(A02)` | Đọc · `P01, B, 1000, 1000, H2` |
| 40 | V | `mintVerifiedCredit(A03, P01, A, 500, H3)` | Thành công · `CreditIssued` |
| 41 | A | `recordOffset(30, A03, 0)` | Revert · `QuotaNotSet` |
| 42 | A | `setQuota(30, A, 0)` | Thành công · `QuotaSet` |
| 43 | A | `setQuota(30, A, 1)` | Revert · `QuotaAlreadySet` |
| 44 | A | `recordOffset(30, A03, 1)` | Revert · `OffsetCapExceeded` |
| 45 | A | `setQuota(30, V, MAX)` | Thành công · `QuotaSet` |
| 46 | A | `quotaStatus(30, V)` | Đọc · `true, MAX, 34737626771194858627071295502606372355980995399692169211837275202373938891980, 0` |
| 47 | A | `advancePeriod(31)` | Thành công · `PeriodOpened` |
| 48 | A | `setQuota(30, B, 70000)` | Revert · `InvalidPeriod` |
| 49 | B | `recordOffset(30, A01, 1)` | Revert · `InvalidPeriod` |
| 50 | B | `quotaStatus(30, B)` | Đọc · `true, 70000, 21000, 21000` |
| 51 | B | `quotaStatus(31, B)` | Đọc · `false, 0, 0, 0` |
| 52 | A | `setQuota(31, B, 3334)` | Thành công · `QuotaSet` |
| 53 | B | `recordOffset(31, A02, 1000)` | Thành công · `OffsetRecorded` |
| 54 | B | `lotStatus(A02)` | Đọc · `P01, B, 1000, 0, H2` |
| 55 | B | `usedMrvHash(H2)` | Đọc · `true` |
| 56 | V | `mintVerifiedCredit(A02, P01, B, 1, H2)` | Revert · `DuplicateSerial` |
| 57 | B | `quotaStatus(31, B)` | Đọc · `true, 3334, 1000, 1000` |

## Mã giao dịch của lần chạy

Địa chỉ hợp đồng `0xf8e81D47203A594245E36C48e151709F0C19fBe8`. Các mã dưới đây thuộc phiên VM cục bộ. Khi Sơn chạy lại trên Remix, ghi mã giao dịch của phiên mới.

| Bước | Transaction hash |
|---:|---|
| 1 | `0x7ec6684fa7a748441ef86d209e2cdb14af772e12b1c2b06a80e450660d23a3c9` |
| 2 | `0xe4faef4eb85374829fccf9ae725a4fe6f0ad56968e9f3babfc8ee420f9e38c74` |
| 3 | `0xeaed884dd5874888f4e91e1be29d81f826dc21a1f120c33df23dfb44849f7daf` |
| 7 | `0x9117aaa1f17392ef31b2983ec5592aee2a472d237b449bd84695744fff41ce6e` |
| 8 | `0x01f9891e8413d83d6fb9a6078c25d5dad4dd934df5ab052957a0c8bf91925461` |
| 9 | `0x58f843a8e9e86a84ba350bb30e9b3b97ddf2013be7667e39b655f665d5276dac` |
| 10 | `0x443dca6f7e56c2f273eb792ec7c67d099fb73790566e83c10ab65ff8e7034c53` |
| 11 | `0x7a22e1444d407a881186d4b4989cb169bdd6c6da23faab6dfcc4fa7705685867` |
| 12 | `0x4ba5b9be3c51289dcba53821a85500f58db21b11ef418601e60bcbea9a6ac9d8` |
| 13 | `0x933aeb354551101e46b263a2b684ebcee947d067ab9640e4c0339b6a403b998b` |
| 14 | `0xbdeb8ea71615fadffb465427a9715634d256e6509867194b38d81ed6ccc3fb12` |
| 16 | `0x42853230b20f496ed16413de986af99b90861577351c0bc446000580a4a61c7e` |
| 18 | `0x35c1bb0ccfb8d757b224981ff50c2e8e17e295edab1467e28b51fb75be9f4fd3` |
| 19 | `0xc30360750b8497861d0e9d5a1624d4ddcb061eede2bf3770ab47ce01bddf18f1` |
| 20 | `0xe8205d6239a2632bc0ed45a857cdcb1e11fb641032b793a5480706ed07b06f03` |
| 21 | `0x87e832135c52dd87ee256db8015173b0df656016595098e621b4c8373880f630` |
| 22 | `0xacba7ca8d0f956ab6f93378bce3c5d028274ac656cb99a0191626d2482cc46cd` |
| 25 | `0xbab8a2a205cf0564ebae1b8d4fead18489dddcf2b5aa1852d0518912bc2d61ec` |
| 26 | `0xe1122a169572cc3989bfeaef669e6ff0754adc2c148f5c7f24e119a64ac49d0d` |
| 27 | `0xb435a9619b4081b3aca836ac9932c9a1b925b17d39f793cf2ba1df63a6f19256` |
| 28 | `0x60253fa6e593531d357ba4b5ca897b4682cf81bf908e0051e5b60eeed910d56f` |
| 29 | `0x30297688bce052f9f16688e01a66a5f6ce97bb4eab2fd6de64c9f12cd36fe204` |
| 30 | `0x217ad2733c6dbc74c51a45427b76ad801901e765290959763a262d60aef25879` |
| 31 | `0x8517e3e52e3a289bdf526f2119501d58758b9e4c57a0a9d825dab914a344fa3a` |
| 32 | `0x3f36c60312e1d171e006824c4b3c1e37c82a2f801031784bee59f0859c328051` |
| 34 | `0xac50c3cd6e6d35d41db171c8bf78fa6643176c9ae27c8d01159007111231955b` |
| 35 | `0x59bb59f8238420a1ea4d7a266fcedf7f6712992b726389ac531dfabf67885c2a` |
| 36 | `0x7874a58bc145d48e7dcb04e1db3882fbb8b434e16dfe322ed8ce9be06dfc307a` |
| 37 | `0x62775cce18fb8cb136bad600fc36edce03e375d05b09cc55d5d9df601fdea929` |
| 38 | `0x3e9d56c99a30678b9ae14dd130591b3e19c888a6d5c9db72203eb38ebd43ae63` |
| 40 | `0xa1f851908bd94bf75a28889bd5bef4e719feb17a3f975f1b05e71e6eb67253f5` |
| 41 | `0x42b206c0c6dfdebce60d3642af48aed7f9ab6d5c97f2deb973f2d1c5588d7056` |
| 42 | `0x70bae8ccccb0953d3b7843897120417072c62a507f0e4fe075cc960658a46b6e` |
| 43 | `0x7c507bd51f22903bdbe1880f6df148ab33555ebe4eacaf037a3469b703e265e1` |
| 44 | `0x07025dcf4c03b3e9d9ebe7f3c18e970650ba302d9d570c66ddc153c2a471c16d` |
| 45 | `0xd46491908dc40581856e1aa4858b1fac5b1364c093cf743482052ca95754f630` |
| 47 | `0xf3beb4330e19cbf5d60be7b63c1958e5cf5a6fcfdf75eaf4e45d82faaa456998` |
| 48 | `0x25e753b04f7dd560980fdedf3aa1fd81fc49c9d79c713026f48e9d03d4453c0b` |
| 49 | `0x7bb526e7e0a97d67d0c8563b7ef0265f000ca4f85f4b520699ca004e6de24036` |
| 52 | `0x1a0506c9b48ec6c1ede4335575227e56f16049a6bfe27ec90d898103e3faa9a7` |
| 53 | `0x3eba03d4d669d74add4de72e6bc804462290309ade7437b57e532ef738a0ae78` |
| 56 | `0x588ec12212e234b2e967cd60313f5208a40d787e45a343163c43690382a4667a` |

SHA-256 của file Solidity đã biên dịch: `6e91ce5ec9bf4976dd662500e1e36d31203e777f37e63b614d3884db68514081`.
