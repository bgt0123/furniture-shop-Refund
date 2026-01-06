import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supportApi } from '../../services/supportApi'
import { SupportCase } from '../../types/supportTypes'
import { Button } from '../Button'

interface SupportCaseFormProps {
  onCaseCreated: (caseData: SupportCase) => void
  token: string
}

export const SupportCaseForm: React.FC<SupportCaseFormProps> = ({ onCaseCreated, token }) => {
  const [orderId, setOrderId] = useState('')
  const [issueDescription, setIssueDescription] = useState('')
  const [products, setProducts] = useState([{ productId: '', quantity: 1 }])
  const [attachments, setAttachments] = useState<File[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleProductChange = (index: number, field: string, value: string | number) => {
    const newProducts = [...products]
    if (field === 'productId') {
      newProducts[index].productId = value as string
    } else {
      newProducts[index].quantity = value as number
    }
    setProducts(newProducts)
  }

  const addProduct = () => {
    setProducts([...products, { productId: '', quantity: 1 }])
  }

  const removeProduct = (index: number) => {
    if (products.length > 1) {
      const newProducts = products.filter((_, i) => i !== index)
      setProducts(newProducts)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments(Array.from(e.target.files))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      // Prepare the request data
      const caseData = {
        order_id: orderId,
        issue_description: issueDescription,
        products: products.map(p => ({
          product_id: p.productId,
          quantity: p.quantity
        })),
        attachments: [] // We'll handle file uploads separately
      }

      // Create support case
      supportApi.setAuthToken(token)
      const response = await supportApi.createSupportCase(caseData)
      
      // Handle file uploads if needed
      if (attachments.length > 0) {
        // In a real app, you would upload files here
        console.log('Files to upload:', attachments)
      }

      onCaseCreated(response.data)
      navigate('/support')
    } catch (err) {
      console.error('Error creating support case:', err)
      setError('Failed to create support case. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="support-case-form">
      <h2>Create Support Case</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="orderId">Order ID</label>
          <input
            id="orderId"
            type="text"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="issueDescription">Issue Description</label>
          <textarea
            id="issueDescription"
            value={issueDescription}
            onChange={(e) => setIssueDescription(e.target.value)}
            required
            minLength={10}
            rows={5}
          />
        </div>

        <div className="products-section">
          <h3>Products</h3>
          {products.map((product, index) => (
            <div key={index} className="product-item">
              <div className="form-group">
                <label htmlFor={`productId-${index}`}>Product ID</label>
                <input
                  id={`productId-${index}`}
                  type="text"
                  value={product.productId}
                  onChange={(e) => handleProductChange(index, 'productId', e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor={`quantity-${index}`}>Quantity</label>
                <input
                  id={`quantity-${index}`}
                  type="number"
                  min="1"
                  value={product.quantity}
                  onChange={(e) => handleProductChange(index, 'quantity', parseInt(e.target.value))}
                  required
                />
              </div>
              
              {products.length > 1 && (
                <button type="button" onClick={() => removeProduct(index)}>
                  Remove
                </button>
              )}
            </div>
          ))}
          
          <button type="button" onClick={addProduct} className="add-product-btn">
            Add Another Product
          </button>
        </div>

        <div className="form-group">
          <label htmlFor="attachments">Attachments (optional)</label>
          <input
            id="attachments"
            type="file"
            multiple
            onChange={handleFileChange}
          />
        </div>

        <Button type="submit" variant="primary" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Support Case'}
        </Button>
      </form>
    </div>
  )
}