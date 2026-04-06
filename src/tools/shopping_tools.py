"""
Shopping Tools — 3 công cụ mock data cho Trợ Lý Mua Sắm.
Agent sẽ gọi các tools này trong vòng lặp ReAct.

Mock data = dữ liệu giả lập để demo, không cần API thật.
"""


def search_products(query: str) -> str:
    """Tìm sản phẩm theo từ khóa + budget."""
    
    # Mock database sản phẩm
    products = {
        "laptop": [
            {"name": "Acer Aspire 5", "price": "12.990.000đ", "cpu": "Intel i5-1235U", "ram": "8GB", "storage": "512GB SSD", "rating": 4.2},
            {"name": "Lenovo IdeaPad 3", "price": "13.490.000đ", "cpu": "AMD Ryzen 5 7520U", "ram": "8GB", "storage": "512GB SSD", "rating": 4.0},
            {"name": "ASUS VivoBook 15", "price": "15.990.000đ", "cpu": "Intel i5-1335U", "ram": "16GB", "storage": "512GB SSD", "rating": 4.5},
            {"name": "HP Pavilion 15", "price": "18.490.000đ", "cpu": "Intel i7-1355U", "ram": "16GB", "storage": "512GB SSD", "rating": 4.3},
            {"name": "MacBook Air M2", "price": "27.990.000đ", "cpu": "Apple M2", "ram": "8GB", "storage": "256GB SSD", "rating": 4.8},
            {"name": "Dell Inspiron 15", "price": "14.990.000đ", "cpu": "Intel i5-1235U", "ram": "8GB", "storage": "256GB SSD", "rating": 4.1},
            {"name": "MSI Modern 14", "price": "16.490.000đ", "cpu": "Intel i5-1335U", "ram": "16GB", "storage": "512GB SSD", "rating": 4.2},
        ],
        "phone": [
            {"name": "Samsung Galaxy A15", "price": "4.490.000đ", "cpu": "Helio G99", "ram": "6GB", "storage": "128GB", "rating": 4.0},
            {"name": "iPhone 15", "price": "19.990.000đ", "cpu": "A16 Bionic", "ram": "6GB", "storage": "128GB", "rating": 4.7},
            {"name": "Xiaomi Redmi Note 13", "price": "5.490.000đ", "cpu": "Snapdragon 685", "ram": "8GB", "storage": "128GB", "rating": 4.3},
            {"name": "OPPO Reno 11", "price": "9.990.000đ", "cpu": "Dimensity 7050", "ram": "8GB", "storage": "256GB", "rating": 4.4},
            {"name": "Samsung Galaxy S24", "price": "22.990.000đ", "cpu": "Snapdragon 8 Gen 3", "ram": "8GB", "storage": "256GB", "rating": 4.6},
            {"name": "Realme C67", "price": "3.990.000đ", "cpu": "Snapdragon 685", "ram": "6GB", "storage": "128GB", "rating": 3.9},
        ],
        "tablet": [
            {"name": "iPad 10 2022", "price": "9.990.000đ", "cpu": "A14 Bionic", "ram": "4GB", "storage": "64GB", "rating": 4.5},
            {"name": "Samsung Galaxy Tab A9+", "price": "7.490.000đ", "cpu": "Snapdragon 695", "ram": "4GB", "storage": "64GB", "rating": 4.1},
            {"name": "iPad Air M1", "price": "15.990.000đ", "cpu": "Apple M1", "ram": "8GB", "storage": "64GB", "rating": 4.7},
            {"name": "Xiaomi Pad 6", "price": "7.990.000đ", "cpu": "Snapdragon 870", "ram": "6GB", "storage": "128GB", "rating": 4.4},
        ],
        "headphone": [
            {"name": "Sony WH-1000XM5", "price": "7.490.000đ", "cpu": "Sony V1", "ram": "—", "storage": "—", "rating": 4.8},
            {"name": "Apple AirPods Pro 2", "price": "5.990.000đ", "cpu": "Apple H2", "ram": "—", "storage": "—", "rating": 4.7},
            {"name": "Samsung Galaxy Buds FE", "price": "1.990.000đ", "cpu": "—", "ram": "—", "storage": "—", "rating": 4.2},
            {"name": "JBL Tune 520BT", "price": "1.290.000đ", "cpu": "—", "ram": "—", "storage": "—", "rating": 4.0},
        ],
        "smartwatch": [
            {"name": "Apple Watch SE 2", "price": "6.990.000đ", "cpu": "Apple S8", "ram": "—", "storage": "32GB", "rating": 4.6},
            {"name": "Samsung Galaxy Watch 6", "price": "5.490.000đ", "cpu": "Exynos W930", "ram": "—", "storage": "16GB", "rating": 4.4},
            {"name": "Xiaomi Watch S3", "price": "3.490.000đ", "cpu": "—", "ram": "—", "storage": "—", "rating": 4.1},
        ],
        "camera": [
            {"name": "Sony Alpha A6400", "price": "22.990.000đ", "cpu": "BIONZ X", "ram": "—", "storage": "SD Card", "rating": 4.7},
            {"name": "Canon EOS M50 Mark II", "price": "16.490.000đ", "cpu": "DIGIC 8", "ram": "—", "storage": "SD Card", "rating": 4.5},
            {"name": "Fujifilm X-T30 II", "price": "21.490.000đ", "cpu": "X-Processor 4", "ram": "—", "storage": "SD Card", "rating": 4.6},
        ],
    }

    # Tìm theo keyword
    query_lower = query.lower()
    for category, items in products.items():
        if category in query_lower:
            result = f"Tìm thấy {len(items)} sản phẩm {category}:\n"
            for i, p in enumerate(items, 1):
                result += f"  {i}. {p['name']} — {p['price']} | {p['cpu']} | RAM {p['ram']} | {p['storage']} | ⭐{p['rating']}\n"
            return result

    return f"Không tìm thấy sản phẩm cho từ khóa '{query}'. Thử: laptop, phone, tablet, headphone, smartwatch, camera."


