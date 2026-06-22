import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: "ScenarioTwin",
    description: 'Monte Carlo financial simulation with correlated shocks'
}

export default function RootLayout({ children }: { children: React.ReactNode}) {
    return (
        <html lang="en" className="dark">
            <body>{children}</body>
        </html>
    )
}