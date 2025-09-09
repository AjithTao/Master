'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from './ui/card'
import { Badge } from './ui/badge'
import { 
  Zap, 
  Shield, 
  CreditCard, 
  Cloud,
  TrendingUp,
  Users,
  Globe,
  CheckCircle,
  Star
} from 'lucide-react'

export function CompanyShowcase() {
  const [currentService, setCurrentService] = useState(0)

  const services = [
    { icon: <Zap className="w-4 h-4" />, title: "Product Engineering", highlight: "30% Faster" },
    { icon: <Shield className="w-4 h-4" />, title: "Cybersecurity", highlight: "60% ROI" },
    { icon: <CreditCard className="w-4 h-4" />, title: "Payment Services", highlight: "2M+ ATMs" },
    { icon: <Cloud className="w-4 h-4" />, title: "Cloud Services", highlight: "24/7 Ops" }
  ]

  const globalLocations = [
    { country: "USA", flag: "🇺🇸" },
    { country: "Canada", flag: "🇨🇦" },
    { country: "Nigeria", flag: "🇳🇬" },
    { country: "India", flag: "🇮🇳" },
    { country: "Australia", flag: "🇦🇺" }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentService((prev) => (prev + 1) % services.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-3 h-full flex flex-col">
      {/* Company Header */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-3">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mr-2 animate-pulse">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <div>
                <h3 className="text-sm font-bold text-blue-800 dark:text-blue-200 animate-pulse">TAO Digital</h3>
                <p className="text-xs text-blue-600 dark:text-blue-300 animate-pulse">Solutions Inc.</p>
              </div>
            </div>
            <p className="text-xs text-blue-600 dark:text-blue-300 mb-2 animate-pulse">
              Transformation • Automation • Optimization
            </p>
            <Badge variant="outline" className="text-xs animate-pulse">
              <Globe className="w-3 h-3 mr-1" />
              Global Delivery
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Services Showcase */}
      <Card className="flex-1">
        <CardContent className="p-0 h-full flex flex-col">
          <div className="bg-gray-50 dark:bg-gray-800 p-2">
            <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center">
              <Star className="w-3 h-3 mr-1 text-yellow-500" />
              Core Services
            </h4>
          </div>
          <div className="p-3 flex-1 flex flex-col">
            <div className="relative h-16 overflow-hidden flex-1">
              <div 
                className="absolute inset-0 transition-all duration-500 ease-in-out"
                style={{ transform: `translateY(-${currentService * 100}%)` }}
              >
                {services.map((service, index) => (
                  <div key={index} className="h-16 flex items-center space-x-2">
                    <div className="p-1.5 bg-blue-50 dark:bg-blue-900/20 rounded text-blue-600">
                      {service.icon}
                    </div>
                    <div className="flex-1 flex flex-col justify-center">
                      <h5 className="font-semibold text-xs text-gray-900 dark:text-white mb-1">
                        {service.title}
                      </h5>
                      <Badge variant="secondary" className="text-xs w-fit">
                        {service.highlight}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex justify-center mt-2 space-x-1">
              {services.map((_, index) => (
                <div
                  key={index}
                  className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                    index === currentService 
                      ? 'bg-blue-600 w-6' 
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Success Stories */}
      <Card className="flex-1">
        <CardContent className="p-0 h-full flex flex-col">
          <div className="bg-green-50 dark:bg-green-900/20 p-2">
            <h4 className="text-xs font-semibold text-green-700 dark:text-green-300 flex items-center">
              <CheckCircle className="w-3 h-3 mr-1 animate-pulse" />
              Success Stories
            </h4>
          </div>
          <div className="p-3 flex-1">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-3 h-3 text-green-600 animate-bounce" />
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-900 dark:text-white animate-pulse">World's Largest Manufacturer</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">30% Faster Time to Market</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="w-3 h-3 text-green-600 animate-bounce" />
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-900 dark:text-white animate-pulse">Automotive Leader</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">50% Lower Delivery Cost</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Global Presence */}
      <Card className="flex-1">
        <CardContent className="p-3 h-full flex flex-col">
          <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center">
            <Users className="w-3 h-3 mr-1 animate-pulse" />
            Global Presence
          </h4>
          <div className="flex flex-wrap gap-1 justify-center flex-1 items-center">
            {globalLocations.map((location, index) => (
              <div
                key={index}
                className="flex items-center justify-center w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
                style={{ animationDelay: `${index * 200}ms` }}
                title={location.country}
              >
                <span className="text-lg">{location.flag}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2 animate-pulse">
            24/7 support across 5 hubs
          </p>
        </CardContent>
      </Card>

      {/* Company Stats */}
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800">
        <CardContent className="p-3">
          <h4 className="text-xs font-semibold text-purple-700 dark:text-purple-300 mb-2 text-center animate-pulse">
            By the Numbers
          </h4>
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="overflow-hidden">
              <div className="text-sm font-bold text-purple-600 dark:text-purple-400 animate-bounce" style={{ animationDelay: '0ms' }}>$213B</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">Revenue</div>
            </div>
            <div className="overflow-hidden">
              <div className="text-sm font-bold text-purple-600 dark:text-purple-400 animate-bounce" style={{ animationDelay: '200ms' }}>200+</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">Countries</div>
            </div>
            <div className="overflow-hidden">
              <div className="text-sm font-bold text-purple-600 dark:text-purple-400 animate-bounce" style={{ animationDelay: '400ms' }}>15K+</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">Locations</div>
            </div>
            <div className="overflow-hidden">
              <div className="text-sm font-bold text-purple-600 dark:text-purple-400 animate-bounce" style={{ animationDelay: '600ms' }}>100M+</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 animate-pulse">Data Points</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
