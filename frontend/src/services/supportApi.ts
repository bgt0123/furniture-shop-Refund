import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const supportApi = createApi({
  reducerPath: 'supportApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  endpoints: (builder) => ({
    getSupportCases: builder.query({
      query: () => '/support/cases',
    }),
    createSupportCase: builder.mutation({
      query: (caseData) => ({
        url: '/support/cases',
        method: 'POST',
        body: caseData,
      }),
    }),
  }),
})

export const { useGetSupportCasesQuery, useCreateSupportCaseMutation } = supportApi