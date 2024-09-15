import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  user: "",
  auth: false,
  role: "",
  accessToken: null,
};

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setAuth: (state, action) => {
      // console.log("Action ",action.payload);
      const { user, auth, role, accessToken } = action.payload;
      state.user = user;
      state.auth = auth;
      state.role = role;
      state.accessToken = accessToken;
    },
    clearAuth: (state) => {
      state.user = "";
      state.auth = false;
      state.role = "";
      state.accessToken = null;
    },
  },
});

export const { setAuth, clearAuth } = authSlice.actions;
// export const { setAuth } = authSlice.actions;

export default authSlice.reducer;
