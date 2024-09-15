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
      state.roomid = action.payload.roomid;
    },
    setPublishers: (state, action) => {
      state.publishers = action.payload.publishers;
    },
    clearStream: (state) => {
      state.roomId = 0;
      state.publishers = 0;
    },
  },
});

export const { setRoomID, setPublishers, clearStream } = streamSlice.actions;
export default streamSlice.reducer;
