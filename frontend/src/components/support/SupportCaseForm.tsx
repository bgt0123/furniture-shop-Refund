import React, { useState } from 'react'

type SupportCaseFormProps = {
  onSubmit: (data: SupportCaseFormData) => void
}

export interface SupportCaseFormData {
  title: string
  description: string
  orderId: string
}

const SupportCaseForm: React.FC<SupportCaseFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<SupportCaseFormData>({
    title: '',
    description: '',
    orderId: ''
  })
  
  const [errors, setErrors] = useState<Partial<SupportCaseFormData>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (errors[name as keyof SupportCaseFormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<SupportCaseFormData> = {}
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    }
    
    if (!formData.orderId.trim()) {
      newErrors.orderId = 'Order ID is required'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onSubmit(formData)
      setFormData({
        title: '',
        description: '',
        orderId: ''
      })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="support-case-form">
      <div className="form-group">
        <label htmlFor="title" className="form-label">Title *</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`form-input ${errors.title ? 'error' : ''}`}
          placeholder="Enter a brief title for your support case"
        />
        {errors.title && <span className="error-text">{errors.title}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="description" className="form-label">Description *</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          className={`form-textarea ${errors.description ? 'error' : ''}`}
          placeholder="Please describe your issue in detail"
          rows={4}
        />
        {errors.description && <span className="error-text">{errors.description}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="orderId" className="form-label">Order ID *</label>
        <input
          type="text"
          id="orderId"
          name="orderId"
          value={formData.orderId}
          onChange={handleChange}
          className={`form-input ${errors.orderId ? 'error' : ''}`}
          placeholder="Enter your order ID"
        />
        {errors.orderId && <span className="error-text">{errors.orderId}</span>}
      </div>

      <button type="submit" className="submit-button">
        Create Support Case
      </button>
    </form>
  )
}

export default SupportCaseForm