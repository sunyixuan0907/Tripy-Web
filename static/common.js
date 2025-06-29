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