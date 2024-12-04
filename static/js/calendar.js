console.log("Full Booked Slots Data:", bookedSlots);

const calendar = document.getElementById("calendar");
const timeSlotsContainer = document.getElementById("time-slots-container");
const bookingForm = document.getElementById("booking-form");
const selectedDateInput = document.getElementById("selected-date");
const selectedTimeInput = document.getElementById("selected-time");

const allTimes = [
    { time: "8:00 AM", period: "Morning" },
    { time: "9:00 AM", period: "Morning" },
    { time: "10:00 AM", period: "Morning" },
    { time: "11:00 AM", period: "Morning" },
    { time: "12:00 PM", period: "Afternoon" },
    { time: "1:00 PM", period: "Afternoon" },
    { time: "2:00 PM", period: "Afternoon" },
    { time: "3:00 PM", period: "Afternoon" },
    { time: "4:00 PM", period: "Afternoon" },
    { time: "5:00 PM", period: "Evening" },
    { time: "6:00 PM", period: "Evening" }
];

let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

function normalizeTime(time) {
    const [hour, minuteAndPeriod] = time.split(":");
    const [minute, period] = minuteAndPeriod.split(" ");
    const normalizedHour = hour.padStart(2, "0");
    return `${normalizedHour}:${minute} ${period}`;
}

function updateCalendar() {
    calendar.innerHTML = ""; // Clear existing calendar
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    const monthName = new Date(currentYear, currentMonth).toLocaleString("default", { month: "long", year: "numeric" });
    document.getElementById("current-month").textContent = monthName;

    // Add empty cells for offset
    for (let i = 0; i < firstDayOfMonth; i++) {
        const emptyCell = document.createElement("div");
        emptyCell.className = "day";
        calendar.appendChild(emptyCell);
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const dayString = `${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

        const dayDiv = document.createElement("div");
        dayDiv.className = "day";
        dayDiv.dataset.date = dayString;
        dayDiv.innerHTML = `<div>${day}</div><div class="indicators"></div>`;

        const indicators = dayDiv.querySelector(".indicators");

        ["Morning", "Afternoon", "Evening"].forEach(period => {
            const indicator = document.createElement("div");
            indicator.className = "indicator";

            const periodBooked =
                bookedSlots[dayString] &&
                allTimes
                    .filter(slot => slot.period === period)
                    .every(slot => {
                        const normalizedSlotTime = normalizeTime(slot.time);
                        const isBooked = bookedSlots[dayString].includes(normalizedSlotTime);
                        return isBooked;
                    });

            if (periodBooked) {
                indicator.classList.add("booked");
            }

            indicators.appendChild(indicator);
        });

        dayDiv.onclick = () => showTimeSlots(dayString, bookedSlots[dayString] || []);
        calendar.appendChild(dayDiv);
    }
}

function showTimeSlots(date, times) {
    console.log(`Selected Date: ${date}, Booked Times:`, times);

    selectedDateInput.value = date;

    document.querySelectorAll(".day").forEach(day => day.classList.remove("selected"));
    const selectedDay = document.querySelector(`.day[data-date='${date}']`);
    if (selectedDay) selectedDay.classList.add("selected");

    bookingForm.style.display = "none";

    const availableTimes = allTimes.filter(slot => {
        const normalizedSlotTime = normalizeTime(slot.time);
        return !times.includes(normalizedSlotTime);
    });

    const periods = { Morning: [], Afternoon: [], Evening: [] };
    availableTimes.forEach(slot => periods[slot.period].push(slot.time));

    ["Morning", "Afternoon", "Evening"].forEach(period => {
        const container = document.getElementById(`${period.toLowerCase()}-slots`);
        container.innerHTML = `<h4>${period}</h4>`;
        periods[period].forEach(time => {
            const timeSlot = document.createElement("div");
            timeSlot.className = "time-slot";
            timeSlot.textContent = time;
            timeSlot.onclick = () => selectTime(time, timeSlot);
            container.appendChild(timeSlot);
        });
    });

    timeSlotsContainer.style.display = "flex";
}

function selectTime(time, timeSlotElement) {
    selectedTimeInput.value = time;

    document.querySelectorAll(".time-slot").forEach(slot => slot.classList.remove("selected"));
    timeSlotElement.classList.add("selected");

    bookingForm.style.display = "block";
}

async function submitBooking(event) {
    event.preventDefault();
    const data = {
        date: selectedDateInput.value,
        time: selectedTimeInput.value,
        first_name: document.getElementById("first-name").value,
        last_name: document.getElementById("last-name").value,
        email: document.getElementById("email").value,
        phone_number: document.getElementById("phone-number").value,
    };

    const response = await fetch("/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    alert(result.message);
}

document.getElementById("prev-month").onclick = () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    updateCalendar();
};

document.getElementById("next-month").onclick = () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    updateCalendar();
};

// Initialize the calendar for the current month
updateCalendar();
