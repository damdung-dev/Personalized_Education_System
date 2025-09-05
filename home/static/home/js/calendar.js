// Hiển thị giờ hiện tại + highlight ngày hôm nay
function updateTime() {
    const now = new Date();
    const hh = now.getHours().toString().padStart(2,'0');
    const mm = now.getMinutes().toString().padStart(2,'0');
    const ss = now.getSeconds().toString().padStart(2,'0');
    document.getElementById('current-time').textContent = `${hh}:${mm}:${ss}`;

    // Reset highlight
    document.querySelectorAll('.calendar-cell.today').forEach(el => el.classList.remove('today'));
    document.querySelectorAll('.calendar-cell').forEach(el => {
        const dayId = el.id.replace('day-', '');
        const cellDate = new Date(dayId);
        if (!isNaN(cellDate) && cellDate.toDateString() === now.toDateString()) {
            el.classList.add('today');
        }
    });
}

// Nút "Hôm nay"
document.getElementById('today-btn').addEventListener('click', () => {
    const todayElem = document.querySelector('.calendar-cell.today');
    if (todayElem) {
        todayElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        todayElem.animate([
            { boxShadow: '0 0 0 0 rgba(0,122,255,0.8)' },
            { boxShadow: '0 0 20px 6px rgba(0,122,255,0.6)' },
            { boxShadow: '0 0 0 0 rgba(0,122,255,0)' }
        ], { duration: 1500 });
    }
});

// Cập nhật mỗi giây
setInterval(updateTime, 1000);
updateTime();
