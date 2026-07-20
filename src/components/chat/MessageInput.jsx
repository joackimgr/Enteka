import { Send } from "lucide-react"
import { useState } from "react"

export default function MessageInput({ SendMessage, onTyping }) {
    const [inputText, setInputText] = useState('')

    function handleSend() {
        SendMessage(inputText)
        setInputText('')
    }

    return (
        <div className="bg-[#272B3D] rounded-4xl px-5 py-3 flex items-center gap-3 shadow-sm">
            <input type="text" value={inputText} placeholder="Type a message..." onChange={(e) => {setInputText(e.target.value); if (onTyping) onTyping()}} onKeyDown={(e) => e.key === "Enter" && handleSend()} className="flex-1 bg-[#2F3347] text-white placeholder:text-[#A7ABBD] rounded-[1.2rem] px-4 py-2 text-[18px] font-light outline-none transition duration-150 ease-out focus:ring-2 focus:ring-[#646A84]"/>
            <Send size={30} alt="Send Message" onClick={handleSend} className="cursor-pointer text-white transition-transform duration-150 ease-out hover:-translate-y-1"/>
        </div>
    )
}