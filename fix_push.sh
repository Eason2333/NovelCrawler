#!/bin/bash
# Git 推送问题修复脚本

echo "=========================================="
echo "开始修复 Git 推送问题"
echo "=========================================="
echo ""

# 1. 拉取远程更改（允许不相关的历史）
echo "步骤 1: 拉取远程更改..."
git pull origin main --allow-unrelated-histories

# 检查是否有冲突
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  检测到合并冲突，需要手动解决"
    echo "请查看冲突文件，解决后执行："
    echo "  git add ."
    echo "  git commit -m '解决合并冲突'"
    echo "  git push origin main"
    exit 1
fi

echo ""
echo "步骤 2: 推送更改到远程..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
else
    echo ""
    echo "❌ 推送失败，请检查错误信息"
fi

