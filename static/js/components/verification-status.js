/**
 * SmartKeja - Verification Status Component
 * Displays AI verification status with badges
 */

export class VerificationStatus {
    constructor(containerId, status = 'pending') {
        this.containerId = containerId;
        this.status = status;
        this.render();
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const statusConfig = {
            pending: {
                badge: 'bg-secondary',
                icon: 'bi-clock-history',
                text: 'Pending Review',
                message: 'Your property is awaiting AI verification'
            },
            approved: {
                badge: 'bg-success',
                icon: 'bi-shield-check',
                text: 'Verified',
                message: 'Property verified and approved'
            },
            rejected: {
                badge: 'bg-danger',
                icon: 'bi-x-circle',
                text: 'Rejected',
                message: 'Property verification failed'
            },
            partial: {
                badge: 'bg-warning',
                icon: 'bi-exclamation-triangle',
                text: 'Partial Match',
                message: 'Some verification checks passed'
            },
            failed: {
                badge: 'bg-danger',
                icon: 'bi-x-octagon',
                text: 'Failed',
                message: 'AI verification failed'
            }
        };

        const config = statusConfig[this.status] || statusConfig.pending;

        container.innerHTML = `
            <div class="verification-status ${this.status}">
                <div class="d-flex align-items-center mb-3">
                    <span class="badge ${config.badge} fs-6 me-3">
                        <i class="bi ${config.icon} me-2"></i>${config.text}
                    </span>
                    <span class="text-muted">${config.message}</span>
                </div>
                ${this.renderProgressBar()}
            </div>
        `;
    }

    renderProgressBar() {
        if (this.status === 'pending') {
            return `
                <div class="verification-progress">
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             style="width: 50%"></div>
                    </div>
                    <small class="text-muted mt-1 d-block">Verification in progress...</small>
                </div>
            `;
        } else if (this.status === 'approved') {
            return `
                <div class="verification-details mt-3">
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle me-2"></i>
                        <strong>Verification Complete</strong>
                        <p class="mb-0 mt-2">Your property has been verified and is now live on the platform.</p>
                    </div>
                </div>
            `;
        } else if (this.status === 'partial') {
            return `
                <div class="verification-details mt-3">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <strong>Partial Verification</strong>
                        <p class="mb-0 mt-2">Some verification checks passed. Please review and update your listing.</p>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="verification-details mt-3">
                    <div class="alert alert-danger">
                        <i class="bi bi-x-circle me-2"></i>
                        <strong>Verification Failed</strong>
                        <p class="mb-0 mt-2">Please review your property details and resubmit for verification.</p>
                    </div>
                </div>
            `;
        }
    }

    updateStatus(newStatus) {
        this.status = newStatus;
        this.render();
    }

    getStatus() {
        return this.status;
    }
}


