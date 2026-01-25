# menu_data.py
food_database = {
    "lose": {  # GIẢM CÂN
        "breakfast": [
            {"name": "Yến mạch (50g) trộn sữa chua không đường + 5 quả dâu tây", "calo": 300},
            {"name": "2 Trứng luộc + 1 củ khoai lang nhỏ (100g)", "calo": 320},
            {"name": "2 lát Bánh mì đen + 1/2 quả Bơ thái lát", "calo": 310},
            {"name": "Cháo yến mạch (1 bát vừa) + Thịt nạc bằm (50g)", "calo": 330},
            {"name": "Bún gạo lứt (1 bát nhỏ) + 100g Ức gà xé", "calo": 350},
            {"name": "Sinh tố (1 chuối, 100ml sữa tươi k đường) + 1 muỗng Whey", "calo": 280}
        ],
        "lunch": [
            {"name": "1 bát cơm gạo lứt + 150g Ức gà áp chảo + 1 đĩa Súp lơ luộc", "calo": 450},
            {"name": "Salad cá ngừ (1/2 hộp) + 1 lát bánh mì đen + Rau xà lách", "calo": 400},
            {"name": "Bún chùm ngây (1 tô vừa) + 100g Thịt nạc luộc", "calo": 420},
            {"name": "1 bát cơm gạo lứt + 200g Cá hồi hấp xì dầu + Dưa leo", "calo": 480},
            {"name": "150g Thịt bò xào bông cải + 1 bát cơm gạo lứt nhỏ", "calo": 460},
            {"name": "Tôm luộc (5 con to) + Salad (Rau mầm, cà chua bi)", "calo": 390}
        ],
        "dinner": [
            {"name": "Salad ức gà (100g) xé phay + Sốt mè rang ít béo", "calo": 300},
            {"name": "Canh bí đỏ nấu thịt bằm (1 tô lớn, không ăn cơm)", "calo": 280},
            {"name": "Cá diêu hồng hấp gừng (1 khứa) + Rau cải luộc", "calo": 320},
            {"name": "Gỏi cuốn tôm thịt (3 cái) + Nước chấm pha loãng", "calo": 330},
            {"name": "Miến gà (1 bát vừa, bỏ da gà, nhiều giá đỗ)", "calo": 340},
            {"name": "Súp cua óc heo (1 chén súp, ít bột năng)", "calo": 310}
        ]
    },
    "keep": {  # GIỮ CÂN
        "breakfast": [
            {"name": "Phở bò tái (1 tô tiêu chuẩn, ít nước béo)", "calo": 450},
            {"name": "Bánh mì ốp la (1 ổ, 2 trứng, dưa leo)", "calo": 420},
            {"name": "Hủ tiếu Nam Vang (1 tô vừa, đủ tôm thịt)", "calo": 480},
            {"name": "Bún mọc (1 tô, kèm rau sống)", "calo": 430},
            {"name": "Xôi bắp (1 gói) + Đậu xanh + Hành phi", "calo": 400},
            {"name": "Bánh cuốn (1 đĩa) + 2 lát Chả lụa", "calo": 460}
        ],
        "lunch": [
            {"name": "1 bát Cơm trắng + Thịt kho trứng (1 trứng, 3 miếng thịt)", "calo": 600},
            {"name": "Cơm tấm sườn bì (1 miếng sườn cốt lết)", "calo": 650},
            {"name": "Cơm chiên dương châu (1 đĩa đầy) + Canh rau", "calo": 620},
            {"name": "Lẩu thái (ăn kèm 1 đĩa bún nhỏ + rau muống)", "calo": 610},
            {"name": "1 bát Cơm + 1/2 con Cá diêu hồng chiên xù", "calo": 580},
            {"name": "Bún đậu mắm tôm (1 mẹt vừa, không gọi thêm)", "calo": 600}
        ],
        "dinner": [
            {"name": "1 bát Cơm + Canh cua rau đay + 5 quả Cà pháo", "calo": 500},
            {"name": "Cháo gà (1 tô lớn) + Gỏi gà xé phay", "calo": 450},
            {"name": "Bò né (1 phần) + 1 ổ Bánh mì + Xíu mại", "calo": 550},
            {"name": "Mì xào bò (1 gói mì, 100g bò, cải ngọt)", "calo": 520},
            {"name": "Bánh canh cua (1 tô, có chả cua, huyết)", "calo": 480},
            {"name": "1 bát Cơm + Mực xào chua ngọt (dứa, cà chua)", "calo": 530}
        ]
    },
    "gain": {  # TĂNG CÂN
        "breakfast": [
            {"name": "Xôi mặn thập cẩm (Hộp lớn: chả, lạp xưởng, chà bông)", "calo": 650},
            {"name": "Cơm tấm sườn non (Miếng to) + 2 trứng ốp la + Bì", "calo": 750},
            {"name": "Bò kho (Tô lớn, nhiều nạm) + 2 ổ bánh mì đặc ruột", "calo": 700},
            {"name": "Bún bò Huế (Tô đặc biệt: Giò heo, chả cua, nạm)", "calo": 720},
            {"name": "Phở bò đặc biệt (Tô xe lửa, thêm chén bò viên)", "calo": 680},
            {"name": "2 gói Mì xào bò + 2 Trứng ốp la", "calo": 690}
        ],
        "lunch": [
            {"name": "2 bát Cơm đầy + Thịt ba chỉ kho tàu (5 miếng to)", "calo": 800},
            {"name": "Cơm gà xối mỡ (Đùi góc tư to) + Canh rong biển", "calo": 850},
            {"name": "Mì Ý sốt kem (Phần lớn) + Thịt xông khói + Xúc xích", "calo": 900},
            {"name": "Cơm niêu bò tiêu đen (Nhiều sốt) + Khoai tây chiên", "calo": 820},
            {"name": "Cơm chiên hải sản (Đĩa lớn) + 1 Đùi gà rán", "calo": 880},
            {"name": "Bún chả Hà Nội (Phần đặc biệt nhiều thịt nướng)", "calo": 780}
        ],
        "dinner": [
            {"name": "2 bát Cơm + Giò heo hầm măng (1 khoanh giò to)", "calo": 750},
            {"name": "Lẩu riêu cua bắp bò (Ăn kèm 2 vắt mì trứng)", "calo": 780},
            {"name": "Pizza bò xay (3 lát size L) + Salad dầu giấm", "calo": 800},
            {"name": "Vịt quay (1/4 con) + 2 cái Bánh bao chiên", "calo": 820},
            {"name": "Burger bò phô mai 2 lớp + Khoai tây chiên + Cola", "calo": 850},
            {"name": "Cơm rang dưa bò (Đĩa đầy, nhiều bò)", "calo": 760}
        ]
    }
}
