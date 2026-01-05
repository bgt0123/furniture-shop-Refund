import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const refundApi = createApi({
  reducerPath: 'refundApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  endpoints: (builder) => ({
    getRefundCases: builder.query({
      query: () => '/refunds/cases',
    }),
    createRefundRequest: builder.mutation({
      query: ({ caseId, products }) => ({
        url: `/support/cases/${caseId}/refunds`,
        method: 'POST',
        body: { products },
      }),
    }),
  }),
})

export const { useGetRefundCasesQuery, useCreateRefundRequestMutation } = refundApi