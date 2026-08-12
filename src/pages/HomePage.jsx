import NavBar from "../components/layout/NavBar"
import Sidebar from "../components/layout/Sidebar"
import WelcomeView from "../components/chat/WelcomeView"
import SettingsPanel from "../components/settings/SettingsPanel"
import NewMessage from "../components/chat/NewMessage"
import ChatView from "../components/chat/ChatView"
import FriendsView from "../components/friends/FriendsView"
import { useState, useRef, useEffect } from "react"
import { WS_BASE } from "../components/api/client"

export default function HomePage({userName}) {
    const [chatMode, setChatMode] = useState(true)
    const [welcome, setWelcome] = useState(true)
    const [activeSettings, setActiveSettings] = useState(false)
    const [selectedChat, setSelectedChat] = useState(null)
    const [chatRefresh, setChatRefresh] = useState(0)
    const [friendsRefresh, setFriendsRefresh] = useState(0)
    const [friendsMode, setFriendsMode] = useState(false)
    const wsRef = useRef(null)
    const genRef = useRef(0)
    const reconnectAttemptRef = useRef(0)
    const reconnectTimerRef = useRef(null)
    const isIntentionalCloseRef = useRef(false)

    function connect() {
        const myGen = ++genRef.current
        if (wsRef.current) {
            wsRef.current.onclose = null
            wsRef.current.close()
        }
        const token = localStorage.getItem('token')
        const wsUri = `${WS_BASE}/ws/notifications?token=${token}`
        const websocket = new WebSocket(wsUri)
        wsRef.current = websocket

        websocket.onopen = () => {
            reconnectAttemptRef.current = 0
        }

        websocket.onmessage = (event) => {
            if (myGen !== genRef.current) return
            const data = JSON.parse(event.data)
            if (data.type === "new_message") {
                bumpChatRefresh()
            } else if (data.type === "new_friend_request") {
                bumpFriendsRefresh()
            }
        }

        websocket.onclose = () => {
            if (myGen !== genRef.current) return
            if (!isIntentionalCloseRef.current) {
                const max_attempts = 5
                if (reconnectAttemptRef.current < max_attempts) {
                    const delay = 1000 * (2 ** reconnectAttemptRef.current)
                    reconnectAttemptRef.current += 1
                    reconnectTimerRef.current = setTimeout(() => {
                        connect()
                    }, delay)
                }
            }
        }
    }

    useEffect(() => {
        isIntentionalCloseRef.current = false
        connect()
        return () => {
            isIntentionalCloseRef.current = true
            if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
            wsRef.current.close()
        }
    }, [])

    function toggleChatMode() {
        setChatMode(prevChatMode => !prevChatMode)
    }

    function turnOffWelcomeMode() {
        setWelcome(false)
    }

    function toggleStatus() {
        setActiveSettings(prevState => !prevState)
    }

    function handleBack() {
        setSelectedChat(null)
    }

    function goHome() {
        setSelectedChat(null)
        setWelcome(true)
        setChatMode(true)
    }

    function bumpChatRefresh() {
        setChatRefresh(prev => prev + 1)
    }

    function bumpFriendsRefresh() {
        setFriendsRefresh(prev => prev + 1)
    }

    function toggleFriendsMode() {
        setFriendsMode(prev => !prev)
    }

    return (
        <div className="h-screen flex flex-col">
            <NavBar toggleChatMode={toggleChatMode} goHome={goHome} toggleFriendsMode={toggleFriendsMode} />
            <section className="grid grid-cols-[1fr_5fr] m-2.75 gap-2.75 flex-1 min-h-0 grid-rows-[minmax(0,1fr)]">
                <Sidebar chatMode={chatMode} friendsMode={friendsMode} toggleFriendsMode={toggleFriendsMode} toggleStatus={toggleStatus} setSelectedChat={setSelectedChat} chatRefresh={chatRefresh} friendsRefresh={friendsRefresh} />
                    {!friendsMode && chatMode && selectedChat && 
                        <ChatView selectedChat={selectedChat} handleBack={handleBack} bumpChatRefresh={bumpChatRefresh} userName={userName} />
                    }
                    {!friendsMode && !selectedChat && chatMode && welcome &&
                        <WelcomeView turnOffWelcomeMode={turnOffWelcomeMode} userName={userName} />
                    }
                    {!friendsMode && !selectedChat && chatMode && !welcome &&
                        <NewMessage setSelectedChat={setSelectedChat} bumpChatRefresh={bumpChatRefresh} />
                    }
                    {!friendsMode && !chatMode &&
                        <SettingsPanel activeSettings={activeSettings} />
                    }
                    {friendsMode &&
                        <FriendsView userName={userName}/>
                    }
            </section>
        </div>
    )
}