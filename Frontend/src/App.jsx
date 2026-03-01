import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import ChatPage from './ChatPage'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1A1A1A' },  // Deep Black
    secondary: { main: '#FCD12A' },  // Vibrant Yellow
    info: { main: '#4DBAC1' },  // Accent Teal
    background: {
      default: '#F2F2F2', // Off-White
      paper: '#FFFFFF', // White
    },
    text: {
      primary: '#1A1A1A',
      secondary: '#4D4D4D',
    },
  },
  typography: {
    fontFamily: "'Montserrat', sans-serif",
    button: {
      textTransform: 'uppercase',
      fontWeight: 700,
      letterSpacing: '0.05em',
    }
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiButtonBase: {
      defaultProps: {
        disableRipple: true, // Flat design feel
      },
    },
  },
})

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ChatPage />
    </ThemeProvider>
  )
}

