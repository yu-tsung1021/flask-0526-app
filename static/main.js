// main.js：主頁菜單互動、點餐動畫、桌號選擇、分類分群
console.log('main.js loaded');
document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/items')
    .then(res => res.json())
    .then(items => {
      // 分類規則
      const categoryMap = {
        '飯類': ['雞排飯','滷肉飯','排骨便當','燒臘飯','咖哩飯','雞腿飯','三杯雞飯','麻婆豆腐飯','蔥爆豬肉飯'],
        '麵類': ['牛肉麵','陽春麵','紅燒牛腩麵','炸醬麵','酸辣湯麵'],
        '湯類': ['青菜蛋花湯','紫菜蛋花湯','玉米濃湯','酸辣湯'],
        '水餃類': ['水餃(10顆)'],
        '鍋貼類': ['鍋貼(10顆)']
      };
      // 依分類渲染
      const list = document.getElementById('item-list');
      list.innerHTML = '';
      // 先依照原本 categoryMap 渲染預設菜單
      Object.entries(categoryMap).forEach(([cat, names]) => {
        // 插入分類錨點
        const anchor = document.createElement('tr');
        anchor.id = 'menu-' + cat.replace('類','').replace('飯','fan').replace('麵','mian').replace('湯','tang').replace('水餃','shuijiao').replace('鍋貼','guotie');
        anchor.innerHTML = `<td colspan="3" class="menu-category-title">${cat}</td>`;
        list.appendChild(anchor);
        // 原本預設菜單
        items.filter(item => names.includes(item.name)).forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="menu-name">${item.name}</td>
            <td class="menu-price">$${item.price}</td>
            <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
          `;
          tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
            showOptionModal(item.name, item.price, this);
          });
          list.appendChild(tr);
        });
        // 新增：渲染該分類下資料庫有但 categoryMap 沒有的自訂菜品
        items.filter(item => item.category === cat && !names.includes(item.name)).forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="menu-name">${item.name}</td>
            <td class="menu-price">$${item.price}</td>
            <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
          `;
          tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
            showOptionModal(item.name, item.price, this);
          });
          list.appendChild(tr);
        });
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
  '雞腿飯': ['加飯', '不要蔥'],
  '紅燒牛腩麵': ['加麵', '不要香菜'],
  '三杯雞飯': ['加飯', '不要九層塔'],
  '麻婆豆腐飯': ['加飯', '微辣', '中辣', '大辣'],
  '蔥爆豬肉飯': ['加飯', '不要蔥'],
  '炸醬麵': ['加麵', '不要蔥'],
  '酸辣湯麵': ['加麵', '加辣'],
  '青菜蛋花湯': ['加蛋', '加青菜'],
  '紫菜蛋花湯': ['加蛋', '加紫菜'],
  '玉米濃湯': ['加蛋', '加玉米'],
  '酸辣湯': ['加辣', '不要香菜'],
  '醬油乾麵': ['不要蔥', '不要香菜']
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
      // 分類規則
      const categoryMap = {
        '飯類': ['雞排飯','滷肉飯','排骨便當','燒臘飯','咖哩飯','雞腿飯','三杯雞飯','麻婆豆腐飯','蔥爆豬肉飯'],
        '麵類': ['牛肉麵','陽春麵','紅燒牛腩麵','炸醬麵','酸辣湯麵'],
        '湯類': ['青菜蛋花湯','紫菜蛋花湯','玉米濃湯','酸辣湯'],
        '水餃類': ['水餃(10顆)'],
        '鍋貼類': ['鍋貼(10顆)']
      };
      // 依分類渲染
      const list = document.getElementById('item-list');
      list.innerHTML = '';
      // 先依照原本 categoryMap 渲染預設菜單
      Object.entries(categoryMap).forEach(([cat, names]) => {
        // 插入分類錨點
        const anchor = document.createElement('tr');
        anchor.id = 'menu-' + cat.replace('類','').replace('飯','fan').replace('麵','mian').replace('湯','tang').replace('水餃','shuijiao').replace('鍋貼','guotie');
        anchor.innerHTML = `<td colspan="3" class="menu-category-title">${cat}</td>`;
        list.appendChild(anchor);
        // 原本預設菜單
        items.filter(item => names.includes(item.name)).forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="menu-name">${item.name}</td>
            <td class="menu-price">$${item.price}</td>
            <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
          `;
          tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
            showOptionModal(item.name, item.price, this);
          });
          list.appendChild(tr);
        });
        // 新增：渲染該分類下資料庫有但 categoryMap 沒有的自訂菜品
        items.filter(item => item.category === cat && !names.includes(item.name)).forEach(item => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="menu-name">${item.name}</td>
            <td class="menu-price">$${item.price}</td>
            <td class="menu-plus"><button class="menu-plus-btn">＋</button></td>
          `;
          tr.querySelector('.menu-plus-btn').addEventListener('click', function() {
            showOptionModal(item.name, item.price, this);
          });
          list.appendChild(tr);
        });
      });
    });
});