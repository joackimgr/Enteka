import { useState, useEffect } from "react"
import { CircleUserRound, SearchAlert } from "lucide-react"
import { search, sendFriendRequest } from "../api/client.js"
import { Search } from "lucide-react"

export default function FriendsView(props) {
    const [searchText, setSearchText] = useState('')
    const [users, setUsers] = useState([])
    const [sentRequest, setSentRequest] = useState(new Set())

    const listToShow = searchText !== "" ? users : []

    async function handleUserClick(user) {
        const data = await sendFriendRequest(user.id)
        if (data?.auth === false && data.message === "Network error. Try again.") return;
        setSentRequest(prev => new Set(prev).add(user.id))
    }

    const userNames = listToShow.map((user) => {
        return (
        <div key={user.id} onClick={() => handleUserClick(user)} className="flex items-center justify-between bg-[#272B3D] rounded-[1.2rem] p-2.75 mb-2.75 text-3xl cursor-pointer hover:bg-[#363B52] transition-colors duration-100 ease-in">
            <div className="flex items-center gap-2.75 ml-5 font-light">
                <CircleUserRound size={70} alt="Profile" className="text-white" />
                <p>{`${user.username}`}</p>
            </div>
            {sentRequest.has(user.id) ? <p>{`Request Sent`}</p> : <p>{`Send Friend Request`}</p>}
        </div>
        )
    })

    function handleSearchText(e) {
        let value = e.target.value
        setSearchText(value)
        if (value === "") setUsers([])
    }

    useEffect(() => {
        if (searchText === "") return

        let cancelled = false
        const timeoutId = setTimeout(async () => {
            const response = await search(searchText)
            const filteredUsers = response ? response.filter(u => u.username !== props.userName) : []
            if (!cancelled) setUsers(filteredUsers)
        }, 300)

        return () => {
            cancelled = true
            clearTimeout(timeoutId)
        }
    }, [searchText, props.userName])


    return (
        <div className="bg-[#272B3D] flex flex-col items-center justify-start rounded-4xl p-2.75 text-white">
            <div className="flex items-center w-full bg-[#2F3347] h-auto p-2.75 text-4xl font-light box-border rounded-[1.2rem] gap-2.75 mb-2.75">
                <Search size={30} />
                <input type="text" id="recipientName" placeholder="Find People" onChange={handleSearchText} className="w-full py-2 box-border rounded-[1.2rem] border-0 bg-[#2F3347] text-[30px] text-white focus:outline-none"/>
            </div>
            <div className="flex flex-col p-2.75 w-full bg-[#2F3347] box-border rounded-[1.2rem] flex-1">
                <p className="text-2xl mt-1.25 mb-3.75">Search Results:</p>
                {listToShow.length >= 1 && userNames}
                {listToShow.length == 0 && 
                    <div className="flex flex-col items-center justify-center gap-7 flex-1">
                        <SearchAlert size={80}/>
                        <p className="text-4xl mb-2">No Users found.</p>
                    </div>
                }
            </div>
        </div>
    )
}