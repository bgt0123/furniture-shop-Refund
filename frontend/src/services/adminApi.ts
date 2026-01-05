import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const adminApi = createApi({
  reducerPath: 'adminApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  endpoints: (builder) => ({
    getAllRefundCases: builder.query({
      query: (params) => ({
        url: '/admin/refunds/cases',
        params,
      }),
    }),
    approveRefund: builder.mutation({
      query: (refundId) => ({
        url: `/admin/refunds/cases/${refundId}/approve`,
        method: 'POST',
      }),
    }),
    rejectRefund: builder.mutation({
      query: ({ refundId, reason }) => ({
        url: `/admin/refunds/cases/${refundId}/reject`,
        method: 'POST',
        body: { reason },
      }),
    }),
  }),
})

export const { 
  useGetAllRefundCasesQuery, 
  useApproveRefundMutation, 
  useRejectRefundMutation 
} = adminApi