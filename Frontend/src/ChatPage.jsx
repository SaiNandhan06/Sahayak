import { useState, useRef, useEffect, useCallback } from 'react'
import {
    Box, Paper, Typography, TextField, IconButton, Avatar,
    Chip, CircularProgress, Divider, Tooltip, Fade, Zoom,
    useTheme, alpha,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import PersonIcon from '@mui/icons-material/Person'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import AutorenewIcon from '@mui/icons-material/Autorenew'
import AssessmentIcon from '@mui/icons-material/Assessment'

// ── API config ────────────────────────────────────────────────────────────────
const API_BASE = 'http://localhost:8000'

// ── Quick-prompt suggestions ──────────────────────────────────────────────────
const SUGGESTIONS = [
    '🍕 How do I track food expenses?',
    '💰 What apps help me save money?',
    '☕ Categorize my ₹500 Starbucks spend',
    '📊 Explain the 50/30/20 budget rule',
    '🔔 How do overspend alerts work?',
    '📱 What is the CRED app?',
]

// ── Helpers ───────────────────────────────────────────────────────────────────
function generateSessionId() {
    return 'session_' + Math.random().toString(36).slice(2, 10)
}

function formatTime(date) {
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

// ── Typing dots animation ─────────────────────────────────────────────────────
function TypingIndicator() {
    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8, px: 1, py: 0.5 }}>
            {[0, 1, 2].map(i => (
                <Box
                    key={i}
                    sx={{
                        width: 10, height: 10, borderRadius: '0%', // Square geometric dots
                        bgcolor: '#1A1A1A',
                        animation: 'bounce 1.2s infinite ease-in-out',
                        animationDelay: `${i * 0.2}s`,
                        '@keyframes bounce': {
                            '0%, 60%, 100%': { transform: 'translateY(0)' },
                            '30%': { transform: 'translateY(-6px)' },
                        },
                    }}
                />
            ))}
        </Box>
    )
}

// ── Single message bubble ─────────────────────────────────────────────────────
function MessageBubble({ msg }) {
    const isUser = msg.role === 'user'

    return (
        <Fade in timeout={350}>
            <Box
                sx={{
                    display: 'flex',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                    alignItems: 'flex-end',
                    gap: 1.5,
                    mb: 3,
                }}
            >
                {/* Avatar */}
                <Avatar
                    sx={{
                        width: 44, height: 44, flexShrink: 0,
                        bgcolor: isUser ? '#1A1A1A' : '#4DBAC1', // Teal for AI, Black for User
                        color: isUser ? '#FCD12A' : '#1A1A1A',
                        border: '2px solid #1A1A1A',
                    }}
                >
                    {isUser ? <PersonIcon /> : <SmartToyIcon />}
                </Avatar>

                {/* Bubble */}
                <Box sx={{ maxWidth: '75%', display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
                    <Paper
                        elevation={0}
                        sx={{
                            px: 3, py: 2,
                            borderRadius: isUser ? '24px 24px 0px 24px' : '24px 24px 24px 0px',
                            bgcolor: isUser ? '#FCD12A' : '#FFFFFF',
                            color: '#1A1A1A',
                            border: '2px solid #1A1A1A',
                            boxShadow: isUser ? '-4px 4px 0px #1A1A1A' : '4px 4px 0px #1A1A1A', // Sharp geometric shadows
                            transition: 'transform 0.1s',
                            '&:hover': { transform: 'translateY(-2px)' },
                        }}
                    >
                        <Typography
                            variant="body1"
                            sx={{
                                fontWeight: 500,
                                lineHeight: 1.6,
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                            }}
                        >
                            {msg.content}
                        </Typography>
                    </Paper>
                    <Typography variant="caption" sx={{ color: '#666', mt: 1, px: 1, fontWeight: 700 }}>
                        {formatTime(msg.time)}
                    </Typography>
                </Box>
            </Box>
        </Fade>
    )
}

// ── Welcome screen ────────────────────────────────────────────────────────────
function WelcomeScreen({ onSuggestion }) {
    return (
        <Box
            sx={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                height: '100%', textAlign: 'center', px: 3, gap: 4,
            }}
        >
            <Zoom in timeout={500}>
                <Box
                    sx={{
                        width: 100, height: 100, borderRadius: '50%',
                        bgcolor: '#1A1A1A',
                        border: '4px solid #FCD12A',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '8px 8px 0px #FCD12A',
                    }}
                >
                    <AssessmentIcon sx={{ fontSize: 50, color: '#FCD12A' }} />
                </Box>
            </Zoom>

            <Fade in timeout={700}>
                <Box>
                    <Typography variant="h2" gutterBottom
                        sx={{
                            fontWeight: 900,
                            letterSpacing: '0.1em',
                            color: '#1A1A1A',
                            textTransform: 'uppercase',
                        }}
                    >
                        S A H A Y ▲ K
                    </Typography>
                    <Typography variant="h6" sx={{ maxWidth: 500, mx: 'auto', fontWeight: 500, color: '#4D4D4D' }}>
                        YOUR AI-POWERED PERSONAL FINANCE ASSISTANT.
                        <br /><br />
                        Track expenses, get budgeting tips, and discover the best Indian fintech tools — Powered By AI.
                    </Typography>
                </Box>
            </Fade>

            {/* Suggestion pills */}
            <Fade in timeout={900}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'center', maxWidth: 600 }}>
                    {SUGGESTIONS.map((s, i) => (
                        <Chip
                            key={i}
                            label={s}
                            clickable
                            onClick={() => onSuggestion(s)}
                            sx={{
                                bgcolor: '#FFFFFF',
                                border: '2px solid #1A1A1A',
                                color: '#1A1A1A',
                                fontWeight: 700,
                                px: 1,
                                py: 2.5,
                                borderRadius: '999px',
                                transition: 'all 0.2s',
                                boxShadow: '2px 2px 0px #1A1A1A',
                                '&:hover': {
                                    bgcolor: '#FCD12A', // Hover to signature yellow
                                    transform: 'translate(-2px, -2px)',
                                    boxShadow: '4px 4px 0px #1A1A1A',
                                },
                            }}
                        />
                    ))}
                </Box>
            </Fade>
        </Box>
    )
}

