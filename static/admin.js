// static/admin.js
// 管理员后台的逻辑

document.addEventListener('DOMContentLoaded', () => {
    // 简单的前端密码验证 (仅作为演示，不防君子)
    const adminPass = prompt("请输入管理员密码 (任意输入即可进入，实际使用请修改源码):");
    if (adminPass === null) {
        window.location.href = '/';
        return;
    }

    refreshStats();

    // --- 导入用户 ---
    document.getElementById('import-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = document.getElementById('user-data').value;
        const status = document.getElementById('import-status');

        if (!text.trim()) return;

        // 解析 CSV/Excel 粘贴的文本
        // 假设格式: UID 昵称 QQ 数量 (或者是 Tab 分隔)
        const lines = text.trim().split('\n');
        const users = [];

        for (let line of lines) {
            // 支持逗号、Tab、空格分隔
            const parts = line.split(/[,\t\s]+/).filter(x => x);
            if (parts.length >= 4) {
                users.push({
                    ycy_id: parts[0],
                    nickname: parts[1],
                    qq: parts[2],
                    zhihe: parseInt(parts[3])
                });
            }
        }

        if (users.length === 0) {
            status.textContent = "未识别到有效数据，请检查格式。";
            return;
        }

        status.textContent = "正在导入...";

        try {
            const res = await fetch('/api/admin/import_users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(users)
            });
            const data = await res.json();
            status.textContent = `✅ ${data.message}`;
            document.getElementById('user-data').value = '';
            refreshStats();
        } catch (err) {
            status.textContent = "❌ 导入失败: " + err;
        }
    });

    // --- 添加卡密 ---
    document.getElementById('card-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = document.getElementById('card-content').value;
        const value = document.querySelector('input[name="card-value"]:checked').value;
        const status = document.getElementById('card-status');

        if (!content.trim()) return;

        status.textContent = "正在添加...";

        try {
            // 注意：这里用 URLSearchParams 传参数，跟后端接收对应
            const url = `/api/admin/add_cards?value=${value}&content=${encodeURIComponent(content)}`;
            const res = await fetch(url, {
                method: 'POST'
            });
            const data = await res.json();
            status.textContent = `✅ ${data.message}`;
            document.getElementById('card-content').value = '';
            refreshStats();
        } catch (err) {
            status.textContent = "❌ 添加失败: " + err;
        }
    });
});

async function refreshStats() {
    try {
        const res = await fetch('/api/admin/stats');
        const data = await res.json();

        // 更新显示
        document.getElementById('stat-10').textContent = data.stock['10'];
        document.getElementById('stat-5').textContent = data.stock['5'];
        document.getElementById('stat-3').textContent = data.stock['3'];
        document.getElementById('stat-1').textContent = data.stock['1'];

        document.getElementById('stat-users').textContent = data.users.total;
        document.getElementById('stat-claimed').textContent = data.users.claimed;
    } catch (err) {
        console.error("获取统计失败", err);
    }
}
