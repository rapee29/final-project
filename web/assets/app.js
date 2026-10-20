const SIZE_OPTIONS = [
  { code: 'S', label: 'เล็ก', extra: 0 },
  { code: 'M', label: 'กลาง', extra: 10 },
  { code: 'L', label: 'ใหญ่', extra: 20 },
];
const MILK_OPTIONS = [
  { id: 1, label: 'นมปกติ', extra: 0 },
  { id: 2, label: 'นมถั่วเหลือง', extra: 10 },
  { id: 3, label: 'นมอัลมอนด์', extra: 15 },
];
const SWEETNESS = ['0%', '25%', '50%', '100%'];
const ICONS = ['☕', '🧊', '🥛', '☕', '🍫', '🍵'];
const ART = ['espresso', 'americano', 'latte', 'cappuccino', 'mocha', 'matcha'];
const state = { menu: [], members: [], cart: [], category: 'all', selectedDrink: null, selection: { size: 'M', milkId: 1, sweetness: '50%' }, toastTimer: null };
const $ = (selector) => document.querySelector(selector);
const money = (value) => `฿${Number(value || 0).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));

function showToast(message, isError = false) {
  const toast = $('#toast'); toast.textContent = message; toast.classList.toggle('error', isError); toast.classList.add('show');
  clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}
async function api(path, options = {}) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}
async function refreshData() {
  if (window.location.protocol === 'file:') {
    $('#menu-grid').innerHTML = '<div class="loading-card file-mode-notice">เปิดไฟล์ HTML โดยตรงจึงเชื่อมต่อข้อมูลไม่ได้<br><a href="http://127.0.0.1:8000/">เปิดเว็บ POS ผ่านเซิร์ฟเวอร์</a><small>หากลิงก์เปิดไม่ได้ ให้รัน <code>python3 web_app.py</code> ในโฟลเดอร์โปรเจกต์ก่อน</small></div>';
    $('#checkout-hint').textContent = 'เปิดเว็บผ่าน http://127.0.0.1:8000 เพื่อเริ่มรับออเดอร์';
    return;
  }
  try {
    const [menu, members] = await Promise.all([api('/api/menu'), api('/api/members')]);
    state.menu = menu.items || []; state.members = members.items || [];
    renderMenu(); renderCart();
  } catch (error) {
    showToast(`เชื่อมต่อระบบไม่ได้: ${error.message}`, true);
    $('#menu-grid').innerHTML = '<div class="loading-card">โหลดข้อมูลไม่สำเร็จ กรุณากด ↻ เพื่อลองใหม่</div>';
  }
}
function renderMenu() {
  const query = $('#menu-search').value.trim().toLocaleLowerCase('th');
  const filtered = state.menu.filter((drink) => {
    const matchQuery = drink.name.toLocaleLowerCase('th').includes(query);
    const isOther = /matcha|ชา|โกโก้|ช็อกโกแลต/i.test(drink.name);
    const matchCategory = state.category === 'all' || (state.category === 'other' ? isOther : !isOther);
    return matchQuery && matchCategory;
  });
  $('#menu-count').textContent = state.menu.length; $('#all-count').textContent = state.menu.length;
  if (!filtered.length) { $('#menu-grid').innerHTML = '<div class="loading-card">ไม่พบเมนูที่ค้นหา</div>'; return; }
  $('#menu-grid').innerHTML = filtered.map((drink) => {
    const index = Math.max(0, state.menu.findIndex((item) => item.drink_id === drink.drink_id));
    const isOther = /matcha|ชา|โกโก้|ช็อกโกแลต/i.test(drink.name);
    return `<article class="menu-card"><div class="drink-art art-${ART[index % ART.length]}"><span>${ICONS[index % ICONS.length]}</span><small class="drink-tag">${isOther ? 'SIGNATURE' : 'COFFEE'}</small></div><div class="drink-name-row"><strong class="drink-name" title="${esc(drink.name)}">${esc(drink.name)}</strong><span class="drink-price">${money(drink.price)}</span></div><p class="drink-caption">ชงสดทุกแก้ว · เลือกสูตรได้</p><button class="add-button" data-add="${Number(drink.drink_id)}">＋ &nbsp; ปรับสูตรและเพิ่ม</button></article>`;
  }).join('');
}
function selectedMember() {
  const phone = $('#member-phone').value.trim();
  return phone ? state.members.find((member) => member.phone === phone) : null;
}
function cartSubtotal() { return state.cart.reduce((sum, line) => sum + line.unitPrice * line.qty, 0); }
function cartDiscount() { const member = selectedMember(); return member ? Math.round(cartSubtotal() * member.discount_rate * 100) / 100 : 0; }
function cartTotal() { return Math.max(0, cartSubtotal() - cartDiscount()); }
function renderCart() {
  const empty = state.cart.length === 0;
  $('#cart-empty').classList.toggle('hidden', !empty); $('#cart-list').classList.toggle('hidden', empty); $('#checkout-fields').classList.toggle('hidden', empty); $('#totals').classList.toggle('hidden', empty);
  $('#cart-count').textContent = state.cart.reduce((sum, line) => sum + line.qty, 0);
  $('#cart-list').innerHTML = state.cart.map((line) => `<div class="cart-row"><span class="cart-row-title">${esc(line.name)}</span><span class="cart-row-price">${money(line.unitPrice * line.qty)}</span><span class="cart-row-meta">${line.size} · ${esc(line.milkLabel)} · หวาน ${line.sweetness}</span><div class="cart-row-controls"><button data-cart-action="minus" data-key="${line.key}" aria-label="ลดจำนวน">−</button><span>${line.qty}</span><button data-cart-action="plus" data-key="${line.key}" aria-label="เพิ่มจำนวน">+</button><button class="remove-line" data-cart-action="remove" data-key="${line.key}" aria-label="ลบรายการ">×</button></div></div>`).join('');
  const member = selectedMember();
  $('#member-hint').textContent = $('#member-phone').value.trim() ? (member ? `สมาชิก ${member.name} · รับส่วนลด ${Math.round(member.discount_rate * 100)}%` : 'ไม่พบเบอร์สมาชิกนี้ ตรวจสอบอีกครั้ง') : 'กรอกเบอร์สมาชิกเพื่อรับส่วนลด 10%';
  $('#member-hint').classList.toggle('valid', Boolean(member));
  $('#subtotal').textContent = money(cartSubtotal()); $('#discount').textContent = `− ${money(cartDiscount())}`; $('#total').textContent = money(cartTotal()); $('#exact-amount').textContent = money(cartTotal());
  const cash = Number($('#cash-input').value);
  $('#checkout-button').disabled = empty || !Number.isFinite(cash) || cash < cartTotal() || Boolean($('#member-phone').value.trim() && !member);
  const hint = $('#checkout-hint');
  if (empty) hint.textContent = 'เพิ่มสินค้าในออเดอร์ก่อนชำระ';
  else if ($('#member-phone').value.trim() && !member) hint.textContent = 'ไม่พบสมาชิก ตรวจสอบเบอร์โทรก่อนชำระ';
  else if (!Number.isFinite(cash) || $('#cash-input').value === '') hint.textContent = 'กรอกเงินสดที่รับเพื่อเปิดใช้ปุ่มชำระ';
  else if (cash < cartTotal()) hint.textContent = `เงินสดยังขาด ${money(cartTotal() - cash)}`;
  else hint.textContent = `พร้อมชำระ · เงินทอน ${money(cash - cartTotal())}`;
}
function openCustomize(drinkId) {
  const drink = state.menu.find((item) => item.drink_id === drinkId); if (!drink) return;
  state.selectedDrink = drink; state.selection = { size: 'M', milkId: 1, sweetness: '50%' };
  $('#dialog-drink-id').value = drink.drink_id; $('#dialog-drink-name').textContent = drink.name; $('#dialog-drink-price').textContent = `เริ่มต้น ${money(drink.price)}`;
  const index = state.menu.findIndex((item) => item.drink_id === drinkId); $('#dialog-icon').textContent = ICONS[Math.max(0, index) % ICONS.length]; $('#dialog-qty').value = 1;
  $('#size-options').innerHTML = SIZE_OPTIONS.map((item) => `<button type="button" class="option-button ${item.code === state.selection.size ? 'selected' : ''}" data-option="size" data-value="${item.code}">${item.label}<small>+${money(item.extra)}</small></button>`).join('');
  $('#milk-options').innerHTML = MILK_OPTIONS.map((item) => `<button type="button" class="option-button ${item.id === state.selection.milkId ? 'selected' : ''}" data-option="milkId" data-value="${item.id}">${item.label}<small>+${money(item.extra)}</small></button>`).join('');
  $('#sweetness-options').innerHTML = SWEETNESS.map((item) => `<button type="button" class="option-button ${item === state.selection.sweetness ? 'selected' : ''}" data-option="sweetness" data-value="${item}">${item}</button>`).join('');
  updateDialogTotal(); $('#customize-dialog').showModal();
}
function unitPrice() {
  const size = SIZE_OPTIONS.find((item) => item.code === state.selection.size); const milk = MILK_OPTIONS.find((item) => item.id === state.selection.milkId);
  return Number(state.selectedDrink?.price || 0) + (size?.extra || 0) + (milk?.extra || 0);
}
function updateDialogTotal() { $('#dialog-total').textContent = money(unitPrice() * Math.max(1, Number($('#dialog-qty').value) || 1)); }
function addSelectedDrink(event) {
  event.preventDefault(); if (!state.selectedDrink) return;
  const qty = Math.max(1, Math.min(99, Number($('#dialog-qty').value) || 1)); const milk = MILK_OPTIONS.find((item) => item.id === state.selection.milkId);
  const key = [state.selectedDrink.drink_id, state.selection.size, state.selection.milkId, state.selection.sweetness].join('-');
  const existing = state.cart.find((line) => line.key === key);
  if (existing) existing.qty = Math.min(99, existing.qty + qty);
  else state.cart.push({ key, drinkId: state.selectedDrink.drink_id, name: state.selectedDrink.name, size: state.selection.size, milkId: state.selection.milkId, milkLabel: milk.label, sweetness: state.selection.sweetness, qty, unitPrice: unitPrice() });
  $('#customize-dialog').close(); renderCart(); showToast(`เพิ่ม ${state.selectedDrink.name} ลงออเดอร์แล้ว`);
}
function formatTimestamp(value) {
  const [day, time = ''] = String(value || '').split(' '); const [year, month, date] = day.split('-');
  return `${date || ''}/${month || ''}/${year || ''} · ${time.slice(0, 5)}`;
}
async function checkout() {
  if (!state.cart.length) return;
  const phone = $('#member-phone').value.trim(); const member = selectedMember(); const cash = Number($('#cash-input').value);
  if (phone && !member) { showToast('ไม่พบสมาชิก กรุณาตรวจสอบเบอร์โทร', true); return; }
  if (!Number.isFinite(cash) || cash < cartTotal()) { showToast('จำนวนเงินสดไม่พอชำระ', true); return; }
  const button = $('#checkout-button'); button.disabled = true; button.innerHTML = 'กำลังบันทึกออเดอร์…';
  try {
    const payload = { items: state.cart.map((line) => ({ drink_id: line.drinkId, size: line.size, milk_id: line.milkId, sweetness: line.sweetness, qty: line.qty })), cash_received: cash };
    if (phone) payload.member_phone = phone;
    const result = await api('/api/orders', { method: 'POST', body: JSON.stringify(payload) });
    const order = result.order; renderReceipt(order); state.cart = []; $('#member-phone').value = ''; $('#cash-input').value = ''; renderCart();
    $('#receipt-dialog').showModal();
  } catch (error) { showToast(error.message, true); }
  finally { button.innerHTML = 'ชำระเงิน <span>→</span>'; renderCart(); }
}
function renderReceipt(order) {
  $('#receipt-order-no').textContent = `ออเดอร์ #${String(order.order_id).padStart(4, '0')} · ${formatTimestamp(order.timestamp)}`;
  $('#receipt-lines').innerHTML = (order.items || []).map((item) => `<div class="receipt-line"><span>${esc(item.name)} · ${item.size} × ${item.qty}</span><strong>${money(item.total_price)}</strong></div>`).join('');
  $('#receipt-paid').textContent = money(order.total); $('#receipt-cash').textContent = money(order.cash_received); $('#receipt-change').textContent = money(order.change);
}
function setTodayLabel() {
  $('#today-label').textContent = new Intl.DateTimeFormat('th-TH', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }).format(new Date());
}

