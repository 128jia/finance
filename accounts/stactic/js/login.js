document.addEventListener("DOMContentLoaded", function() {
    // 選擇登入表單
    const loginForm = document.querySelector("form");

    // 檢查是否找到了表單
    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            // 禁止默認的表單提交行為
            event.preventDefault();

            // 獲取表單數據
            const formData = new FormData(loginForm);

            // 建立一個新的 AJAX 請求
            fetch(loginForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                // 處理伺服器返回的數據
                if (data.success) {
                    alert("登入成功！");
                    window.location.href = data.redirect_url || "/";
                } else {
                    alert("無效的登入憑證");
                }
            })
            .catch(error => {
                console.error("錯誤：", error);
                alert("發生錯誤，請稍後再試。");
            });
        });
    }
});