def compare_specs(query: str) -> str:
    """So sánh thông số 2 sản phẩm."""
    
    specs_db = {
        "acer aspire 5": {"cpu": "Intel i5-1235U (10 cores)", "ram": "8GB DDR4", "gpu": "Intel Iris Xe", "screen": "15.6 inch FHD IPS", "battery": "8 tiếng", "weight": "1.76kg", "price": "12.990.000đ"},
        "asus vivobook 15": {"cpu": "Intel i5-1335U (10 cores)", "ram": "16GB DDR4", "gpu": "Intel Iris Xe", "screen": "15.6 inch FHD OLED", "battery": "6 tiếng", "weight": "1.7kg", "price": "15.990.000đ"},
        "hp pavilion 15": {"cpu": "Intel i7-1355U (12 cores)", "ram": "16GB DDR5", "gpu": "Intel Iris Xe", "screen": "15.6 inch FHD IPS", "battery": "7 tiếng", "weight": "1.74kg", "price": "18.490.000đ"},
        "lenovo ideapad 3": {"cpu": "AMD Ryzen 5 7520U (4 cores)", "ram": "8GB DDR5", "gpu": "AMD Radeon 610M", "screen": "15.6 inch FHD TN", "battery": "7.5 tiếng", "weight": "1.63kg", "price": "13.490.000đ"},
        "macbook air m2": {"cpu": "Apple M2 (8 cores)", "ram": "8GB Unified", "gpu": "Apple M2 10-core GPU", "screen": "13.6 inch Liquid Retina", "battery": "18 tiếng", "weight": "1.24kg", "price": "27.990.000đ"},
        "dell inspiron 15": {"cpu": "Intel i5-1235U (10 cores)", "ram": "8GB DDR4", "gpu": "Intel UHD Graphics", "screen": "15.6 inch FHD WVA", "battery": "6 tiếng", "weight": "1.65kg", "price": "14.990.000đ"},
        "msi modern 14": {"cpu": "Intel i5-1335U (10 cores)", "ram": "16GB DDR4", "gpu": "Intel Iris Xe", "screen": "14 inch FHD IPS", "battery": "10 tiếng", "weight": "1.4kg", "price": "16.490.000đ"},
        "iphone 15": {"cpu": "A16 Bionic", "ram": "6GB", "gpu": "Apple 5-core GPU", "screen": "6.1 inch Super Retina XDR", "battery": "20h video", "weight": "171g", "price": "19.990.000đ"},
        "samsung galaxy s24": {"cpu": "Snapdragon 8 Gen 3", "ram": "8GB", "gpu": "Adreno 750", "screen": "6.2 inch Dynamic AMOLED 2X", "battery": "22h video", "weight": "167g", "price": "22.990.000đ"},
        "oppo reno 11": {"cpu": "Dimensity 7050", "ram": "8GB", "gpu": "Mali-G68 MC4", "screen": "6.7 inch AMOLED 120Hz", "battery": "17h video", "weight": "184g", "price": "9.990.000đ"},
        "sony wh-1000xm5": {"cpu": "Sony V1 + QN1", "ram": "—", "gpu": "—", "screen": "—", "battery": "30 tiếng", "weight": "250g", "price": "7.490.000đ"},
        "apple airpods pro 2": {"cpu": "Apple H2", "ram": "—", "gpu": "—", "screen": "—", "battery": "6h (30h với case)", "weight": "5.3g/tai", "price": "5.990.000đ"},
    }

    query_lower = query.lower()
    found = []
    for name, specs in specs_db.items():
        if name in query_lower:
            found.append((name, specs))

    if len(found) >= 2:
        result = f"📊 So sánh {found[0][0].title()} vs {found[1][0].title()}:\n"
        result += f"{'Thông số':<12} | {found[0][0].title():<25} | {found[1][0].title():<25}\n"
        result += "-" * 70 + "\n"
        for key in found[0][1]:
            result += f"{key:<12} | {found[0][1][key]:<25} | {found[1][1][key]:<25}\n"
        return result
    elif len(found) == 1:
        name, specs = found[0]
        result = f"📋 Thông số {name.title()}:\n"
        for key, val in specs.items():
            result += f"  - {key}: {val}\n"
        return result + "\n⚠️ Chỉ tìm thấy 1 sản phẩm. Hãy nêu tên sản phẩm thứ 2 để so sánh."

    return f"Không tìm thấy sản phẩm trong database. Có: Acer Aspire 5, ASUS VivoBook 15, HP Pavilion 15, Lenovo IdeaPad 3, MacBook Air M2, Dell Inspiron 15, MSI Modern 14, iPhone 15, Samsung Galaxy S24, Sony WH-1000XM5, AirPods Pro 2."


