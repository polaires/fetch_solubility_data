import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Solubility Data Viewer',
  description: 'Examine and browse extracted solubility data from SDS-31 PDFs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
