import  NavBar  from "../components/NavBar"
import  Sidebar  from "../components/Sidebar"
import  WelcomeView  from "../components/WelcomeView"
import SettingsPanel from "../components/SettingsPanel"
import NewMessage from "../components/NewMessage"
import { useState } from "react"

export default function HomePage({userName}) {
    const [chatMode, setChatMode] = useState(true)
    const [welcome, setWelcome] = useState(true)
    const [activeSettings, setActiveSettings] = useState(false)

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
        <div className="min-h-screen flex flex-col">
            <NavBar toggleChatMode={toggleChatMode} />
            <section className="grid grid-cols-[1fr_5fr] m-2.75 gap-2.75 flex-1">
                <Sidebar chatMode={chatMode} toggleStatus={toggleStatus} />
                {chatMode && welcome &&
                    <WelcomeView turnOffWelcomeMode={turnOffWelcomeMode} userName={userName} />
                }
                {chatMode && !welcome &&
                    <NewMessage />
                }
                {!chatMode &&
                    <SettingsPanel activeSettings={activeSettings} />
                }
            </section>
        </div>
    )
}