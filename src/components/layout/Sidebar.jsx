import { Frown, CircleUserRound, Check, X } from "lucide-react"
import { useState, useEffect} from "react"
import { getChats, createChat, getFriendsList, getFriendRequests, acceptFriendRequest, rejectFriendRequest } from "../api/client"

export default function Sidebar(props) {
    const [loadingChats, setLoadingChats] = useState(true)
    const [loadingFriends, setLoadingFriends] = useState(true)
    const [chats, setChats] = useState()
    const [friends, setFriends] = useState()
    const [requests, setRequests] = useState()

    async function handleFriendClick(friend) {
        const chat = await createChat(friend.friend_id)
        if (!chat) return
        props.setSelectedChat({id: friend.friend_id, username: friend.username, chat_id: chat.chat.chat_id})
        props.toggleFriendsMode()
    }

    useEffect(() => {
        async function fetchChats() {
            const data = await getChats()
            if (data && data.chats) {
                setChats(data.chats) 
            }
            setLoadingChats(false)
        }
        fetchChats()
    }, [props.chatRefresh])

    useEffect(() => {
        async function fetchFriends() {
            const data = await getFriendsList()
            if (data && data.friends) {
                setFriends(data.friends) 
            }
            setLoadingFriends(false)
        }
        fetchFriends()
    }, [props.friendsRefresh])

    useEffect(() => {
        async function fetchRequests() {
            const data = await getFriendRequests()
            if (data && data.requests) {
                setRequests(data.requests) 
            }
        }
        fetchRequests()
    }, [props.friendsRefresh])

    async function handleAccept(request) {
        await acceptFriendRequest(request.id)

        const friendsData = await getFriendsList()
        const requestsData = await getFriendRequests()

        if (friendsData?.friends) setFriends(friendsData.friends)
        if (requestsData?.requests) setRequests(requestsData.requests)
    }

    async function handleReject(request) {
        await rejectFriendRequest(request.id)

        const data = await getFriendRequests()
        if (data?.requests) setRequests(data.requests)
    }

    const requestBlocks = (requests || []).map((request) => {
        return (
            <div key={request.id} className="flex justify-between gap-3 p-3 my-1.5 rounded-xl bg-[#2F3347]" >
                <div className="flex justify-between gap-2">
                    <CircleUserRound size={45} className="shrink-0" color="white"/>
                    <div className="flex flex-col justify-between">
                        <p className="text-lg truncate text-white">{request.username}</p>
                        <p className="text-sm truncate text-gray-400">{new Date(request.created_at).toLocaleDateString()}</p>
                    </div>
                </div>
                <div className="flex flex-col justify-between">
                    <Check size={20} color="white" className="cursor-pointer" onClick={() => handleAccept(request)} />
                    <X size={20} color="white" className="cursor-pointer" onClick={() => handleReject(request)} />
                </div>
            </div>
        )
    })


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

    const friendsBlocks = (friends || []).map((friend) => {
        return (
            <div key={friend.friend_id} onClick={() => handleFriendClick(friend)} className="flex items-center gap-3 p-3 my-1.5 rounded-xl cursor-pointer bg-[#2F3347] hover:bg-[#363B52] transition-colors duration-100" >
                <CircleUserRound size={45} className="shrink-0" color="white"/>
                <div className="min-w-0 flex-1">
                    <p className="text-lg truncate text-white">{friend.username}</p>
                </div>
            </div>
        )
    })

    return (
        <>
            {!props.friendsMode && props.chatMode && loadingChats &&
                <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl text-white">
                    <Frown size={70} alt="Sad Emoji"/>
                    <p className="text-white">Loading...</p>
                </div>
            }
            {!props.friendsMode && props.chatMode && !loadingChats && (!chats || chats.length === 0) &&
                <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl text-white">
                    <Frown size={70} alt="Sad Emoji"/>
                    <p className="text-white">You have no chats yet.</p>
                </div>
            }
            {!props.friendsMode && props.chatMode && !loadingChats && chats && chats.length > 0 &&
                <div className="flex flex-col bg-[#272B3D] rounded-4xl text-white overflow-y-auto min-h-0 py-4 px-4">
                    {chatBlocks}
                </div>
            }
            {!props.friendsMode && !props.chatMode && 
                <div className="bg-[#272B3D] rounded-[1.2rem] p-2.75 flex flex-col items-center gap-2.75">
                    <div onClick={props.toggleStatus} className="bg-[#40465d] mb-2.75 p-2.75 w-full box-border rounded-[1.2rem] flex items-center gap-5 cursor-pointer hover:bg-[#3a3f54] transition-colors duration-100 ease-in">
                        <CircleUserRound size={50} alt="Account Settings Icon" className="text-white"/>
                        <p className="text-white text-[23px] font-light m-0">Account Settings</p>
                    </div>
                </div>
            }
            {props.friendsMode &&
                <div className="flex flex-col bg-[#272B3D] rounded-4xl text-white overflow-y-auto min-h-0 py-4 px-4">
                    {requests && requests.length > 0 && 
                        <div>
                            <p className="text-lg font-light mb-2">Requests</p>
                            {requestBlocks}
                        </div>
                    }
                    {friends && friends.length > 0 && 
                        <div>
                            <p className="text-lg font-light mb-2">Friends List</p>
                            {friendsBlocks}
                        </div>
                    }
                    {!loadingFriends && (!friends || friends.length === 0) && (!requests || requests.length === 0) &&
                        <div className="flex flex-col justify-center items-center flex-1 text-white">
                            <Frown size={70} alt="Sad Emoji"/>
                            <p className="text-white">You have no friends yet.</p>
                        </div>
                    }
                </div>
            }
        </>
    )
}