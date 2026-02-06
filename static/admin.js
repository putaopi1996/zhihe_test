// admin.js
// =============================================
// 管理后台逻辑 v2.0
// =============================================

// 全局变量
let adminPassword = "";
let usersPage = 1;
let cardsPage = 1;
const pageSize = 20;

// =============================================
// 初始化
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    // 优先从 sessionStorage 获取密码 (来自首页登录)
    const storedPwd = sessionStorage.getItem('adminPassword');

    if (storedPwd) {
        adminPassword = storedPwd;
        verifyAndInit();
    } else {
        // 如果没有预存密码，弹出输入框 (备用)
        adminPassword = prompt("请输入管理员密码:");

        if (!adminPassword) {
            alert("必须输入密码才能访问后台！");
            window.location.href = '/';
            return;
        }
        verifyAndInit();
    }
});

async function verifyAndInit() {
    try {
        const res = await apiCall('/api/admin/stats', 'GET');

        if (res.ok) {
            // 密码正确，显示内容
            document.getElementById('admin-content').style.display = 'block';

            // 更新统计
            const data = await res.json();
            updateStats(data);

            // 加载数据
            loadUsers();
            loadCards();

            // 绑定事件
            bindEvents();
        } else {
            // 验证失败
            sessionStorage.removeItem('adminPassword'); // 清除错误密码

            // 给用户重试机会
            adminPassword = prompt("密码错误或过期，请重新输入管理员密码:");
            if (adminPassword) {
                // 递归重试
                verifyAndInit();
            } else {
                window.location.href = '/';
            }
        }
    } catch (err) {
        alert("连接服务器失败：" + err.message);
        // 不强制跳转，允许用户检查网络
    }
}

// =============================================
// API 调用封装
// =============================================

async function apiCall(url, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'X-Admin-Password': adminPassword
        }
    };

    if (body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    return fetch(url, options);
}

// =============================================
// 统计数据
// =============================================

function updateStats(data) {
    document.getElementById('stat-users').textContent = data.users.total;
    document.getElementById('stat-claimed').textContent = data.users.claimed;
    document.getElementById('stat-10').textContent = data.stock['10'];
    document.getElementById('stat-5').textContent = data.stock['5'];
    document.getElementById('stat-3').textContent = data.stock['3'];
    document.getElementById('stat-1').textContent = data.stock['1'];
}

async function refreshStats() {
    try {
        const res = await apiCall('/api/admin/stats');
        if (res.ok) {
            const data = await res.json();
            updateStats(data);
        }
    } catch (e) {
        console.error("刷新统计失败", e);
    }
}

// =============================================
// 用户管理
// =============================================

async function loadUsers() {
    try {
        const res = await apiCall(`/api/admin/users?page=${usersPage}&page_size=${pageSize}`);
        if (!res.ok) {
            console.error("加载用户失败");
            return;
        }

        const data = await res.json();
        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = '';

        data.users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.ycy_uid}</td>
                <td>${user.nickname}</td>
                <td>${user.qq}</td>
                <td>${user.zhihe_count}</td>
                <td><span class="status-badge ${user.has_claimed ? 'yes' : 'no'}">${user.has_claimed ? '是' : '否'}</span></td>
                <td>
                    <button class="btn btn-edit" onclick="editUser(${user.id}, '${user.nickname}', '${user.qq}', ${user.zhihe_count}, ${user.has_claimed})">编辑</button>
                    <button class="btn btn-delete" onclick="deleteUser(${user.id})">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('users-page-info').textContent = `第 ${usersPage} 页 / 共 ${Math.ceil(data.total / pageSize)} 页`;
    } catch (e) {
        console.error("加载用户出错", e);
    }
}

function editUser(id, nickname, qq, zhihe, claimed) {
    document.getElementById('edit-user-id').value = id;
    document.getElementById('edit-user-nickname').value = nickname;
    document.getElementById('edit-user-qq').value = qq;
    document.getElementById('edit-user-zhihe').value = zhihe;
    document.getElementById('edit-user-claimed').checked = claimed;
    document.getElementById('edit-user-modal').classList.add('active');
}

async function saveUser() {
    const id = document.getElementById('edit-user-id').value;
    const data = {
        nickname: document.getElementById('edit-user-nickname').value,
        qq: document.getElementById('edit-user-qq').value,
        zhihe_count: parseInt(document.getElementById('edit-user-zhihe').value),
        has_claimed: document.getElementById('edit-user-claimed').checked
    };

    try {
        const res = await apiCall(`/api/admin/users/${id}`, 'PUT', data);
        if (res.ok) {
            alert("保存成功！");
            closeModal('edit-user-modal');
            loadUsers();
            refreshStats();
        } else {
            const err = await res.json();
            alert("保存失败：" + err.detail);
        }
    } catch (e) {
        alert("保存出错：" + e.message);
    }
}

async function deleteUser(id) {
    if (!confirm("确定要删除这个用户吗？")) return;

    try {
        const res = await apiCall(`/api/admin/users/${id}`, 'DELETE');
        if (res.ok) {
            alert("删除成功！");
            loadUsers();
            refreshStats();
        } else {
            const err = await res.json();
            alert("删除失败：" + err.detail);
        }
    } catch (e) {
        alert("删除出错：" + e.message);
    }
}

// =============================================
// 卡密管理
// =============================================

