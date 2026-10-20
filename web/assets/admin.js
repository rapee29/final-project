const $ = (selector) => document.querySelector(selector);
const money = (value) => `฿${Number(value || 0).toLocaleString('th-TH', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
const dateTime = (value) => value ? value.replace('T', ' ') : '—';
let menuItems = [];
let toastTimer;

function showToast(message, error = false) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.toggle('error', error);
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {'Content-Type': 'application/json', ...(options.headers || {})},
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'ไม่สามารถโหลดข้อมูลได้');
  return body;
}

function renderSummary(summary) {
  $('#revenue').textContent = money(summary.revenue);
  $('#discounts').textContent = `ส่วนลด ${money(summary.discounts)}`;
  $('#transactions').textContent = Number(summary.transactions || 0).toLocaleString('th-TH');
  $('#cups').textContent = Number(summary.cups || 0).toLocaleString('th-TH');
  $('#top-drink').textContent = summary.top_drink
    ? `ขายดี: ${summary.top_drink} ${summary.top_drink_cups} แก้ว`
    : 'ยังไม่มีเมนูขายวันนี้';
  $('#advice').textContent = summary.advice || 'ยังไม่มีคำแนะนำสำหรับวันนี้';
}

function renderMenu(items) {
  menuItems = items;
  const body = $('#menu-body');
  body.replaceChildren();
  if (!items.length) {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="4" class="loading">ยังไม่มีเมนู</td>';
    body.append(row);
    return;
  }
  for (const item of items) {
    const row = document.createElement('tr');
    const id = document.createElement('td'); id.textContent = `#${item.drink_id}`;
    const name = document.createElement('td'); name.textContent = item.name;
    const price = document.createElement('td'); price.textContent = money(item.price);
    const actions = document.createElement('td');
    const edit = document.createElement('button'); edit.className = 'table-action'; edit.textContent = 'แก้ไข';
    edit.addEventListener('click', () => openMenuDialog(item));
    const remove = document.createElement('button'); remove.className = 'table-action delete'; remove.textContent = 'ลบ';
    remove.addEventListener('click', () => deleteMenu(item));
    actions.append(edit, remove); row.append(id, name, price, actions); body.append(row);
  }
}

function renderOrders(items) {
  const body = $('#orders-body');
  body.replaceChildren();
  $('#order-count').textContent = `${items.length} ออเดอร์`;
  $('#orders-empty').classList.toggle('hidden', items.length > 0);
  for (const order of [...items].reverse().slice(0, 12)) {
    const row = document.createElement('tr');
    const values = [
      `#${order.order_id}`,
      dateTime(order.timestamp),
      order.member_name || 'ลูกค้าทั่วไป',
      (order.items || []).map((item) => `${item.name} ×${item.qty}`).join(', '),
      money(order.total), money(order.change),
    ];
    for (const value of values) {
      const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
    }
    body.append(row);
  }
  if (!items.length) body.innerHTML = '<tr><td colspan="6" class="loading">ยังไม่มีออเดอร์</td></tr>';
}

async function refreshDashboard() {
  $('#menu-body').innerHTML = '<tr><td colspan="4" class="loading">กำลังโหลดเมนู...</td></tr>';
  try {
    const [summary, menu, orders] = await Promise.all([
      api('/api/admin/summary'), api('/api/admin/menu'), api('/api/admin/orders'),
    ]);
    renderSummary(summary);
    renderMenu(menu.items || []);
    renderOrders(orders.items || []);
  } catch (error) {
    showToast(error.message, true);
  }
}

function openMenuDialog(item = null) {
  $('#menu-form').reset();
  $('#form-error').textContent = '';
  $('#menu-id').value = item ? item.drink_id : '';
  $('#form-title').textContent = item ? 'แก้ไขเมนู' : 'เพิ่มเมนู';
  $('#menu-name').value = item ? item.name : '';
  $('#menu-price').value = item ? item.price : '';
  $('#menu-dialog').showModal();
}

async function deleteMenu(item) {
  if (!window.confirm(`ยืนยันลบเมนู “${item.name}” หรือไม่?`)) return;
  try {
    await api(`/api/admin/menu/${item.drink_id}`, {method: 'DELETE'});
    showToast('ลบเมนูแล้ว');
    await refreshDashboard();
  } catch (error) {
    showToast(error.message, true);
  }
}

$('#add-menu').addEventListener('click', () => openMenuDialog());
$('#close-dialog').addEventListener('click', () => $('#menu-dialog').close());
$('#refresh-button').addEventListener('click', refreshDashboard);
$('#menu-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const id = $('#menu-id').value;
  const payload = {name: $('#menu-name').value.trim(), price: Number($('#menu-price').value)};
  try {
    await api(id ? `/api/admin/menu/${id}` : '/api/admin/menu', {
      method: id ? 'PUT' : 'POST', body: JSON.stringify(payload),
    });
    $('#menu-dialog').close();
    showToast(id ? 'บันทึกการแก้ไขแล้ว' : 'เพิ่มเมนูแล้ว');
    await refreshDashboard();
  } catch (error) {
    $('#form-error').textContent = error.message;
  }
});

refreshDashboard();
