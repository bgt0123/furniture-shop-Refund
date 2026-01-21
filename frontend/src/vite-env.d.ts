interface ImportMetaEnv {
  readonly VITE_DEFAULT_USER_ID: string
  readonly VITE_SUPPORT_SERVICE_URL: string
  readonly VITE_REFUND_SERVICE_URL: string
  readonly VITE_APP_ENV: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}