import { createStore } from 'vuex'


// Create a new store instance.
export const store = createStore({
    state : {
        currentLevel: 0,
        nextTrips: [],
        moving: false
    },
    getters:{
        currentLevel (state){
            return state.currentLevel
        },
        nextTrips (state){
            return state.nextTrips
        },
        isMoving (state){
            return state.moving
        },
        isActive: (state) => (floor) => {
            return state.nextTrips.includes(floor)
        }
    },
    mutations: {
        updateState (state, newState){
            state.moving = newState.moving
            state.nextTrips = newState.next
            state.currentLevel = newState.currentLevel
        },
        updateLevel(state, message){
            console.log(message)
            state.currentLevel = message.currentLevel
        }
    }
})

