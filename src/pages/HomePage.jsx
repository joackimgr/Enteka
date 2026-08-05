import NavBar from "../components/layout/NavBar"
import Sidebar from "../components/layout/Sidebar"
import WelcomeView from "../components/chat/WelcomeView"
import SettingsPanel from "../components/settings/SettingsPanel"
import NewMessage from "../components/chat/NewMessage"
import ChatView from "../components/chat/ChatView"
import FriendsView from "../components/friends/FriendsView"
import { useState } from "react"

export default function HomePage({userName, setUserName}) {
    const [chatMode, setChatMode] = useState(true)
    const [welcome, setWelcome] = useState(true)
    const [activeSettings, setActiveSettings] = useState(false)
    const [selectedChat, setSelectedChat] = useState(null)
    const [chatRefresh, setChatRefresh] = useState(0)
    const [friendsMode, setFriendsMode] = useState(false)

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

    function toggleFriendsMode() {
        setFriendsMode(prev => !prev)
    }

    return (
        <div className="h-screen flex flex-col">
            <NavBar toggleChatMode={toggleChatMode} goHome={goHome} toggleFriendsMode={toggleFriendsMode} />
            <section className="grid grid-cols-[1fr_5fr] m-2.75 gap-2.75 flex-1 min-h-0 grid-rows-[minmax(0,1fr)]">
                <Sidebar chatMode={chatMode} friendsMode={friendsMode} toggleFriendsMode={toggleFriendsMode} toggleStatus={toggleStatus} setSelectedChat={setSelectedChat} chatRefresh={chatRefresh} />
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
                        <SettingsPanel activeSettings={activeSettings} setUserName={setUserName} />
                    }
                    {friendsMode &&
                        <FriendsView userName={userName}/>
                    }
            </section>
        </div>
    )
}