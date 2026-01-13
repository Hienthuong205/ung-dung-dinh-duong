<?php
session_start();

// --- GỌI FILE DỮ LIỆU ---
if (file_exists('menu_data.php')) {
    require_once 'menu_data.php';
} else {
    die("Lỗi: Thiếu file menu_data.php.");
}

// --- LOGIC XỬ LÝ ---

// 1. Reset
if (isset($_GET['action']) && $_GET['action'] == 'reset') {
    session_destroy();
    header("Location: index.php");
    exit();
}

// 2. Thiết lập hồ sơ
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['setup_profile'])) {
    $weight = floatval($_POST["weight"]);
    $height = floatval($_POST["height"]);
    $age    = intval($_POST["age"]);
    $gender = $_POST["gender"];
    $activity = floatval($_POST["activity"]);
    $goal = $_POST["goal"];

    // Tính BMR & TDEE
    $bmr = ($gender == "male") 
        ? (10 * $weight + 6.25 * $height - 5 * $age + 5)
        : (10 * $weight + 6.25 * $height - 5 * $age - 161);
    $tdee = $bmr * $activity;

    if ($goal == "lose") $baseTarget = $tdee - 500;
    elseif ($goal == "gain") $baseTarget = $tdee + 400;
    else $baseTarget = $tdee;

    $_SESSION['user'] = [
        'start_weight' => $weight,
        'final_weight' => 0,
        'base_target' => round($baseTarget),
        'daily_target' => round($baseTarget),
        'current_day' => 1,
        'current_meal' => 0, 
        'balance' => 0
    ];

    $_SESSION['calorie_history'] = array_fill(1, 7, 0); 

    // Tạo menu
    $menuList = isset($foodDatabase[$goal]) ? $foodDatabase[$goal] : [];
    $_SESSION['menu_plan'] = [];
    
    function getRandomDish($list) {
        if (empty($list)) return ["name" => "Chưa có món", "calo" => 0];
        return $list[array_rand($list)];
    }

    if (!empty($menuList)) {
        for($i = 1; $i <= 7; $i++) {
            $bf = getRandomDish($menuList['breakfast']);
            $ln = getRandomDish($menuList['lunch']);
            $dn = getRandomDish($menuList['dinner']);
            $_SESSION['menu_plan'][$i] = [
                'breakfast' => $bf, 'lunch' => $ln, 'dinner' => $dn,
                'targets' => [0 => $bf['calo'], 1 => $ln['calo'], 2 => $dn['calo']],
                'eaten' => [0 => 0, 1 => 0, 2 => 0],
                'is_custom' => [0 => false, 1 => false, 2 => false] // Đánh dấu món nào bị thay đổi
            ];
        }
    }
    header("Location: index.php");
    exit();
}

// 3. XỬ LÝ CẬP NHẬT BỮA ĂN (ĐÃ NÂNG CẤP)
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_meal'])) {
    if (isset($_SESSION['user'])) {
        $day = $_SESSION['user']['current_day'];
        $mealIndex = $_SESSION['user']['current_meal'];
        
        // Mapping index sang key mảng
        $mealKeys = [0 => 'breakfast', 1 => 'lunch', 2 => 'dinner'];
        $currentMealKey = $mealKeys[$mealIndex];

        $actualCalo = 0;
        // Lấy mục tiêu calo HIỆN TẠI của bữa này
        $plannedCalo = $_SESSION['menu_plan'][$day]['targets'][$mealIndex];

        if ($_POST['type'] == 'standard') {
            // Ăn đúng món gợi ý
            $actualCalo = $plannedCalo;
        } else {
            // Ăn món khác -> LƯU VÀO SESSION ĐỂ HIỂN THỊ
            $customName = $_POST['custom_name'];
            $actualCalo = floatval($_POST['custom_calo']);

            // 1. Cập nhật tên món mới vào thực đơn
            $_SESSION['menu_plan'][$day][$currentMealKey]['name'] = $customName . " (Món bạn chọn)";
            // 2. Cập nhật calo mới vào thực đơn
            $_SESSION['menu_plan'][$day][$currentMealKey]['calo'] = $actualCalo;
            // 3. Đánh dấu là món custom để tô màu
            $_SESSION['menu_plan'][$day]['is_custom'][$mealIndex] = true;
        }

        // Lưu lượng calo đã ăn
        $_SESSION['menu_plan'][$day]['eaten'][$mealIndex] = $actualCalo;

        // --- TÍNH TOÁN ĐIỀU CHỈNH CÁC BỮA SAU ---
        $diff = $actualCalo - $plannedCalo;

        if ($mealIndex < 2) {
            $remainingMealsCount = 2 - $mealIndex;
            $adjustment = $diff / $remainingMealsCount;

            for ($i = $mealIndex + 1; $i <= 2; $i++) {
                $oldTarget = $_SESSION['menu_plan'][$day]['targets'][$i];
                $newTarget = $oldTarget - $adjustment;
                if ($newTarget < 50) $newTarget = 50;

                // Cập nhật mục tiêu (Target) cho các bữa sau
                $_SESSION['menu_plan'][$day]['targets'][$i] = round($newTarget);
                
                // Cập nhật luôn số hiển thị trong object món ăn của các bữa sau
                // Để giao diện hiển thị con số mới
                $nextMealKey = $mealKeys[$i];
                $_SESSION['menu_plan'][$day][$nextMealKey]['calo'] = round($newTarget);
            }
        } 
        elseif ($mealIndex == 2) {
            $_SESSION['user']['balance'] += $diff;
        }

        $_SESSION['user']['current_meal']++;

        if ($_SESSION['user']['current_meal'] > 2) {
            $dayTotal = array_sum($_SESSION['menu_plan'][$day]['eaten']);
            $_SESSION['calorie_history'][$day] = $dayTotal;

            $_SESSION['user']['current_day']++;
            $_SESSION['user']['current_meal'] = 0;
            
            $newDailyTarget = $_SESSION['user']['base_target'] - $_SESSION['user']['balance'];
            if ($newDailyTarget < 1000) $newDailyTarget = 1000;
            $_SESSION['user']['daily_target'] = $newDailyTarget;
        }
    }
    header("Location: index.php");
    exit();
}

