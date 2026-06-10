import { Cog } from "lucide-react"

export default function SettingsPanel(props) {
    const options = ["username", "password", "email", "profile picture"]

    const optionsItems = options.map((i) => {
        return (
            <div key={i} className="bg-[#2F3347] rounded-[1.2rem] p-5 box-border h-auto text-3xl w-full flex justify-center cursor-pointer hover:bg-[#363B52] transition-colors duration-100 ease-in">
                <p className="text-white m-0 font-light">{`Change your ${i}.`}</p>
            </div>
        )
    })


    return (
        <>
            {!props.activeSettings && 
                <div className="flex items-center justify-center">
                    <Cog size={200} alt="Settings Icon" className="text-white"/>
                </div>
            }
            {props.activeSettings && 
                <div className="bg-[#272B3D] rounded-[1.2rem] p-2.75 flex flex-col items-center gap-2.75">
                    {optionsItems}
                </div>
            }
        </>
    )
}