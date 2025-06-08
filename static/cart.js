document.addEventListener('DOMContentLoaded', () => {
  renderCart();
});

function renderCart() {
  const cart = JSON.parse(localStorage.getItem('cart') || '[]');
  const list = document.getElementById('cart-list');
  list.innerHTML = '';
  if (cart.length === 0) {
    list.innerHTML = '<li>購物車是空的</li>';
    return;
  }
  cart.forEach((item, idx) => {
    const li = document.createElement('li');
    li.className = 'card';
    const optionsText = (item.options && item.options.length > 0)
      ? item.options.join('、')
      : '無';
    li.innerHTML = `
      <button class="card-remove-btn" onclick="removeCartItem(${idx})">&times;</button>
      <div class="card-title">${item.name}</div>
      <div class="card-price">$${item.price}</div>
      <div>細項：${optionsText}${item.note ? '，備註：' + item.note : ''}</div>
    `;
    list.appendChild(li);
  });
}

window.removeCartItem = function(idx) {
  let cart = JSON.parse(localStorage.getItem('cart') || '[]');
  cart.splice(idx, 1);
  localStorage.setItem('cart', JSON.stringify(cart));
  renderCart();
  window.dispatchEvent(new Event('cart-updated'));
};