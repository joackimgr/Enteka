import profile from "../assets/profile_icon.png"

export default function NewMessage() {

    const users = [1, 2, 3]

    const userNames = users.map((i) => {
        return (
        <div key={i} className="flex items-center justify-between bg-[#272B3D] rounded-[1.2rem] p-2.75 mb-2.75 text-3xl cursor-pointer hover:bg-[#363B52] transition-colors duration-100 ease-in">
            <div className="flex items-center gap-2.75 ml-5 font-light">
                <img src={profile} alt={`User${i} Icon`} className="w-17.5 h-17.5"/>
                <p>{`User${i}`}</p>
            </div>
            <p>{`Start a chat with User${i}`}</p>
        </div>
        )
    })

    return (

        <div className="bg-[#272B3D] flex flex-col items-center justify-start rounded-4xl p-2.75 text-white">
            <div className="flex items-center w-full bg-[#2F3347] h-auto p-2.75 text-4xl font-light box-border rounded-[1.2rem] gap-2.75 mb-2.75">
                <label htmlFor="recipientName">To:</label>
                <input type="text" id="recipientName" className="w-full h-full box-border rounded-[1.2rem] border-0 bg-[#2F3347] text-[30px] text-white focus:outline-none"/>
            </div>
            <div className="flex flex-col p-2.75 w-full bg-[#2F3347] box-border rounded-[1.2rem]">
                <p className="text-2xl mt-1.25 mb-3.75">Suggestions:</p>
                {userNames}
            </div>
        </div>
    )
}