def check_reviews(query: str) -> str:
    """Tra đánh giá người dùng thực tế."""
    
    reviews_db = {
        "acer aspire 5": {"rating": "4.2/5", "total_reviews": 1250, "pros": "Giá rẻ, hiệu năng ổn cho sinh viên, bàn phím thoải mái", "cons": "Màn hình hơi tối, loa yếu, vỏ nhựa dễ trầy", "verdict": "Phù hợp sinh viên cần laptop cơ bản"},
        "asus vivobook 15": {"rating": "4.5/5", "total_reviews": 890, "pros": "Màn OLED đẹp, 16GB RAM mạnh, thiết kế gọn", "cons": "Pin không lâu, quạt hơi ồn khi nặng", "verdict": "Tốt nhất tầm 15-16 triệu"},
        "hp pavilion 15": {"rating": "4.3/5", "total_reviews": 670, "pros": "CPU i7 mạnh, RAM DDR5 nhanh, build quality tốt", "cons": "Giá hơi cao so với cấu hình, nặng hơn đối thủ", "verdict": "Phù hợp ai cần hiệu năng cao hơn"},
        "lenovo ideapad 3": {"rating": "4.0/5", "total_reviews": 1580, "pros": "Nhẹ nhất phân khúc, giá tốt, AMD tiết kiệm pin", "cons": "Màn TN góc nhìn hẹp, chỉ 8GB RAM, GPU yếu", "verdict": "Giá rẻ nhất nhưng màn hình là điểm trừ lớn"},
        "macbook air m2": {"rating": "4.8/5", "total_reviews": 3200, "pros": "Pin 18h cực trâu, nhẹ 1.24kg, macOS mượt, im lặng hoàn toàn", "cons": "Giá cao, chỉ 256GB, không chơi game Windows được", "verdict": "Tốt nhất nếu đủ budget, đặc biệt cho lập trình iOS/web"},
        "dell inspiron 15": {"rating": "4.1/5", "total_reviews": 980, "pros": "Bền bỉ, bàn phím gõ sướng, hỗ trợ nâng cấp dễ", "cons": "Thiết kế hơi dày, SSD chỉ 256GB, màn hình trung bình", "verdict": "Laptop bền cho văn phòng, dễ nâng cấp sau"},
        "msi modern 14": {"rating": "4.2/5", "total_reviews": 450, "pros": "Nhẹ 1.4kg, pin 10h, 16GB RAM, màn IPS sắc nét", "cons": "Loa nhỏ, webcam chất lượng trung bình", "verdict": "Tốt cho người hay di chuyển"},
        "iphone 15": {"rating": "4.7/5", "total_reviews": 5400, "pros": "Camera 48MP xuất sắc, Dynamic Island, USB-C, chip nhanh", "cons": "Giá cao, sạc chậm 20W, bộ nhớ chỉ 128GB bản rẻ", "verdict": "iPhone đáng mua nhất nếu thích iOS"},
        "samsung galaxy s24": {"rating": "4.6/5", "total_reviews": 3100, "pros": "AI Galaxy tích hợp, màn AMOLED 120Hz rực rỡ, camera zoom tốt", "cons": "Pin trung bình, nóng khi chơi game nặng", "verdict": "Android cao cấp tốt nhất 2024"},
        "oppo reno 11": {"rating": "4.4/5", "total_reviews": 720, "pros": "Thiết kế đẹp, sạc nhanh 67W, camera selfie tốt", "cons": "Không chống nước, hiệu năng gaming trung bình", "verdict": "Tầm trung tốt cho người thích chụp ảnh"},
        "xiaomi redmi note 13": {"rating": "4.3/5", "total_reviews": 2800, "pros": "Giá rẻ, màn AMOLED 120Hz, pin 5000mAh lâu", "cons": "Camera đêm yếu, MIUI nhiều quảng cáo", "verdict": "Rẻ nhất có màn AMOLED, hợp sinh viên"},
        "sony wh-1000xm5": {"rating": "4.8/5", "total_reviews": 4500, "pros": "Chống ồn số 1, âm thanh Hi-Res, đeo cả ngày thoải mái", "cons": "Giá cao, không gập được, không chống nước", "verdict": "Tai nghe chống ồn tốt nhất thế giới"},
        "apple airpods pro 2": {"rating": "4.7/5", "total_reviews": 6200, "pros": "Chống ồn tốt, tích hợp sâu iOS, nhỏ gọn, spatial audio", "cons": "Chỉ tốt nhất với iPhone, giá cao", "verdict": "Tai nghe TWS tốt nhất cho iPhone"},
        "samsung galaxy buds fe": {"rating": "4.2/5", "total_reviews": 1800, "pros": "Giá rẻ, chống ồn được, bass tốt", "cons": "Chống nước yếu, mic call trung bình", "verdict": "Tai nghe TWS giá rẻ tốt nhất Samsung"},
        "ipad 10 2022": {"rating": "4.5/5", "total_reviews": 2400, "pros": "Chip A14 mạnh, USB-C, màn 10.9 inch sắc nét", "cons": "Không hỗ trợ Apple Pencil 2, giá tăng so với thế hệ trước", "verdict": "iPad cơ bản tốt nhất cho sinh viên"},
        "xiaomi pad 6": {"rating": "4.4/5", "total_reviews": 1200, "pros": "Snapdragon 870 mạnh, màn 144Hz, 4 loa Dolby Atmos", "cons": "Không có GPS, phụ kiện ít hơn iPad", "verdict": "Tablet Android tốt nhất giá rẻ"},
    }

    query_lower = query.lower()
    for name, review in reviews_db.items():
        if name in query_lower:
            return (
                f"📝 Đánh giá {name.title()}:\n"
                f"  ⭐ Rating: {review['rating']} ({review['total_reviews']} reviews)\n"
                f"  ✅ Ưu điểm: {review['pros']}\n"
                f"  ❌ Nhược điểm: {review['cons']}\n"
                f"  💬 Kết luận: {review['verdict']}"
            )

    return f"Không có review cho sản phẩm này. Có review cho: Acer Aspire 5, ASUS VivoBook 15, HP Pavilion 15, Lenovo IdeaPad 3, MacBook Air M2, Dell Inspiron 15, MSI Modern 14, iPhone 15, Samsung Galaxy S24, OPPO Reno 11, Xiaomi Redmi Note 13, Sony WH-1000XM5, AirPods Pro 2, iPad 10, Xiaomi Pad 6."


# ==============================
# Đăng ký tools cho Agent
# ==============================
TOOLS = [
    {
        "name": "search_products",
        "description": "Search for products by category keyword. Input: a keyword like 'laptop', 'phone', 'tablet', 'headphone', 'smartwatch', or 'camera' (string). Output: list of products with name, price, specs, and rating.",
        "function": search_products
    },
    {
        "name": "compare_specs",
        "description": "Compare specifications of two products side by side. Input: two product names separated by space, e.g. 'acer aspire 5 asus vivobook 15' (string). Output: comparison table.",
        "function": compare_specs
    },
    {
        "name": "check_reviews",
        "description": "Check user reviews and ratings for a specific product. Input: product name, e.g. 'asus vivobook 15' (string). Output: rating, pros, cons, and verdict.",
        "function": check_reviews
    },
]
