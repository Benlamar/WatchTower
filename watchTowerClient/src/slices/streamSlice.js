import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    roomid: 0,
    publishers: 0,
};

export const streamSlice = createSlice({
    name: "stream",
    initialState,
    reducers: {
        setRoomID: (state, action) => {
            state.roomid = action.payload.roomid
        },
        setPublishers: (state, action) => {
            state.publishers = action.payload.publishers
        }
    }
});

export const {setRoomID, setPublishers} = streamSlice.actions;
export default streamSlice.reducer;