import send from "../assets/send.png"

export default function MessageInput() {

    return (
        <div className="bg-[#272B3D] border border-[#343954] rounded-4xl px-5 py-3 flex items-center gap-3 shadow-sm">
            <input type="text" placeholder="Type a message..." className="flex-1 bg-[#2F3347] text-white placeholder:text-[#A7ABBD] rounded-[1.2rem] px-4 py-2 text-[18px] font-light outline-none transition duration-150 ease-out focus:ring-2 focus:ring-[#646A84]"/>
            <img src={send} alt="Send Message" className="w-10 h-10 cursor-pointer transition-transform duration-150 ease-out hover:-translate-y-1"/>
        </div>
    )
}