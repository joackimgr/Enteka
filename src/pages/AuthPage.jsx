import { useState } from "react"
import LoginForm from "../components/LoginForm"
import SignUpForm from "../components/SignUpForm"

export default function AuthPage(props) {
    const [showSignUp, setShowSignUp] = useState(false)

    function toggleSwitch() {
        setShowSignUp(prevState => !prevState)
    }

    return (
        <section className="bg-[#272B3D] h-full rounded-4xl flex-1 flex flex-col items-center justify-center min-h-150">
            {showSignUp
                ? <SignUpForm onSwitch = {toggleSwitch} isAuthenticated={props.isAuthenticated}/>
                : <LoginForm onSwitch = {toggleSwitch} isAuthenticated={props.isAuthenticated}/>
            }
        </section>
    )
}