async function loadCards() {
    try {
        let url = `/api/admin/cards?page=${cardsPage}&page_size=${pageSize}`;

        const valueFilter = document.getElementById('card-filter-value').value;
        const usedFilter = document.getElementById('card-filter-used').value;

        if (valueFilter) url += `&value=${valueFilter}`;
        if (usedFilter) url += `&used=${usedFilter}`;

        const res = await apiCall(url);
        if (!res.ok) {
            console.error("加载卡密失败");
            return;
        }

        const data = await res.json();
        const tbody = document.getElementById('cards-table-body');
        tbody.innerHTML = '';

        data.cards.forEach(card => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${card.id}</td>
                <td>${card.code}</td>
                <td>${card.value} 纸鹤</td>
                <td><span class="status-badge ${card.is_used ? 'yes' : 'no'}">${card.is_used ? '已使用' : '未使用'}</span></td>
                <td>${card.used_by || '-'}</td>
                <td>
                    <button class="btn btn-edit" onclick="editCard(${card.id}, '${card.code}', ${card.value}, ${card.is_used})">编辑</button>
                    <button class="btn btn-delete" onclick="deleteCard(${card.id})">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('cards-page-info').textContent = `第 ${cardsPage} 页 / 共 ${Math.ceil(data.total / pageSize)} 页`;
    } catch (e) {
        console.error("加载卡密出错", e);
    }
}

function editCard(id, code, value, used) {
    document.getElementById('edit-card-id').value = id;
    document.getElementById('edit-card-code').value = code;
    document.getElementById('edit-card-value').value = value;
    document.getElementById('edit-card-used').checked = used;
    document.getElementById('edit-card-modal').classList.add('active');
}

async function saveCard() {
    const id = document.getElementById('edit-card-id').value;
    const data = {
        code: document.getElementById('edit-card-code').value,
        value: parseInt(document.getElementById('edit-card-value').value),
        is_used: document.getElementById('edit-card-used').checked
    };

    try {
        const res = await apiCall(`/api/admin/cards/${id}`, 'PUT', data);
        if (res.ok) {
            alert("保存成功！");
            closeModal('edit-card-modal');
            loadCards();
            refreshStats();
        } else {
            const err = await res.json();
            alert("保存失败：" + err.detail);
        }
    } catch (e) {
        alert("保存出错：" + e.message);
    }
}

async function deleteCard(id) {
    if (!confirm("确定要删除这个卡密吗？")) return;

    try {
        const res = await apiCall(`/api/admin/cards/${id}`, 'DELETE');
        if (res.ok) {
            alert("删除成功！");
            loadCards();
            refreshStats();
        } else {
            const err = await res.json();
            alert("删除失败：" + err.detail);
        }
    } catch (e) {
        alert("删除出错：" + e.message);
    }
}

// =============================================
// 导入功能
// =============================================

async function importUsers() {
    const text = document.getElementById('import-user-data').value;
    const status = document.getElementById('import-user-status');

    if (!text.trim()) {
        status.textContent = "请输入数据";
        return;
    }

    const lines = text.trim().split('\n');
    const users = [];

    for (let line of lines) {
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
        status.textContent = "未识别到有效数据";
        return;
    }

    status.textContent = "导入中...";

    try {
        const res = await apiCall('/api/admin/users/import', 'POST', users);
        if (res.ok) {
            const data = await res.json();
            status.textContent = "✅ " + data.message;
            document.getElementById('import-user-data').value = '';
            loadUsers();
            refreshStats();
        } else {
            const err = await res.json();
            status.textContent = "❌ " + err.detail;
        }
    } catch (e) {
        status.textContent = "❌ 导入失败：" + e.message;
    }
}

async function addCards() {
    const codes = document.getElementById('card-codes').value;
    const value = document.getElementById('card-value').value;
    const status = document.getElementById('add-card-status');

    if (!codes.trim()) {
        status.textContent = "请输入卡密";
        return;
    }

    status.textContent = "添加中...";

    try {
        const body = {
            content: codes,
            value: parseInt(value)
        };
        const res = await apiCall('/api/admin/cards/add', 'POST', body);

        if (res.ok) {
            const data = await res.json();
            status.textContent = "✅ " + data.message;
            document.getElementById('card-codes').value = '';
            loadCards();
            refreshStats();
        } else {
            const err = await res.json();
            // 如果 detail 是对象（如验证错误），转为字符串显示
            const msg = typeof err.detail === 'object' ? JSON.stringify(err.detail) : err.detail;
            status.textContent = "❌ " + msg;
        }
    } catch (e) {
        status.textContent = "❌ 添加失败：" + e.message;
    }
}

// =============================================
// 辅助函数
// =============================================

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function bindEvents() {
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    // 用户分页
    document.getElementById('users-prev').addEventListener('click', () => {
        if (usersPage > 1) {
            usersPage--;
            loadUsers();
        }
    });
    document.getElementById('users-next').addEventListener('click', () => {
        usersPage++;
        loadUsers();
    });

    // 卡密分页
    document.getElementById('cards-prev').addEventListener('click', () => {
        if (cardsPage > 1) {
            cardsPage--;
            loadCards();
        }
    });
    document.getElementById('cards-next').addEventListener('click', () => {
        cardsPage++;
        loadCards();
    });

    // 卡密筛选
    document.getElementById('apply-card-filter').addEventListener('click', () => {
        cardsPage = 1;
        loadCards();
    });

    // 导入按钮
    document.getElementById('import-users-btn').addEventListener('click', importUsers);
    document.getElementById('add-cards-btn').addEventListener('click', addCards);
}
