/**
 * SmartKeja - Booking Component
 */

import { formatDate, validateEmail, validatePhone, showNotification } from '../utils/helpers.js';

export class Booking {
    constructor() {
        this.selectedDate = null;
        this.selectedTime = null;
        this.currentPropertyId = null;
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        this.init();
    }

    init() {
        this.setupCalendar();
        this.setupTimeSlots();
        this.setupBookingModal();
        this.setupFormValidation();
        
        // Try to render calendar immediately if container exists
        // Otherwise it will render when modal opens
        if (document.getElementById('calendarDays')) {
            this.renderCalendar();
        }
    }

    setupBookingModal() {
        const bookingModal = document.getElementById('bookingModal');
        if (!bookingModal) return;

        bookingModal.addEventListener('show.bs.modal', (e) => {
            const button = e.relatedTarget;
            this.currentPropertyId = button ? button.getAttribute('data-property-id') : null;
            // Reset form first
            this.resetBookingForm();
        });

        // Render calendar when modal is fully shown (Bootstrap 5)
        bookingModal.addEventListener('shown.bs.modal', () => {
            // Ensure calendar renders after modal is visible
            this.renderCalendar();
        });

        // Confirm booking button
        const confirmBtn = bookingModal.querySelector('#confirmBooking');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.submitBooking());
        }
    }

    setupCalendar() {
        // Month navigation
        const prevMonthBtn = document.getElementById('prevMonth');
        const nextMonthBtn = document.getElementById('nextMonth');
        
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', () => {
                this.currentMonth--;
                if (this.currentMonth < 0) {
                    this.currentMonth = 11;
                    this.currentYear--;
                }
                this.renderCalendar();
            });
        }
        
        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', () => {
                this.currentMonth++;
                if (this.currentMonth > 11) {
                    this.currentMonth = 0;
                    this.currentYear++;
                }
                this.renderCalendar();
            });
        }
    }

    renderCalendar() {
        const calendarDaysContainer = document.getElementById('calendarDays');
        const monthYearElement = document.getElementById('currentMonthYear');
        
        if (!calendarDaysContainer) {
            console.warn('Calendar container (#calendarDays) not found');
            return;
        }
        
        console.log('Rendering calendar for', this.currentMonth + 1, this.currentYear);
        
        // Update month/year display
        if (monthYearElement) {
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December'];
            monthYearElement.textContent = `${monthNames[this.currentMonth]} ${this.currentYear}`;
        }
        
        // Get first day of month and number of days
        const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
        const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
        const today = new Date();
        const currentDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        
        // Clear previous calendar
        calendarDaysContainer.innerHTML = '';
        
        // Add empty cells for days before month starts
        const rows = [];
        let currentRow = [];
        
        for (let i = 0; i < firstDay; i++) {
            currentRow.push('<div class="col calendar-day text-muted disabled"></div>');
        }
        
        // Add days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(this.currentYear, this.currentMonth, day);
            const isPast = date < currentDate;
            const isToday = date.getTime() === currentDate.getTime();
            const dateStr = `${this.currentYear}-${String(this.currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            
            let classes = 'col calendar-day';
            if (isPast) {
                classes += ' disabled text-muted';
            } else {
                classes += ' available';
            }
            if (isToday) {
                classes += ' today';
            }
            
            currentRow.push(`<div class="${classes}" data-date="${dateStr}">${day}</div>`);
            
            if (currentRow.length === 7) {
                rows.push(`<div class="row g-0">${currentRow.join('')}</div>`);
                currentRow = [];
            }
        }
        
        // Fill remaining cells
        while (currentRow.length > 0 && currentRow.length < 7) {
            currentRow.push('<div class="col calendar-day text-muted disabled"></div>');
        }
        if (currentRow.length > 0) {
            rows.push(`<div class="row g-0">${currentRow.join('')}</div>`);
        }
        
        calendarDaysContainer.innerHTML = rows.join('');
        
        // Add click listeners to available days
        const availableDays = calendarDaysContainer.querySelectorAll('.calendar-day.available');
        console.log('Calendar rendered with', availableDays.length, 'available days');
        
        availableDays.forEach(day => {
            day.addEventListener('click', (e) => {
                const clickedDay = e.target;
                
                // Remove selected class from all days
                calendarDaysContainer.querySelectorAll('.calendar-day').forEach(d => {
                    d.classList.remove('selected');
                });
                
                // Add selected class to clicked day
                clickedDay.classList.add('selected');
                
                // Store selected date
                this.selectedDate = clickedDay.getAttribute('data-date');
                document.getElementById('selectedDateValue').value = this.selectedDate;
                this.updateSelectedInfo();
            });
        });
    }

    setupTimeSlots() {
        const timeSlots = document.querySelectorAll('.time-slot:not(.disabled)');
        timeSlots.forEach(slot => {
            slot.addEventListener('click', (e) => {
                const clickedSlot = e.target;
                
                // Remove selected class from all slots
                timeSlots.forEach(s => s.classList.remove('selected'));
                
                // Add selected class to clicked slot
                clickedSlot.classList.add('selected');
                
                // Get time value
                this.selectedTime = clickedSlot.textContent.trim();
                this.updateSelectedInfo();
            });
        });
    }

    updateSelectedInfo() {
        const infoElement = document.querySelector('#selectedDateTime');
        if (infoElement && this.selectedDate && this.selectedTime) {
            const dateObj = new Date(this.selectedDate);
            const dateStr = dateObj.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            infoElement.innerHTML = `
                <i class="bi bi-calendar-check me-2"></i>
                <strong>Selected:</strong> ${dateStr} at ${this.selectedTime}
            `;
        } else if (infoElement && this.selectedDate) {
            const dateObj = new Date(this.selectedDate);
            const dateStr = dateObj.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            infoElement.innerHTML = `
                <i class="bi bi-info-circle me-2"></i>
                <strong>Date:</strong> ${dateStr} - Please select a time slot
            `;
        } else if (infoElement) {
            infoElement.innerHTML = '<i class="bi bi-info-circle me-2"></i>Please select a date and time';
        }
    }

    setupFormValidation() {
        const bookingForm = document.querySelector('#bookingForm');
        if (!bookingForm) return;

        const nameInput = bookingForm.querySelector('#bookingName');
        const emailInput = bookingForm.querySelector('#bookingEmail');
        const phoneInput = bookingForm.querySelector('#bookingPhone');

        if (nameInput) {
            nameInput.addEventListener('blur', () => {
                this.validateField(nameInput, nameInput.value.trim().length >= 2, 'Name must be at least 2 characters');
            });
        }

        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                this.validateField(emailInput, validateEmail(emailInput.value), 'Please enter a valid email address');
            });
        }

        if (phoneInput) {
            phoneInput.addEventListener('blur', () => {
                this.validateField(phoneInput, validatePhone(phoneInput.value), 'Please enter a valid Kenyan phone number');
            });
        }
    }

    validateField(field, isValid, errorMessage) {
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            const feedback = field.parentElement.querySelector('.invalid-feedback');
            if (feedback) feedback.remove();
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            let feedback = field.parentElement.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentElement.appendChild(feedback);
            }
            feedback.textContent = errorMessage;
        }
        return isValid;
    }

    validateBookingForm() {
        const nameInput = document.querySelector('#bookingName');
        const emailInput = document.querySelector('#bookingEmail');
        const phoneInput = document.querySelector('#bookingPhone');

        let isValid = true;

        if (!this.selectedDate || !this.selectedTime) {
            showNotification('Please select a date and time for your viewing', 'warning');
            isValid = false;
        }

        if (!nameInput || !this.validateField(nameInput, nameInput.value.trim().length >= 2, 'Name is required')) {
            isValid = false;
        }

        if (!emailInput || !this.validateField(emailInput, validateEmail(emailInput.value), 'Valid email is required')) {
            isValid = false;
        }

        if (!phoneInput || !this.validateField(phoneInput, validatePhone(phoneInput.value), 'Valid phone number is required')) {
            isValid = false;
        }

        return isValid;
    }

    async submitBooking() {
        if (!this.validateBookingForm()) {
            return;
        }

        // Format date as YYYY-MM-DD
        const dateStr = this.selectedDate || document.getElementById('selectedDateValue')?.value;
        if (!dateStr) {
            showNotification('Please select a date', 'warning');
            return;
        }

        const bookingData = {
            propertyId: this.currentPropertyId,
            date: dateStr, // Already in YYYY-MM-DD format
            time: this.selectedTime,
            name: document.querySelector('#bookingName')?.value.trim(),
            email: document.querySelector('#bookingEmail')?.value.trim(),
            phone: document.querySelector('#bookingPhone')?.value.trim(),
            whatsappUpdates: document.querySelector('#whatsappUpdates')?.checked || false
        };

        // Submit to Django API
        showNotification('Processing your booking...', 'info');
        
        try {
            const apiUrl = window.DJANGO_BOOKING_API_URL || '/api/booking/';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(bookingData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                const whatsappEnabled = bookingData.whatsappUpdates;
                let message = 'Booking confirmed!';
                if (whatsappEnabled) {
                    message += ' You will receive WhatsApp updates and reminders.';
                } else {
                    message += ' You will receive a confirmation email shortly.';
                }
                showNotification(message, 'success');
                
                // Send WhatsApp message if enabled
                if (whatsappEnabled && bookingData.phone) {
                    this.sendWhatsAppConfirmation(bookingData, result.booking);
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
                if (modal) modal.hide();
                
                this.resetBookingForm();
            } else {
                showNotification(result.error || 'Booking failed. Please try again.', 'danger');
            }
        } catch (error) {
            console.error('Error submitting booking:', error);
            showNotification('An error occurred. Please try again.', 'danger');
        }
    }

    sendWhatsAppConfirmation(bookingData, bookingInfo) {
        // Format phone number (remove +, spaces, etc.)
        let phone = bookingData.phone.replace(/[^\d]/g, '');
        
        // Add country code if not present (Kenya: +254)
        if (!phone.startsWith('254')) {
            if (phone.startsWith('0')) {
                phone = '254' + phone.substring(1);
            } else {
                phone = '254' + phone;
            }
        }
        
        // Create WhatsApp message
        const dateObj = new Date(bookingData.date);
        const dateStr = dateObj.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const message = encodeURIComponent(
            `🏠 *SmartKeja Booking Confirmation*\n\n` +
            `Hello ${bookingData.name},\n\n` +
            `Your property viewing has been confirmed!\n\n` +
            `📅 *Date:* ${dateStr}\n` +
            `⏰ *Time:* ${bookingData.time}\n` +
            `🏘️ *Property:* ${bookingInfo?.property_name || 'Property'}\n\n` +
            `We'll send you a reminder 24 hours before your viewing.\n\n` +
            `Thank you for choosing SmartKeja!`
        );
        
        // Open WhatsApp with pre-filled message
        const whatsappUrl = `https://wa.me/${phone}?text=${message}`;
        window.open(whatsappUrl, '_blank');
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    resetBookingForm() {
        this.selectedDate = null;
        this.selectedTime = null;
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        
        // Reset calendar
        this.renderCalendar();
        
        // Reset time slot selection
        document.querySelectorAll('.time-slot').forEach(slot => {
            slot.classList.remove('selected');
        });
        
        // Reset form fields
        const form = document.querySelector('#bookingForm');
        if (form) {
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
                field.classList.remove('is-valid', 'is-invalid');
            });
            // Re-check WhatsApp checkbox
            const whatsappCheckbox = document.querySelector('#whatsappUpdates');
            if (whatsappCheckbox) whatsappCheckbox.checked = true;
        }
        
        // Reset info display
        const infoElement = document.querySelector('#selectedDateTime');
        if (infoElement) {
            infoElement.innerHTML = '<i class="bi bi-info-circle me-2"></i>Please select a date and time';
        }
        
        // Reset hidden date input
        const dateInput = document.getElementById('selectedDateValue');
        if (dateInput) dateInput.value = '';
    }
}
