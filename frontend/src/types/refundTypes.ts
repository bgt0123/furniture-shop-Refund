export interface RefundCase {
  id: string
  supportCaseId: string
  customerId: string
  orderId: string
  status: 'Pending' | 'Approved' | 'Rejected' | 'Completed'
  eligibilityStatus: 'Eligible' | 'Partially Eligible' | 'Ineligible'
  totalRefundAmount: number
  createdAt: string
  processedAt?: string
  rejectionReason?: string
  agentId?: string
  products?: Array<{
    productId: string
    quantity: number
    name: string
    price: number
    refundAmount: number
    deliveryDate: string
    eligibility: 'Eligible' | 'Ineligible'
  }>
}

export interface RefundRequestCreate {
  products: Array<{
    productId: string
    quantity: number
  }>
}