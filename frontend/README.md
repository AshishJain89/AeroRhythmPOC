# Crew Rostering — React + Vite POC UI

A production-ready frontend for AI-powered crew rostering built with React, Vite, and modern web technologies. Features a beautiful Glassmorphism design with smooth micro-interactions and realistic airline operations data.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔐 Demo Login

- **Username:** `admin`
- **Password:** `password`

## 🏗️ Architecture

- **Frontend:** React 18 + TypeScript + Vite
- **Styling:** Tailwind CSS with custom Glassmorphism design system
- **State Management:** Zustand + React Query
- **Routing:** React Router DOM
- **UI Components:** shadcn/ui with custom variants
- **Data Fetching:** Axios with mock data fallback
- **Drag & Drop:** @dnd-kit for roster management

## 📁 Project Structure

```
src/
├── api/                 # API clients and types
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── CrewList/       # Crew management components
│   ├── RosterCalendar/ # Timeline and calendar views
│   └── Filters/        # Search and filter components
├── data/seed/          # Mock data for development
├── pages/              # Application pages
├── hooks/              # Custom React hooks
└── lib/                # Utilities and helpers
```

## 🎨 Design System

The application uses a custom Glassmorphism design system with:

- **Aviation-inspired color palette** (blues, whites, oranges)
- **Glass morphism effects** with backdrop blur and translucent surfaces
- **Smooth micro-interactions** with cubic-bezier transitions
- **Semantic design tokens** for consistent theming
- **Responsive layouts** for mobile and desktop

## 🌐 API Integration

Configure API settings in your environment:

```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false  # Set to true for mock data
```

The application includes fallback to realistic seed data when the API is unavailable.

## ✨ Key Features

- **Dashboard:** Real-time KPIs, crew utilization, and system metrics
- **Roster Management:** Timeline view with drag-drop crew assignments
- **Crew Management:** Searchable crew database with detailed profiles
- **Disruption Handling:** Real-time alerts and AI-powered recommendations
- **Settings:** Comprehensive system configuration options

## 🧪 Testing

```bash
npm run test     # Run unit tests
npm run lint     # Lint code
npm run type-check # TypeScript type checking
```

## 🔧 Environment Configuration

The system supports both live API and mock data modes. When `VITE_USE_MOCK_DATA=true`, it uses realistic seed data for:

- Flight schedules and crew assignments
- DGCA compliance violations
- Real-time disruption scenarios
- Crew qualifications and availability

## 📈 Performance

- **Lazy loading** for route-based code splitting
- **Optimistic UI** updates for better UX
- **React Query** for efficient data caching
- **Glass morphism** with hardware-accelerated CSS

---

Built with ❤️ for modern airline operations control centers.