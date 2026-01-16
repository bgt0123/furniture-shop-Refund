import React, { useState } from 'react';
import { Button, Card } from '../components';
import { apiService } from '../services/api';

interface Product {
  id: string;
  name: string;
  price?: number;
}

interface SupportCaseFormProps {
  customerId: string;
  orderId: string;
  products: Product[];
  onCaseCreated?: (caseId: string) => void;
}

export const SupportCaseForm: React.FC<SupportCaseFormProps> = ({
  customerId,
  orderId,
  products,
  onCaseCreated
}) => {
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [issueDescription, setIssueDescription] = useState('');
  const [intendsRefund, setIntendsRefund] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleProductSelect = (productId: string) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId));
    } else {
      setSelectedProducts([...selectedProducts, productId]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!issueDescription.trim()) {
      setError('Issue description is required');
      return;
    }

    if (selectedProducts.length === 0) {
      setError('Please select at least one product');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const selectedProductDetails = products.filter(p => selectedProducts.includes(p.id));
      
      const response = await apiService.createSupportCase({
        customer_id: customerId,
        order_id: orderId,
        products: selectedProductDetails,
        issue_description: issueDescription,
        attachments: [],
        intends_refund: intendsRefund ? "Yes" : "No"
      });

      setIssueDescription('');
      setSelectedProducts([]);
      
      if (onCaseCreated) {
        onCaseCreated(response.data.id);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create support case');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="support-case-form">
      <h2>Create Support Case</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Select Products</h3>
          <div className="product-list">
            {products.map(product => (
              <label key={product.id} className="product-checkbox">
                <input
                  type="checkbox"
                  checked={selectedProducts.includes(product.id)}
                  onChange={() => handleProductSelect(product.id)}
                />
                {product.name}
                {product.price && ` - $${product.price}`}
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h3>Issue Description</h3>
          <textarea
            value={issueDescription}
            onChange={(e) => setIssueDescription(e.target.value)}
            placeholder="Please describe the issue in detail..."
            rows={5}
            required
          />
        </div>

        <div className="form-section">
          <h3>Refund Intention</h3>
          <label className="refund-intention-checkbox">
            <input
              type="checkbox"
              checked={intendsRefund}
              onChange={(e) => setIntendsRefund(e.target.checked)}
            />
            <span className="refund-intention-label">
              I intend to request a refund for these products
            </span>
          </label>
          <p className="hint">
            📝 Checking this box will indicate to our support team that you may want to request a refund. 
            You can still create a refund request later if you don't select this now.
          </p>
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating Case...' : 'Create Support Case'}
        </Button>
      </form>
    </Card>
  );
};