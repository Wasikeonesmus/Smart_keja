/**
 * SmartKeja - Multi-Step Form Wizard Component
 * Similar to React StepWizard but in vanilla JavaScript
 */

export class StepWizard {
    constructor(containerId, steps = [], options = {}) {
        this.containerId = containerId;
        this.steps = steps;
        this.currentStep = 0;
        this.data = {};
        this.onStepChange = options.onStepChange || null;
        this.onComplete = options.onComplete || null;
        this.init();
    }

    init() {
        this.render();
        this.setupEventListeners();
        this.goToStep(0);
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`StepWizard container #${this.containerId} not found`);
            return;
        }

        // Create step indicator
        const stepIndicator = document.createElement('div');
        stepIndicator.className = 'step-indicator mb-4';
        stepIndicator.innerHTML = this.renderStepIndicator();

        // Create step content container
        const stepContent = document.createElement('div');
        stepContent.className = 'step-content';
        stepContent.id = `${this.containerId}-content`;

        // Create navigation buttons
        const navigation = document.createElement('div');
        navigation.className = 'step-navigation d-flex justify-content-between mt-4';
        navigation.innerHTML = `
            <button class="btn btn-outline-secondary" id="${this.containerId}-prev" disabled>
                <i class="bi bi-arrow-left me-2"></i>Previous
            </button>
            <button class="btn btn-primary" id="${this.containerId}-next">
                Next<i class="bi bi-arrow-right ms-2"></i>
            </button>
        `;

        container.innerHTML = '';
        container.appendChild(stepIndicator);
        container.appendChild(stepContent);
        container.appendChild(navigation);
    }

    renderStepIndicator() {
        let html = '<div class="d-flex justify-content-between align-items-center">';
        
        this.steps.forEach((step, index) => {
            const isActive = index === this.currentStep;
            const isCompleted = index < this.currentStep;
            
            html += `
                <div class="step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}" style="flex: 1;">
                    <div class="step-number d-flex align-items-center justify-content-center">
                        ${isCompleted ? '<i class="bi bi-check-circle-fill"></i>' : (index + 1)}
                    </div>
                    <div class="step-label mt-2 text-center">
                        <small>${step.label}</small>
                    </div>
                </div>
            `;
            
            if (index < this.steps.length - 1) {
                html += '<div class="step-connector"></div>';
            }
        });
        
        html += '</div>';
        return html;
    }

    setupEventListeners() {
        const prevBtn = document.getElementById(`${this.containerId}-prev`);
        const nextBtn = document.getElementById(`${this.containerId}-next`);

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previous());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.next());
        }
    }

    goToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            return;
        }

        const previousStep = this.currentStep;
        this.currentStep = stepIndex;

        // Update step indicator
        const indicator = document.querySelector(`#${this.containerId} .step-indicator`);
        if (indicator) {
            indicator.innerHTML = this.renderStepIndicator();
        }

        // Render step content
        const contentContainer = document.getElementById(`${this.containerId}-content`);
        if (contentContainer && this.steps[stepIndex].render) {
            contentContainer.innerHTML = '';
            const stepElement = this.steps[stepIndex].render(this.data, (data) => {
                this.updateData(data);
            });
            if (stepElement) {
                contentContainer.appendChild(stepElement);
            }
        }

        // Update navigation buttons
        this.updateNavigation();

        // Call step change callback
        if (this.onStepChange) {
            this.onStepChange(stepIndex, previousStep, this.data);
        }
    }

    updateNavigation() {
        const prevBtn = document.getElementById(`${this.containerId}-prev`);
        const nextBtn = document.getElementById(`${this.containerId}-next`);

        if (prevBtn) {
            prevBtn.disabled = this.currentStep === 0;
        }

        if (nextBtn) {
            const isLastStep = this.currentStep === this.steps.length - 1;
            nextBtn.innerHTML = isLastStep 
                ? '<i class="bi bi-check-circle me-2"></i>Submit' 
                : 'Next<i class="bi bi-arrow-right ms-2"></i>';
        }
    }

    next() {
        // Validate current step
        if (this.steps[this.currentStep].validate) {
            const isValid = this.steps[this.currentStep].validate(this.data);
            if (!isValid) {
                return;
            }
        }

        if (this.currentStep < this.steps.length - 1) {
            this.goToStep(this.currentStep + 1);
        } else {
            // Last step - submit form
            this.submit();
        }
    }

    previous() {
        if (this.currentStep > 0) {
            this.goToStep(this.currentStep - 1);
        }
    }

    updateData(newData) {
        this.data = { ...this.data, ...newData };
    }

    getData() {
        return this.data;
    }

    async submit() {
        if (this.onComplete) {
            await this.onComplete(this.data);
        }
    }

    setStepData(stepIndex, data) {
        if (this.steps[stepIndex]) {
            this.data = { ...this.data, ...data };
        }
    }
}


