// 通用脚本：加载 header.html 并绑定下拉交互
;(function(){
  const container = document.getElementById("headerContainer");
  if (!container) return;
  fetch("/static/header.html")
    .then(r => r.text())
    .then(html => {
      container.innerHTML = html;
      const dd = container.querySelector(".dropdown");
      const dc = container.querySelector(".dropdown-content");
      dd.addEventListener("mouseenter", () => dc.style.display = "block");
      dd.addEventListener("mouseleave", () => dc.style.display = "none");
    });
})();

// 动态引入 GSAP 动画库
(function() {
  if (!window.gsap) {
    const script = document.createElement('script');
    script.src = "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js";
    script.onload = () => { window.gsapLoaded = true; };
    document.head.appendChild(script);
  }
})();

// 添加带认证的请求函数
function authFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    ...(token ? { "Authorization": `Bearer ${token}` } : {})
  };
  
  return fetch(url, {
    ...options,
    headers
  }).then(res => {
    if (res.status === 401) {
      alert("请先登录！");
      window.location.href = "/static/login.html";
      throw new Error("认证失败");
    }
    return res;
  });
}

// 检查用户登录状态并更新顶栏
function updateAuthState() {
  const token = localStorage.getItem("access_token");
  const authBtn = document.getElementById("authBtn");
  if (authBtn) {
    if (token) {
      authBtn.textContent = "退出";
      authBtn.href = "javascript:logout()";
    } else {
      authBtn.textContent = "登录";
      authBtn.href = "/static/login.html";
    }
  }
}

// 退出登录
function logout() {
  localStorage.removeItem("access_token");
  alert("已退出登录");
  updateAuthState();
  window.location.href = "/static/index.html";
}