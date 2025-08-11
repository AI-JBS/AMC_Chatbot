# Asset Management Chatbot Frontend

A modern, responsive frontend for the AI-powered financial advisory chatbot, built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

🎯 **Modern Chat Widget**
- Floating chat button in bottom-right corner
- Smooth animations and transitions
- Real-time typing indicators
- Message bubbles with markdown support
- Session management and conversation history

💼 **Financial Advisory UI**
- Professional design with financial theming
- Responsive layout for all devices
- Intuitive user experience
- Real-time backend health monitoring

🚀 **Technical Stack**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend server running on port 8000

### Installation

1. **Install dependencies**
   ```bash
   cd front-end
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Open in Browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
npm run type-check # TypeScript type checking
```

## Project Structure

```
front-end/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Homepage
│   ├── components/            # React components
│   │   └── ChatWidget/        # Chat widget components
│   │       ├── index.tsx      # Main widget component
│   │       ├── FloatingButton.tsx
│   │       ├── ChatInterface.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── TypingIndicator.tsx
│   │       └── ChatInput.tsx
│   ├── hooks/                 # Custom React hooks
│   │   └── useChat.ts         # Chat management hook
│   ├── types/                 # TypeScript definitions
│   │   └── chat.ts            # Chat-related types
│   ├── utils/                 # Utility functions
│   │   └── api.ts             # API client configuration
│   └── globals.css            # Global styles
├── public/                    # Static assets
├── package.json              # Dependencies and scripts
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── next.config.js            # Next.js configuration
```

## Chat Widget Usage

The chat widget is automatically included on all pages and provides:

### Core Features
- **Floating Button**: Always visible in bottom-right corner
- **Chat Interface**: Expandable chat window with full conversation history
- **Message Types**: Support for user messages and AI responses with markdown
- **Session Management**: Automatic session creation and management
- **Error Handling**: Graceful error handling with user-friendly messages
- **Offline Detection**: Backend connectivity monitoring

### Customization

The chat widget can be customized through:

1. **Styling**: Modify `tailwind.config.js` and component styles
2. **Configuration**: Update environment variables in `.env.local`
3. **API Endpoints**: Configure backend URL in `utils/api.ts`
4. **Welcome Message**: Customize in `hooks/useChat.ts`

## Integration with Backend

The frontend communicates with the FastAPI backend through:

- **Chat API**: `/chat` endpoint for sending messages
- **Session Management**: `/sessions/{id}/history` for conversation history
- **Health Check**: `/health` for backend status monitoring
- **Tools API**: `/tools` for available financial tools

## Deployment

### Production Build
```bash
npm run build
npm start
```

### Environment Variables
Make sure to set the following in production:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_NAME`: Application name
- `NEXT_PUBLIC_APP_VERSION`: Version number

## Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

## Performance

- **Bundle Size**: Optimized with Next.js automatic code splitting
- **Loading Speed**: Fast initial page load with SSR
- **Runtime Performance**: Efficient React rendering with proper memoization
- **Network Efficiency**: Axios interceptors for request/response optimization

## Contributing

1. Follow TypeScript strict mode guidelines
2. Use Tailwind CSS for styling (avoid custom CSS)
3. Implement proper error boundaries
4. Add TypeScript types for all props and state
5. Test responsive design on multiple devices

## License

This project is part of the Asset Management Chatbot platform.