// 4. Xử lý cân nặng cuối
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['submit_final_weight'])) {
    $_SESSION['user']['final_weight'] = floatval($_POST['final_weight']);
    header("Location: index.php"); 
    exit();
}
?>

<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trợ Lý Dinh Dưỡng</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

<div class="container">
    <?php $isUserSet = isset($_SESSION['user']) && isset($_SESSION['user']['current_day']); ?>

    <?php if (!$isUserSet): ?>
        <div id="step-1" class="step-section active">
            <h2>Thiết Lập Hồ Sơ</h2>
            <form method="post">
                <input type="hidden" name="setup_profile" value="1">
                <div class="form-group"><label>Cân nặng (kg)</label><input type="number" step="0.1" name="weight" required></div>
                <div class="form-group"><label>Chiều cao (cm)</label><input type="number" name="height" required></div>
                <div class="form-group"><label>Tuổi</label><input type="number" name="age" required></div>
                <div class="form-group"><label>Giới tính</label><select name="gender"><option value="male">Nam</option><option value="female">Nữ</option></select></div>
                <div class="form-group"><label>Mức vận động</label><select name="activity"><option value="1.2">Ít vận động</option><option value="1.375">Nhẹ</option><option value="1.55">Vừa</option><option value="1.725">Nhiều</option></select></div>
                <div class="form-group"><label>Mục tiêu</label><select name="goal"><option value="lose">Giảm cân</option><option value="keep">Giữ cân</option><option value="gain">Tăng cân</option></select></div>
                <button type="submit" class="btn btn-primary">Bắt Đầu</button>
            </form>
        </div>

    <?php elseif ($_SESSION['user']['current_day'] > 7): ?>
        <?php if ($_SESSION['user']['final_weight'] == 0): ?>
            <div class="step-section active">
                <h2>🎉 Hoàn Thành!</h2>
                <div style="text-align: center; margin-bottom: 20px;"><i class="fas fa-weight-scale" style="font-size: 60px; color: #11998e;"></i></div>
                <p style="text-align: center;">Nhập cân nặng hiện tại để xem kết quả.</p>
                <form method="post">
                    <input type="hidden" name="submit_final_weight" value="1">
                    <div class="form-group"><label>Cân nặng hiện tại (kg):</label><input type="number" step="0.1" name="final_weight" required></div>
                    <button type="submit" class="btn btn-primary">Xem Biểu Đồ</button>
                </form>
            </div>
        <?php else: ?>
            <div class="step-section active">
                <h2>📊 Tổng Kết</h2>
                <div class="summary-stats">
                    <div class="stat-item"><div class="stat-label">Ban đầu</div><div class="stat-value"><?= $_SESSION['user']['start_weight'] ?> kg</div></div>
                    <div class="stat-item"><div class="stat-label">Hiện tại</div><div class="stat-value"><?= $_SESSION['user']['final_weight'] ?> kg</div></div>
                </div>
                <div class="chart-box"><canvas id="caloChart"></canvas></div>
                <a href="index.php?action=reset" class="btn btn-outline" style="border:none;">Lập Kế Hoạch Mới</a>
            </div>
            <script>
                const caloHistory = <?= json_encode(array_values($_SESSION['calorie_history'])) ?>;
                const baseTarget = <?= $_SESSION['user']['base_target'] ?>;
                new Chart(document.getElementById('caloChart'), {
                    type: 'line',
                    data: {
                        labels: ['Ngày 1', 'Ngày 2', 'Ngày 3', 'Ngày 4', 'Ngày 5', 'Ngày 6', 'Ngày 7'],
                        datasets: [{
                            label: 'Calo nạp vào', data: caloHistory, borderColor: '#38ef7d', backgroundColor: 'rgba(56, 239, 125, 0.2)', fill: true, tension: 0.4
                        }, {
                            label: 'Mục tiêu', data: Array(7).fill(baseTarget), borderColor: '#ff7675', borderDash: [5, 5], fill: false
                        }]
                    }
                });
            </script>
        <?php endif; ?>

    <?php else: ?>
        <?php
            $day = $_SESSION['user']['current_day'];
            $mealIdx = $_SESSION['user']['current_meal'];
            
            if (isset($_SESSION['menu_plan'][$day])) {
                $menuToday = $_SESSION['menu_plan'][$day];
            } else { echo "<script>window.location.href='index.php?action=reset';</script>"; exit; }

            $mealNames = [0 => 'breakfast', 1 => 'lunch', 2 => 'dinner'];
            $mealLabels = [0 => '🍳 Bữa Sáng', 1 => '🍛 Bữa Trưa', 2 => '🍲 Bữa Tối'];
        ?>
        <div id="dashboard" class="step-section active">
            <h2>Ngày <?= $day ?> / 7</h2>
            <div class="progress-container"><div class="progress-bar" style="width: <?= (($day-1)*3 + $mealIdx)/21 * 100 ?>%;"></div></div>

            <div class="menu-card">
                <?php for($i=0; $i<3; $i++): 
                    $key = $mealNames[$i];
                    $dishName = $menuToday[$key]['name'];
                    // Lấy calo hiện tại (đã được cập nhật nếu có)
                    $currentCalo = $menuToday[$key]['calo'];
                    $isCustom = $menuToday['is_custom'][$i];
                    
                    $statusClass = 'meal-pending';
                    $badge = '<span class="meal-badge badge-pending">Chờ</span>';
                    
                    if ($i < $mealIdx) {
                        $statusClass = 'meal-done';
                        $badge = '<span class="meal-badge badge-done"><i class="fas fa-check"></i> Xong</span>';
                    } elseif ($i == $mealIdx) {
                        $statusClass = 'meal-active';
                        $badge = '<span class="meal-badge badge-active">Đang ăn</span>';
                    }
                ?>
                <div class="meal-row <?= $statusClass ?>">
                    <?= $badge ?>
                    <span class="meal-name <?= $isCustom ? 'changed' : '' ?>">
                        <strong><?= $mealLabels[$i] ?>:</strong> <?= $dishName ?>
                        
                        <?php if($i > $mealIdx && isset($menuToday['targets'][$i]) && $currentCalo != $_SESSION['user']['base_target']/3 /* Logic kiểm tra đơn giản */): ?>
                            <?php 
                                // Logic hiển thị cảnh báo thông minh hơn
                                $originalTargetEstimate = $_SESSION['user']['daily_target'] * ($i==1?0.4:0.3); // Ước lượng
                                $diffShow = $currentCalo - $originalTargetEstimate;
                             ?>
                            <span class="adjust-note">
                                <i class="fas fa-sync-alt"></i> 
                                Khẩu phần đã điều chỉnh: <strong><?= $currentCalo ?> kcal</strong>
                            </span>
                        <?php endif; ?>
                    </span>
                    <span class="meal-cal"><?= $currentCalo ?> kcal</span>
                </div>
                <?php endfor; ?>
            </div>

            <div style="background: #fff; padding: 15px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; font-size: 18px; color: #11998e;">Cập nhật <?= $mealLabels[$mealIdx] ?></h3>
                <form method="post" id="updateForm">
                    <input type="hidden" name="update_meal" value="1">
                    <input type="hidden" name="update_type" id="updateType" value="standard">
                    
                    <div class="action-buttons">
                        <button type="button" onclick="submitStandard()" class="btn btn-finish"><i class="fas fa-check"></i> Đúng món này</button>
                        <button type="button" onclick="toggleCustom()" class="btn btn-custom"><i class="fas fa-edit"></i> Món khác</button>
                    </div>

                    <div id="customInput" class="custom-input-box">
                        <label>Tên món bạn đã ăn:</label>
                        <input type="text" name="custom_name" placeholder="VD: Bún bò, Cơm tấm...">
                        
                        <label>Tổng Calo thực tế:</label>
                        <input type="number" name="custom_calo" placeholder="VD: 500">
                        
                        <button type="submit" class="btn btn-primary" style="margin-top: 10px;">Cập nhật & Tính lại</button>
                    </div>
                </form>
            </div>
            <a href="index.php?action=reset" style="display: block; text-align: center; margin-top: 20px; font-size: 14px; color: #999;">Reset lộ trình</a>
        </div>
    <?php endif; ?>
</div>

<script>
    function submitStandard() { document.getElementById('updateType').value = 'standard'; document.getElementById('updateForm').submit(); }
    function toggleCustom() {
        var box = document.getElementById('customInput');
        document.getElementById('updateType').value = 'custom';
        box.style.display = (box.style.display === "block") ? "none" : "block";
    }
</script>

</body>
</html>