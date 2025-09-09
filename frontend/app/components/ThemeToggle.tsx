'use client'

import React from 'react'
import { Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center w-12 h-6 bg-gray-200 dark:bg-gray-700 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
      aria-label="Toggle theme"
    >
      <div className={`absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-200 ${
        theme === 'dark' ? 'translate-x-6' : 'translate-x-0'
      }`}>
        {theme === 'light' ? (
          <Sun className="w-3 h-3 text-yellow-500 m-0.5" />
        ) : (
          <Moon className="w-3 h-3 text-blue-600 m-0.5" />
        )}
      </div>
    </button>
  )
}

export function ThemeSelector() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="flex items-center space-x-2">
      <Sun className={`w-4 h-4 ${theme === 'light' ? 'text-yellow-500' : 'text-gray-400'}`} />
      <button
        onClick={toggleTheme}
        className="relative inline-flex items-center justify-center w-12 h-6 bg-gray-200 dark:bg-gray-700 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
        aria-label="Toggle theme"
      >
        <div className={`absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-200 ${
          theme === 'dark' ? 'translate-x-6' : 'translate-x-0'
        }`}>
          <div className="w-full h-full rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center">
            {theme === 'light' ? (
              <Sun className="w-2.5 h-2.5 text-white" />
            ) : (
              <Moon className="w-2.5 h-2.5 text-white" />
            )}
          </div>
        </div>
      </button>
      <Moon className={`w-4 h-4 ${theme === 'dark' ? 'text-blue-500' : 'text-gray-400'}`} />
    </div>
  )
}
