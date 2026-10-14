import { CircleArrowLeft } from "lucide-react"
import Avatar from "../Avatar"


export default function ChatHeader({username, handleBack, profilePicture}) {

    return (
        <div className="flex justify-center items-center gap-5 py-2 px-4 border-b border-[#40465D] bg-[#2F3347] relative">
            <CircleArrowLeft size={40} color="white" onClick={handleBack} className="absolute left-4 cursor-pointer transition-transform duration-150 ease-out hover:-translate-y-0.5"/>
            <Avatar src={profilePicture} size={50} />
            <h3 className="text-white">{username}</h3>
        </div>
    )
}
