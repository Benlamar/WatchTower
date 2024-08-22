import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    user: "",
    auth: "",
    role: ""
};

export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setAuth: (state, action) => {
            // console.log("Action -->",action.payload)
            state.user = action.payload.user
            state.auth = action.payload.auth
            state.role = action.payload.role
        }
    }
});

export const { setAuth } = authSlice.actions
export default authSlice.reducer