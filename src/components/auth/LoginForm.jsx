import { useState } from "react"
import logo from "../../assets/EntekaLogo.png"
import { useNavigate } from "react-router-dom"
import { loginDataPython } from "../api/client"
import { Eye, EyeOff } from "lucide-react"

export default function LoginForm({onSwitch, setIsAuthenticated, setUserName}) {
    let navigate = useNavigate()

    const [formData, setFormData] = useState({
        username: '',
        password: ''
    })

    const [errorMessage, setErrorMessage] = useState('')
    const [showPassword, setShowPassword] = useState(false)

    async function handleSubmit(e) {
        e.preventDefault()
        let data = await loginDataPython(formData)
        if (data.auth) {
            setErrorMessage("")
            setIsAuthenticated(true)
            setUserName(formData.username)
            localStorage.setItem("token", data.token)
            navigate("/home")
        }
        else {
            setErrorMessage(data.message)
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    return <form onSubmit={handleSubmit}  id="logInForm" className="flex flex-col bg-[#272B3D] justify-center items-center w-112.5 h-129.5 my-5 mx-auto rounded-[1.6rem] gap-4"> 
            <img src={logo} alt="EntekaLogo" id="logoOnLogInForm" className="mt-6" width={95} height={95}></img>
            
            <label htmlFor="logInUsername" className="text-2xl text-[#F0F0F5]">Username</label>
            <input value={formData.username} type="text" name="username" id="logInUsername" onChange={handleChange} className="w-62.5 text-[#F0F0F5] border-none rounded-[1.1rem] h-9.25 bg-[#2F3347] p-0 box-border focus:outline-none pl-3.5 focus:box-border" required/>
            
            <label htmlFor="logInPassword" className="text-2xl text-[#F0F0F5]">Password</label>
            <div className="relative w-62.5">
                <input value={formData.password} type={showPassword ? "text" : "password"} name="password" id="logInPassword" onChange={handleChange}
                    className="w-full text-[#F0F0F5] border-none rounded-[1.1rem] h-9.25 bg-[#2F3347] p-0
                    box-border focus:outline-none pl-3.5 pr-10 focus:box-border" required />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[#9B9DB8] hover:text-white">
                    {showPassword ?  <Eye size={20} /> : <EyeOff size={20} /> }
                </button>
            </div>            
            {errorMessage &&
                <p className="text-red-400 text-sm">{errorMessage}</p>
            }
            <p className="my-2.5 text-xl text-[#F0F0F5]">Don't have an account? <span id="signUp" onClick={onSwitch} className="cursor-pointer text-[#7C6AF7]">Sign Up!</span></p>
           
            <input type="submit" value="Login" id="logInBtn" className="w-30 h-12.5 text-xl border-none rounded-[1.2rem] bg-[#7C6AF7] mb-4.5 cursor-pointer transition-colors hover:bg-[#6A59E0]"/>
         </form>
}