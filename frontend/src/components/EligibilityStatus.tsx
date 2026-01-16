import React from 'react';

interface EligibilityStatusProps {
  status: 'Eligible' | 'Partially Eligible' | 'Ineligible';
  deliverDate?: string;
  className?: string;
}

const getStatusInfo = (status: string) => {
  switch (status) {
    case 'Eligible':
      return { 
        label: 'Eligible',
        description: 'Product is eligible for full refund',
        icon: '✓',
        className: 'eligible'
      };
    case 'Partially Eligible':
      return { 
        label: 'Partially Eligible',
        description: 'Some products are eligible for refund',
        icon: '⦿',
        className: 'partial'
      };
    case 'Ineligible':
      return { 
        label: 'Ineligible',
        description: 'Product is not eligible for refund',
        icon: '✗',
        className: 'ineligible'
      };
    default:
      return { 
        label: 'Unknown',
        description: 'Eligibility unknown',
        icon: '?',
        className: 'unknown'
      };
  }
};

export const EligibilityStatus: React.FC<EligibilityStatusProps> = ({ 
  status, 
  deliverDate,
  className = '' 
}) => {
  const statusInfo = getStatusInfo(status);

  const calculateDaysDiff = (dateString?: string) => {
    if (!dateString) return null;
    const deliveryDate = new Date(dateString);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - deliveryDate.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysDiff = deliverDate ? calculateDaysDiff(deliverDate) : null;

  return (
    <div className={`eligibility-status ${statusInfo.className} ${className}`}>
      <div className="status-badge">
        <span className="status-icon">{statusInfo.icon}</span>
        <span className="status-label">{statusInfo.label}</span>
      </div>
      
      <div className="status-details">
        <p className="description">{statusInfo.description}</p>
        
        {deliverDate && (
          <div className="delivery-info">
            <span>Delivered: {new Date(deliverDate).toLocaleDateString('en-US')}</span>
            {daysDiff !== null && (
              <span className="days-ago">
                ({daysDiff} days ago)
              </span>
            )}
          </div>
        )}

        {status === 'Ineligible' && daysDiff && daysDiff > 14 && (
          <p className="eligibility-note">
            ⓘ Product was delivered outside the 14-day refund window
          </p>
        )}

        {status === 'Eligible' && (
          <p className="eligibility-note">
            ⓘ Refund request will be processed within 5-7 business days
          </p>
        )}

        {status === 'Partially Eligible' && (
          <p className="eligibility-note">
            ⓘ Only products within 14-day window are eligible
          </p>
        )}
      </div>
    </div>
  );
};