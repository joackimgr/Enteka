import { Frown, CircleUserRound } from "lucide-react"
import { useState, useEffect} from "react"
import { getChats } from "../api/client"

export default function Sidebar(props) {
    const [loading, setLoading] = useState(true)
    const [chats, setChats] = useState()

    useEffect(() => {
        async function fetchChats() {
            const data = await getChats()
            if (data && data.chats) {
                setChats(data.chats) 
            }
            setLoading(false)
        }
        fetchChats()
    }, [props.chatRefresh])

    const chatBlocks = (chats || []).map((chat) => {
        return (
            <div key={chat.chat_id} onClick={() => {props.setSelectedChat({chat_id: chat.chat_id, username: chat.other_username})}} className="flex items-center gap-3 p-3 my-1.5 rounded-xl cursor-pointer bg-[#2F3347] hover:bg-[#363B52] transition-colors duration-100" >
                <CircleUserRound size={45} className="shrink-0" color="white"/>
                <div className="min-w-0 flex-1">
                    <p className="text-lg truncate text-white">{chat.other_username}</p>
                    <div className="flex justify-between">
                        <p className="text-sm truncate text-gray-400">{chat.last_message}</p>
                        <p className="text-sm truncate text-gray-400">{chat.last_timestamp}</p>
                    </div>
                </div>
            </div>
        )
    })

    return (
        <>
            {props.chatMode && loading &&
                <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl text-white">
                    <Frown size={70} alt="Sad Emoji"/>
                    <p className="text-white">Loading...</p>
                </div>
            }
            {props.chatMode && !loading && (!chats || chats.length === 0) &&
                <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl text-white">
                    <Frown size={70} alt="Sad Emoji"/>
                    <p className="text-white">You have no chats yet.</p>
                </div>
            }
            {props.chatMode && !loading && chats && chats.length > 0 &&
                <div className="flex flex-col bg-[#272B3D] rounded-4xl text-white overflow-y-auto min-h-0 py-4 px-4">
                    {chatBlocks}
                </div>
            }
            {!props.chatMode && 
                <div className="bg-[#272B3D] rounded-[1.2rem] p-2.75 flex flex-col items-center gap-2.75">
                    <div onClick={props.toggleStatus} className="bg-[#40465d] mb-2.75 p-2.75 w-full box-border rounded-[1.2rem] flex items-center gap-5 cursor-pointer hover:bg-[#3a3f54] transition-colors duration-100 ease-in">
                        <CircleUserRound size={50} alt="Account Settings Icon" className="text-white"/>
                        <p className="text-white text-[23px] font-light m-0">Account Settings</p>
                    </div>
                </div>
            }
        </>
    )
}