// ── Main ChatPage ─────────────────────────────────────────────────────────────
export default function ChatPage() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState(generateSessionId)
    const [isOnline, setIsOnline] = useState(null)
    const messagesEndRef = useRef(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    useEffect(() => {
        fetch(`${API_BASE}/health`)
            .then(r => r.ok ? setIsOnline(true) : setIsOnline(false))
            .catch(() => setIsOnline(false))
    }, [])

    const addMessage = useCallback((role, content) => {
        setMessages(prev => [...prev, { role, content, time: new Date() }])
    }, [])

    const sendMessage = useCallback(async (text) => {
        const msg = (text || input).trim()
        if (!msg || loading) return

        setInput('')
        addMessage('user', msg)
        setLoading(true)

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, message: msg }),
            })

            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                addMessage('assistant', `⚠️ Error: ${err.detail || `Server returned ${res.status}`}`)
                return
            }

            const data = await res.json()
            addMessage('assistant', data.response)
        } catch {
            addMessage('assistant', '⚠️ Cannot reach server. Is uvicorn running on port 8000?')
        } finally {
            setLoading(false)
        }
    }, [input, loading, sessionId, addMessage])

    const clearHistory = useCallback(async () => {
        try {
            await fetch(`${API_BASE}/history/${sessionId}`, { method: 'DELETE' })
        } catch { }
        setMessages([])
    }, [sessionId])

    const newSession = useCallback(() => {
        setMessages([])
        setSessionId(generateSessionId())
    }, [])

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <Box
            sx={{
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.default',
            }}
        >
            {/* ── Header ─────────────────────────────────────────────── */}
            <Paper
                elevation={0}
                square
                sx={{
                    px: { xs: 2, sm: 4 }, py: 2,
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    borderBottom: '4px solid #1A1A1A', // Thick industrial bottom border
                    bgcolor: '#FCD12A', // Solid yellow header
                    position: 'sticky', top: 0, zIndex: 10,
                }}
            >
                {/* Title */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, cursor: 'pointer', transition: 'transform 0.2s', '&:hover': { transform: 'scale(1.02)' } }} onClick={() => window.location.href = '/'}>
                    <Box
                        component="img"
                        src="/logo.jpg"
                        alt="Sahayak Logo"
                        sx={{
                            width: 54, height: 54, borderRadius: '12px',
                            objectFit: 'contain',
                        }}
                    />
                    <Box>
                        <Typography variant="h6" fontWeight={900} letterSpacing="0.05em" sx={{ color: '#1A1A1A' }}>
                            SAHAYAK
                        </Typography>
                        <Typography variant="caption" fontWeight={700} sx={{ color: '#1A1A1A' }}>
                            AI FINANCIAL ASSISTANT
                        </Typography>
                    </Box>
                </Box>

                {/* Right side */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Chip
                        size="medium"
                        label={isOnline === null ? 'CHECKING...' : isOnline ? 'SYSTEM ONLINE' : 'OFFLINE'}
                        sx={{
                            fontWeight: 800,
                            letterSpacing: '0.05em',
                            bgcolor: isOnline ? '#4DBAC1' : isOnline === false ? '#FF4D4D' : '#F2F2F2',
                            color: '#1A1A1A',
                            border: '2px solid #1A1A1A',
                            borderRadius: '999px',
                            boxShadow: '2px 2px 0px #1A1A1A',
                        }}
                    />

                    <Tooltip title="Clear chat" arrow>
                        <span>
                            <IconButton
                                size="large"
                                onClick={clearHistory}
                                disabled={messages.length === 0}
                                sx={{
                                    bgcolor: '#FFFFFF',
                                    border: '2px solid #1A1A1A',
                                    boxShadow: '2px 2px 0px #1A1A1A',
                                    color: '#1A1A1A',
                                    '&:hover': { bgcolor: '#FF4D4D', color: '#FFF', transform: 'translate(-2px, -2px)', boxShadow: '4px 4px 0px #1A1A1A' },
                                    '&:disabled': { opacity: 0.5 },
                                    transition: 'all .1s',
                                }}
                            >
                                <DeleteOutlineIcon fontSize="medium" />
                            </IconButton>
                        </span>
                    </Tooltip>

                    <Tooltip title="New session" arrow>
                        <IconButton
                            size="large"
                            onClick={newSession}
                            sx={{
                                bgcolor: '#FFFFFF',
                                border: '2px solid #1A1A1A',
                                boxShadow: '2px 2px 0px #1A1A1A',
                                color: '#1A1A1A',
                                '&:hover': { bgcolor: '#F2F2F2', transform: 'translate(-2px, -2px)', boxShadow: '4px 4px 0px #1A1A1A' },
                                transition: 'all .1s',
                            }}
                        >
                            <AutorenewIcon fontSize="medium" />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Paper>

            {/* ── Messages area ───────────────────────────────────────── */}
            <Box
                sx={{
                    flex: 1, overflowY: 'auto',
                    px: { xs: 2, sm: 6, md: 14, lg: 24 },
                    py: 5,
                    display: 'flex', flexDirection: 'column',
                }}
            >
                {messages.length === 0 ? (
                    <WelcomeScreen onSuggestion={(s) => sendMessage(s)} />
                ) : (
                    <>
                        {messages.map((msg, i) => (
                            <MessageBubble key={i} msg={msg} />
                        ))}

                        {/* Typing indicator */}
                        {loading && (
                            <Fade in>
                                <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1.5, mb: 3 }}>
                                    <Avatar sx={{
                                        width: 44, height: 44,
                                        bgcolor: '#4DBAC1', color: '#1A1A1A', border: '2px solid #1A1A1A',
                                    }}>
                                        <SmartToyIcon />
                                    </Avatar>
                                    <Paper
                                        elevation={0}
                                        sx={{
                                            px: 3, py: 2,
                                            borderRadius: '24px 24px 24px 0px',
                                            bgcolor: '#FFFFFF',
                                            border: '2px solid #1A1A1A',
                                            boxShadow: '4px 4px 0px #1A1A1A',
                                        }}
                                    >
                                        <TypingIndicator />
                                    </Paper>
                                </Box>
                            </Fade>
                        )}
                    </>
                )}
                <div ref={messagesEndRef} />
            </Box>

            {/* ── Input area ──────────────────────────────────────────── */}
            <Box
                sx={{
                    px: { xs: 2, sm: 6, md: 14, lg: 24 },
                    py: 3,
                    bgcolor: '#FFFFFF',
                    borderTop: '4px solid #1A1A1A', // Sharp industrial split
                }}
            >
                {/* Active Suggestion Chips */}
                {messages.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                        {SUGGESTIONS.slice(0, 3).map((s, i) => (
                            <Chip
                                key={i}
                                label={s}
                                size="small"
                                clickable
                                onClick={() => sendMessage(s)}
                                sx={{
                                    bgcolor: '#F2F2F2',
                                    border: '2px solid #1A1A1A',
                                    color: '#1A1A1A',
                                    fontWeight: 700,
                                    borderRadius: '999px',
                                    boxShadow: '2px 2px 0px #1A1A1A',
                                    '&:hover': {
                                        bgcolor: '#FCD12A',
                                        transform: 'translate(-2px, -2px)',
                                        boxShadow: '4px 4px 0px #1A1A1A',
                                    },
                                    transition: 'all 0.1s',
                                }}
                            />
                        ))}
                    </Box>
                )}

                <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your prompt here... (Enter to send)"
                        disabled={loading}
                        variant="outlined"
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                borderRadius: '999px', // Pill shape input
                                bgcolor: '#F2F2F2',
                                fontSize: '1rem',
                                fontWeight: 500,
                                px: 3,
                                '& fieldset': { border: '2px solid #1A1A1A' },
                                '&:hover fieldset': { border: '2px solid #1A1A1A' },
                                '&.Mui-focused fieldset': {
                                    border: '2px solid #1A1A1A',
                                    boxShadow: '0 0 0 4px rgba(252, 209, 42, 0.4)', // Yellow glow
                                },
                            },
                        }}
                    />

                    <IconButton
                        onClick={() => sendMessage()}
                        disabled={loading || !input.trim()}
                        sx={{
                            width: 56, height: 56, // Large circular black button
                            bgcolor: '#1A1A1A',
                            border: '2px solid #1A1A1A',
                            borderRadius: '50%',
                            flexShrink: 0,
                            boxShadow: input.trim() ? '4px 4px 0px #FCD12A' : 'none',
                            color: '#FCD12A', // signature yellow icon
                            transition: 'all 0.1s',
                            '&:hover': {
                                bgcolor: '#1A1A1A',
                                transform: input.trim() ? 'translate(-2px, -2px)' : 'none',
                                boxShadow: input.trim() ? '6px 6px 0px #FCD12A' : 'none',
                            },
                            '&:active': { transform: 'translate(0px, 0px)', boxShadow: 'none' },
                            '&.Mui-disabled': { bgcolor: '#CCCCCC', color: '#888', border: '2px solid #888' },
                        }}
                    >
                        {loading ? <CircularProgress size={24} sx={{ color: '#1A1A1A' }} /> : <SendIcon fontSize="medium" />}
                    </IconButton>
                </Box>

                <Typography
                    variant="caption"
                    sx={{ display: 'block', textAlign: 'center', mt: 2, fontWeight: 700, color: '#999', letterSpacing: '0.05em' }}
                >
                    SESSION ID: {sessionId}
                </Typography>
                <Typography
                    variant="caption"
                    sx={{
                        display: 'block', textAlign: 'center', mt: 1, fontWeight: 700, color: '#1A1A1A',
                        '& a': { color: '#1A1A1A', textDecoration: 'none', borderBottom: '2px solid #1A1A1A', transition: 'all 0.2s' },
                        '& a:hover': { color: '#FCD12A', background: '#1A1A1A' }
                    }}
                >
                    Developed by <a href="https://www.linkedin.com/in/sainandhan/" target="_blank" rel="noopener noreferrer">M. Sainandhan</a>
                </Typography>
            </Box>
        </Box>
    )
}

