import { Send, ImagePlus } from "lucide-react"
import { useState, useRef } from "react"

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
const MAX_SIZE = 5 * 1024 * 1024

export default function MessageInput({ SendMessage, onTyping, onImageSelected, uploading }) {
    const [inputText, setInputText] = useState('')
    const fileInputRef = useRef(null)

    function handleSend() {
        if (!inputText.trim()) return
        SendMessage(inputText)
        setInputText('')
    }

    function handleFileChange(e) {
        const file = e.target.files?.[0]
        e.target.value = ''
        if (!file) return
        if (!ALLOWED_TYPES.includes(file.type) || file.size > MAX_SIZE) return
        if (onImageSelected) onImageSelected(file)
    }

    return (
        <div className="bg-[#272B3D] rounded-4xl px-5 py-3 flex items-center gap-3 shadow-sm">
            <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleFileChange}
                className="hidden"
            />
            <ImagePlus
                size={30}
                onClick={() => { if (!uploading) fileInputRef.current?.click() }}
                className={`text-white transition-transform duration-150 ease-out ${uploading ? "opacity-40" : "cursor-pointer hover:-translate-y-1"}`}
            />
            <input type="text" value={inputText} placeholder={uploading ? "Uploading image..." : "Type a message..."} onChange={(e) => {setInputText(e.target.value); if (onTyping) onTyping()}} onKeyDown={(e) => e.key === "Enter" && handleSend()} className="flex-1 bg-[#2F3347] text-white placeholder:text-[#A7ABBD] rounded-[1.2rem] px-4 py-2 text-[18px] font-light outline-none transition duration-150 ease-out focus:ring-2 focus:ring-[#646A84]"/>
            <Send size={30} alt="Send Message" onClick={handleSend} className="cursor-pointer text-white transition-transform duration-150 ease-out hover:-translate-y-1"/>
        </div>
    )
}
