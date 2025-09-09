import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import { CompanyShowcase } from './components/CompanyShowcase'
import { ChatProvider } from './contexts/ChatContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { LoadingScreen } from './components/LoadingComponents'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Leadership Management Tool - TAO Digital Solutions',
  description: 'Connect • Analyze • Lead - AI-powered leadership analytics platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <ChatProvider>
            <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
              {/* Fixed Header */}
              <Header />
              
              {/* Main Content Area with Three Columns */}
              <div className="flex-1 flex overflow-hidden">
                {/* Fixed Left Sidebar */}
                <div className="w-80 flex-shrink-0">
                  <Sidebar />
                </div>
                
                {/* Scrollable Center Content */}
                <main className="flex-1 overflow-y-auto">
                  {children}
                </main>
                
                {/* Fixed Right Sidebar */}
                <div className="w-80 flex-shrink-0 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto transition-colors duration-200">
                  <CompanyShowcase />
                </div>
              </div>
            </div>
          </ChatProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
