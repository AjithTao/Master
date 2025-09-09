'use client'

import { ThemeToggle } from './ThemeToggle'

export function Header() {
  return (
    <header className="bg-white dark:bg-background border-b border-gray-200 dark:border-border px-6 py-4 transition-colors duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 dark:bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white dark:text-primary-foreground font-bold text-sm">📊</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-foreground">Leadership Management Tool</h1>
              <p className="text-sm text-gray-500 dark:text-muted-foreground">Connect • Analyze • Lead</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900 dark:text-foreground">Ajith Kumar</p>
            <p className="text-xs text-gray-500 dark:text-muted-foreground">Principal QA Engineer</p>
          </div>
          <div className="w-8 h-8 bg-gray-200 dark:bg-muted rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-gray-600 dark:text-muted-foreground">AK</span>
          </div>
        </div>
      </div>
    </header>
  )
}
