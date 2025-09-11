# Leadership Management Tool - Frontend

## Setup Instructions

### 1. Install Dependencies
```bash
npm install recharts clsx
```

### 2. Environment Configuration
Create a `.env.local` file in the frontend directory with:
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Or set the environment variable when running:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 npm run dev
```

### 3. Run Development Server
```bash
npm run dev
```

## Components

### VelocityChart
- Displays sprint velocity with projections
- Shows confidence bands for forecasts
- Includes capacity baseline reference line

### KpiCards
- Completion rate percentage
- Defect ratio percentage  
- Capacity baseline value

### BandwidthChart
- Team member workload visualization
- Shows total issues vs completed issues
- Stacked bar chart format

### Suggestions
- AI-generated insights and recommendations
- Color-coded by suggestion type (excellent/good/risk)
- Responsive chip layout

## Leadership Page
- Comprehensive dashboard at `/leadership`
- Real-time data from backend API
- Responsive design with dark mode support
- Loading states and error handling
