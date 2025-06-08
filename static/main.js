console.log('main.js loaded');
document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/items')
    .then(res => res.json())
    .then(items => {
      const list = document.getElementById('item-list');
      list.innerHTML = '';
      items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="menu-name">${item.name}</td>
          <td class="menu-price">$${item.price}</td>
          <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
        `;
        // 新增事件監聽，傳遞正確的 btn
        tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
          showOptionModal(item.name, item.price, this);
        });
        list.appendChild(tr);
      });
    });

  window.orderItem = function(id, name) {
    alert(`你選擇了「${name}」！(可在這裡實作點餐功能)`);
  }
});
const itemOptions = {
  '牛肉麵': ['不要蔥', '加麵'],
  '雞排飯': ['不要蔥', '加飯'],
  '陽春麵': ['加麵'],
  '滷肉飯': ['加飯'],
  '排骨便當': ['加飯', '不要蔥'],
  '燒臘飯': ['加飯'],
  '咖哩飯': ['加飯'],
  '水餃(10顆)': [],
  '鍋貼(10顆)': [],
  '雞腿飯': ['加飯', '不要蔥']
};

// Modal 元件互動
function showOptionModal(name, price, plusBtn) {
    const modal = document.getElementById('option-modal');
    const title = document.getElementById('modal-title');
    const checkboxes = document.getElementById('option-checkboxes');
    const noteInput = document.getElementById('option-note');
    title.textContent = `請選擇「${name}」細項`;
    checkboxes.innerHTML = '';
    noteInput.value = '';
    (itemOptions[name] || []).forEach(opt => {
        const label = document.createElement('label');
        label.style.display = 'block';
        label.innerHTML = `<input type='checkbox' name='options' value='${opt}'> ${opt}`;
        checkboxes.appendChild(label);
    });
    modal.style.display = 'block';
    // 關閉按鈕
    document.getElementById('modal-close').onclick = () => {
        modal.style.display = 'none';
    };
    // 表單送出
    document.getElementById('option-form').onsubmit = function(e) {
        e.preventDefault();
        const selected = Array.from(checkboxes.querySelectorAll('input:checked')).map(cb => cb.value);
        const note = noteInput.value;
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        cart.push({ name, price, options: selected, note });
        localStorage.setItem('cart', JSON.stringify(cart));
        modal.style.display = 'none';
        animateAddToCart(plusBtn); // 傳入正確的 + 按鈕
    };
}

function animateAddToCart(plusBtn) {
    const cartBtn = document.querySelector('.cart-btn-container') || document.querySelector('.cart-btn');
    if (!cartBtn) return;
    let lastBtn = plusBtn || document.querySelector('.menu-plus-btn');
    if (!lastBtn) return;
    const startRect = lastBtn.getBoundingClientRect();
    const endRect = cartBtn.getBoundingClientRect();
    const anim = document.createElement('div');
    anim.textContent = '+1';
    anim.style.position = 'fixed';
    anim.style.left = startRect.left + startRect.width / 2 + 'px';
    anim.style.top = startRect.top + 'px';
    anim.style.fontSize = '1.6em';
    anim.style.color = '#e67e22';
    anim.style.fontWeight = 'bold';
    anim.style.background = 'rgba(255,255,255,0.95)';
    anim.style.borderRadius = '50%';
    anim.style.padding = '6px 12px';
    anim.style.boxShadow = '0 2px 8px #0002';
    anim.style.zIndex = 9999;
    anim.style.pointerEvents = 'none';
    anim.style.transition = 'all 1.2s cubic-bezier(.4,1.6,.6,1)';
    anim.style.opacity = '1';
    anim.style.transform = 'scale(1)';
    document.body.appendChild(anim);
    setTimeout(() => {
        anim.style.left = endRect.left + endRect.width / 2 + 'px';
        anim.style.top = endRect.top + endRect.height / 2 + 'px';
        anim.style.opacity = '0';
        anim.style.transform = 'scale(1)'; // 保持一樣大小
    }, 20);
    setTimeout(() => {
        anim.remove();
    }, 1300);
}

document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/items')
    .then(res => res.json())
    .then(items => {
      const list = document.getElementById('item-list');
      list.innerHTML = '';
      items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="menu-name">${item.name}</td>
          <td class="menu-price">$${item.price}</td>
          <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
        `;
        // 新增事件監聽，傳遞正確的 btn
        tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
          showOptionModal(item.name, item.price, this);
        });
        list.appendChild(tr);
      });
    });
});