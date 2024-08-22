import React, { useRef, useState } from 'react'
import { setAuth } from "../../slices/authSlice";
import {useDispatch, useSelector}  from 'react-redux';

const Login = () => {
  const username_ref = useRef("");
  const password_ref = useRef("");

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState([])

  const auth = useSelector(state => state);
  const dispatch = useDispatch();

  const handleLogin = async (e) => {
    e.preventDefault();
    const errors = []
    if (username_ref.current.value.length === 0) {
      errors.push("Username cannot be empty!")
    }
    if (password_ref.current.value.length === 0) {
      errors.push("Password cannot be empty!")
    }
    if (errors.length) {
      errors.forEach(error => {
        console.errors("Error: " + error)
      });
      setErrors(errors)
      return;
    }
    // console.log("Starting to send login request")
    setLoading(true);
    try {
      dispatch(setAuth({user:username_ref.current.value, role:"normal", auth:true}));
    }
    catch (err) {
      console.log(err)
    }
    finally {
      setLoading(false)
    }
  };


  return (
    <div className='login-page'>
      <div className="text-4xl page-header font-semibold text-gray-900 text-center">Login</div>

      <div className='flex p-4 justify-center mt-8'>

        <form className='border border-gray-200 shadow-sm rounded p-4 min-w-80 w-2/5'>
          <div className="flex flex-col">
            <label htmlFor="username" className='ps-1 text-sm font-medium leading-6 text-gray-900'>Username</label>
            <div className=' flex ease-in duration-200 focus-within:border-b focus-within:border-lime-500'>
              <input ref={username_ref} type="text" name="username" id="username" autoComplete="username" className="bg-gray-100 p-1 w-full rounded font-light text-black focus:outline-none focus:ring-0 placeholder:text-gray-500" placeholder="Enter username" />
            </div>
          </div>

          <div className="flex flex-col mt-2">
            <label htmlFor="password" className='ps-1 text-sm font-medium leading-6 text-gray-900'>Password</label>
            <div className='flex ease-in duration-200 focus-within:border-b focus-within:border-lime-500'>
              <input ref={password_ref} type={showPassword ? "text" : "password"} name="password" autoComplete="current-password" id="password" className="bg-gray-100 p-1 w-full rounded font-light text-black focus:outline-none focus:ring-0 placeholder:text-gray-500" placeholder="Enter password" />
            </div>
          </div>

          <div className="flex mt-2 gap-2">
            <input type="checkbox" checked={showPassword} onChange={() => setShowPassword(!showPassword)} />
            <label className='text-sm text-gray-600'>Show password</label>
          </div>

          <div className="flex gap-2 mt-6">
            <div className={`flex items-center rounded ${loading ? 'bg-gray-600' : 'bg-lime-800 hover:bg-lime-900'}`}>
              <svg aria-hidden="true" className={`inline h-4  text-slate-50 dark:text-gray-600 fill-lime-700 
                  ${loading ? `animate-spin w-4 ms-2` : `w-0 ms-0`}`}
                viewBox="0 0 100 101"
                fill="none"
                xmlns="http://www.w3.org/2000/svg">

                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
              </svg>
              <button className="px-2 py-1 text-white" type="submit" disabled={loading} onClick={e => handleLogin(e)}>{loading ? "Logging" : "Login"}</button>
            </div>

            {/* <div className="mx-2 flex items-center gap-2"> */}
            {/* <span className='text-gray-800 text-sm font-light'>logging in ...</span>
            </div> */}
          </div>

          <button type="button" className='text-red-800 mt-3 text-sm font-normal underline hover:text-red-900'>Forgot password</button>
        </form>
      </div>

      <div className="flex justify-center">
        <ul className='text-red-800 list-none p-0 m-0 text-center'>
          {errors.map((value, index) => (
            <li key={index}>{value}</li>
          ))}
        </ul>
      </div>

    </div>
  )
}

export default Login