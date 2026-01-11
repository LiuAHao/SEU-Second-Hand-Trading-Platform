# ================================================
# 数据库迁移脚本 - PowerShell 版
# 东南大学校园二手交易平台 v1.0 -> v2.0
# ================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "数据库迁移向导" -ForegroundColor Cyan
Write-Host "版本: v1.0 -> v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已备份
Write-Host "步骤 1/4: 检查备份文件..." -ForegroundColor Yellow
$backupFile = "backup.sql"
if (Test-Path $backupFile) {
    Write-Host "✅ 找到备份文件: $backupFile" -ForegroundColor Green
    $fileSize = (Get-Item $backupFile).Length / 1KB
    Write-Host "   文件大小: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "❌ 未找到备份文件: $backupFile" -ForegroundColor Red
    Write-Host "   请先执行: mysqldump -u root -p seu_second_hand > backup.sql" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 确认执行
Write-Host "步骤 2/4: 确认迁移信息..." -ForegroundColor Yellow
Write-Host "数据库: seu_second_hand" -ForegroundColor White
Write-Host "迁移脚本: database\migration_v1_to_v2.sql" -ForegroundColor White
Write-Host ""
$confirmation = Read-Host "确认执行迁移? (输入 YES 继续，其他任意键取消)"

if ($confirmation -ne "YES") {
    Write-Host "❌ 迁移已取消" -ForegroundColor Red
    exit 0
}
Write-Host ""

# 执行迁移
Write-Host "步骤 3/4: 执行数据库迁移..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Gray

try {
    # 使用 cmd 执行 MySQL 命令（PowerShell 不支持 < 重定向）
    $cmd = "mysql -u root -p seu_second_hand < database\migration_v1_to_v2.sql"
    $output = cmd /c "$cmd 2>&1" | Out-String

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 迁移执行成功!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 迁移执行完成，但可能存在警告" -ForegroundColor Yellow
        Write-Host $output -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ 迁移执行失败!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
Write-Host ""

# 验证迁移
Write-Host "步骤 4/4: 验证迁移结果..." -ForegroundColor Yellow
Write-Host "请手动执行以下 SQL 验证:" -ForegroundColor White
Write-Host ""
Write-Host "mysql -u root -p seu_second_hand" -ForegroundColor Cyan
Write-Host "SHOW TABLES;" -ForegroundColor Cyan
Write-Host "DESC favorites;" -ForegroundColor Cyan
Write-Host "DESC orders;" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "迁移完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 重启 Flask 应用: python run.py" -ForegroundColor White
Write-Host "2. 测试收藏功能" -ForegroundColor White
Write-Host "3. 检查订单数据完整性" -ForegroundColor White
Write-Host ""
