export interface SupportCase {
  id: string
  customerId: string
  orderId: string
  status: 'Open' | 'Closed'
  createdAt: string
  closedAt?: string
  issueDescription?: string
  products?: Array<{
    productId: string
    quantity: number
    name?: string
    price?: number
  }>
  attachments?: Array<{
    id: string
    name: string
    url: string
  }>
}

export interface SupportCaseCreate {
  orderId: string
  products: Array<{
    productId: string
    quantity: number
  }>
  issueDescription: string
  attachments?: Array<string> // base64 encoded
}