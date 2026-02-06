// static/script.js
// 这个文件控制网页的交互逻辑：点击按钮、发送请求、显示结果

document.addEventListener('DOMContentLoaded', () => {
    // 获取页面上的元素
    const form = document.getElementById('claim-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const resultArea = document.getElementById('result-area');
    const resultContent = document.getElementById('result-content');

    // 监听表单提交事件 (点击领取按钮时触发)
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // 阻止表单默认刷新页面的行为

        // 1. 获取用户输入
        const ycy_uid = document.getElementById('ycy_uid').value.trim();
        const qq = document.getElementById('qq').value.trim();

        if (!ycy_uid || !qq) {
            alert("请把信息填写完整哦！");
            return;
        }

        // 2. 界面切换为"加载中"状态
        setLoading(true);
        hideResult();

        try {
            // 3. 向后端发送请求
            const response = await fetch('/api/claim', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ycy_uid: ycy_uid,
                    qq: qq
                })
            });

            const data = await response.json();

            // 4. 处理返回结果
            if (data.success) {
                showSuccess(data);
            } else {
                showError(data.message);
            }

        } catch (error) {
            console.error('Error:', error);
            showError("网络连接出现问题，请稍后再试。");
        } finally {
            // 5. 恢复按钮状态
            setLoading(false);
        }
    });

    // 辅助函数：设置加载状态
    function setLoading(isLoading) {
        submitBtn.disabled = isLoading;
        if (isLoading) {
            btnText.style.display = 'none';
            loader.style.display = 'block';
        } else {
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    }

    // 辅助函数：显示成功结果
    function showSuccess(data) {
        let cardsHtml = '';
        // 遍历所有卡密，生成 HTML
        data.cards.forEach(card => {
            cardsHtml += `
            <div class="card-item" onclick="copyText('${card.content}')" title="点击复制">
                <span>${card.content}</span>
                <span style="font-size: 12px; color: #666; background: #eee; padding: 2px 6px; border-radius: 4px;">${card.value}鹤</span>
            </div>`;
        });

        const html = `
            <div class="result-card">
                <div class="success-header">🎉 ${data.message}</div>
                <div style="margin-bottom: 10px; font-size: 14px; text-align: center;">
                    共获得 <b>${data.zhihe_total}</b> 纸鹤
                </div>
                <div>${cardsHtml}</div>
                <div class="copy-hint">点击卡密可以直接复制</div>
            </div>
        `;

        resultContent.innerHTML = html;
        resultArea.classList.add('show');
    }

    // 辅助函数：显示错误信息
    function showError(msg) {
        const html = `
            <div class="result-card error">
                <div style="font-weight: bold; margin-bottom: 5px;">❌ 哎呀，出错了</div>
                <div>${msg}</div>
            </div>
        `;
        resultContent.innerHTML = html;
        resultArea.classList.add('show');
    }

    // 辅助函数：隐藏结果区域
    function hideResult() {
        resultArea.classList.remove('show');
        resultContent.innerHTML = '';
    }
});

// 全局函数：复制文本
function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        // 创建一个临时的浮动提示
        const toast = document.createElement('div');
        toast.textContent = '已复制!';
        toast.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 1000;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1000);
    }).catch(err => {
        console.error('无法复制', err);
    });
}
