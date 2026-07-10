import NavBar from "../components/layout/NavBar"
import Sidebar from "../components/layout/Sidebar"
import WelcomeView from "../components/chat/WelcomeView"
import SettingsPanel from "../components/settings/SettingsPanel"
import NewMessage from "../components/chat/NewMessage"
import ChatView from "../components/chat/ChatView"
import { useState } from "react"

export default function HomePage({userName}) {
    const [chatMode, setChatMode] = useState(true)
    const [welcome, setWelcome] = useState(true)
    const [activeSettings, setActiveSettings] = useState(false)
    const [selectedChat, setSelectedChat] = useState(null)

    function toggleChatMode() {
        setChatMode(prevChatMode => !prevChatMode)
    }

    function turnOffWelcomeMode() {
        setWelcome(false)
    }

    function toggleStatus() {
        setActiveSettings(prevState => !prevState)
    }

    return (
        <div className="h-screen flex flex-col">
            <NavBar toggleChatMode={toggleChatMode} />
            <section className="grid grid-cols-[1fr_5fr] m-2.75 gap-2.75 flex-1 min-h-0 grid-rows-[minmax(0,1fr)]">
                <Sidebar chatMode={chatMode} toggleStatus={toggleStatus} />
                    {chatMode && selectedChat && 
                        <ChatView selectedChat={selectedChat}/>
                    }
                    {!selectedChat && chatMode && welcome &&
                        <WelcomeView turnOffWelcomeMode={turnOffWelcomeMode} userName={userName} />
                    }
                    {!selectedChat && chatMode && !welcome &&
                        <NewMessage setSelectedChat={setSelectedChat}/>
                    }
                    {!chatMode &&
                        <SettingsPanel activeSettings={activeSettings} />
                    }
            </section>
        </div>
    )
}