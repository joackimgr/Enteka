import { useState, useEffect } from "react"
import { CircleUserRound } from "lucide-react"

export default function NewMessage() {
    const [searchText, setSearchText] = useState('')
    const [users, setUsers] = useState([])
    const [suggestions, setSuggestions] = useState([])

    const listToShow = searchText !== "" ? users : suggestions
    const userNames = listToShow.map((i) => {
        return (
        <div key={i} className="flex items-center justify-between bg-[#272B3D] rounded-[1.2rem] p-2.75 mb-2.75 text-3xl cursor-pointer hover:bg-[#363B52] transition-colors duration-100 ease-in">
            <div className="flex items-center gap-2.75 ml-5 font-light">
                <CircleUserRound size={70} alt="Profile" className="text-white" />
                <p>{`User${i}`}</p>
            </div>
            <p>{`Start a chat with User${i}`}</p>
        </div>
        )
    })

    function handleSearchText(e) {
        setSearchText(e.target.value)
    }

    useEffect(() => {
        if (searchText !== "") {
            console.log("Call Backend")
        }
    }, [searchText])

    useEffect(() => {
        console.log("Load Suggestions")
    }, [])

    return (

        <div className="bg-[#272B3D] flex flex-col items-center justify-start rounded-4xl p-2.75 text-white">
            <div className="flex items-center w-full bg-[#2F3347] h-auto p-2.75 text-4xl font-light box-border rounded-[1.2rem] gap-2.75 mb-2.75">
                <label htmlFor="recipientName">To:</label>
                <input type="text" id="recipientName" onChange={handleSearchText} className="w-full h-full box-border rounded-[1.2rem] border-0 bg-[#2F3347] text-[30px] text-white focus:outline-none"/>
            </div>
            <div className="flex flex-col p-2.75 w-full bg-[#2F3347] box-border rounded-[1.2rem]">
                <p className="text-2xl mt-1.25 mb-3.75">Suggestions:</p>
                {userNames}
            </div>
        </div>
    )
}