document.addEventListener('click', (event) => {
  const add = event.target.closest('[data-add]'); if (add) openCustomize(Number(add.dataset.add));
  const option = event.target.closest('[data-option]');
  if (option) { state.selection[option.dataset.option] = option.dataset.option === 'milkId' ? Number(option.dataset.value) : option.dataset.value; option.parentElement.querySelectorAll('.option-button').forEach((button) => button.classList.toggle('selected', button === option)); updateDialogTotal(); }
  const action = event.target.closest('[data-cart-action]');
  if (action) { const line = state.cart.find((item) => item.key === action.dataset.key); if (!line) return; if (action.dataset.cartAction === 'plus') line.qty = Math.min(99, line.qty + 1); if (action.dataset.cartAction === 'minus') line.qty -= 1; if (action.dataset.cartAction === 'remove' || line.qty < 1) state.cart = state.cart.filter((item) => item !== line); renderCart(); }
  const category = event.target.closest('[data-category]');
  if (category) { state.category = category.dataset.category; document.querySelectorAll('.category-chip').forEach((chip) => chip.classList.toggle('selected', chip === category)); renderMenu(); }
});
$('#customize-form').addEventListener('submit', addSelectedDrink);
$('#dialog-close').addEventListener('click', () => $('#customize-dialog').close());
$('#qty-minus').addEventListener('click', () => { $('#dialog-qty').value = Math.max(1, Number($('#dialog-qty').value) - 1); updateDialogTotal(); });
$('#qty-plus').addEventListener('click', () => { $('#dialog-qty').value = Math.min(99, Number($('#dialog-qty').value) + 1); updateDialogTotal(); });
$('#dialog-qty').addEventListener('input', updateDialogTotal);
$('#member-phone').addEventListener('input', renderCart); $('#cash-input').addEventListener('input', renderCart);
$('#exact-cash').addEventListener('click', () => { $('#cash-input').value = cartTotal().toFixed(2); renderCart(); });
$('#checkout-button').addEventListener('click', checkout);
$('#refresh-button').addEventListener('click', refreshData);
$('#menu-search').addEventListener('input', renderMenu);
$('#receipt-close').addEventListener('click', () => $('#receipt-dialog').close()); $('#receipt-done').addEventListener('click', () => $('#receipt-dialog').close());
setTodayLabel(); refreshData();
