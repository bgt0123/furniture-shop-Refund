import React, { useState, useEffect } from 'react';
import { Button, Card } from '../components';
import { apiService } from '../services/api';

interface Product {
  id: string;
  name: string;
  price?: number;
  deliveryDate?: string;
}

interface RefundRequestFormProps {
  supportCaseId: string;
  onRefundCreated?: (refundId: string) => void;
}

export const RefundRequestForm: React.FC<RefundRequestFormProps> = ({
  supportCaseId,
  onRefundCreated
}) => {
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [supportCase, setSupportCase] = useState<any>(null);

  // Load support case details
  useEffect(() => {
    const loadSupportCase = async () => {
      try {
        const response = await apiService.getSupportCase(supportCaseId);
        setSupportCase(response.data);
      } catch (err: any) {
        setError('Failed to load support case details');
      }
    };

    if (supportCaseId) {
      loadSupportCase();
    }
  }, [supportCaseId]);

  const handleProductSelect = (productId: string) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId));
    } else {
      setSelectedProducts([...selectedProducts, productId]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!reason.trim()) {
      setError('Refund reason is required');
      return;
    }

    if (selectedProducts.length === 0) {
      setError('Please select at least one product for refund');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Get selected product details
      const selectedProductDetails = supportCase.products.filter((p: Product) => 
        selectedProducts.includes(p.id)
      );
      
      const response = await apiService.createRefundCase(supportCaseId, {
        customer_id: supportCase.customer_id,
        order_id: supportCase.order_id,
        products: selectedProductDetails,
        reason: reason
      });

      setReason('');
      setSelectedProducts([]);
      
      if (onRefundCreated) {
        onRefundCreated(response.data.id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Failed to create refund request');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!supportCase) {
    return (
      <Card className="refund-request-form">
        <div className="loading">Loading support case details...</div>
      </Card>
    );
  }

  return (
    <Card className="refund-request-form">
      <h2>Request Refund</h2>
      <p className="case-info">
        Support Case #{supportCase.id} - Order #{supportCase.order_id}
      </p>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Select Products for Refund</h3>
          <div className="product-list">
            {supportCase.products.map((product: Product) => (
              <label key={product.id} className="product-checkbox">
                <input
                  type="checkbox"
                  checked={selectedProducts.includes(product.id)}
                  onChange={() => handleProductSelect(product.id)}
                />
                <span className="product-info">
                  <strong>{product.name}</strong>
                  {product.price && (
                    <span className="product-price"> - ${product.price}</span>
                  )}
                  {product.deliveryDate && (
                    <span className="delivery-date">
                      {/* Delivery date will be used for eligibility calculation */}
                    </span>
                  )}
                </span>
              </label>
            ))}
          </div>
          <p className="hint">
            ⓘ Products delivered within the last 14 days are eligible for refund
          </p>
        </div>

        <div className="form-section">
          <h3>Refund Reason</h3>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Please explain why you're requesting a refund (e.g., product damaged, wrong item received, etc.)"
            rows={4}
            required
          />
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating Refund Request...' : 'Request Refund'}
        </Button>
      </form>
    </Card>
  );
};

export { apiService };